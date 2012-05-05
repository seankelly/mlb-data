from sqlalchemy import MetaData, create_engine

def connect_db(database):
    engine = create_engine(database)
    conn = engine.connect()
    meta = MetaData()
    meta.reflect(bind=conn)
    return conn, meta
