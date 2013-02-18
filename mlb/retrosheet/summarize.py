"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

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
            summarize_years_games(h5_file, game_groups)

def summarize_years_games(h5_file, games):
    players = {}
    for game in games:
        for event in game['events']:
            involved = players_involved(event)
            batter = event[12]
            pitcher = event[16]
            event_type = event[34]

def players_involved(event):
    players = {
        'batter': event[12],
        'pitcher': event[16],
    }
    for pos in range(2, 10):
        # Catcher, position 2, is at index 18.
        players[pos] = event[16+pos]
    return players
