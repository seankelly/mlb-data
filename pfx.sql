CREATE TABLE player (
    mlbid integer,
    name text
);

CREATE TABLE atbat (
    id integer PRIMARY KEY,
    pitcher integer,
    batter integer,
    batter_stand text,
    pitcher_throw text,
    des text,
    event text,
    brief_event text
);

CREATE TABLE raw_pitch (
    id integer PRIMARY KEY,
    atbat integer,
    enhanced integer,
    balls integer,  -- count data
    strikes integer,
    px real,
    pz real,
    x real,
    y real,
    break_angle real,
    break_length real,
    break_y real,
    pfx_x real,
    pfx_z real,
    spin_dir real,
    spin_rate real,
    start_speed real,
    end_speed real,
    sz_bot real,
    sz_top real,
    sv_id text,
    pitch_type text,
    type text,
    type_confidence text,
    x0 real,
    y0 real,
    z0 real,
    vx0 real,
    vy0 real,
    vz0 real,
    ax real,
    ay real,
    az real
);
