"""
All Retrosheet parsing requires Chadwick.

http://chadwick.sourceforge.net
"""

import csv
import os
import re
import subprocess


def parse_files(files):
    retrogames = RetrosheetParser(files)
    retrogames.process()
    return retrogames.games

class RetrosheetParser():
    def __init__(self, event_files):
        self.event_files = event_files
        self.games = []

    def __iter__(self):
        return self.each_pbp_file()

    def process(self):
        for game_events in self.each_pbp_file():
            self.games.append(game_events)

    #def parse_pbp_files(event_files):
    def each_pbp_file(self):
        """
        Parse event files to get the game and event information.
        """
        # Need to get the year to tell cwgame what year roster to look up.
        get_year = re.compile('^(\d+)')
        start_cwd = os.getcwd()
        for f in self.event_files:
            file_dir, base_file = os.path.split(f)
            Y = get_year.match(base_file)
            year = Y.group(1)
            # Since Chadwick requires the roster files to be in the current
            # directory, change directory to the event files to parse before
            # parsing.
            os.chdir(file_dir)
            cwgame = ['cwgame', '-q', '-y', year, base_file]
            # Same as cwgame, except need to explicitly ask for all of the
            # fields.
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
                self.sanitize_game_fields(game)
                gameid = game[0]
                for event in event_csv:
                    self.sanitize_event_fields(event)
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

    def sanitize_game_fields(self, game):
        for index in [5]:
            if game[index] == 'T':
                game[index] = True
            elif game[index] == 'F':
                game[index] = False

    # Fix event to mark all flag fields as True or False.
    def sanitize_event_fields(self, event):
        for index in [30, 31, 35, 36, 37, 38, 39, 41, 42, 44, 45, 48, 49, 66, 67, 68, 69, 70, 71, 72, 73, 74, 78, 79, 80, 81, 82]:
            if event[index] == 'T':
                event[index] = True
            elif event[index] == 'F':
                event[index] = False
