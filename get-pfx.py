#!/usr/bin/python

from optparse import OptionParser  
from datetime import date, datetime, timedelta
import urllib2, os, os.path, time
import mlbhtml

def parse_date(date, default=date.today()):
    if date:
        try:
            day = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print "Invalid date given:", date
            raise
    else:
        day = default
    return day


def fetch_game(url, gid):
    pitchers = url + gid + "/pbp/pitchers/"
    try:
        pitcher_dir = urllib2.urlopen(pitchers)
    except urllib2.HTTPError:
        return

    mlb = mlbhtml.HTML()
    mlb.feed(pitcher_dir.read())
    mlb.close()

    gid_dir = os.path.join(out_dir, gid)
    if os.path.exists(gid_dir) == False:
        os.makedirs(gid_dir)

    for pitcher in mlb.get_links('\d+\.xml'):
        xml_output = open(os.path.join(gid_dir, pitcher), 'w')
        xml_file   = urllib2.urlopen(pitchers + pitcher)
        xml_output.write(xml_file.read())
        time.sleep(2)


def fetch_day(day):
    url = "http://gd2.mlb.com/components/game/mlb/" + day.strftime("year_%Y/month_%m/day_%d/")
    day_dir = urllib2.urlopen(url)
    mlb = mlbhtml.HTML()
    mlb.feed(day_dir.read())
    mlb.close()

    for gid in mlb.get_links('^gid_'):
        fetch_game(url, gid)
        time.sleep(5)


parser = OptionParser()
parser.add_option("-o", "--out", dest="outdir",
                  help="Save the XML in this directory")
parser.add_option("-s", "--start", dest="start_time", metavar="START",
                  help="Start day")
parser.add_option("-e", "--end", dest="end_time", metavar="END",
                  help="End day")

(options, args) = parser.parse_args()

# Default the start day to yesterday
start_day = parse_date(options.start_time, date.today() - timedelta(1))
# Keep the default end day to be today
end_day = parse_date(options.end_time)

if start_day > end_day:
    raise ValueError, "Starting day after ending day"

if options.outdir:
    out_dir = os.path.abspath(options.outdir)
    if os.path.exists(out_dir) == False:
        os.makedirs(out_dir)
else:
    raise ValueError, "Output directory not given"

current_day = start_day

while current_day <= end_day:
    fetch_day(current_day)
    current_day += timedelta(1)
