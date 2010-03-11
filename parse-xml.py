from lxml import etree
import gameday
import os, fnmatch


game_children = etree.XPath('/game/*')
def parse_game_xml(game_dir, day):
    game_sql = 'INSERT INTO game (home,away,park,day) VALUES (?,?,?,?)'
    game = { 'day': str(day) }
    for el in game_children(etree.parse(os.path.join(game_dir, 'game.xml'))):
        if el.tag == 'team':
            game[el.get('type')] = el.get('id')
        elif el.tag == 'stadium':
            game['park'] = el.get('id')
    insert = [ game['home'], game['away'], game['park'], game['day'] ]
    cur = conn.execute(game_sql, insert)
    game['id'] = cur.lastrowid
    return game


find_atbats = etree.XPath('/inning/*/atbat')
find_bip = etree.XPath('/hitchart/hip')
def parse_game(game_dir, day):
    game = parse_game_xml(game_dir, day)
    # Skip inning_hit.xml. It is special and needs different processing.
    xml_files = fnmatch.filter(os.listdir(game_dir), 'inning_[!h]*.xml')
    bip = find_bip(etree.parse(os.path.join(game_dir, 'inning_hit.xml')))
    # Reverse it because python 2.5 doesn't have popleft()
    bip.reverse()

    # Keep these fields.
    # Right now this is all but one ('des'), but MLBAM has added fields before.
    atbat_fields = {'pitcher': 'pitcher', 'batter': 'batter', 'stand': 'batter_stand', 'p_throws': 'pitcher_throw', 'des': 'des', 'event': 'event'}
    # Add in bip_x/y columns
    atbat_sql = "INSERT INTO atbat (" + ",".join(atbat_fields[key] for key in sorted(atbat_fields.keys())) + ",game) VALUES (" + ",".join(map(lambda a: '?', atbat_fields.keys())) + ",?)"
    bip_sql = "INSERT INTO bip (atbat, park, type, x, y, x_feet, y_feet) VALUES (?,?,?,?,?,?,?)"
    pitch_fields = {'spin_rate': 'spin_rate', 'break_angle': 'break_angle', 'pitch_type': 'pitch_type', 'ax': 'ax', 'ay': 'ay', 'y0': 'y0', 'az': 'az', 'end_speed': 'end_speed', 'spin_dir': 'spin_dir', 'start_speed': 'start_speed', 'pz': 'pz', 'px': 'px', 'type': 'type', 'sz_bot': 'sz_bot', 'pfx_z': 'pfx_z', 'vy0': 'vy0', 'pfx_x': 'pfx_x', 'break_length': 'break_length', 'x0': 'x0', 'z0': 'z0', 'break_y': 'break_y', 'sz_top': 'sz_top', 'type_confidence': 'type_confidence', 'y': 'y', 'x': 'x', 'vz0': 'vz0', 'sv_id': 'sv_id', 'vx0': 'vx0'}
    pitch_sql = "INSERT INTO raw_pitch (" + ",".join(pitch_fields[key] for key in sorted(pitch_fields.keys())) + ",atbat,enhanced,balls,strikes) VALUES (" + ",".join(map(lambda a: '?', pitch_fields.keys())) + ",?,?,?,?)"
    pitch_inserts = []

    for inning in range(1, len(xml_files) + 1):
        xml_file = 'inning_' + str(inning) + '.xml'
        atbats = find_atbats(etree.parse(os.path.join(game_dir, xml_file)))
        for atbat in atbats:
            atbat_insert = [atbat.get(key).strip() for key in sorted(atbat_fields.keys())]
            atbat_insert.append(game['id']);
            cur = conn.execute(atbat_sql, atbat_insert)
            atbat_id = cur.lastrowid

            # Try to match the atbat with entry in inning_hit.xml
            idx = len(bip)-1
            while idx >= 0 and atbat.get('pitcher') == bip[idx].get('pitcher') and atbat.get('batter') == bip[idx].get('batter') and inning == int(bip[idx].get('inning')):
                conn.execute(bip_sql, [ atbat_id, game['park'], bip[idx].get('type'), bip[idx].get('x'), bip[idx].get('y') ])
                bip.pop()
                idx = len(bip)-1

            balls, strikes = 0, 0
            for pitch in atbat.getiterator('pitch'):
                insert = [pitch.get(key).strip() if pitch.get(key) else None for key in sorted(pitch_fields.keys())]

                insert.append(atbat_id)
                # This is for the enhanced column
                insert.append(1 if pitch.get('pitch_type') else 0)
                insert.append(balls)
                insert.append(strikes)
                pitch_inserts.append(insert)

                # Calculate the count
                # ..after the pitch!
                called = pitch.get('type')
                des    = pitch.get('des')
                if called == 'B':
                    balls += 1
                elif called == 'S' and (strikes < 2 or (des != 'Foul' and des != 'Foul (Runner Going)')):
                    strikes += 1

    conn.executemany(pitch_sql, pitch_inserts)


def parse_day(output_dir, day):
    datematch = day.strftime("gid_%Y_%m_%d*")
    games = fnmatch.filter(os.listdir(output_dir), datematch)
    for game in games:
        parse_game(os.path.join(output_dir, game), day)


gd = gameday.Options()
gd.parse_options()
conn = gd.conn

for day in gd.each_day():
    parse_day(gd.output_dir, day)

conn.commit()
