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
