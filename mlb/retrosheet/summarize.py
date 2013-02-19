"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from collections import defaultdict
from datetime import date
import h5py

def summarize_stats(args):
    hdf5_file = args['file']
    start = args['start']
    end = args['end']
    h5_file = h5py.File(hdf5_file)
    summarize_games(h5_file, start, end)
    h5_file.close()

def summarize_games(h5_file, start, end, leagues=('mlb',)):
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

def summarize_years_games(h5_file, games):
    players = defaultdict(
        lambda: {'offense': defaultdict(int), 'defense': defaultdict(int)}
    )
    for game in games:
        for event in game['events']:
            allot_event_stats(players, event)
    return players

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
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][stat] += 1
        players[involved['batter']]['offense'][stat] += 1
    return handle_event

def baserunning(stat, offset):
    """
    For base-running, need to credit the runner and maybe catcher.
    """
    def handle_event(players, involved, event):
        if event[offset]:
            players[involved['base1']]['offense'][stat] += 1
            players[involved[1]]['defense'][stat] += 1
            players[involved[2]]['defense'][stat] += 1
        if event[offset+1]:
            players[involved['base2']]['offense'][stat] += 1
            players[involved[1]]['defense'][stat] += 1
            players[involved[2]]['defense'][stat] += 1
        if event[offset+2]:
            players[involved['base3']]['offense'][stat] += 1
            players[involved[1]]['defense'][stat] += 1
            players[involved[2]]['defense'][stat] += 1
    return handle_event

def pitching(stat):
    """
    For handling events where stats are primarily marked against the pitcher
    and catcher.
    """
    def handle_event(players, involved, event):
        players[involved[1]]['defense'][stat] += 1
        players[involved[2]]['defense'][stat] += 1
    return handle_event

def pickoff(stat):
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
            players[involved['batter']]['offense'][stat] += 1
            players[involved[orig_player]]['defense'][stat] += 1
    return handle_event

event_types = {
    0: None, # Unknown (obsolete)
    1: None, # None (obsolete)
    2: simple('O'), # Generic out
    3: simple('K'),
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
    14: simple('BB'),
    15: simple('IBB'),
    16: simple('IBB'),
    17: None, # Interference
    18: None, # Error
    19: None, # Fielder's choice
    20: simple('1B'),
    21: simple('2B'),
    22: simple('3B'),
    23: simple('HR'),
    24: None, # Missing play (obsolete)
}

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
