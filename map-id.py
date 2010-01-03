import csv, sqlite3
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--db", dest="db", help="SQLite database file")

(options, args) = parser.parse_args()

conn = sqlite3.connect(options.db)
mlb_map = csv.reader(open(args[0]), delimiter="|")

players = {}

for row in conn.execute("SELECT mlbid,name FROM player"):
    players[row[0]] = row[1]


mappings = []

for player in mlb_map:
    # Make sure he's in MLB first.
    # Then ensure he's not already in the database
    if int(player[1]) == 1 and player[0] not in players:
        mappings.append([player[0], player[3]])

conn.executemany("INSERT INTO player (mlbid, name) VALUES(?,?)", mappings)

conn.commit()
conn.close()
