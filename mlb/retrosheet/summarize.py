"""
Summarize Retrosheet stats into game and season summaries, and splits.
"""

from datetime import datetime

def summarize_stats(args):
    hdf5_file = args['file']
    start_time = args['start']
    end_time = args['end']
    start = datetime.strptime(start_time, '%Y-%m-%d')
    end = datetime.strptime(end_time, '%Y-%m-%d')
    h5_file = h5py.File(hdf5_file)
    summarize_games(h5_file, start, end)
    h5_file.close()

def summarize_games(h5_file, start, end, leagues=('mlb',)):
    pass
