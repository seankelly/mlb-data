# Dump XML files containing BIP data for each park.

import gameday
from lxml import objectify, etree

gd = gameday.Options()
gd.parse_options()
conn = gd.conn

park_sql = "SELECT id, name, hp_x, hp_y, scale FROM park"
bip_sql = "SELECT bip.x AS x, bip.y AS y, atbat.event AS event, bip.type AS type, p.name AS pitcher, b.name AS batter FROM bip JOIN park ON bip.park = park.id JOIN atbat ON bip.atbat = atbat.id LEFT JOIN player p ON p.mlbid = atbat.pitcher LEFT JOIN player b ON b.mlbid = atbat.batter where park.id = ?"
bip_col = [ 'x', 'y', 'event', 'type', 'pitcher', 'batter' ]

park = {}
cur = conn.execute(park_sql)
for row in cur.fetchall():
    park[row[0]] = { 'name': row[1], 'hp_x': row[2], 'hp_y': row[3], 'scale': row[4] }

for park_id in park.keys():
    cur = conn.execute(bip_sql, [park_id])
    park_xml = objectify.Element("park")
    for park_opt in park[park_id].keys():
        park_xml.set(park_opt, str(park[park_id][park_opt]))
    num_bip = 0
    for bip in cur.fetchall():
        num_bip += 1
        bip_xml = objectify.Element("bip")
        for i, col in enumerate(bip_col):
            bip_xml.set(col, str(bip[i]))
        park_xml.append(bip_xml)
    # No need to write empty files!
    if num_bip > 0:
        objectify.deannotate(park_xml)
        etree.cleanup_namespaces(park_xml)
        xml_file = open("park-" + str(park_id) + ".xml", "w")
        xml_file.write(etree.tostring(park_xml))
        xml_file.close()
