'''
Parse the Gameday data.
'''

from lxml import etree
import fnmatch
import os

def parse(directory, **kwargs):
    return GamedayParser(directory, **kwargs)

class GamedayParser():
    def __init__(self, directory):
        self.directory = directory
        self.game_children = etree.XPath('/game/*')
        self.find_players = etree.XPath('/game/team/player')
        self.find_atbats = etree.XPath('/inning/*/atbat')
        self.find_bip = etree.XPath('/hitchart/hip')
        self.game = {'team':{}, 'player':set(), 'atbat':[]}
        self._parse()

    def _parse_game_xml(self):
        game_xml = os.path.join(self.directory, 'game.xml')
        game = self.game
        for el in self.game_children(etree.parse(game_xml)):
            if el.tag == 'team':
                game['team'][el.get('type')] = el.get('id')
            elif el.tag == 'stadium':
                game['park'] = el.get('id')

    def add_players_xml(self):
        players_xml = os.path.join(game_dir, 'players.xml')
        if not os.path.exists(players_xml):
            return
        for player in find_players(etree.parse(players_xml)):
            mlbid = int(player.get('id'))
            self.game['player'].add(mlbamid)

    def _parse(self):
        self._parse_game_xml()
        self._parse_players_xml()
        add_players_xml(game_dir)
        # Skip inning_hit.xml. It is special and needs different processing.
        xml_files = fnmatch.filter(os.listdir(game_dir), 'inning_[!h]*.xml')
        bip = find_bip(etree.parse(os.path.join(game_dir, 'inning_hit.xml')))
        # Reverse it because python 2.5 doesn't have popleft()
        bip.reverse()

        # Keep these fields.
        # Right now this is all but one ('brief_event'), but MLBAM has added fields before.
        ab_fields = {'pitcher': 'pitcher', 'batter': 'batter', 'stand': 'batter_stand', 'p_throws': 'pitcher_throw', 'des': 'des', 'event': 'event'}
        # Add in bip_x/y columns
        ab_ins = gd.meta.tables['atbat'].insert()
        bip_ins = gd.meta.tables['bip'].insert()
        pitch_fields = {'spin_rate': 'spin_rate', 'break_angle': 'break_angle', 'pitch_type': 'pitch_type', 'ax': 'ax', 'ay': 'ay', 'y0': 'y0', 'az': 'az', 'end_speed': 'end_speed', 'spin_dir': 'spin_dir', 'start_speed': 'start_speed', 'pz': 'pz', 'px': 'px', 'type': 'type', 'sz_bot': 'sz_bot', 'pfx_z': 'pfx_z', 'vy0': 'vy0', 'pfx_x': 'pfx_x', 'break_length': 'break_length', 'x0': 'x0', 'z0': 'z0', 'break_y': 'break_y', 'sz_top': 'sz_top', 'type_confidence': 'type_confidence', 'y': 'y', 'x': 'x', 'vz0': 'vz0', 'sv_id': 'sv_id', 'vx0': 'vx0', 'des': 'des'}
        pitch_ins = gd.meta.tables['raw_pitch'].insert()
        pitch_inserts = []

        for inning in range(1, len(xml_files) + 1):
            xml_file = 'inning_' + str(inning) + '.xml'
            atbats = find_atbats(etree.parse(os.path.join(game_dir, xml_file)))
            for atbat in atbats:
                ab_data = { 'game': game['id'], 'inning': inning }
                for field in ab_fields:
                    key = ab_fields[field]
                    ab_data[key] = atbat.get(field)
                    if ab_data[key]:
                        ab_data[key] = ab_data[key].strip()
                res = gd.conn.execute(ab_ins, ab_data)
                ab_id = res.inserted_primary_key[0]

                # Try to match the atbat with entry in inning_hit.xml
                idx = len(bip)-1
                while idx >= 0 and ab_data['pitcher'] == bip[idx].get('pitcher') and ab_data['batter'] == bip[idx].get('batter') and inning == int(bip[idx].get('inning')):
                    try:
                        x = int(float(bip[idx].get('x')) * 249/250)
                        y = int(float(bip[idx].get('y')) * 249/250)
                        gd.conn.execute(bip_ins, { 'atbat': ab_id, 'park': game['park'], 'type': bip[idx].get('type'), 'x': x, 'y': y })
                    except ValueError:
                        pass
                    bip.pop()
                    idx = len(bip)-1

                balls, strikes = 0, 0
                sequence = 1
                for pitch in atbat.getiterator('pitch'):
                    enhanced = True if pitch.get('pitch_type') else False
                    pitch_data = { 'atbat': ab_id, 'enhanced': enhanced, 'balls': balls, 'strikes': strikes, 'sequence': sequence, 'game': game['id'], 'batter': ab_data['batter'], 'pitcher': ab_data['pitcher'] }
                    for key in pitch_fields:
                        pitch_data[key] = pitch.get(key)
                        if pitch_data[key]:
                            pitch_data[key] = pitch_data[key].strip()
                    pitch_inserts.append(pitch_data)

                    sequence += 1
                    # Calculate the count
                    # ..after the pitch!
                    called = pitch.get('type')
                    des    = pitch.get('des')
                    if called == 'B':
                        balls += 1
                    elif called == 'S' and (strikes < 2 or (des != 'Foul' and des != 'Foul (Runner Going)')):
                        strikes += 1


def load_players():
    player_table = gd.meta.tables['mlbam_player']
    select_ids = select([player_table.c.mlbamid], player_table.c.mlbamid != None)
    for row in gd.conn.execute(select_ids):
        mlbamids.add(row['mlbamid'])

find_players = etree.XPath('/game/team/player')
def add_players_xml(game_dir):
    players_xml = os.path.join(game_dir, 'players.xml')
    if not os.path.exists(players_xml):
        return
    add_player = gd.meta.tables['mlbam_player'].insert()
    ins = []
    for player in find_players(etree.parse(players_xml)):
        mlbid = int(player.get('id'))
        if mlbid not in mlbamids:
            ins.append({ 'mlbamid': mlbid, 'namefirst': player.get('first'), 'namelast': player.get('last') })
            mlbamids.add(mlbid)
    if (len(ins) > 0):
        gd.conn.execute(add_player, ins)


game_children = etree.XPath('/game/*')
def parse_game_xml(game_dir, day):
    game_ins = gd.meta.tables['game'].insert()
    game = { 'day': str(day) }
    for el in game_children(etree.parse(os.path.join(game_dir, 'game.xml'))):
        if el.tag == 'team':
            game[el.get('type')] = el.get('id')
        elif el.tag == 'stadium':
            game['park'] = el.get('id')
    res = gd.conn.execute(game_ins, game)
    game['id'] = res.inserted_primary_key[0]
    return game


find_atbats = etree.XPath('/inning/*/atbat')
find_bip = etree.XPath('/hitchart/hip')
