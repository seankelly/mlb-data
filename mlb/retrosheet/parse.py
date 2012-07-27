"""
All Retrosheet parsing requires Chadwick.

http://chadwick.sourceforge.net
"""

import csv
import os
import re
import subprocess

def game_info(event_files):
    """
    Parse the event files to create game summaries.
    """
    # Since Chadwick requires the roster files to be in the current directory,
    # change directory to the event files to parse before parsing.
    info = {}
    start_cwd = os.getcwd()
    # Need to get the year to tell cwgame what year roster to look up.
    get_year = re.compile('^(\d+)')
    games = 0
    for f in event_files:
        file_dir, base_file = os.path.split(f)
        Y = get_year.match(base_file)
        year = Y.group(1)
        if year not in info:
            info[year] = []
        os.chdir(file_dir)
        cwgame = ['cwgame', '-y', year, base_file]
        p = subprocess.Popen(cwgame, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        # Ignore stderr. I don't want it echoed or merged with stdout.
        for game in p.stdout.readlines():
            info[year].append(game)
        os.chdir(start_cwd)
    return info

def parse_game_info(hdf5_file, event_files):
    csv_info = game_info(event_files)
    for year in csv_info:
        info = csv.reader(csv_info[year])
