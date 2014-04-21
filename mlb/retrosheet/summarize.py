"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from collections import defaultdict
from datetime import date
from itertools import chain
from mlb.retrosheet.chadwick import Chadwick
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
            lambda: {
                'offense': defaultdict(int),
                'pitching': defaultdict(int),
                'fielding': defaultdict(lambda: defaultdict(int)),
            }
        )
        self.stats = {
            'offense': set(['G', 'GS', 'PA', 'AB', 'R', '1B', '2B', '3B', 'HR', 'ROE', 'RBI', 'K', 'BB', 'IBB', 'HBP', 'O', 'SF', 'SH', 'SB', 'CS', 'PO',]),
            'pitching': set(['G', 'GS', 'GF', 'CG', 'SHO', 'W', 'L', 'S', 'O', 'R', 'ER', 'K', 'BB', 'IBB', 'HBP', 'BK', 'SB', 'CS', 'WP', '1B', '2B', '3B', 'HR', 'GDP', 'ROE',]),
            'fielding': set(['G', 'GS', 'Pos', 'O', 'Ch', 'PO', 'A', 'E', 'DP', 'SB', 'CS', 'WP', 'PB', 'Pickoff',]),
        }
        self.event_types = {
            0: None, # Unknown (obsolete)
            1: None, # None (obsolete)
            2: 'O', # Generic out
            3: 'K', # Strikeout
            4: None, #'SB', # Stolen base
            5: None, # Defensive indifference
            6: None, #'CS', # Caught stealing
            7: None, # Pickoff error (obsolete)
            8: None, #'PO', # Pickoff
            9: 'WP', # Wild pitch
            10: 'PB', # Passed ball
            11: 'BK', # Balk
            12: None, # Other advance/out advancing
            13: None, # Foul error
            14: 'BB', # Unintentional walk
            15: 'IBB', # Intentional walk
            16: 'HBP', # Hit by pitch
            17: None, # Interference
            18: 'E', # Error
            19: 'O', # Fielder's choice
            20: '1B', # Single
            21: '2B', # Double
            22: '3B', # Triple
            23: 'HR', # Home run
            24: None, # Missing play (obsolete)
        }

    def process(self, game):
        """
        Process a game's worth of events.
        """
        year, gameid, game_info, events = game
        self.summarize_game_info(game_info)

    def summarize_game_info(self, game_info):
        """
        Summarize information about one game from cwgame.
        """
        players = self.players
        # Credit non-pitchers with a game started.
        for idx in range(46, 81, 2):
            pos = game_info[idx+1]
            if pos == 1:
                continue
            players[game_info[idx]]['offense']['GS'] += 1
            players[game_info[idx]]['fielding'][pos]['GS'] += 1
        # Credit pitcher win, loss, and save.
        players[game_info[42]]['pitching']['W'] += 1
        players[game_info[43]]['pitching']['L'] += 1
        players[game_info[44]]['pitching']['S'] += 1
        # Credit game starters and finishers.
        players[game_info[10]]['pitching']['GS'] += 1
        players[game_info[11]]['pitching']['GS'] += 1
        # If there's no finishing pitcher, then it's a complete game.
        for gf_idx, gs_idx, other_score in [[82, 10, 35], [83, 11, 34]]:
            if game_info[gf_idx]:
                players[game_info[gf_idx]]['pitching']['GF'] += 1
            else:
                players[game_info[gs_idx]]['pitching']['CG'] += 1
                # Check if it's a shutout.
                if game_info[other_score] == 0:
                    players[game_info[gs_idx]]['pitching']['SHO'] += 1

    def summarize_game_events(self, events):
        # Keep track of all players that appear in this game.
        appeared = {
            'offense': set(),
            'pitching': set(),
            # Ignore the zero index. 1-10 are the indices that matter.
            'fielding': [set() for x in xrange(11)],
        }
        for event in events:
            involved = self.players_involved(event)
            self._summarize_event_batter(event, appeared, involved)
            self._summarize_event_baserunning(event, involved)
            self._summarize_event_pitching(event, appeared, involved)
            self._summarize_event_defense(event, involved)
        self._summarize_game_appearances(appeared)

    def _summarize_event_batter(self, event, appeared, involved):
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
            players[batter]['offense'][stat] += 1
        # Field 36 indicates whether the event counts as an official at
        # bat. Use that instead of trying to calculate it. The one
        # downside is if trying to apply historical rules since Chadwick
        # uses modern rules.
        if event[36]:
            players[batter]['offense']['PA'] += 1
            players[batter]['offense']['AB'] += 1
        elif event[38]:
            players[batter]['offense']['PA'] += 1
            players[batter]['offense']['SH'] += 1
        elif event[39]:
            players[batter]['offense']['PA'] += 1
            players[batter]['offense']['SF'] += 1
        elif 14 <= event[34] <= 16:
            players[batter]['offense']['PA'] += 1
        # Field 43 is the RBI on play.
        players[involved['batter']]['offense']['RBI'] += event[43]

    def _summarize_event_baserunning(self, event, involved):
        players = self.players
        # Base running accounting. The batter is included when calculating
        # scoring a run.
        # Count up runs scored and the pitcher resonsible for it.
        for idx in [58, 59, 60, 61]:
            if event[idx] >= 4:
                base = 'base' + str(idx-58)
                players[involved[base]]['offense']['R'] += 1
                if idx > 58:
                    charged_pitcher = event[75+idx-59]
                else:
                    charged_pitcher = involved[1]
                players[charged_pitcher]['pitching']['R'] += 1
                # Code of 5 means the run is unearned.
                if event[idx] != 5:
                    players[charged_pitcher]['pitching']['ER'] += 1

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
                    players[involved[base]]['offense'][br_stat] += 1

    def _summarize_event_pitching(self, event, appeared, involved):
        players = self.players
        # FIXME
        pitcher_stats = set([3, 9, 11, 14, 15, 16, 20, 21, 22, 23])
        # Pitcher accounting.
        if event[34] in pitcher_stats:
            stat = self.event_types[event[34]]
            players[involved[1]]['pitching'][stat] += 1
        # Field 40 is number of outs in the event. None of the other stats
        # affect the 'O' field for the pitcher.
        appeared['pitching'].add(involved[1])
        players[involved[1]]['pitching']['O'] += event[40]
        for pos in xrange(2, 10):
            p = involved[pos]
            appeared['fielding'][pos].add(p)
            players[p]['fielding'][pos]['O'] += event[40]

    def _summarize_event_defense(self, event, involved):
        players = self.players
        # Defense accounting.
        # Track WP and PB for catchers.
        if event[44]:
            players[involved[2]]['fielding'][2]['WP'] += 1
        if event[45]:
            players[involved[2]]['fielding'][2]['PB'] += 1
        if event[52] != 0:
            players[involved[event[52]]]['fielding'][event[52]]['E'] += 1
        if event[54] != 0:
            players[involved[event[54]]]['fielding'][event[54]]['E'] += 1
        if event[56] != 0:
            players[involved[event[56]]]['fielding'][event[56]]['E'] += 1
        # Record who got the putouts.
        for idx in xrange(88, 91):
            if event[idx] != 0:
                pos = event[idx]
                player = involved[pos]
                players[player]['fielding'][pos]['PO'] += 1
                # Fields 41 and 42 are the double play and triple play
                # turned flags.
                if event[41] or event[42]:
                    players[player]['fielding'][pos]['DP'] += 1
        # Record all of the assists, if any.
        for idx in xrange(91, 96):
            if event[idx] != 0:
                pos = event[idx]
                players[involved[pos]]['fielding'][pos]['A'] += 1

    def _summarize_game_appearances(self, appeared):
        players = self.players
        # Credit each player with a game played at the appropriate position(s).
        # Iterate in a specific order.
        for idx, what in enumerate(['offense', 'pitching']):
            for player in appeared[what]:
                players[player][what]['G'] += 1
        # Fielding requires indexing position, so put in a different loop.
        for pos in xrange(1, 11):
            for player in appeared['fielding'][pos]:
                players[player]['fielding'][pos]['G'] += 1

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


def summarize_games(h5_file, start, end, leagues=('mlb',)):
    populate_stats_map()
    populate_event_types()
    def game_matches(gameid):
        game_date = [int(gameid[3:7]), int(gameid[7:9]), int(gameid[9:11])]
        d = date(*game_date)
        return start <= d <= end

    start_year = start.year
    end_year = end.year
    for league in leagues:
        for year in range(start_year, end_year+1):
            # Get all games in this league's year that fit between the start
            # and end dates.
            path = '/games/{0}/{1}'.format(league, year)
            if path not in h5_file:
                continue
            games = h5_file[path]
            matching_games = filter(game_matches, games.keys())
            affected_players = summarize_years_games(h5_file, path, matching_games)
            merge_players(h5_file, year, affected_players)

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
