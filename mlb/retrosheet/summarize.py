"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from collections import defaultdict
from mlb.retrosheet.chadwick import Chadwick
from itertools import chain
import numpy as np

def summarize_stats(args, extra_args):
    summary = SeasonSummary()
    for game in Chadwick(extra_args):
        summary.process(game)

class SeasonSummary():
    def __init__(self):
        # Create nested defaultdicts. The offense and pitching keys contain
        # stats accumulated while the player was in that role. Fielding is a
        # dict where the keys are the position and each position has keys for
        # the stats accumulated while the player was at that position.
        self.players = defaultdict(
            # First step maps year to stats.
            lambda: defaultdict(
                # Second step maps type of stats to the stats themselves.
                lambda: {
                    'offense': defaultdict(int),
                    'pitching': defaultdict(int),
                    'fielding': defaultdict(lambda: defaultdict(int)),
                }
            )
        )
        # Only the offense key is used.
        self.stats = {
            'offense': set(['G', 'GS', 'PA', 'AB', 'R', '1B', '2B', '3B', 'HR', 'ROE', 'RBI', 'K', 'BB', 'IBB', 'HBP', 'O', 'SF', 'SH', 'SB', 'CS', 'PO',]),
            'pitching': set(['G', 'GS', 'GF', 'CG', 'SHO', 'W', 'L', 'S', 'O', 'R', 'ER', 'K', 'BB', 'IBB', 'HBP', 'BK', 'SB', 'CS', 'WP', '1B', '2B', '3B', 'HR', 'GDP', 'ROE',]),
            'fielding': set(['G', 'GS', 'Pos', 'O', 'Ch', 'PO', 'A', 'E', 'DP', 'SB', 'CS', 'WP', 'PB', 'Pickoff',]),
        }
        self.event_types = [
            None, # 0: Unknown (obsolete)
            None, # 1: None (obsolete)
            'O', # 2: Generic out
            'K', # 3: Strikeout
            None, # 4: 'SB', # Stolen base
            None, # 5: Defensive indifference
            None, # 6: 'CS', # Caught stealing
            None, # 7: Pickoff error (obsolete)
            None, # 8: 'PO', # Pickoff
            'WP', # 9: Wild pitch
            'PB', # 10: Passed ball
            'BK', # 11: Balk
            None, # 12: Other advance/out advancing
            None, # 13: Foul error
            'BB', # 14: Unintentional walk
            'IBB', # 15: Intentional walk
            'HBP', # 16: Hit by pitch
            None, # 17: Interference
            'E', # 18: Error
            'O', # 19: Fielder's choice
            '1B', # 20: Single
            '2B', # 21: Double
            '3B', # 22: Triple
            'HR', # 23: Home run
            None, # 24: Missing play (obsolete)
        ]

    def process(self, game):
        """
        Process a game's worth of events.
        """
        year, gameid, game_info, events = game
        self.summarize_game_info(year, game_info)
        self.summarize_game_events(year, events)

    def summarize_game_info(self, year, game_info):
        """
        Summarize information about one game from cwgame.
        """
        players = self.players
        # Credit non-pitchers with a game started.
        for idx in range(46, 81, 2):
            pos = game_info[idx+1]
            if pos == 1:
                continue
            players[game_info[idx]][year]['offense']['GS'] += 1
            players[game_info[idx]][year]['fielding'][pos]['GS'] += 1
        # Credit pitcher win, loss, and save.
        players[game_info[42]][year]['pitching']['W'] += 1
        players[game_info[43]][year]['pitching']['L'] += 1
        players[game_info[44]][year]['pitching']['S'] += 1
        # Credit game starters and finishers.
        players[game_info[10]][year]['pitching']['GS'] += 1
        players[game_info[11]][year]['pitching']['GS'] += 1
        # If there's no finishing pitcher, then it's a complete game.
        for gf_idx, gs_idx, other_score in [[82, 10, 35], [83, 11, 34]]:
            if game_info[gf_idx]:
                players[game_info[gf_idx]][year]['pitching']['GF'] += 1
            else:
                players[game_info[gs_idx]][year]['pitching']['CG'] += 1
                # Check if it's a shutout.
                if game_info[other_score] == 0:
                    players[game_info[gs_idx]][year]['pitching']['SHO'] += 1

    def summarize_game_events(self, year, events):
        # Keep track of all players that appear in this game.
        appeared = {
            'offense': set(),
            'pitching': set(),
            # Ignore the zero index. 1-10 are the indices that matter.
            'fielding': [set() for x in xrange(11)],
        }
        for event in events:
            involved = self.players_involved(event)
            self._summarize_event_batter(year, event, appeared, involved)
            self._summarize_event_baserunning(year, event, involved)
            self._summarize_event_pitching(year, event, appeared, involved)
            self._summarize_event_defense(year, event, involved)
        self._summarize_game_appearances(year, appeared)

    def _summarize_event_batter(self, year, event, appeared, involved):
        players = self.players
        batter = involved['batter']
        # Batter accounting.
        appeared['offense'].add(involved['batter'])
        # Add the batter for the defensive position. This is the only way
        # to acount for the DH.
        # 11 is the PH position.
        if event[32] <= 10:
            appeared['fielding'][event[32]].add(involved['batter'])
        stat = self.event_types[event[34]]
        if stat and stat in self.stats['offense']:
            players[batter][year]['offense'][stat] += 1
        # Field 36 indicates whether the event counts as an official at
        # bat. Use that instead of trying to calculate it. The one
        # downside is if trying to apply historical rules since Chadwick
        # uses modern rules.
        if event[36]:
            players[batter][year]['offense']['PA'] += 1
            players[batter][year]['offense']['AB'] += 1
        elif event[38]:
            players[batter][year]['offense']['PA'] += 1
            players[batter][year]['offense']['SH'] += 1
        elif event[39]:
            players[batter][year]['offense']['PA'] += 1
            players[batter][year]['offense']['SF'] += 1
        elif 14 <= event[34] <= 16:
            players[batter][year]['offense']['PA'] += 1
        # Field 43 is the RBI on play.
        players[involved['batter']][year]['offense']['RBI'] += event[43]

    def _summarize_event_baserunning(self, year, event, involved):
        players = self.players
        # Base running accounting. The batter is included when calculating
        # scoring a run.
        # Count up runs scored and the pitcher resonsible for it.
        for idx in [58, 59, 60, 61]:
            if event[idx] >= 4:
                base = 'base' + str(idx-58)
                players[involved[base]][year]['offense']['R'] += 1
                if idx > 58:
                    charged_pitcher = event[75+idx-59]
                else:
                    charged_pitcher = involved[1]
                players[charged_pitcher][year]['pitching']['R'] += 1
                # Code of 5 means the run is unearned.
                if event[idx] != 5:
                    players[charged_pitcher][year]['pitching']['ER'] += 1

        # Count up base running stats.
        baserunning = [
            ['SB', [66, 67, 68]],
            ['CS', [69, 70, 71]],
            ['PO', [72, 73, 74]],
        ]
        for br_stat, offsets in baserunning:
            offset = offsets[0]
            for idx in offsets:
                if event[idx]:
                    base = 'base' + str(idx-offset+1)
                    players[involved[base]][year]['offense'][br_stat] += 1

    def _summarize_event_pitching(self, year, event, appeared, involved):
        players = self.players
        # These are the indices in event_types that apply to pitchers.
        pitcher_stats = set([3, 9, 11, 14, 15, 16, 20, 21, 22, 23])
        # Pitcher accounting.
        if event[34] in pitcher_stats:
            stat = self.event_types[event[34]]
            players[involved[1]][year]['pitching'][stat] += 1
        # Field 40 is number of outs in the event. None of the other stats
        # affect the 'O' field for the pitcher.
        appeared['pitching'].add(involved[1])
        players[involved[1]][year]['pitching']['O'] += event[40]
        for pos in xrange(2, 10):
            p = involved[pos]
            appeared['fielding'][pos].add(p)
            players[p][year]['fielding'][pos]['O'] += event[40]

    def _summarize_event_defense(self, year, event, involved):
        players = self.players
        # Defense accounting.
        # Track WP and PB for catchers.
        if event[44]:
            players[involved[2]][year]['fielding'][2]['WP'] += 1
        if event[45]:
            players[involved[2]][year]['fielding'][2]['PB'] += 1
        if event[52] != 0:
            players[involved[event[52]]][year]['fielding'][event[52]]['E'] += 1
        if event[54] != 0:
            players[involved[event[54]]][year]['fielding'][event[54]]['E'] += 1
        if event[56] != 0:
            players[involved[event[56]]][year]['fielding'][event[56]]['E'] += 1
        # Record who got the putouts.
        for idx in xrange(88, 91):
            if event[idx] != 0:
                pos = event[idx]
                player = involved[pos]
                players[player][year]['fielding'][pos]['PO'] += 1
                # Fields 41 and 42 are the double play and triple play
                # turned flags.
                if event[41] or event[42]:
                    players[player][year]['fielding'][pos]['DP'] += 1
        # Record all of the assists, if any.
        for idx in xrange(91, 96):
            if event[idx] != 0:
                pos = event[idx]
                players[involved[pos]][year]['fielding'][pos]['A'] += 1

    def _summarize_game_appearances(self, year, appeared):
        players = self.players
        # Credit each player with a game played at the appropriate position(s).
        # Iterate in a specific order.
        for idx, what in enumerate(['offense', 'pitching']):
            for player in appeared[what]:
                players[player][year][what]['G'] += 1
        # Fielding requires indexing position, so put in a different loop.
        for pos in xrange(1, 11):
            for player in appeared['fielding'][pos]:
                players[player][year]['fielding'][pos]['G'] += 1

    def players_involved(self, event):
        players = {
            'batter': event[12],
            'base0': event[12],
            1: event[16],
        }
        for pos in range(2, 10):
            # Catcher, position 2, is at index 18. It goes in order through the
            # right fielder.
            players[pos] = event[16+pos]
        for pos in range(1, 4):
            # Account for the three runners. They are at indices 26-28.
            players['base' + str(pos)] = event[pos+25]
        return players



def merge_players(h5_file, year, players):
    for playerid in players:
        stats = players[playerid]
        player_season = '/stats/{0}/{1}'.format(playerid, year)
        # If there are already stats for this player's season, add the existing
        # stats to the new stats and store that.
        if player_season in h5_file:
            season_group = h5_file[player_season]
            stats['offense'] += np.array(season_group['offense'], dtype='i2')
            stats['pitching'] += np.array(season_group['pitching'], dtype='i2')
            stats['fielding'] = merge_fielding(season_group['fielding'], stats['fielding'])
            del season_group['offense'], season_group['pitching'], season_group['fielding']
        else:
            season_group = h5_file.create_group(player_season)
            stats['fielding'] = merge_fielding({}, stats['fielding'])
        # Don't write stats if they're all zero.
        for k in stats:
            if np.sum(stats[k]) != 0:
                season_group.create_dataset(k, data=stats[k])

def merge_fielding(existing_stats, fielding):
    """
    Merge an existing multi-dimension array in existing_stats of fielding data
    with a dict representation of the new fielding data in fielding.
    """
    # Expand the existing fielding data into a dict representation to make it
    # easier to merge the two.
    old = {}
    for pos in existing_stats:
        old[pos[stat_map[2]['Pos']]] = pos
    positions = set(chain(fielding.keys(), old.keys()))
    merged = np.zeros(shape=(len(positions), len(stat_map[2])), dtype='i2')
    ordered_pos = sorted(list(positions))
    for i, pos in enumerate(ordered_pos):
        if pos in old:
            merged[i] += old[pos]
        if pos in fielding:
            merged[i] += fielding[pos]
        merged[i][stat_map[2]['Pos']] = pos
    return merged
