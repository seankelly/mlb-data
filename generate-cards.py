# colors:
# FA: #008000
# FF: 
# FT: #000080
# FC: #00FFFF
# FS: #B1E0E6
# CH: #FFA500
# CU: #800080
# SL: #FF0000
# KN: #A52A2A

import pitchfx
import sqlite3
import os
from optparse import OptionParser
import matplotlib.pyplot as plt

parser = OptionParser()
parser.add_option("-f", "--file", dest="file", help="SQLite database file")
parser.add_option("-d", "", dest="backend", help="Matplotlib backend")

(options, args) = parser.parse_args()

conn = sqlite3.connect(options.file)

class Pitch(object):
    def __init__(self, type):
        self.type = type
        self.total = 0
        self.pitches = []

    def add(self, pitch):
        # Every pitch should be enhanced
        # But check just in case I flub
        if not pitch['enhanced']:
            return
        self.pitches.append(pitch)
        self.total += 1

    def avg(self, field):
        if len(self.pitches) == 0:
            return 0

        total = sum(pitch[field] for pitch in self.pitches)
        return (total / len(self.pitches))


class Pitcher(object):
    def __init__(self, name, cursor):
        self.name = name
        self.pitches = {}
        self.total = 0
        self.enhanced = 0
        for pitch in cursor:
            self.total += 1
            # Can only analyze enhanced pitches
            if pitch['enhanced']:
                self.enhanced += 1
                if pitch['pitch_type'] not in self.pitches:
                    self.pitches[pitch['pitch_type']] = Pitch(pitch['pitch_type'])

                self.pitches[pitch['pitch_type']].add(pitch)


def build_pitcher_card(pitcher, output_dir, img_dir):
    mlbid = [pitcher]
    row = conn.execute("SELECT name FROM player WHERE mlbid = ?", mlbid)
    name = row.fetchone()
    if not name:
        return
    name = name[0]

    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT pitch.* FROM raw_pitch pitch JOIN atbat ON pitch.atbat = atbat.id WHERE atbat.pitcher = ?", mlbid)
    pitcher = Pitcher(name, row)


def build_cards(pitchers):
    output_dir = 'html'
    img_dir = 'html/img'
    if os.path.exists(img_dir) == False:
        os.makedirs(img_dir)

    if not pitchers:
        pitchers = [row[0] for row in conn.execute("SELECT distinct(pitcher) FROM atbat")]

    for pitcher in pitchers:
        build_pitcher_card(pitcher, output_dir, img_dir)


if len(args) > 0:
    build_cards(args)
else:
    build_cards(None)

conn.close()
