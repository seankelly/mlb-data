__all__ = [ 'pitchfx' ]

from datetime import date, datetime, timedelta
from HTMLParser import HTMLParser
from optparse import OptionParser
import os, re

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


def row_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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


class Options(object):
    def __init__(self):
        self.start_day = date.today() - timedelta(1)
        self.end_day = date.today() - timedelta(1)
        self.conn = None
        self.row_factory = None

    def __del__(self):
        if self.conn:
            self.conn.close()

    def _init_conn(self, options):
        conn = None
        if options.driver == 'sqlite' or options.driver == 'sqlite3':
            import sqlite3
            conn = sqlite3.connect(options.db)
            self.row_factory = sqlite3.Row
        elif options.driver == 'postgres' or options.driver == 'pygresql':
            import pgdb
            conn = pgdb.connect(database=options.db, user=options.user, password=options.password)
            self.row_factory = row_factory
        self.conn = conn

    def parse_options(self, parser=OptionParser()):
        parser.add_option("-o", "--out", dest="outdir",
                        help="XML saved in this directory")
        parser.add_option("-s", "--start", dest="start_time", metavar="START",
                        help="Start day")
        parser.add_option("-e", "--end", dest="end_time", metavar="END",
                        help="End day")
        parser.add_option("-d", "--db", dest="db", metavar="DATABASE",
                        help="Database to use")
        parser.add_option("-D", "--driver", dest="driver", metavar="DRIVER",
                        help="Database driver to use")
        parser.add_option("-U", "--user", dest="user", metavar="USER",
                        help="Database user to connect as")
        parser.add_option("-P", "--password", dest="password", metavar="PASSWORD",
                        help="Password for database")

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

        return options, args

    def each_day(self):
        current_day = self.start_day
        while current_day <= self.end_day:
            yield current_day
            current_day += timedelta(1)
