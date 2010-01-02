from HTMLParser import HTMLParser
from datetime import date, datetime, timedelta
from optparse import OptionParser  
import os
import re

class HTML(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))

    def get_links(self, pattern):
        link_match = re.compile(pattern)
        links = []
        for link in self.links:
            if link_match.match(link['href']):
                links.append(link['href'])

        return links


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


class PitchFX(object):
    def __init__(self):
        self.start_day = date.today() - timedelta(1)
        self.end_day = date.today()

    def parse_options(self, parser=OptionParser()):
        parser.add_option("-o", "--out", dest="outdir",
                        help="XML saved in this directory")
        parser.add_option("-s", "--start", dest="start_time", metavar="START",
                        help="Start day")
        parser.add_option("-e", "--end", dest="end_time", metavar="END",
                        help="End day")

        (options, args) = parser.parse_args()
        # Default the start day to yesterday
        self.start_day = parse_date(options.start_time, self.start_day)
        # Keep the default end day to be today
        self.end_day = parse_date(options.end_time, self.end_day)

        if self.start_day > self.end_day:
            raise ValueError, "Starting day after ending day"

        if options.outdir:
            self.output_dir = os.path.abspath(options.outdir)
            if os.path.exists(self.output_dir) == False:
                os.makedirs(self.output_dir)
        else:
            raise ValueError, "Output directory not given"

        return args


    def each_day(self):
        current_day = self.start_day
        while current_day < self.end_day:
            yield current_day
            current_day += timedelta(1)


