from datetime import datetime
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
    park_dim_table = meta.tables['park_dimension']
    bip_table = meta.tables['bip']
    game_table = meta.tables['game']
    player_table = meta.tables['mlbam_player']
    ab_table = meta.tables['atbat']

    # Arg, postgres requires every column to be in the ORDER BY clause
    park_sql = select([park_table.c.id, park_table.c.name,
        func.count(bip_table.c.id).label('num')],
        from_obj=park_table.join(bip_table)).group_by(park_table.c.id,
                park_table.c.name)

    parks = {}
    for row in conn.execute(park_sql):
        p = {}
        for key in row.keys():
            if key in set(['id', 'num']):
                p[key] = int(row[key])
            else:
                p[key] = str(row[key])
        p['bip'] = p['num']
        p['years'] = {}
        del p['num']
        parks[p['id']] = p

    # Skipping the closing year for simplicity. If a team switches parks in the
    # middle of the year, it will be a park with a new id. I believe the only
    # issue will be if MLBAM updates the image in the middle of the season.
    # This might happen for Citi Field (no bases or foul lines!).
    dimension_sql = select([park_dim_table.c.park_id,
        park_dim_table.c.image_file, park_dim_table.c.opening,
        park_dim_table.c.hp_x, park_dim_table.c.hp_y, park_dim_table.c.scale],
        from_obj=park_dim_table)

    for row in conn.execute(dimension_sql):
        id = row['park_id']
        if id not in parks:
            continue
        opening = row['opening']
        images = {'file': row['image_file'], 'scale': float(row['scale']),
                'hp_x': float(row['hp_x']), 'hp_y': float(row['hp_y']),
                'opening': opening.year}
        if 'images' not in parks[id]:
            parks[id]['images'] = {}
        parks[id]['images'][opening.year] = images

    years_sql = select([func.distinct(text(get_year(conn, 'day')))],
                       from_obj=game_table)
    years = [int(row[0]) for row in conn.execute(years_sql)]

    p = player_table.alias()
    b = player_table.alias()
    bip_sql = select([game_table.c.day.label('day'),
        bip_table.c.type.label('type'), bip_table.c.x.label('x'),
        bip_table.c.y.label('y'), ab_table.c.event.label('event'),
        (b.c.namelast + ', ' + b.c.namefirst).label('batter'),
        ab_table.c.batter_stand.label('stand'), (p.c.namelast + ', ' +
            p.c.namefirst).label('pitcher'),
        ab_table.c.pitcher_throw.label('throw')],
            and_(park_table.c.id == bindparam('park'),
                text(get_year(conn, 'day')) == bindparam('year')),
        from_obj=bip_table.join(park_table).join(ab_table).join(game_table).outerjoin(p,
            onclause=p.c.mlbamid==ab_table.c.pitcher).outerjoin(b,
                onclause=b.c.mlbamid==ab_table.c.batter))

    for park_id in parks.keys():
        for year in years:
            bip_list = []
            str_y = str(year)
            for bip in conn.execute(bip_sql, {'park': park_id, 'year': str_y}):
                bip_list.append({'x': bip['x'], 'y': bip['y'],
                    'event': bip['event'], 'type': bip['type'],
                    'pitcher': bip['pitcher'], 'throw': bip['throw'],
                    'batter': bip['batter'], 'stand': bip['stand']})
            # No need to write empty files!
            if len(bip_list) > 0:
                parks[park_id]['years'][year] = True
                park_file = os.path.join(args['output_dir'],
                        "park-" + str(park_id) + "-" + str(year) + ".json")
                dump_json(park_file, bip_list)

    parks_file = os.path.join(args['output_dir'], "parks.json")
    dump_json(parks_file, parks)

if __name__ == "main":
    run()
