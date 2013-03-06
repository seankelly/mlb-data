"""
Return two numpy arrays with all of the stats to track. This will make it
easier to incrementally add stats for the players.
"""

import numpy as np

def get_stats_mapping():
    stats = {
        'offense': ['PA', 'AB', 'R', '1B', '2B', '3B', 'HR', 'ROE', 'RBI', 'K', 'BB', 'IBB', 'HBP', 'O', 'SF', 'SH', 'SB', 'CS', 'PO',],
        'pitching': ['G', 'GS', 'GF', 'CG', 'SHO', 'W', 'L', 'S', 'O', 'R', 'ER', 'K', 'BB', 'IBB', 'HBP', 'BK', 'SB', 'CS', 'WP', '1B', '2B', '3B', 'HR', 'GDP', 'ROE',],
        'fielding': ['Pos', 'Ch', 'PO', 'A', 'E', 'DP', 'SB', 'CS', 'WP', 'PB', 'Pickoff',],
    }
    stat_map = {}
    for what in stats:
        stat_map[what] = {}
        for index, stat in enumerate(stats[what]):
            stat_map[what][stat] = index
    return stat_map
