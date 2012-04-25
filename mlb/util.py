import argparse

def commandline_args(desc):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-o', '--output_dir', metavar='DIR',
                        help='Output directory')
    parser.add_argument('-s', '--start', metavar='DATE', help='Start day')
    parser.add_argument('-e', '--end', metavar='DATE', help='End day')
    parser.add_argument('-l', '--leagues', action='append',
                        help='Fetch these leagues')
    args = parser.parse_args()
    return args

def each_day(start_day, end_day):
    current_day = start_day
    while current_day <= end_day:
        yield current_day
        current_day += timedelta(1)
