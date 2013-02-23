"""
Return two numpy arrays with all of the stats to track. This will make it
easier to incrementally add stats for the players.
"""

import numpy as np

def get_stats_mapping():
    offense_stats = ['1B', '2B', '3B', 'HR', 'K', 'BB', 'IBB', 'HBP', 'O', 'SB', 'CS', 'PO',]
    defense_stats = ['1B', '2B', '3B', 'HR', 'K', 'BB', 'IBB', 'HBP', 'O', 'SB', 'CS', 'PO', 'WP', 'PB',]
    offense_map = {}
    defense_map = {}
    for index, stat in enumerate(offense_stats):
        offense_map[stat] = index
    for index, stat in enumerate(defense_stats):
        defense_map[stat] = index
    return offense_map, defense_map

def get_stats():
    offense_map, defense_map = get_stats_mapping()
    offense = tuple(['i2']*len(offense_map))
    # Pitching and general defense merged together for now. Future obvious
    # optimization will be to split these.
    defense = tuple(['i2']*len(defense_map))

    return np.dtype('i2'), np.dtype('i2')
