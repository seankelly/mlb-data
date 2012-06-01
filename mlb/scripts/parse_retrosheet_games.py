from ..database import connect_db
from ...util import commandline_args

def run():
    args = commandline_args('Parse Retrosheet game log files')
    conn, meta = connect_db(options['database'])
