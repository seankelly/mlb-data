from mlb.retrosheet.parse import parse_files
from mlb.util import commandline_args

def run():
    args, extra_args = commandline_args('Parse Retrosheet extended game description')
    parse_files(extra_args)
