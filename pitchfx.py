from HTMLParser import HTMLParser
from datetime import date, datetime, timedelta
from optparse import OptionParser  
from math import atan
import os, re

def flatten(L):
    if type(L) != type([]): return [L]
    if L == []: return L
    return flatten(L[0]) + flatten(L[1:])

def parse_date(date, default=date.today()):
    if date:
        try:
            day = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print "Invalid date given:", date
            raise
    else:
        day = default
    return day


class HTML(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))

    def get_links(self, pattern):
        link_match = re.compile(pattern)
        links = []
        for link in self.links:
            if link_match.match(link['href']):
                links.append(link['href'])

        return links


class PitchFX(object):
    def __init__(self):
        self.start_day = date.today() - timedelta(1)
        self.end_day = date.today()

    def parse_options(self, parser=OptionParser()):
        parser.add_option("-o", "--out", dest="outdir",
                        help="XML saved in this directory")
        parser.add_option("-s", "--start", dest="start_time", metavar="START",
                        help="Start day")
        parser.add_option("-e", "--end", dest="end_time", metavar="END",
                        help="End day")

        (options, args) = parser.parse_args()
        # Default the start day to yesterday
        self.start_day = parse_date(options.start_time, self.start_day)
        # Keep the default end day to be today
        self.end_day = parse_date(options.end_time, self.end_day)

        if self.start_day > self.end_day:
            raise ValueError, "Starting day after ending day"

        if options.outdir:
            self.output_dir = os.path.abspath(options.outdir)
            if os.path.exists(self.output_dir) == False:
                os.makedirs(self.output_dir)
        else:
            raise ValueError, "Output directory not given"

        return args


    def each_day(self):
        current_day = self.start_day
        while current_day < self.end_day:
            yield current_day
            current_day += timedelta(1)


class Pitch(object):
    def __init__(self, type):
        self.type = type
        self.total = 0
        self.pitches = []

    def add(self, pitch_row):
        # Every pitch should be enhanced
        # But check just in case I flub
        if not pitch_row['enhanced']:
            return
        self.pitches.append(pitch_row)
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

    def split(self):
        left = []
        right = []
        for p in self.pitches:
            if p['batter_stand'] == 'R':
                right.append(p)
            else:
                left.append(p)
        return left, right


class Pitcher(object):
    ignore_types = ['IN', 'PO', 'AB', 'UN']
    merge_types = {'SI': 'FT', 'FF': 'FA'}

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
                pitch_type = pitch['pitch_type']
                if pitch_type in self.ignore_types:
                    continue

                # Check if this pitch should be merged with another
                if pitch_type in self.merge_types:
                    pitch_type = self.merge_types[pitch_type]
                if pitch_type not in self.pitches:
                    self.pitches[pitch_type] = Pitch(pitch_type)

                self.pitches[pitch_type].add(pitch)

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

    def all(self, field, pitch_type=None):
        return flatten(list(pitch.all(field) for pitch in self._pitches(field, pitch_type)))

    def avg(self, field, pitch_type=None):
        pitches = self.all(field, pitch_type)
        total = sum(pitches)
        count = len(pitches)
        return (total / count)

    def split(self):
        split = {'L': {'num': 0}, 'R': {'num': 0}}
        for t in self.pitches.keys():
            left, right = self.pitches[t].split()
            split['L'][t] = left
            split['L']['num'] += len(left)
            split['R'][t] = right
            split['R']['num'] += len(right)
            split[t] = len(left) + len(right)

        split['count'] = split['L']['num'] + split['R']['num']

        return split
