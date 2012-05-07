from sqlalchemy.sql import select, bindparam, func, text, and_
from ..util import commandline_args
from ..database import connect_db
import json
import os

def get_year(conn, label):
    if 'sqlite' not in conn.dialect.__module__:
        return "EXTRACT(year from " + label + ")"
    else:
        return "strftime('%Y', " + label + ")"

def dump_json(filename, obj):
    json_file = open(filename, "w")
    json.dump(obj, json_file, separators=(',',':'))
    json_file.close()

def run():
    args = commandline_args('Dump BIP into JSON files')
    conn, meta = connect_db(args['database'])

    park_table = meta.tables['park']
    bip_table = meta.tables['bip']
    game_table = meta.tables['game']
    player_table = meta.tables['mlbam_player']
    ab_table = meta.tables['atbat']

    # Arg, postgres requires every column to be in the ORDER BY clause
    park_sql = select([park_table.c.id, park_table.c.name, park_table.c.hp_x,
        park_table.c.hp_y, park_table.c.scale,
        func.count(bip_table.c.id).label('num')],
        from_obj=[park_table.outerjoin(bip_table)]).group_by(park_table.c.id,
                park_table.c.name, park_table.c.hp_x, park_table.c.hp_y,
                park_table.c.scale)

    p = player_table.alias()
    b = player_table.alias()
    bip_sql = select([game_table.c.day.label('day'),
        bip_table.c.type.label('type'), bip_table.c.x.label('x'),
        bip_table.c.y.label('y'), ab_table.c.event.label('event'),
        (b.c.namelast + ', ' + b.c.namefirst).label('batter'),
        ab_table.c.batter_stand.label('stand'), (p.c.namelast + ', ' +
            p.c.namefirst).label('pitcher'),
        ab_table.c.pitcher_throw.label('throw')], and_(park_table.c.id ==
            bindparam('park'), text(get_year(conn, 'day')) ==
            bindparam('year')),
        from_obj=bip_table.join(park_table).join(ab_table).join(game_table).outerjoin(p,
            onclause=p.c.mlbamid==ab_table.c.pitcher).outerjoin(b,
                onclause=b.c.mlbamid==ab_table.c.batter))

    park = {}
    stadiums = []
    for row in conn.execute(park_sql):
        p = {}
        for key in row.keys():
            if key in ['hp_x', 'hp_y', 'id', 'num']:
                p[key] = int(row[key])
            else:
                p[key] = str(row[key])
        p['bip'] = p['num']
        p['years'] = {}
        del p['num']
        park[p['id']] = park_json = p
        stadiums.append(park_json)

    years_sql = select([func.distinct(text(get_year(conn, 'day')))],
                       from_obj=game_table)
    years = [int(row[0]) for row in conn.execute(years_sql)]

    for park_id in park.keys():
        for year in years:
            bip_list = []
            for bip in conn.execute(bip_sql, { 'park': park_id, 'year': year }):
                bip_list.append({'x': bip['x'], 'y': bip['y'],
                    'event': bip['event'], 'type': bip['type'],
                    'pitcher': bip['pitcher'], 'throw': bip['throw'],
                    'batter': bip['batter'], 'stand': bip['stand']  })
            # No need to write empty files!
            if len(bip_list) > 0:
                park[park_id]['years'][year] = True
                dump_json("park-" + str(park_id) + "-" + str(year) + ".json",
                        bip_list)

    dump_json("parks.json", stadiums)

if __name__ == "main":
    run()
