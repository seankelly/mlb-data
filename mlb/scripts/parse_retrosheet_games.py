from mlb.retrosheet.parse import parse_game_info
from ..util import commandline_args

def run():
    args, extra_args = commandline_args('Parse Retrosheet extended game description')
    parse_game_info(extra_args)
