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
import os, string
from math import atan
from optparse import OptionParser
import matplotlib.pyplot as P

default_colors = {
    'FA': '#008000',
    'FF': '#008000',
    'FT': '#000080',
    'SI': '#000080',
    'FC': '#00FFFF',
    'FS': '#B1E0E6',
    'CH': '#FFA500',
    'CU': '#800080',
    'SL': '#FF0000',
    'KN': '#A52A2A'
}

parser = OptionParser()
parser.add_option("-f", "--file", dest="file", help="SQLite database file")
parser.add_option("-d", "", dest="backend", help="Matplotlib backend")

(options, args) = parser.parse_args()

conn = sqlite3.connect(options.file)

def flatten(L):
    if type(L) != type([]): return [L]
    if L == []: return L
    return flatten(L[0]) + flatten(L[1:])

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

    def all(self, field):
        if len(self.pitches) == 0:
            return []

        return list(pitch[field] for pitch in self.pitches)


class Pitcher(object):
    ignore_types = ['IN', 'PO', 'AB', 'UN']

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
                if pitch['pitch_type'] in self.ignore_types:
                    continue

                if pitch['pitch_type'] not in self.pitches:
                    self.pitches[pitch['pitch_type']] = Pitch(pitch['pitch_type'])

                self.pitches[pitch['pitch_type']].add(pitch)

    def _pitches(self, field, pitch_type):
        if pitch_type:
            if type(pitch_type) == type(u'unicode'):
                pitches = [ self.pitches[pitch_type] ]
            elif type(pitch_type) == type([]):
                pitches = list(self.pitches[t] for t in pitch_type)
            elif type(pitch_type) == type('str'):
                pitches = [ self.pitches[unicode(pitch_type)] ]
            else:
                raise KeyError, "pitch_type not unicode or list"
        else:
            pitches = list(self.pitches[t] for t in self.pitches)
        return pitches

    # Default to merging none of the pitches
    def all(self, field, pitch_type=None):
        return flatten(list(pitch.all(field) for pitch in self._pitches(field, pitch_type)))

    def avg(self, field, pitch_type=None):
        pitches = self.all(field, pitch_type)
        total = sum(pitches)
        count = len(pitches)
        return (total / count)


def map_name(name):
    # Remove punctuation
    pname = str(name)
    tr = string.maketrans('', '')
    pname = pname.translate(tr, string.punctuation)
    # Map spaces to underscores
    pname = pname.replace(' ', '_')
    return pname

def save(name, img_dir, graph_number):
    filename = os.path.join(img_dir, name + graph_number + '.png')
    P.savefig(filename)

def graph_pitcher_card(pitcher, img_dir):
    name = map_name(pitcher.name)

    fig = P.figure(figsize=(5,5), dpi=100)

    def graph(x, y, f=lambda x:x):
        types = pitcher.pitches.keys()
        for t in types:
            P.scatter(map(f, pitcher.all(x, t)), pitcher.all(y, t), c=default_colors[t], edgecolors="none")

    # first vertical vs horizontal movement
    fig.add_axes((0.15, 0.12, 0.75, 0.78), xlim=[-20, 20], xlabel="Horizontal Movement", ylabel="Vertical Movement", ylim=[-20, 20])
    graph('pfx_x', 'pfx_z')
    P.xticks([-20, -10, 0, 10, 20])
    P.yticks([-20, -10, 0, 10, 20])
    save(name, img_dir, '-1')
    fig.clear()

    # second vertical vs horizontal release point
    fig.add_axes((0.15, 0.12, 0.75, 0.78), xlabel="Horizontal Release Point", ylabel="Vertical Release Point")
    graph('x0', 'z0')
    P.xticks([-4, -2, 0, 2, 4])
    P.yticks([0, 2, 4, 6, 8])
    save(name, img_dir, '-2')
    fig.clear()

    # third velocity versus horizontal movement
    fig.add_axes((0.15, 0.12, 0.75, 0.78), xlim=[-20, 20], xlabel="Horizontal Movement", ylabel="Velocity", ylim=[65, 105])
    graph('pfx_x', 'start_speed')
    P.xticks([-20, -10, 0, 10, 20])
    P.yticks([65, 75, 85, 95, 105])
    save(name, img_dir, '-3')
    fig.clear()

    # fourth vertical movement versus velocity
    fig.add_axes((0.15, 0.12, 0.75, 0.78), xlabel="Velocity", xlim=[65, 105], ylim=[-20, 20], ylabel="Vertical Movement")
    graph('start_speed', 'pfx_z')
    P.xticks([65, 75, 85, 95, 105])
    P.yticks([ -20, -10, 0, 10, 20])
    save(name, img_dir, '-4')
    fig.clear()

    # fifth velocity versus spin rate in a polar plot
    fig.add_axes((0.15, 0.15, 0.75, 0.75), projection="polar")
    graph('spin_dir', 'start_speed', lambda x: x*3.14159/180)
    save(name, img_dir, '-5')
    fig.clear()


def build_pitcher_card(pitcher, output_dir, img_dir):
    mlbid = [pitcher]
    row = conn.execute("SELECT name FROM player WHERE mlbid = ?", mlbid)
    name = row.fetchone()
    if not name:
        return
    name = name[0]

    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT pitch.*,atbat.* FROM raw_pitch pitch JOIN atbat ON pitch.atbat = atbat.id WHERE atbat.pitcher = ?", mlbid)
    pitcher = Pitcher(name, row)
    # Ensure there is at least one enhanced pitch
    if pitcher.enhanced == 0:
        return

    graph_pitcher_card(pitcher, img_dir)


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
