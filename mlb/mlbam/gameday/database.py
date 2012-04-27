'''
Add parsed Gameday data to the database.
'''

from sqlalchemy import MetaData, create_engine
from sqlalchemy.sql import select

# No command line interface because it requires parsed Gameday data. There
# currently isn't a way to save the parsed data to disk, so it would be wasted
# work to add a command line interface.
def add_to_db(options, games):
    pass
