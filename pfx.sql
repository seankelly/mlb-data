CREATE TABLE player (
    mlbid integer,
    name text
);

CREATE TABLE egd_pitch (
    id integer,
    pitcher integer,
    batter integer,
    enhanced integer
    break_angle real,
    break_length real,
    break_y real,
    end_speed real,
    pfx_x real,
    pfx_z real,
    px real,
    pz real,
    spin_dir real,
    spin_rate real,
    start_speed real,
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
    az real,
    x real,
    y real
);
