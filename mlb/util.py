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
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--output_dir', metavar='DIR',
                        help='Output directory')
    parser.add_argument('-s', '--start', metavar='DATE',
                        default=yesterday, help='Start day')
    parser.add_argument('-e', '--end', metavar='DATE',
                        default=yesterday, help='End day')
    parser.add_argument('-l', '--leagues', action='append',
                        help='Fetch these leagues')
    parser.add_argument('-d', '--database',
                        help='Database to use')
    args = parser.parse_args()
    options = {}
    args_dict = args.__dict__
    for key in args_dict:
        if args_dict[key]:
            options[key] = map_options[key](args_dict[key])
    return options

def each_day(start_day, end_day):
    current_day = start_day
    while current_day <= end_day:
        yield current_day
        current_day += datetime.timedelta(1)
