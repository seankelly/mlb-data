"""
Miscellaneous functions for manipulating HDF5 files.
"""

import h5py

def init_hdf5(h5_file):
    """
    Initializes the HDF5 file with empty datasets to make it easier to import
    data into different parts.
    """
    _create_groups(h5_file)

def _create_groups(h5_file):
    group_tree = {
        'games': {},
        'people': {},
        'stats': {
            'teams': {},
            'players': {},
        },
    }

    def recurse_tree(h5_group, tree):
        for group in tree:
            # Create the group, if missing.
            if group not in h5_group:
                subgroup = h5_group.create_group(group)
                # And recurse.
                recurse_tree(subgroup, tree[group])
    recurse_tree(h5_file, group_tree)
