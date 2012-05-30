'''
Parse the Gameday data.
'''

from lxml import etree
import fnmatch
import os

def parse_day(output_dir, day):
    parsed_games = []
    datematch = day.strftime("gid_%Y_%m_%d_*")
    year_dir = os.path.join(output_dir, str(day.year))
    games = fnmatch.filter(os.listdir(year_dir), datematch)
    for game in games:
        game_dir = os.path.join(year_dir, game)
        parsed_games.append(GamedayParser(game_dir, day))
    return parsed_games

class GamedayParser():
    def __init__(self, directory, day):
        self.directory = directory
        self.game_children = etree.XPath('/game/*')
        self.find_players = etree.XPath('/game/team/player')
        self.find_atbats = etree.XPath('/inning/*/atbat')
        self.find_bip = etree.XPath('/hitchart/hip')
        self.game = {}
        self.day = day
        self._parse()

    def _parse_game_xml(self):
        game_xml = os.path.join(self.directory, 'game.xml')
        game = self.game
        info = {'day': self.day}
        for el in self.game_children(etree.parse(game_xml)):
            if el.tag == 'team':
                league = el.get('league')
                if league == 'NL' or league == 'AL':
                    info['league'] = 'MLB'
                fullname = el.get('name_full')
                location = el.get('name')
                # In old-style game.xml files, the 'name_full' and 'name_brief'
                # attributes do not exist. Since there is no way to get the
                # team name, just stick with None.
                if fullname:
                    if fullname.startswith(location):
                        # This is to ensure the name is the full, unabbreviated
                        # team name. For instance, the Diamondbacks are
                        # abbreviated as 'D-backs' when I want the full name.
                        team_name = fullname[len(location):len(fullname)].strip()
                    else:
                        # Just in case.
                        team_name = el.get('name_brief')
                else:
                    team_name = None
                team_type = el.get('type')
                game['team'][team_type] = {'id': int(el.get('id')),
                        'code': el.get('code'), 'name': team_name,
                        'fullname': fullname}
                info[team_type] = int(el.get('id'))
            elif el.tag == 'stadium':
                game['park'] = {'id': int(el.get('id')), 'name': el.get('name'),
                                'location': el.get('location')}
                info['park'] = int(el.get('id'))
        game['info'] = info

    def _parse_players_xml(self):
        players_xml = os.path.join(self.directory, 'players.xml')
        if not os.path.exists(players_xml):
            return
        for player in self.find_players(etree.parse(players_xml)):
            mlbamid = int(player.get('id'))
            self.game['player'][mlbamid] = {
                'first': player.get('first'),
                'last': player.get('last'),
            }

    def _parse_inning_hit_xml(self):
        xml_file = etree.parse(os.path.join(self.directory, 'inning_hit.xml'))
        BIP = []
        for bip in self.find_bip(xml_file):
            bip_x = bip.get('x')
            bip_y = bip.get('y')
            # Errors are stored with empty x and y attributes. Mark them as
            # zero instead so they will still be added. They will then need to
            # be filtered out when dumping.
            if not bip_x:
                bip_x = 0
            if not bip_x:
                bip_y = 0
            x = int(float(bip_x) * 249/250)
            y = int(float(bip_y) * 249/250)
            # Skip the 'des' field, since it will be in the atbat XML.
            bip_data = {'x': x, 'y': y, 'park': self.game['park']['id'],
                        'type': bip.get('type')}
            for key in ['inning', 'pitcher', 'batter']:
                bip_data[key] = int(bip.get(key))
            BIP.append(bip_data)
        self.game['bip'] = BIP

    def _parse_pitches(self, atbat, ab_data):
        pitch_fields = set(['spin_rate', 'break_angle', 'pitch_type', 'ax',
            'ay', 'y0', 'az', 'end_speed', 'spin_dir', 'start_speed', 'pz',
            'px', 'type', 'sz_bot', 'pfx_z', 'vy0', 'pfx_x', 'break_length',
            'x0', 'z0', 'break_y', 'sz_top', 'type_confidence', 'y', 'x',
            'vz0', 'sv_id', 'vx0', 'des'])
        float_fields = set(['spin_rate', 'break_angle', 'ax', 'ay', 'y0', 'az',
            'end_speed', 'spin_dir', 'start_speed', 'pz', 'px', 'sz_bot',
            'pfx_z', 'vy0', 'pfx_x', 'break_length', 'x0', 'z0', 'break_y',
            'sz_top', 'type_confidence', 'y', 'x', 'vz0', 'vx0'])
        balls, strikes = 0, 0
        sequence = 1
        pitches = []
        for pitch in atbat.getiterator('pitch'):
            enhanced = True if pitch.get('pitch_type') else False
            pitch_data = {'enhanced': enhanced, 'balls': balls, 'strikes':
                    strikes, 'sequence': sequence, 'batter': ab_data['batter'],
                    'pitcher': ab_data['pitcher']}
            for key in pitch_fields:
                value = pitch.get(key)
                if value:
                    if key in float_fields:
                        value = float(value)
                    else:
                        value = value.strip()
                pitch_data[key] = value
            pitches.append(pitch_data)
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
        return pitches

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
            inning_atbats = self.find_atbats(etree.parse(xml_file))
            for atbat in inning_atbats:
                ab_data = {'inning': inning}
                for field in ab_fields:
                    key = ab_fields[field]
                    if key != 'pitcher' and key != 'batter':
                        ab_data[key] = atbat.get(field)
                        if ab_data[key]:
                            ab_data[key] = ab_data[key].strip()
                    else:
                        ab_data[key] = int(atbat.get(field))
                ab_data['pitches'] = self._parse_pitches(atbat, ab_data)
                atbats.append(ab_data)
        self.game['atbat'] = atbats

    def _match_bip(self):
        ab_idx, ab_max = 0, len(self.game['atbat'])
        for bip_idx, bip in enumerate(self.game['bip']):
            while ab_idx < ab_max:
                ab = self.game['atbat'][ab_idx]
                ab_idx += 1
                if (bip['pitcher'] == ab['pitcher'] and
                        bip['batter'] == ab['batter'] and
                        bip['inning'] == ab['inning']):
                    ab['bip'] = bip_idx
                    break

    def _parse(self):
        game_xml = os.path.join(self.directory, 'game.xml')
        if not os.path.exists(game_xml):
            return
        self.game = {'team':{}, 'player':{}, 'atbat':[]}
        self._parse_game_xml()
        self._parse_players_xml()
        # Parse the inning_hit.xml first to make it easier to match each bip
        # with data in the inning XML files.
        self._parse_inning_hit_xml()
        self._parse_inning_xml()
        self._match_bip()


def load_players():
    player_table = gd.meta.tables['mlbam_player']
    select_ids = select([player_table.c.mlbamid], player_table.c.mlbamid != None)
    for row in gd.conn.execute(select_ids):
        mlbamids.add(row['mlbamid'])
