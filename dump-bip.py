# Dump XML files containing BIP data for each park.

import gameday, os
try:
    import json
except ImportError:
    import simplejson as json

gd = gameday.Options()
gd.parse_options()
conn = gd.conn

park_sql = "SELECT id, name, hp_x, hp_y, scale FROM park ORDER BY id asc"
bip_sql = "SELECT bip.x AS x, bip.y AS y, atbat.event AS event, bip.type AS type, p.name AS pitcher, b.name AS batter FROM bip JOIN park ON bip.park = park.id JOIN atbat ON bip.atbat = atbat.id LEFT JOIN player p ON p.mlbid = atbat.pitcher LEFT JOIN player b ON b.mlbid = atbat.batter where park.id = ?"
bip_col = [ 'x', 'y', 'event', 'type', 'pitcher', 'batter' ]

def dump_json(filename, obj):
    filename = os.path.join(gd.output_dir, filename)
    json_file = open(filename, "w")
    json.dump(obj, json_file, separators=(',',':'))
    json_file.close()

park = {}
cur = conn.execute(park_sql)
stadiums = []
for row in cur.fetchall():
    park[row[0]] = { 'id': row[0], 'name': row[1], 'hp_x': str(row[2]), 'hp_y': str(row[3]), 'scale': str(row[4]) }
    park_json = park[row[0]]
    stadiums.append(park_json)

dump_json("parks.json", stadiums)

for park_id in park.keys():
    cur = conn.execute(bip_sql, [park_id])
    park_json = []
    for bip in cur.fetchall():
        park_json.append({ 'x':str(bip[0]), 'y':str(bip[1]), 'event':bip[2], 'type':bip[3], 'pitcher':bip[4], 'batter':bip[5] })
    # No need to write empty files!
    if len(park_json) > 0:
        dump_json("park-" + str(park_id) + ".json", park_json)
