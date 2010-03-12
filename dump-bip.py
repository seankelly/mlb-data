# Dump XML files containing BIP data for each park.

from sqlalchemy.sql import select, bindparam, func
import gameday, os
try:
    import json
except ImportError:
    import simplejson as json

gd = gameday.Options()
gd.parse_options()
gd.init_db()

park_table = gd.meta.tables['park']
bip_table = gd.meta.tables['bip']
park_sql = select([park_table, func.count(bip_table.c.id).label('num')], from_obj=[park_table.outerjoin(bip_table)]).group_by(park_table.c.id)

player_table = gd.meta.tables['player']
pa_table = gd.meta.tables['appearance']

p = player_table.alias()
b = player_table.alias()
bip_sql = select([bip_table.c.type.label('type'), bip_table.c.x.label('x'), bip_table.c.y.label('y'), pa_table.c.event.label('event'), pa_table.c.batter.label('batter'), pa_table.c.batter_stand.label('stand'), pa_table.c.pitcher.label('pitcher'), pa_table.c.pitcher_throw.label('throw')], park_table.c.id==bindparam('park'), from_obj=bip_table.join(park_table).join(pa_table).outerjoin(p, onclause=p.c.mlbid==pa_table.c.pitcher).outerjoin(b, onclause=b.c.mlbid==pa_table.c.batter))
bip_col = [ 'x', 'y', 'event', 'type', 'pitcher', 'throw', 'batter', 'stand' ]

def dump_json(filename, obj):
    filename = os.path.join(gd.output_dir, filename)
    json_file = open(filename, "w")
    json.dump(obj, json_file, separators=(',',':'))
    json_file.close()

park = {}
stadiums = []
for row in gd.conn.execute(park_sql):
    p = {}
    for key in row.keys():
        if key in ['hp_x', 'hp_y', 'id', 'num']:
            p[key] = int(row[key])
        else:
            p[key] = str(row[key])
    p['bip'] = p['num']
    del p['location']
    del p['num']
    park[p['id']] = park_json = p
    stadiums.append(park_json)

dump_json("parks.json", stadiums)

for park_id in park.keys():
    bip_list = []
    for bip in gd.conn.execute(bip_sql, { 'park': park_id }):
        bip_list.append({ 'x': str(bip['x']), 'y': str(bip['y']), 'event': bip['event'], 'type': bip['type'], 'pitcher': bip['pitcher'], 'throw': bip['throw'], 'batter': bip['batter'], 'stand': bip['stand']  })
    # No need to write empty files!
    if len(bip_list) > 0:
        dump_json("park-" + str(park_id) + ".json", bip_list)
