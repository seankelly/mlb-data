"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from collections import defaultdict
from datetime import date
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
            game_groups = map(lambda g: h5_file[path + '/' + g], matching_games)
            affected_players = summarize_years_games(h5_file, game_groups)
            merge_players(h5_file, year, affected_players)

def summarize_years_games(h5_file, games):
    players = defaultdict(
        lambda: {
            'offense': np.zeros(shape=len(stat_map['off']), dtype='i2'),
            'defense': np.zeros(shape=len(stat_map['def']), dtype='i2'),
        }
    )
    pa_idx = stat_map['off']['PA']
    run_idx = stat_map['off']['R']
    rbi_idx = stat_map['off']['RBI']
    ab_idx = stat_map['off']['AB']
    sh_idx = stat_map['off']['SH']
    sf_idx = stat_map['off']['SF']
    for game in games:
        for event in game['events']:
            involved = players_involved(event)

            players[involved[1]]['defense'][def_idx] += 1
            players[involved['batter']]['offense'][off_idx] += 1
            players[involved['batter']]['offense'][pa_idx] += 1
            # Field 36 indicates whether the event counts as an official at bat.
            # Use that instead of trying to calculate it. The one downside is if
            # trying to apply historical rules since Chadwick uses modern rules.
            if event[36]:
                players[involved['batter']]['offense'][ab_idx] += 1
            if event[38]:
                players[involved['batter']]['offense'][sh_idx] += 1
            if event[39]:
                players[involved['batter']]['offense'][sf_idx] += 1
            # Field 43 is the RBI on play.
            if event[43] > 0:
                players[involved['batter']]['offense'][rbi_idx] += event[43]
            if event[58] >= 4:
                players[involved['batter']]['offense'][run_idx] += 1
            if event[59] >= 4:
                players[involved['base1']]['offense'][run_idx] += 1
            if event[60] >= 4:
                players[involved['base2']]['offense'][run_idx] += 1
            if event[61] >= 4:
                players[involved['base3']]['offense'][run_idx] += 1
    return players

def merge_players(h5_file, year, players):
    for playerid in players:
        stats = players[playerid]
        player_season = '/stats/{0}/{1}'.format(playerid, year)
        # If there are already stats for this player's season, add the existing
        # stats to the new stats and store that.
        offense = stats['offense']
        defense = stats['defense']
        if player_season in h5_file:
            season_group = h5_file[player_season]
            offense += np.array(season_group['offense'], dtype='i2')
            defense += np.array(season_group['defense'], dtype='i2')
            del season_group['offense'], season_group['defense']
        else:
            season_group = h5_file.create_group(player_season)
        season_group.create_dataset('offense', data=stats['offense'])
        season_group.create_dataset('defense', data=stats['defense'])

def players_involved(event):
    players = {
        'batter': event[12],
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

def simple(stat):
    """
    Most plays involve stats for just the batter and pitcher.
    """
    off_idx = stat_map['off'][stat]
    pa_idx = stat_map['off']['PA']
    run_idx = stat_map['off']['R']
    rbi_idx = stat_map['off']['RBI']
    ab_idx = stat_map['off']['AB']
    sh_idx = stat_map['off']['SH']
    sf_idx = stat_map['off']['SF']
    def_idx = stat_map['def'][stat]
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][def_idx] += 1
        players[involved['batter']]['offense'][off_idx] += 1
        players[involved['batter']]['offense'][pa_idx] += 1
        # Field 36 indicates whether the event counts as an official at bat.
        # Use that instead of trying to calculate it. The one downside is if
        # trying to apply historical rules since Chadwick uses modern rules.
        if event[36]:
            players[involved['batter']]['offense'][ab_idx] += 1
        if event[38]:
            players[involved['batter']]['offense'][sh_idx] += 1
        if event[39]:
            players[involved['batter']]['offense'][sf_idx] += 1
        # Field 43 is the RBI on play.
        if event[43] > 0:
            players[involved['batter']]['offense'][rbi_idx] += event[43]
        if event[58] >= 4:
            players[involved['batter']]['offense'][run_idx] += 1
        if event[59] >= 4:
            players[involved['base1']]['offense'][run_idx] += 1
        if event[60] >= 4:
            players[involved['base2']]['offense'][run_idx] += 1
        if event[61] >= 4:
            players[involved['base3']]['offense'][run_idx] += 1
    return handle_event

def baserunning(stat, offset):
    """
    For base-running, need to credit the runner and maybe catcher.
    """
    off_idx = stat_map['off'][stat]
    def_idx = stat_map['def'][stat]
    def handle_event(players, involved, event):
        pitcher = players[involved[1]]['defense']
        catcher = players[involved[2]]['defense']
        if event[offset]:
            players[involved['base1']]['offense'][off_idx] += 1
            pitcher[def_idx] += 1
            catcher[def_idx] += 1
        if event[offset+1]:
            players[involved['base2']]['offense'][off_idx] += 1
            pitcher[def_idx] += 1
            catcher[def_idx] += 1
        if event[offset+2]:
            players[involved['base3']]['offense'][off_idx] += 1
            pitcher[def_idx] += 1
            catcher[def_idx] += 1
    return handle_event

def error(stat):
    def_idx = stat_map['def'][stat]
    pa_idx = stat_map['off']['PA']
    ab_idx = stat_map['off']['AB']
    def handle_event(players, involved, event):
        if event[36]:
            # If it's an at bat, then it's also a plate appearance.
            players[involved['batter']]['offense'][pa_idx] += 1
            players[involved['batter']]['offense'][ab_idx] += 1
        # 52 is first player with error, 54 is second player, and 56 is third
        # player with error.
        if event[52] != 0:
            players[involved[event[52]]]['defense'][def_idx] += 1
        if event[54] != 0:
            players[involved[event[54]]]['defense'][def_idx] += 1
        if event[56] != 0:
            players[involved[event[56]]]['defense'][def_idx] += 1
    return handle_event

def pitching(stat):
    """
    For handling events where stats are primarily marked against the pitcher
    and catcher.
    """
    def_idx = stat_map['def'][stat]
    rbi_idx = stat_map['off']['RBI']
    run_idx = stat_map['off']['R']
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][def_idx] += 1
        players[involved[2]]['defense'][def_idx] += 1
        if event[43] > 0:
            players[involved['batter']]['offense'][rbi_idx] += event[43]
        if event[58] >= 4:
            players[involved['batter']]['offense'][run_idx] += 1
        if event[59] >= 4:
            players[involved['base1']]['offense'][run_idx] += 1
        if event[60] >= 4:
            players[involved['base2']]['offense'][run_idx] += 1
        if event[61] >= 4:
            players[involved['base3']]['offense'][run_idx] += 1
    return handle_event

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

stat_map = {'off': {}, 'def': {}}
event_types = {}

def populate_stats_map():
    offense, defense = get_stats_mapping()
    for stat in offense:
        stat_map['off'][stat] = offense[stat]
    for stat in defense:
        stat_map['def'][stat] = defense[stat]

def populate_event_types():
    global event_types
    event_types = {
        0: None, # Unknown (obsolete)
        1: None, # None (obsolete)
        2: 'O', # Generic out
        3: 'K', # Strikeout
        4: 'SB', # Stolen base
        5: None, # Defensive indifference
        6: 'CS', # Caught stealing
        7: None, # Pickoff error (obsolete
        8: 'PO', # Pickoff
        9: 'WP', # Wild pitch
        10: 'PB', # Passed ball
        11: None, # Balk
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
