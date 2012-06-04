import mlb.mlbam.gameday as gameday
from mlb.database import connect_db
from mlb.util import commandline_args, each_day

def run():
    parsed_games = []
    args = commandline_args('Parse Gameday XML files')
    conn, meta = connect_db(options['database'])
    for league in args['leagues']:
        dir = os.path.join(args['output_dir'], league)
        for day in each_day(args['start'], args['end']):
            parsed_games.extend(gameday.parse.parse_day(dir, day))
        # Since I'm running this on a memory constrained system, flush the
        # games to a database periodically. 300 games is a little over three
        # weeks during the middle of the season. The system can handle a full
        # month, but I get the feeling it's swapping when it hits 400 games.
        if len(parsed_games) > 300:
            gameday.database.insert_games(conn, meta, parsed_games)
            parsed_games = []
    # And insert any remaining games.
    if parsed_games:
        gameday.database.insert_games(conn, meta, parsed_games)
