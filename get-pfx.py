#!/usr/bin/python

from random import uniform
import urllib2, os, os.path, time
import pitchfx

def fetch_game(url, gid):
    pitchers = url + gid + "/pbp/pitchers/"
    try:
        pitcher_dir = urllib2.urlopen(pitchers)
    except urllib2.HTTPError:
        return

    mlb = pitchfx.HTML()
    mlb.feed(pitcher_dir.read())
    mlb.close()

    gid_dir = os.path.join(out_dir, gid)
    if os.path.exists(gid_dir) == False:
        os.makedirs(gid_dir)

    for pitcher in mlb.get_links('\d+\.xml'):
        xml_output = open(os.path.join(gid_dir, pitcher), 'w')
        xml_file   = urllib2.urlopen(pitchers + pitcher)
        xml_output.write(xml_file.read())
        time.sleep(uniform(1, 5))


def fetch_day(day):
    url = "http://gd2.mlb.com/components/game/mlb/" + day.strftime("year_%Y/month_%m/day_%d/")
    day_dir = urllib2.urlopen(url)
    mlb = pitchfx.HTML()
    mlb.feed(day_dir.read())
    mlb.close()

    for gid in mlb.get_links('^gid_'):
        fetch_game(url, gid)
        time.sleep(20 + uniform(0, 10))

pfx = pitchfx.PitchFX()

pfx.parse_options()

for day in pfx.each_day():
    fetch_day(day)
