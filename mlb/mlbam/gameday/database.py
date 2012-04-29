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
    parks = load_parks(conn, meta)
    teams = load_teams(conn, meta)
    players = load_players(conn, meta)
    trans = conn.begin()
    try:
        for game in games:
            insert_game(conn, meta, game, parks, teams, players)
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

def insert_game(conn, meta, game, parks, teams, players):
    # Check that there's even a game to parse.
    if not game.game:
        return
    add_players(conn, meta, players, game.game['player'])
    add_park(conn, meta, parks, game.game['park'])
    add_teams(conn, meta, parks, game.game['team'])

def load_players(conn, meta):
    mlbamids = set()
    player_table = meta.tables['mlbam_player']
    select_ids = select([player_table.c.mlbamid],
                        player_table.c.mlbamid != None)
    for row in conn.execute(select_ids):
        mlbamids.add(row['mlbamid'])
    return mlbamids

def add_players(conn, meta, players, player_list):
    new_players = set(player_list) - players
    if new_players:
        insert_players = meta.tables['mlbam_player'].insert()
        plist = []
        for id in new_players:
            plist.append({'mlbamid': id, 'namefirst': player_list[id]['first'],
                          'namelast': player_list[id]['last']})
        conn.execute(insert_players, plist)

def load_parks(conn, meta):
    parkids = set()
    park_table = meta.tables['park']
    select_ids = select([park_table.c.id], park_table.c.id != None)
    for row in conn.execute(select_ids):
        parkids.add(row['id'])
    return parkids

def add_park(conn, meta, parks, park):
    if park['id'] not in parks:
        insert_park = meta.tables['park'].insert()
        conn.execute(insert_park, park)
        parks.add(park['id'])

def load_teams(conn, meta):
    teamids = set()
    team_table = meta.tables['team']
    select_ids = select([team_table.c.id], team_table.c.id != None)
    for row in conn.execute(select_ids):
        teamids.add(row['id'])
    return teamids

def add_teams(conn, meta, teams, team_list):
    for key in ['home', 'away']:
        if team_list[key]['id'] not in teams:
            insert_team = meta.tables['team'].insert()
            conn.execute(insert_team, team_list[key])
            teams.add(team_list[key]['id'])
