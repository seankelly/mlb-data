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


def parse_game(game):
    xml_files = fnmatch.filter(os.listdir(game), '*.xml')
    for xml_file in xml_files:
        xml = etree.parse(os.path.join(game, xml_file))
        pitches = xml.xpath('/player/atbat/pitch')


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
