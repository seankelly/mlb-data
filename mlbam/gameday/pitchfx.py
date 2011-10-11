def counts():
    for balls in range(4):
        for strikes in range(3):
            count = str(balls) + '-' + str(strikes)
            yield count

def flatten(L):
    return reduce(lambda x,y: x+y, L)


class Pitch(object):
    def __init__(self, type):
        self.type = type
        self.total = 0
        self.pitches = []
        self._count = {}
        for c in counts():
            self._count[c] = 0

    def add(self, pitch_row):
        # Every pitch should be enhanced
        # But check just in case I flub
        if not pitch_row['enhanced']:
            return
        self.pitches.append(pitch_row)
        self.total += 1
        count = str(pitch_row['balls']) + '-' + str(pitch_row['strikes'])
        self._count[count] += 1

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

    def count(self):
        return self._count


class Pitcher(object):
    ignore_types = ['IN', 'PO', 'AB', 'UN']
    merge_types = {'SI': 'FT', 'FF': 'FA'}
    map_types = {'FA': 'Fastball', 'FF': 'Fastball', 'FC': 'Cutter',
            'FT': 'Two-seam Fastball', 'SI': 'Two-seam Fastball',
            'CU': 'Curveball', 'CH': 'Changeup', 'SL': 'Slider',
            'FS': 'Splitter', 'KN': 'Knuckleball'}

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
                if pitch_type in self.map_types:
                    pitch_type = self.map_types[pitch_type]
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
        pitches = [ pitch.all(field) for pitch in self._pitches(field, pitch_type) ]
        return flatten(pitches)

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

    def count(self):
        count = {}
        pitch = {}
        for t in self.pitches.keys():
            pitch[t] = self.pitches[t].count()
        for c in counts():
            count[c] = { 'num': 0 }
            for t in self.pitches.keys():
                count[c][t] = pitch[t][c]
                count[c]['num'] += pitch[t][c]

        return count
