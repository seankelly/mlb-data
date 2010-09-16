'''
Create JSON files containing individual pitch data for every pitcher.

Usage:
    python dump-pitches.py -o path/to/output/ -d 'sqlite:///pfx.db'
'''

from sqlalchemy.sql import select, bindparam, func, text, and_
import gameday, os
try:
    import json
except ImportError:
    import simplejson as json


def get_year(conn, label):
    if 'sqlite' not in conn.dialect.__module__:
        return "EXTRACT(year from " + label + ")"
    else:
        return "strftime('%Y', " + label + ")"

gd = gameday.Options()
gd.parse_options()
gd.init_db()

game_table = gd.meta.tables['game']
years_sql = select([func.distinct(text(get_year(gd.conn, 'day')))], from_obj=game_table)

# This should be changed to norm_pitch once normalization is done.
pitch_table = gd.meta.tables['raw_pitch']
pitcher_list = select([func.distinct(pitch_table.c.pitcher)], text(get_year(gd.conn, 'day')) == bindparam('year'), from_obj=pitch_table.join(game_table))

player_table = gd.meta.tables['mlbam_player']
get_pitches = select([pitch_table, game_table.c.day], and_(pitch_table.c.enhanced == True, text(get_year(gd.conn, 'day')) == bindparam('year'), pitch_table.c.pitcher == bindparam('pitcher')), from_obj=pitch_table.join(game_table)).order_by(pitch_table.c.pitcher, game_table.c.day.asc())


def dump_json(filename, obj):
    filename = os.path.join(gd.output_dir, filename)
    json_file = open(filename, "w")
    json.dump(obj, json_file, separators=(',',':'))
    json_file.close()

def load_players():
    player_list = {}
    player_select = select([player_table])
    for player in gd.conn.execute(player_select):
        player_list[int(player['mlbamid'])] = { 'first': player['namefirst'], 'last': player['namelast'] }
    return player_list

def get_name(player_list, id):
    return player_list[id]['last'] + ', ' + player_list[id]['first']

def add_pitch(obj, pitch):
    global player_list
    from decimal import Decimal
    from datetime import date
    t = pitch['pitch_type']
    if t not in obj['average']:
        obj['average'][t] = { 'x0': 0.0, 'y0': 0.0, 'z0': 0.0, 'vx0': 0.0, 'vy0': 0.0, 'vz0': 0.0, 'ax': 0.0, 'ay': 0.0, 'az': 0.0, 'start_speed': 0.0, 'num': 0 } 

    type_dec = type(Decimal(0))
    avg = obj['average'][t]
    avg['num'] += 1
    for x in avg:
        if x != 'num': avg[x] += float(pitch[x])

    p = { 'batter': get_name(player_list, pitch['batter']) }
    for x in ['x0', 'y0', 'z0', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'pitch_type', 'sequence']:
        if type(pitch[x]) != type_dec:
            p[x] = pitch[x]
        else:
            p[x] = float(pitch[x])
    if type(pitch['day']) != type(date.today()):
        ymd = pitch['day'].split('-')
        day = date(int(ymd[0]), int(ymd[1]), int(ymd[2]))
    else:
        day = pitch['day']
    p['day'] = day.strftime('%b %d')
    obj['all'].append(p)

def save_pitches(pitches, year):
    for t in pitches['average']:
        N = pitches['average'][t]['num']
        for x in pitches['average'][t]:
            pitches['average'][t][x] = pitches['average'][t][x] / N
        pitches['average'][t]['num'] = N
    dump_json(str(year) + "-" + str(pitches['id']) + ".json", pitches)

player_list = load_players()

years = [int(row[0]) for row in gd.conn.execute(years_sql)]
for year in years:
    pitcher = 0
    for pitch in gd.conn.execute(get_pitches, { 'year': str(year) }):
        if pitch['pitcher'] != pitcher:
            if pitcher != 0:
                save_pitches(pitches, year)
            pitches = { 'all': [], 'average': {}, 'id': pitch['pitcher'], 'pitcher': pitch['pitcher_name'] }
            pitcher = pitch['pitcher']
        add_pitch(pitches, pitch)
