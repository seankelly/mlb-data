# Dump XML files containing BIP data for each park.

import gameday, os
from lxml import objectify, etree

gd = gameday.Options()
gd.parse_options()
conn = gd.conn

park_sql = "SELECT id, name, hp_x, hp_y, scale FROM park ORDER BY id asc"
bip_sql = "SELECT bip.x AS x, bip.y AS y, atbat.event AS event, bip.type AS type, p.name AS pitcher, b.name AS batter FROM bip JOIN park ON bip.park = park.id JOIN atbat ON bip.atbat = atbat.id LEFT JOIN player p ON p.mlbid = atbat.pitcher LEFT JOIN player b ON b.mlbid = atbat.batter where park.id = ?"
bip_col = [ 'x', 'y', 'event', 'type', 'pitcher', 'batter' ]

def dump_xml(filename, xml):
    objectify.deannotate(xml)
    etree.cleanup_namespaces(xml)
    filename = os.path.join(gd.output_dir, filename)
    xml_file = open(filename, "w")
    xml_file.write(etree.tostring(xml))
    xml_file.close()

park = {}
cur = conn.execute(park_sql)
stadiums = objectify.Element("stadiums")
for row in cur.fetchall():
    park[row[0]] = { 'name': row[1], 'hp_x': row[2], 'hp_y': row[3], 'scale': row[4] }
    park_xml = objectify.Element("park")
    for park_opt in park[row[0]].keys():
        park_xml.set(park_opt, str(park[row[0]][park_opt]))
    stadiums.append(park_xml)

dump_xml("parks.xml", stadiums)

for park_id in park.keys():
    cur = conn.execute(bip_sql, [park_id])
    park_xml = objectify.Element("park")
    num_bip = 0
    for bip in cur.fetchall():
        num_bip += 1
        bip_xml = objectify.Element("bip")
        for i, col in enumerate(bip_col):
            bip_xml.set(col, str(bip[i]))
        park_xml.append(bip_xml)
    # No need to write empty files!
    if num_bip > 0:
        dump_xml("park-" + str(park_id) + ".xml", park_xml)
