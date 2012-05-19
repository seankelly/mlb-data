from optparse import OptionParser
import argparse
import datetime

def parse_str_date(day, default=datetime.date.today()):
    if not day:
        return default
    # First, check if it's a date.
    try:
        if day.year and day.month and day.day:
            return day
    except AttributeError:
        pass
    # Then check if it can be parsed into a date.
    try:
        day = datetime.datetime.strptime(day, "%Y-%m-%d").date()
        return day
    except ValueError:
        print("Invalid date given:", day)
        raise

def commandline_args(desc):
    passthrough = lambda f: f
    map_options = {
        'output_dir': passthrough,
        'leagues': passthrough,
        'database': passthrough,
        'start': parse_str_date,
        'end': parse_str_date,
    }
    yesterday = datetime.date.today() - datetime.timedelta(1)
    parser = OptionParser(description=desc)
    parser.add_option('-o', '--output_dir', metavar='DIR',
                      help='Output directory')
    parser.add_option('-s', '--start', metavar='DATE',
                      default=yesterday, help='Start day')
    parser.add_option('-e', '--end', metavar='DATE',
                      default=yesterday, help='End day')
    parser.add_option('-l', '--leagues', action='append',
                      help='Fetch these leagues')
    parser.add_option('-d', '--database',
                      help='Database to use')
    options, args = parser.parse_args()
    dict_options = {}
    opts_dict = options.__dict__
    for key in opts_dict:
        if opts_dict[key]:
            dict_options[key] = map_options[key](opts_dict[key])
    return dict_options

def each_day(start_day, end_day):
    current_day = start_day
    while current_day <= end_day:
        yield current_day
        current_day += datetime.timedelta(1)
