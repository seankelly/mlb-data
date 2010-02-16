from lxml import etree
import pitchfx
import os.path, os, fnmatch
import sqlite3

db = "pfx_card.db"

db_exists = True
if not os.path.exists(db):
    db_exists = False

conn = sqlite3.connect(db)

# Create some tables if building the database.
if db_exists == False:
    pfx = open("pfx.sql", "r")
    conn.executescript(pfx.read())


find_atbats = etree.XPath('/inning/*/atbat')
def parse_game(game):
    # Skip inning_hit.xml. It is special and needs different processing.
    xml_files = fnmatch.filter(os.listdir(game), 'inning_[!h]*.xml')

    # Keep these fields.
    # Right now this is all but one ('des'), but MLBAM has added fields before.
    atbat_fields = {'pitcher': 'pitcher', 'batter': 'batter', 'stand': 'batter_stand', 'p_throws': 'pitcher_throw', 'des': 'des', 'event': 'event', 'brief_event': 'brief_event'}
    # Add in bip_x/y columns
    atbat_sql = "INSERT INTO atbat (" + ",".join(atbat_fields[key] for key in sorted(atbat_fields.keys())) + ",bip_x,bip_y,bip_x_feet,bip_y_feet) VALUES (" + ",".join(map(lambda a: '?', atbat_fields.keys())) + ",?,?,?,?)"
    pitch_fields = {'spin_rate': 'spin_rate', 'break_angle': 'break_angle', 'pitch_type': 'pitch_type', 'ax': 'ax', 'ay': 'ay', 'y0': 'y0', 'az': 'az', 'end_speed': 'end_speed', 'spin_dir': 'spin_dir', 'start_speed': 'start_speed', 'pz': 'pz', 'px': 'px', 'type': 'type', 'sz_bot': 'sz_bot', 'pfx_z': 'pfx_z', 'vy0': 'vy0', 'pfx_x': 'pfx_x', 'break_length': 'break_length', 'x0': 'x0', 'z0': 'z0', 'break_y': 'break_y', 'sz_top': 'sz_top', 'type_confidence': 'type_confidence', 'y': 'y', 'x': 'x', 'vz0': 'vz0', 'sv_id': 'sv_id', 'vx0': 'vx0'}
    pitch_sql = "INSERT INTO raw_pitch (" + ",".join(pitch_fields[key] for key in sorted(pitch_fields.keys())) + ",atbat,enhanced,balls,strikes) VALUES (" + ",".join(map(lambda a: '?', pitch_fields.keys())) + ",?,?,?,?)"
    pitch_inserts = []

    for inning in range(1, len(xml_files) + 1):
        xml_file = 'inning' + str(inning) + '.xml'
        xml = etree.parse(os.path.join(game, xml_file))
        atbats = find_atbats(xml)
        for atbat in atbats:
            # Try to match the atbat with entry in inning_hit.xml

            cur = conn.execute(atbat_sql, [atbat.get(key).strip() for key in sorted(atbat_fields.keys())])
            atbat_id = cur.lastrowid

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
        parse_game(os.path.join(output_dir, game))


pfx = pitchfx.PitchFX()

pfx.parse_options()

for day in pfx.each_day():
    parse_day(pfx.output_dir, day)

conn.commit()
conn.close()
