# Dump XML files containing BIP data for each park.

import gameday, os
try:
    import json
except ImportError:
    import simplejson as json

gd = gameday.Options()
gd.parse_options()
cur = gd.conn.cursor()

park_sql = "SELECT park.id, name, hp_x, hp_y, scale, count(bip.id) AS num FROM park LEFT JOIN bip ON park.id = bip.park GROUP BY park.id"
bip_sql = "SELECT bip.x AS x, bip.y AS y, atbat.event AS event, bip.type AS type, p.name AS pitcher, atbat.pitcher_throw AS throw, b.name AS batter, atbat.batter_stand AS stand FROM bip JOIN park ON bip.park = park.id JOIN atbat ON bip.atbat = atbat.id LEFT JOIN player p ON p.mlbid = atbat.pitcher LEFT JOIN player b ON b.mlbid = atbat.batter where park.id = ?"
bip_col = [ 'x', 'y', 'event', 'type', 'pitcher', 'throw', 'batter', 'stand' ]

def dump_json(filename, obj):
    filename = os.path.join(gd.output_dir, filename)
    json_file = open(filename, "w")
    json.dump(obj, json_file, separators=(',',':'))
    json_file.close()

park = {}
cur.execute(park_sql)
stadiums = []
for row in cur.fetchall():
    park[row[0]] = { 'id': row[0], 'name': row[1], 'hp_x': str(row[2]), 'hp_y': str(row[3]), 'scale': str(row[4]), 'bip': row[5] }
    park_json = park[row[0]]
    stadiums.append(park_json)

dump_json("parks.json", stadiums)

for park_id in park.keys():
    cur.execute(bip_sql, [park_id])
    bip_list = []
    for bip in cur.fetchall():
        bip_list.append({ 'x': str(bip[0]), 'y': str(bip[1]), 'event': bip[2], 'type': bip[3], 'pitcher': bip[4], 'throw': bip[5], 'batter': bip[6], 'stand': bip[7]  })
    # No need to write empty files!
    if len(bip_list) > 0:
        dump_json("park-" + str(park_id) + ".json", bip_list)
