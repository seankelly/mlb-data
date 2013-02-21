"""
All Retrosheet parsing requires Chadwick.

http://chadwick.sourceforge.net
"""

import csv
import h5py
import numpy as np
import os
import re
import subprocess
from ..hdf5 import init_hdf5
from .types import cwgame_game_dtype, cwevent_dtype


def parse_retrosheet(hdf5_file, event_files):
    h5_file = h5py.File(hdf5_file)
    init_hdf5(h5_file)
    get_info(h5_file, event_files)
    h5_file.close()

def get_info(h5_file, event_files):
    # Passed an already open HDF5 file, so assume it's been set up in the
    # correct form already.
    mlb_group = h5_file.require_group('/games/mlb')
    event_ds_type = cwevent_dtype()
    game_ds_dtype = cwgame_game_dtype()
    for game_events in parse_pbp_files(event_files):
        (year, gameid, game_data, event_data) = game_events
        year_group = mlb_group.require_group(year)
        game_group = year_group.require_group(gameid)
        np_game = np.array(game_data, dtype=game_ds_dtype)
        game_ds = game_group.create_dataset('game', data=np_game)
        np_events = np.array(event_data, dtype=event_ds_type)
        event_ds = game_group.create_dataset('events', data=np_events,
                                             compression='gzip')

def parse_pbp_files(event_files):
    """
    Parse event files to get the game and event information.
    """
    # Need to get the year to tell cwgame what year roster to look up.
    get_year = re.compile('^(\d+)')
    start_cwd = os.getcwd()
    for f in event_files:
        file_dir, base_file = os.path.split(f)
        Y = get_year.match(base_file)
        year = Y.group(1)
        # Since Chadwick requires the roster files to be in the current
        # directory, change directory to the event files to parse before
        # parsing.
        os.chdir(file_dir)
        cwgame = ['cwgame', '-q', '-y', year, base_file]
        # Same as cwgame, except need to explicitly ask for all of the fields.
        cwevent = ['cwevent', '-q', '-y', year, '-f', '0-96', base_file]
        # Keep stderr separate from stdout. It will be ignored.
        game_proc = subprocess.Popen(cwgame, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        event_proc = subprocess.Popen(cwevent, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        # Iterate over each game in from cwgame (one per line) and match up
        # with the games from cwevent (many per game).
        game_csv = csv.reader(game_proc.stdout.readlines())
        event_csv = csv.reader(event_proc.stdout.readlines())
        events = []
        for game in game_csv:
            sanitize_game_fields(game)
            gameid = game[0]
            for event in event_csv:
                sanitize_event_fields(event)
                if event[0] == gameid:
                    events.append(tuple(event))
                else:
                    break
            game_data = (year, gameid, tuple(game), events)
            yield game_data
            # Reset events and append the event that caused the for loop to
            # break, assuming it exists.
            events = []
            if event:
                events.append(tuple(event))
        os.chdir(start_cwd)

def sanitize_game_fields(game):
    for index in [5]:
        if game[index] == 'T':
            game[index] = True
        elif game[index] == 'F':
            game[index] = False

# Fix event to mark all flag fields as True or False.
def sanitize_event_fields(event):
    for index in [30, 31, 35, 36, 37, 38, 39, 41, 42, 44, 45, 48, 49, 66, 67, 68, 69, 70, 71, 72, 73, 74, 78, 79, 80, 81, 82]:
        if event[index] == 'T':
            event[index] = True
        elif event[index] == 'F':
            event[index] = False
