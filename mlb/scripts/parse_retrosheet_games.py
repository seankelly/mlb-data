from mlb.retrosheet.chadwick import Events
from mlb.util import commandline_args

def run():
    args, extra_args = commandline_args('Parse Retrosheet extended game description')
    Events(extra_args)
