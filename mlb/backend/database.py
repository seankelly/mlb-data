'''
Add parsed Gameday data to the database.
'''
from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select


class DB():
    def __init__(self):
        self.parks = None
        self.players = None

    def connect(self, database):
        engine = create_engine(database)
        conn = engine.connect()
        meta = MetaData()
        meta.reflect(bind=conn)
        self.meta = meta
        self.conn = conn
        return conn, meta

    def add_games(self, games):
        self.load_parks()
        self.load_teams()
        self.load_players()
        trans = self.conn.begin()
        try:
            for game in games:
                self.insert_game(game)
            trans.commit()
        except:
            trans.rollback()
            raise

    def insert_game(self, game):
        # Check that there's even a game to parse.
        if not game.game:
            return
        self.add_players(game.game['player'])
        self.add_park(game.game['park'])
        self.add_teams(game.game['team'])
        insert_game = self.meta.tables['game'].insert()
        res = self.conn.execute(insert_game, game.game['info'])
        gameid = res.inserted_primary_key[0]
        self.insert_ab(gameid, game)

    def insert_ab(self, gameid, game):
        insert_atbat = self.meta.tables['atbat'].insert()
        insert_bip = self.meta.tables['bip'].insert()
        atbats = game.game['atbat']
        bip = game.game['bip']
        for ab in atbats:
            ab_ins = ab.copy()
            ab_ins['game'] = gameid
            res = self.conn.execute(insert_atbat, ab_ins)
            abid = res.inserted_primary_key[0]
            if 'bip' in ab:
                ab_bip = []
                for bip_idx in ab['bip']:
                    b = bip[bip_idx].copy()
                    b['atbat'] = abid
                    ab_bip.append(b)
                self.conn.execute(insert_bip, ab_bip)
            if ab['pitches']:
                self.insert_pitches(gameid, abid, ab['pitches'])

    def insert_pitches(self, gameid, abid, pitches):
        insert_pitches = self.meta.tables['raw_pitch'].insert()
        db_pitches = []
        for pitch in pitches:
            p = pitch.copy()
            p['game'] = gameid
            p['atbat'] = abid
            db_pitches.append(p)
        self.conn.execute(insert_pitches, db_pitches)

    def add_players(self, players):
        new_players = set(players) - self.players
        if new_players:
            insert_players = self.meta.tables['mlbam_player'].insert()
            plist = []
            for id in new_players:
                plist.append({'mlbamid': id,
                    'namefirst': players[id]['first'],
                    'namelast': players[id]['last']})
                self.players.add(id)
            self.conn.execute(insert_players, plist)

    def load_players(self):
        mlbamids = set()
        player_table = self.meta.tables['mlbam_player']
        select_ids = select([player_table.c.mlbamid],
                            player_table.c.mlbamid != None)
        for row in self.conn.execute(select_ids):
            mlbamids.add(row['mlbamid'])
        self.players = mlbamids

    def add_park(self, park):
        parks = self.parks
        if park['id'] not in parks:
            insert_park = self.meta.tables['park'].insert()
            self.conn.execute(insert_park, park)
            parks.add(park['id'])

    def load_parks(self):
        parkids = set()
        park_table = self.meta.tables['park']
        select_ids = select([park_table.c.id], park_table.c.id != None)
        for row in self.conn.execute(select_ids):
            parkids.add(row['id'])
        self.parks = parkids

    def add_teams(self, teams):
        for key in ['home', 'away']:
            if teams[key]['id'] not in teams:
                insert_team = self.meta.tables['team'].insert()
                self.conn.execute(insert_team, teams[key])
                self.teams.add(teams[key]['id'])

    def load_teams(self):
        teamids = set()
        team_table = self.meta.tables['team']
        select_ids = select([team_table.c.id], team_table.c.id != None)
        for row in self.conn.execute(select_ids):
            teamids.add(row['id'])
        self.teams = teamids
