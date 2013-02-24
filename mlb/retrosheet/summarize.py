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
    for game in games:
        for event in game['events']:
            allot_event_stats(players, event)
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
    def_idx = stat_map['def'][stat]
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][def_idx] += 1
        players[involved['batter']]['offense'][off_idx] += 1
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
    def handle_event(players, involved, event):
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
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][def_idx] += 1
        players[involved[2]]['defense'][def_idx] += 1
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

def allot_event_stats(players, event):
    """
    Credit/debit the events that happen to the appropriate players.
    The players dict is the overall dict that contains what happens for the
    given players in a year.
    """
    event_type = event[34]
    allot = event_types[event_type]
    if allot:
        involved = players_involved(event)
        allot(players, involved, event)

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
        2: simple('O'), # Generic out
        3: simple('K'), # Strikeout
        4: baserunning('SB', 66), # Stolen base
        5: None, # Defensive indifference
        6: baserunning('CS', 69), # Caught stealing
        7: None, # Pickoff error (obsolete)
        8: pickoff('PO'), # Pickoff
        9: pitching('WP'), # Wild pitch
        10: pitching('PB'), # Passed ball
        11: None, # Balk
        12: None, # Other advance/out advancing
        13: None, # Foul error
        14: simple('BB'), # Unintentional walk
        15: simple('IBB'), # Intentional walk
        16: simple('HBP'), # Hit by pitch
        17: None, # Interference
        18: error('E'), # Error
        19: None, # Fielder's choice
        20: simple('1B'), # Single
        21: simple('2B'), # Double
        22: simple('3B'), # Triple
        23: simple('HR'), # Home run
        24: None, # Missing play (obsolete)
    }
