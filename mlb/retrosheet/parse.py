"""
All Retrosheet parsing requires Chadwick.

http://chadwick.sourceforge.net
"""

import os
import re
import subprocess

def game_info(files):
    """
    Parse the event files to create game summaries.
    """
    # Since Chadwick requires the roster files to be in the current directory,
    # change directory to the event files to parse before parsing.
    info = []
    start_cwd = os.getcwd()
    # Need to get the year to tell cwgame what year roster to look up.
    get_year = re.compile('^(\d+)')
    games = 0
    for f in files:
        file_dir, base_file = os.path.split(f)
        year = get_year.match(base_file)
        os.chdir(file_dir)
        cwgame = ['cwgame', '-y', year.group(1), base_file]
        p = subprocess.Popen(cwgame, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        # Ignore stderr. I don't want it echoed or merged with stdout.
        for game in p.stdout.readlines():
            info.append(game)
        os.chdir(start_cwd)
    return info
