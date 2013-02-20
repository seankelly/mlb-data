"""
Return two numpy arrays with all of the stats to track. This will make it
easier to incrementally add stats for the players.
"""

import numpy as np

def get_stats():
    offense = [
        ('1B', 'i2'),
        ('2B', 'i2'),
        ('3B', 'i2'),
        ('HR', 'i2'),
        ('K', 'i2'),
        ('BB', 'i2'),
        ('IBB', 'i2'),
        ('HBP', 'i2'),
        ('O', 'i2'),
        ('SB', 'i2'),
        ('CS', 'i2'),
        ('PO', 'i2'),
    ]
    # Pitching and general defense merged together for now. Future obvious
    # optimization will be to split these.
    defense = [
        # Matching opposites of offensive stats.
        ('1B', 'i2'),
        ('2B', 'i2'),
        ('3B', 'i2'),
        ('HR', 'i2'),
        ('K', 'i2'),
        ('BB', 'i2'),
        ('IBB', 'i2'),
        ('HBP', 'i2'),
        ('O', 'i2'),
        ('SB', 'i2'),
        ('CS', 'i2'),
        ('PO', 'i2'),
        # Fielding stats.
    ]

    return np.dtype(offense), np.dtype(defense)
