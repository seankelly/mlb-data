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
        sa.Column('id', sa.Integer, sa.Sequence('atbat_id_seq'),
            primary_key=True),
        sa.Column('game', sa.Integer, sa.ForeignKey('game.id'), nullable=False),
        sa.Column('pitcher', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
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
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
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
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
        sa.Column('batter', sa.Integer,
            sa.ForeignKey('mlbam_player.mlbamid'), nullable=False),
        sa.Column('enhanced', sa.Boolean),
        sa.Column('inning', sa.Integer),
        sa.Column('sequence', sa.Integer),
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

    retro_games = sa.Table('retro_games', metadata,
        sa.Column('game_id', sa.String(13)),
        sa.Column('game_dt', sa.String(6)),
        sa.Column('game_ct', sa.Integer),
        sa.Column('game_dy', sa.String(10)),
        sa.Column('start_game_tm', sa.Integer),
        sa.Column('dh_fl', sa.Boolean),
        sa.Column('daynight_park_cd', sa.String(1)),
        sa.Column('away_team_id', sa.String(3)),
        sa.Column('home_team_id', sa.String(3)),
        sa.Column('park_id', sa.String(5)),
        sa.Column('away_start_pit_id', sa.String(8)),
        sa.Column('home_start_pit_id', sa.String(8)),
        sa.Column('base4_ump_id', sa.String(8)),
        sa.Column('base1_ump_id', sa.String(8)),
        sa.Column('base2_ump_id', sa.String(8)),
        sa.Column('base3_ump_id', sa.String(8)),
        sa.Column('lf_ump_id', sa.String(8)),
        sa.Column('rf_ump_id', sa.String(8)),
        sa.Column('attend_park_ct', sa.Integer),
        sa.Column('scorer_record_id', sa.String(10)),
        sa.Column('translator_record_id', sa.String(10)),
        sa.Column('inputter_record_id', sa.String(10)),
        sa.Column('input_record_ts', sa.String(10)),
        sa.Column('edit_record_ts', sa.String(10)),
        sa.Column('method_record_cd', sa.Integer),
        sa.Column('pitches_record_cd', sa.Integer),
        sa.Column('temp_park_ct', sa.Integer),
        sa.Column('wind_direction_park_cd', sa.Integer),
        sa.Column('wind_speed_park_ct', sa.Integer),
        sa.Column('field_park_cd', sa.Integer),
        sa.Column('precip_park_cd', sa.Integer),
        sa.Column('sky_park_cd', sa.Integer),
        sa.Column('minutes_game_ct', sa.Integer),
        sa.Column('inn_ct', sa.Integer),
        sa.Column('away_score_ct', sa.Integer),
        sa.Column('home_score_ct', sa.Integer),
        sa.Column('away_hits_ct', sa.Integer),
        sa.Column('home_hits_ct', sa.Integer),
        sa.Column('away_err_ct', sa.Integer),
        sa.Column('home_err_ct', sa.Integer),
        sa.Column('away_lob_ct', sa.Integer),
        sa.Column('home_lob_ct', sa.Integer),
        sa.Column('win_pit_id', sa.String(8)),
        sa.Column('lose_pit_id', sa.String(8)),
        sa.Column('save_pit_id', sa.String(8)),
        sa.Column('gwrbi_bat_id', sa.String(8)),
        sa.Column('away_lineup1_bat_id', sa.String(8)),
        sa.Column('away_lineup1_fld_cd', sa.Integer),
        sa.Column('away_lineup2_bat_id', sa.String(8)),
        sa.Column('away_lineup2_fld_cd', sa.Integer),
        sa.Column('away_lineup3_bat_id', sa.String(8)),
        sa.Column('away_lineup3_fld_cd', sa.Integer),
        sa.Column('away_lineup4_bat_id', sa.String(8)),
        sa.Column('away_lineup4_fld_cd', sa.Integer),
        sa.Column('away_lineup5_bat_id', sa.String(8)),
        sa.Column('away_lineup5_fld_cd', sa.Integer),
        sa.Column('away_lineup6_bat_id', sa.String(8)),
        sa.Column('away_lineup6_fld_cd', sa.Integer),
        sa.Column('away_lineup7_bat_id', sa.String(8)),
        sa.Column('away_lineup7_fld_cd', sa.Integer),
        sa.Column('away_lineup8_bat_id', sa.String(8)),
        sa.Column('away_lineup8_fld_cd', sa.Integer),
        sa.Column('away_lineup9_bat_id', sa.String(8)),
        sa.Column('away_lineup9_fld_cd', sa.Integer),
        sa.Column('home_lineup1_bat_id', sa.String(8)),
        sa.Column('home_lineup1_fld_cd', sa.Integer),
        sa.Column('home_lineup2_bat_id', sa.String(8)),
        sa.Column('home_lineup2_fld_cd', sa.Integer),
        sa.Column('home_lineup3_bat_id', sa.String(8)),
        sa.Column('home_lineup3_fld_cd', sa.Integer),
        sa.Column('home_lineup4_bat_id', sa.String(8)),
        sa.Column('home_lineup4_fld_cd', sa.Integer),
        sa.Column('home_lineup5_bat_id', sa.String(8)),
        sa.Column('home_lineup5_fld_cd', sa.Integer),
        sa.Column('home_lineup6_bat_id', sa.String(8)),
        sa.Column('home_lineup6_fld_cd', sa.Integer),
        sa.Column('home_lineup7_bat_id', sa.String(8)),
        sa.Column('home_lineup7_fld_cd', sa.Integer),
        sa.Column('home_lineup8_bat_id', sa.String(8)),
        sa.Column('home_lineup8_fld_cd', sa.Integer),
        sa.Column('home_lineup9_bat_id', sa.String(8)),
        sa.Column('home_lineup9_fld_cd', sa.Integer),
        sa.Column('away_finish_pit_id', sa.String(8)),
        sa.Column('home_finish_pit_id', sa.String(8)),
    )

    retro_events = sa.Table('retro_events', metadata,
        sa.Column('game_id', sa.String(13)),
        sa.Column('away_team_id', sa.String(3)),
        sa.Column('inn_ct', sa.Integer),
        sa.Column('bat_home_id', sa.Integer),
        sa.Column('outs_ct', sa.Integer),
        sa.Column('balls_ct', sa.Integer),
        sa.Column('strikes_ct', sa.Integer),
        sa.Column('pitch_seq_tx', sa.String(32)),
        sa.Column('away_score_ct', sa.Integer),
        sa.Column('home_score_ct', sa.Integer),
        sa.Column('bat_id', sa.String(8)),
        sa.Column('bat_hand_cd', sa.String(1)),
        sa.Column('resp_bat_id', sa.String(8)),
        sa.Column('resp_bat_hand_cd', sa.String(1)),
        sa.Column('pit_id', sa.String(8)),
        sa.Column('pit_hand_cd', sa.String(1)),
        sa.Column('resp_pit_id', sa.String(8)),
        sa.Column('resp_pit_hand_cd', sa.String(1)),
        sa.Column('pos2_fld_id', sa.String(8)),
        sa.Column('pos3_fld_id', sa.String(8)),
        sa.Column('pos4_fld_id', sa.String(8)),
        sa.Column('pos5_fld_id', sa.String(8)),
        sa.Column('pos6_fld_id', sa.String(8)),
        sa.Column('pos7_fld_id', sa.String(8)),
        sa.Column('pos8_fld_id', sa.String(8)),
        sa.Column('pos9_fld_id', sa.String(8)),
        sa.Column('base1_run_id', sa.String(8)),
        sa.Column('base2_run_id', sa.String(8)),
        sa.Column('base3_run_id', sa.String(8)),
        sa.Column('event_tx', sa.String(56)),
        sa.Column('leadoff_fl', sa.Boolean),
        sa.Column('ph_fl', sa.Boolean),
        sa.Column('bat_fld_cd', sa.Integer),
        sa.Column('bat_lineup_id', sa.Integer),
        sa.Column('event_cd', sa.Integer),
        sa.Column('bat_event_fl', sa.Boolean),
        sa.Column('ab_fl', sa.Boolean),
        sa.Column('h_fl', sa.Boolean),
        sa.Column('sh_fl', sa.Boolean),
        sa.Column('sf_fl', sa.Boolean),
        sa.Column('event_outs_ct', sa.Integer),
        sa.Column('dp_fl', sa.Boolean),
        sa.Column('tp_fl', sa.Boolean),
        sa.Column('rbi_ct', sa.Integer),
        sa.Column('wp_fl', sa.Boolean),
        sa.Column('pb_fl', sa.Boolean),
        sa.Column('fld_cd', sa.Integer),
        sa.Column('battedball_cd', sa.String(8)),
        sa.Column('bunt_fl', sa.Boolean),
        sa.Column('foul_fl', sa.Boolean),
        sa.Column('battedball_loc_tx', sa.String(8)),
        sa.Column('err_ct', sa.Integer),
        sa.Column('err1_fld_cd', sa.Integer),
        sa.Column('err1_cd', sa.String(1)),
        sa.Column('err2_fld_cd', sa.Integer),
        sa.Column('err2_cd', sa.String(1)),
        sa.Column('err3_fld_cd', sa.Integer),
        sa.Column('err3_cd', sa.String(1)),
        sa.Column('bat_dest_id', sa.Integer),
        sa.Column('run1_dest_id', sa.Integer),
        sa.Column('run2_dest_id', sa.Integer),
        sa.Column('run3_dest_id', sa.Integer),
        sa.Column('bat_play_tx', sa.String(16)),
        sa.Column('run1_play_tx', sa.String(16)),
        sa.Column('run2_play_tx', sa.String(16)),
        sa.Column('run3_play_tx', sa.String(16)),
        sa.Column('run1_sb_fl', sa.Boolean),
        sa.Column('run2_sb_fl', sa.Boolean),
        sa.Column('run3_sb_fl', sa.Boolean),
        sa.Column('run1_cs_fl', sa.Boolean),
        sa.Column('run2_cs_fl', sa.Boolean),
        sa.Column('run3_cs_fl', sa.Boolean),
        sa.Column('run1_pk_fl', sa.Boolean),
        sa.Column('run2_pk_fl', sa.Boolean),
        sa.Column('run3_pk_fl', sa.Boolean),
        sa.Column('run1_resp_pit_id', sa.String(8)),
        sa.Column('run2_resp_pit_id', sa.String(8)),
        sa.Column('run3_resp_pit_id', sa.String(8)),
        sa.Column('game_new_fl', sa.Boolean),
        sa.Column('game_end_fl', sa.Boolean),
        sa.Column('pr_run1_fl', sa.Boolean),
        sa.Column('pr_run2_fl', sa.Boolean),
        sa.Column('pr_run3_fl', sa.Boolean),
        sa.Column('removed_for_pr_run1_id', sa.String(8)),
        sa.Column('removed_for_pr_run2_id', sa.String(8)),
        sa.Column('removed_for_pr_run3_id', sa.String(8)),
        sa.Column('removed_for_ph_bat_id', sa.String(8)),
        sa.Column('removed_for_ph_bat_fld_cd', sa.Integer),
        sa.Column('po1_fld_cd', sa.Integer),
        sa.Column('po2_fld_cd', sa.Integer),
        sa.Column('po3_fld_cd', sa.Integer),
        sa.Column('ass1_fld_cd', sa.Integer),
        sa.Column('ass2_fld_cd', sa.Integer),
        sa.Column('ass3_fld_cd', sa.Integer),
        sa.Column('ass4_fld_cd', sa.Integer),
        sa.Column('ass5_fld_cd', sa.Integer),
        sa.Column('event_id', sa.Integer),
    )