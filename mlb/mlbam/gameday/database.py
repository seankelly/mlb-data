'''
Add parsed Gameday data to the database.
'''

from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select

# No command line interface because it requires parsed Gameday data. There
# currently isn't a way to save the parsed data to disk, so it would be wasted
# work to add a command line interface.
def add_to_db(options, games):
    if 'database' not in options or not options['database']:
        raise ValueError("No database specified.")
    insert_games(options['database'], games)

def insert_games(database, games):
    conn, meta = connect_db(database)
    players = load_players(conn, meta)
    trans = conn.begin()
    try:
        for game in games:
            pass
        trans.commit()
    except:
        trans.rollback()
        raise
    conn.close()

def connect_db(database):
    engine = create_engine(database)
    conn = engine.connect()
    meta = MetaData()
    meta.reflect(bind=conn)
    return conn, meta

def load_players(conn, meta):
    mlbamids = set()
    player_table = meta.tables['mlbam_player']
    select_ids = select([player_table.c.mlbamid],
                        player_table.c.mlbamid != None)
    for row in conn.execute(select_ids):
        mlbamids.add(row['mlbamid'])
    return mlbamids

def insert_game(conn, game):
    pass
