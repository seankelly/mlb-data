from mlb.retrosheet.summarize import summarize_stats
from ..util import commandline_args

def run():
    args, extra_args = commandline_args('Summarize Retrosheet data')
    summarize_stats(args)
