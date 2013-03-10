"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from collections import defaultdict
from datetime import date
from itertools import chain
from .stats import get_stats_mapping
import h5py
import numpy as np

def summarize_stats(args):
    hdf5_file = args['file']
    start = args['start']
    end = args['end']
    h5_file = h5py.File(hdf5_file)
    summarize_games(h5_file, start, end)
    h5_file.close()

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

def summarize_years_games(h5_file, path, games):
    players = defaultdict(
        lambda: {
            'offense': np.zeros(shape=len(stat_map[0]), dtype='i2'),
            'pitching': np.zeros(shape=len(stat_map[1]), dtype='i2'),
            'fielding': defaultdict(lambda: np.zeros(shape=len(stat_map[2]), dtype='i2')),
        }
    )
    pitcher_stats = set([3, 9, 11, 14, 15, 16, 20, 21, 22, 23])
    baserunning = [
        ['SB', [66, 67, 68]],
        ['CS', [69, 70, 71]],
        ['PO', [72, 73, 74]],
    ]
    for game in games:
        h5_game = h5_file[path + '/' + game]
        summarize_game_events(players, h5_game['events'])
    return players

def summarize_game_events(players, events):
    for event in events:
        involved = players_involved(event)
        stat = event_types[event[34]]
        # Batter accounting.
        if stat and stat in stat_map[0]:
            players[involved['batter']]['offense'][stat_map[0][stat]] += 1
        # Field 36 indicates whether the event counts as an official at bat.
        # Use that instead of trying to calculate it. The one downside is if
        # trying to apply historical rules since Chadwick uses modern rules.
        if event[36]:
            players[involved['batter']]['offense'][stat_map[0]['PA']] += 1
            players[involved['batter']]['offense'][stat_map[0]['AB']] += 1
        elif event[38]:
            players[involved['batter']]['offense'][stat_map[0]['PA']] += 1
            players[involved['batter']]['offense'][stat_map[0]['SH']] += 1
        elif event[39]:
            players[involved['batter']]['offense'][stat_map[0]['PA']] += 1
            players[involved['batter']]['offense'][stat_map[0]['SF']] += 1
        elif 14 <= event[34] <= 16:
            players[involved['batter']]['offense'][stat_map[0]['PA']] += 1
        # Field 43 is the RBI on play.
        players[involved['batter']]['offense'][stat_map[0]['RBI']] += event[43]

        # Base running accounting. The batter is included when calculating
        # scoring a run.
        for idx in [58, 59, 60, 61]:
            if event[idx] >= 4:
                base = 'base' + str(idx-58)
                players[involved[base]]['offense'][stat_map[0]['R']] += 1
                if idx > 58:
                    charged_pitcher = event[75+idx-59]
                else:
                    charged_pitcher = involved[1]
                players[charged_pitcher]['pitching'][stat_map[1]['R']] += 1
                # Code of 5 means the run is unearned.
                if event[idx] != 5:
                    players[charged_pitcher]['pitching'][stat_map[1]['ER']] += 1
        for br_stat, offsets in baserunning:
            offset = offsets[0]
            for idx in offsets:
                if event[idx]:
                    base = 'base' + str(idx-offset+1)
                    players[involved[base]]['offense'][stat_map[0][br_stat]] += 1

        # Pitcher accounting.
        if event[34] in pitcher_stats:
            players[involved[1]]['pitching'][stat_map[1][stat]] += 1
        # Field 40 is number of outs in the event. None of the other stats
        # affect the 'O' field for the pitcher.
        players[involved[1]]['pitching'][stat_map[1]['O']] += event[40]
        for pos in xrange(2, 10):
            players[involved[pos]]['fielding'][pos][stat_map[2]['O']] += event[40]

        # Defense accounting.
        # Track WP and PB for catchers.
        if event[44]:
            players[involved[2]]['fielding'][2][stat_map[2]['WP']] += 1
        if event[45]:
            players[involved[2]]['fielding'][2][stat_map[2]['PB']] += 1
        error_idx = stat_map[2]['E']
        if event[52] != 0:
            players[involved[event[52]]]['fielding'][event[52]][error_idx] += 1
        if event[54] != 0:
            players[involved[event[54]]]['fielding'][event[54]][error_idx] += 1
        if event[56] != 0:
            players[involved[event[56]]]['fielding'][event[56]][error_idx] += 1
        # Record who got the putouts.
        for idx in xrange(88, 91):
            if event[idx] != 0:
                players[involved[event[idx]]]['fielding'][event[idx]][stat_map[2]['PO']] += 1
                # Fields 41 and 42 are the double play and triple play
                # turned flags.
                if event[41] or event[42]:
                    players[involved[event[idx]]]['fielding'][event[idx]][stat_map[2]['DP']] += 1
        # Record all of the assists, if any.
        for idx in xrange(91, 96):
            if event[idx] != 0:
                players[involved[event[idx]]]['fielding'][event[idx]][stat_map[2]['A']] += 1

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

def players_involved(event):
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


def pickoff(stat):
    off_idx = stat_map['off'][stat]
    def_idx = stat_map['def'][stat]
    def handle_event(players, involved, event):
        if event[88] != 0:
            # Find the originating assist and credit that player for the
            # pickoff.
            # Start by assuming the player that made the putout originated the
            # pickoff.
            orig_player = event[88]
            for index in range(91, 96):
                if event[index] != 0:
                    orig_player = event[index]
                else:
                    break
            players[involved['batter']]['offense'][off_idx] += 1
            players[involved[orig_player]]['defense'][def_idx] += 1
    return handle_event

stat_map = [{}, {}, {}]
event_types = {}

def populate_stats_map():
    stats = get_stats_mapping()
    for i, what in enumerate(['offense', 'pitching', 'fielding']):
        for stat, index in stats[what].iteritems():
            stat_map[i][stat] = index

def populate_event_types():
    global event_types
    event_types = {
        0: None, # Unknown (obsolete)
        1: None, # None (obsolete)
        2: 'O', # Generic out
        3: 'K', # Strikeout
        4: None, #'SB', # Stolen base
        5: None, # Defensive indifference
        6: None, #'CS', # Caught stealing
        7: None, # Pickoff error (obsolete
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
