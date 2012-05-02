"""
Fetch MLBAM data.

Usage:
    python get-pfx.py -o path/to/save/ [-s <start date>] [-e <end date>]

With no start or end days specified, it will fetch the previous day's data.
"""

import os
import re
import requests
import time
from datetime import date, timedelta
from html.parser import HTMLParser
from random import uniform
from ..util import commandline_args

def fetch():
    args = commandline_args('Fetch MLB Gameday data.')
    f = FetchMLBAM(**args)
    f.fetch()
    return f


class DirectoryList(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))

    def get_links(self, pattern):
        link_match = re.compile(pattern)
        links = []
        for link in self.links:
            if link_match.match(link['href']):
                links.append(link['href'])

        return links


class FetchMLBAM(object):
    base_url = "http://gd2.mlb.com/components/game/"
    mlbam_leagues = set(('aaa', 'aax', 'afa', 'afx', 'mlb', 'win'))

    def __init__(self, start, end, output_dir, leagues, **kwargs):
        self.start = kwargs.get('start', date.today()-timedelta(1))
        self.end = kwargs.get('end', date.today())
        self.output_dir = kwargs.get('output_dir', 'data')
        leagues = kwargs.get('leagues', ('mlb',))
        valid_leagues = []
        for league in leagues:
            if type(league) == str:
                valid_leagues.append(league)
        self.leagues = tuple(valid_leagues)

    def fetch(self):
        current_day = self.start
        end_day = self.end
        one_day = timedelta(1)
        while current_day < end_day:
            for league in self.leagues:
                self.fetch_league_day(league, current_day)
            current_day += one_day

    def fetch_league_day(self, league, day):
        url = (self.base_url + league + '/' +
               day.strftime("year_%Y/month_%m/day_%d/"))
        day_dir = requests.get(url)
        directory = DirectoryList()
        directory.feed(day_dir.text)
        directory.close()
        for gid in directory.get_links("^gid_{0:%Y_%m_%d}_".format(day)):
            self.fetch_game(league, day, gid)
            time.sleep(uniform(20, 30))

    def fetch_game(self, league, day, gid):
        game_url = (self.base_url + league + '/' +
                    day.strftime("year_%Y/month_%m/day_%d/") + gid)
        gid_dir = os.path.join(self.output_dir, league, str(day.year), gid)
        if not os.path.exists(gid_dir):
            os.makedirs(gid_dir)
        # This file only exists for games that were played in
        # some capacity. Try to fetch and return if cannot.
        game_xml = requests.get(game_url + "/game.xml")
        if game_xml.status_code == 404:
            return
        self.save_game_data(gid_dir, game_xml, "game.xml")
        players_xml = requests.get(game_url + "/players.xml")
        self.save_game_data(gid_dir, players_xml, "players.xml")
        # Find and save each inning file.
        self.scrape_game_dir(gid_dir, game_url + "/inning", "inning_(\d+|hit)\.xml")

    def save_game_data(self, output_dir, xml_file, file_name):
        xml_output = open(os.path.join(output_dir, file_name), 'w')
        xml_output.write(xml_file.text)
        xml_output.close()

    def scrape_game_dir(self, output_dir, url, file_re):
        url_dir = requests.get(url)
        mlb = DirectoryList()
        mlb.feed(url_dir.text)
        mlb.close()
        # Scrape the links for what we want
        for filename in mlb.get_links(file_re):
            file = requests.get(url + "/" + filename)
            self.save_game_data(output_dir, file, filename)
            time.sleep(uniform(2, 5))
