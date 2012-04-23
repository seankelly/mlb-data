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
        self.game = {'team':{}, 'player':{}, 'atbat':[]}
        self._parse()

    def _parse_game_xml(self):
        game_xml = os.path.join(self.directory, 'game.xml')
        game = self.game
        for el in self.game_children(etree.parse(game_xml)):
            if el.tag == 'team':
                game['team'][el.get('type')] = el.get('id')
            elif el.tag == 'stadium':
                game['park'] = el.get('id')

    def _parse_players_xml(self):
        players_xml = os.path.join(game_dir, 'players.xml')
        if not os.path.exists(players_xml):
            return
        for player in find_players(etree.parse(players_xml)):
            mlbid = int(player.get('id'))
            self.game['player'][mlbamid] = {
                'first': player.get('first'),
                'last': player.get('last'),
            }

    def _parse_inning_hit_xml(self):
        xml_file = etree.parse(os.path.join(self.directory, 'inning_hit.xml'))
        BIP = []
        for bip in self.find_bip(xml_file)
            x = int(float(bip.get('x')) * 249/250)
            y = int(float(bip.get('y')) * 249/250)
            # Skip the 'des' field, since it will be in the atbat XML.
            BIP.append({'x': x, 'y': y, 'park': self.game['park'], 'type':
                        bip.get('type')}]
        self.game['bip'] = BIP

    def _parse_pitches(self, atbat, ab_data):
        pitch_fields = set(['spin_rate', 'break_angle', 'pitch_type', 'ax',
            'ay', 'y0', 'az', 'end_speed', 'spin_dir', 'start_speed', 'pz',
            'px', 'type', 'sz_bot', 'pfx_z', 'vy0', 'pfx_x', 'break_length',
            'x0', 'z0', 'break_y', 'sz_top', 'type_confidence', 'y', 'x',
            'vz0', 'sv_id', 'vx0', 'des'])
        balls, strikes = 0, 0
        sequence = 1
        for pitch in atbat.getiterator('pitch'):
            enhanced = True if pitch.get('pitch_type') else False
            pitch_data = {'enhanced': enhanced, 'balls': balls, 'strikes':
                    strikes, 'sequence': sequence, 'batter': ab_data['batter'],
                    'pitcher': ab_data['pitcher']}
            for key in pitch_fields:
                pitch_data[key] = pitch.get(key)
                if pitch_data[key]:
                    pitch_data[key] = pitch_data[key].strip()
            sequence += 1
            # The count is the balls and strikes for when the pitch was
            # delivered, rather than the resulting count.
            called = pitch.get('type')
            des = pitch.get('des')
            if called == 'B':
                balls += 1
            elif (called == 'S' and (strikes < 2 or (des != 'Foul' and des !=
                  'Foul (Runner Going)'))):
                strikes += 1

    def _parse_inning_xml(self):
        # Keep these fields.
        # 'atbat' is a misnomer, since these are actually plate appearances.
        # However, since the XML files use the term atbat, use that.
        ab_fields = {'pitcher': 'pitcher', 'batter': 'batter', 'stand':
                'batter_stand', 'p_throws': 'pitcher_throw', 'des': 'des',
                'event': 'event'}
        atbats = []
        # Skip inning_hit.xml. It is special and needs different processing.
        xml_files = fnmatch.filter(os.listdir(self.directory), 'inning_[!h]*.xml')
        for inning in range(1, len(xml_files) + 1):
            xml_file = os.path.join(self.directory, 'inning_' + str(inning) + '.xml')
            inning_atbats = self.find_atbats(etree.parse(xml_file)))
            for atbat in inning_atbats:
                ab_data = {'inning': inning}
                for field in ab_fields:
                    key = ab_fields[field]
                    ab_data[key] = atbat.get(field)
                    if ab_data[key]:
                        ab_data[key] = ab_data[key].strip()
                ab_data['pitches'] = self._parse_pitches(atbat, ab_data)
                atbats.append(ab_data)
        self.game['atbats'] = atbats

    def _parse(self):
        self._parse_game_xml()
        self._parse_players_xml()
        # Parse the inning_hit.xml first to make it easier to match each bip
        # with data in the inning XML files.
        self._parse_inning_hit_xml()
        self._parse_inning_xml()
        return

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


def load_players():
    player_table = gd.meta.tables['mlbam_player']
    select_ids = select([player_table.c.mlbamid], player_table.c.mlbamid != None)
    for row in gd.conn.execute(select_ids):
        mlbamids.add(row['mlbamid'])
