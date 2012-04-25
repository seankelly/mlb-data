import os
import sys

root = os.path.abspath(sys.argv[0])
while os.path.dirname(root) != root:
    init_path = os.path.join(root, 'mlb', 'mlbam', '__init__.py')
    if os.path.exists(init_path):
        sys.path.insert(0, root)
        break
    root = os.path.dirname(root)
