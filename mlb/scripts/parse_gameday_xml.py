import os.path
import mlb.mlbam.gameday.database as db
from mlb.backend.database import DB
from mlb.util import commandline_args, each_day
from mlb.mlbam.gameday.parse import parse_day

def run():
    options, args = commandline_args('Parse Gameday XML files')
    d = DB()
    conn, meta = d.connect(options['database'])
    for league in options['leagues']:
        dir = os.path.join(options['output_dir'], league)
        for day in each_day(options['start'], options['end']):
            parsed_games = parse_day(dir, day)
            db.insert_games(conn, meta, parsed_games)
