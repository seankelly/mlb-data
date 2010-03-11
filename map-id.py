import csv, gameday
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="player_map", help="MLBAM ID player mapping")

gd = gameday.Options()
(options, args) = gd.parse_options(parser)

mlb_map = csv.reader(open(options.player_map), delimiter="|")

players = {}
cur = gd.conn.cursor()

for row in cur.execute("SELECT mlbid,name FROM player"):
    players[row[0]] = row[1]


mappings = []

for player in mlb_map:
    # Make sure he's in MLB first.
    # Then ensure he's not already in the database
    if int(player[1]) == 1 and player[0] not in players:
        mappings.append([player[0], player[3]])

cur.executemany("INSERT INTO player (mlbid, name) VALUES(?,?)", mappings)
cur.commit()
