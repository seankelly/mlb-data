import argparse
import datetime

def parse_str_date(day, default=datetime.date.today()):
    if day:
        try:
            day = datetime.datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date given:", day)
            raise
    else:
        day = default
    return day

def commandline_args(desc):
    passthrough = lambda f: f
    map_options = {
        'output_dir': passthrough,
        'leagues': passthrough,
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
    args = parser.parse_args()
    options = {}
    args_dict = args.__dict__
    for key in args_dict:
        options[key] = map_options[key](args_dict[key])
    return options

def each_day(start_day, end_day):
    current_day = start_day
    while current_day <= end_day:
        yield current_day
        current_day += datetime.timedelta(1)
