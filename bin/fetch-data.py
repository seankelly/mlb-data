'''
Fetch MLBAM's PitchFX data.

Usage:
    python get-pfx.py -o path/to/save/ [-s <start date>] [-e <end date>]

With no start or end days specified, it will fetch the previous day's data.
'''

from random import uniform
import urllib2, os, os.path, time
import gameday

def save_game_data(gid_dir, xml_file, name):
    if os.path.exists(gid_dir) == False:
        os.makedirs(gid_dir)

    xml_output = open(os.path.join(gid_dir, name), 'w')
    xml_output.write(xml_file.read())
    xml_output.close()


def scrape_game_dir(gid_dir, url, xml_re):
    url_dir = urllib2.urlopen(url)
    mlb = gameday.HTML()
    mlb.feed(url_dir.read())
    mlb.close()

    # Scrape the links for what we want
    for filename in mlb.get_links(xml_re):
        xml_file = urllib2.urlopen(url + "/" + filename)
        save_game_data(gid_dir, xml_file, filename)
        time.sleep(uniform(2, 7))


def fetch_game(url, gid):
    gid_dir = os.path.join(gd.output_dir, gid)

    url_base = url + gid
    game = url_base + "/game.xml"
    # This file only exists for games that were played in
    # some capacity. Try to fetch and return if cannot.
    try:
        game_xml = urllib2.urlopen(game)
        save_game_data(gid_dir, game_xml, "game.xml")

        players_xml = urllib2.urlopen(url_base + "/players.xml")
        save_game_data(gid_dir, players_xml, "players.xml")
    except urllib2.HTTPError:
        return

    # Find and save each inning file.
    scrape_game_dir(gid_dir, url_base + "/inning", "inning_(\d+|hit)\.xml")


def fetch_day(day):
    url = "http://gd2.mlb.com/components/game/mlb/" + day.strftime("year_%Y/month_%m/day_%d/")
    day_dir = urllib2.urlopen(url)
    mlb = gameday.HTML()
    mlb.feed(day_dir.read())
    mlb.close()

    for gid in mlb.get_links('^gid_'):
        fetch_game(url, gid)
        time.sleep(uniform(20, 30))


gd = gameday.Options()
gd.parse_options()

for day in gd.each_day():
    fetch_day(day)
