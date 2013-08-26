from mlb.retrosheet.parse import parse_retrosheet
from mlb.util import commandline_args

def run():
    args, extra_args = commandline_args('Parse Retrosheet extended game description')
    parse_retrosheet(args['file'], extra_args)
