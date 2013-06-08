import sqlalchemy as sa

class Model():
    metadata = sa.MetaData()

    mlbam_player = sa.Table('mlbam_player', metadata,
        # Use MLBAM's player ids.
        sa.Column('mlbamid', sa.Integer, primary_key=True),
        sa.Column('namefirst', sa.Text),
        sa.Column('namelast', sa.Text)
    )

    park = sa.Table('park', metadata,
        # Use MLBAM's ids.
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text),
        sa.Column('location', sa.Text)
    )

    park_dimension = sa.Table('park_dimension', metadata,
        sa.Column('park_id', sa.Integer, sa.ForeignKey('park.id'),
            primary_key=True, nullable=False),
        sa.Column('image_file', sa.Text),
        sa.Column('opening', sa.Date),
        sa.Column('closing', sa.Date),
        sa.Column('hp_x', sa.Float),
        sa.Column('hp_y', sa.Float),
        sa.Column('image_hp_x', sa.Float),
        sa.Column('image_hp_y', sa.Float),
        sa.Column('scale', sa.Float)
    )

    team = sa.Table('team', metadata,
        # Use MLBAM's ids.
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.Text),
        sa.Column('fullname', sa.Text),
        sa.Column('name', sa.Text)
    )

    game = sa.Table('game', metadata,
        sa.Column('id', sa.Integer, sa.Sequence('game_id_seq'),
            primary_key=True),
        sa.Column('league', sa.Text),
        sa.Column('home', sa.Integer),
        sa.Column('away', sa.Integer),
        sa.Column('park', sa.Integer),
        sa.Column('day', sa.Date),
    )

    atbat = sa.Table('atbat', metadata,
        sa.Column('id ', sa.Integer, sa.Sequence('atbat_id_seq'),
            primary_key=True)
        sa.Column('game', sa.Integer, sa.ForeignKey('game.id'), nullable=False),
        sa.Column('pitcher', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('batter_stand', sa.Text),
        sa.Column('pitcher_throw', sa.Text),
        sa.Column('des', sa.Text),
        sa.Column('event', sa.Text)
    )

    bip = sa.Table('bip', metadata,
        sa.Column('id', sa.Integer, sa.Sequence('bip_id_seq'),
            primary_key=True),
        sa.Column('atbat', sa.Integer, sa.ForeignKey('atbat.id'),
            nullable=False),
        sa.Column('pitcher', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('park', sa.Integer, sa.ForeignKey('park.id'), nullable=False),
        sa.Column('type', sa.Text),
        sa.Column('x', sa.Integer),
        sa.Column('y', sa.Integer)
    )

    raw_pitch = sa.Table('raw_pitch', metadata,
        sa.Column('id', sa.Integer, sa.Sequence('raw_pitch_id_seq'),
            primary_key=True),
        sa.Column('atbat', sa.Integer, sa.ForeignKey('atbat.id'),
            nullable=False),
        sa.Column('game', sa.Integer, sa.ForeignKey('game.id'), nullable=False),
        sa.Column('pitcher', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbam_player'), nullable=False),
        sa.Column('enhanced', sa.Boolean),
        sa.Column('inning', sa.Integer),
        sa.Column('sequence', sa.Integer),
        # Count data.
        sa.Column('balls', sa.Integer),
        sa.Column('strikes', sa.Integer),
        sa.Column('des', sa.Text),
        sa.Column('px', sa.Float),
        sa.Column('pz', sa.Float),
        sa.Column('x', sa.Float),
        sa.Column('y', sa.Float),
        sa.Column('break_angle', sa.Float),
        sa.Column('break_length', sa.Float),
        sa.Column('break_y', sa.Float),
        sa.Column('pfx_x', sa.Float),
        sa.Column('pfx_z', sa.Float),
        sa.Column('spin_dir', sa.Float),
        sa.Column('spin_rate', sa.Float),
        sa.Column('start_speed', sa.Float),
        sa.Column('end_speed', sa.Float),
        sa.Column('sz_bot', sa.Float),
        sa.Column('sz_top', sa.Float),
        sa.Column('sv_id', sa.Text),
        sa.Column('pitch_type', sa.Text),
        sa.Column('type', sa.Text),
        sa.Column('type_confidence', sa.Text),
        sa.Column('x0', sa.Float),
        sa.Column('y0', sa.Float),
        sa.Column('z0', sa.Float),
        sa.Column('vx0', sa.Float),
        sa.Column('vy0', sa.Float),
        sa.Column('vz0', sa.Float),
        sa.Column('ax', sa.Float),
        sa.Column('ay', sa.Float),
        sa.Column('az', sa.Float)
    )
