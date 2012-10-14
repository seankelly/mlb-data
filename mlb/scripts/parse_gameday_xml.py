import os.path
import mlb.mlbam.gameday.database as db
from mlb.database import connect_db
from mlb.util import commandline_args, each_day
from mlb.mlbam.gameday.parse import parse_day

def run():
    parsed_games = []
    options, args = commandline_args('Parse Gameday XML files')
    conn, meta = connect_db(options['database'])
    for league in options['leagues']:
        dir = os.path.join(options['output_dir'], league)
        for day in each_day(options['start'], options['end']):
            parsed_games.extend(parse_day(dir, day))
        # Since I'm running this on a memory constrained system, flush the
        # games to a database periodically. Currently trying for every 150
        # games, since 300 was about twice the memory I wanted to use.
        if len(parsed_games) > 150:
            db.insert_games(conn, meta, parsed_games)
            parsed_games = []
    # And insert any remaining games.
    if parsed_games:
        db.insert_games(conn, meta, parsed_games)
