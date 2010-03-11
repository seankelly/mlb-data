import csv, gameday
from optparse import OptionParser
from sqlalchemy.sql import select

parser = OptionParser()
parser.add_option("-f", "--file", dest="player_map", help="MLBAM ID player mapping")

gd = gameday.Options()
(options, args) = gd.parse_options(parser)
gd.init_db()

mlb_map = csv.reader(open(options.player_map), delimiter="|")
player_table = gd.meta.tables['player']

s = select([player_table])
players = {}
for row in gd.conn.execute(s):
    players[row['name']] = row['mlbid']

mappings = []
for player in mlb_map:
    # Make sure he's in MLB first.
    # Then ensure he's not already in the database
    if int(player[1]) == 1 and player[0] not in players:
        mappings.append({ 'mlbid': player[0], 'name': player[3] })

trans = gd.conn.begin()
gd.conn.execute(player_table.insert(), mappings)
trans.commit()
