"""
Module to define numpy dtypes for Chadwick's output from parsing
Retrosheet data.
"""

import numpy as np

def cwgame_game_dtype():
    standard_headers = [
        ('GAME_ID', 'a13'), ('GAME_DT', 'a6'), ('GAME_CT', 'i1'),
        ('GAME_DY', 'a10'), ('START_GAME_TM', 'i4'), ('DH_FL', 'a1'),
        ('DAYNIGHT_PARK_CD', 'a1'), ('AWAY_TEAM_ID', 'a3'),
        ('HOME_TEAM_ID', 'a3'), ('PARK_ID', 'a5'),
        ('AWAY_START_PIT_ID', 'a8'), ('HOME_START_PIT_ID', 'a8'),
        ('BASE4_UMP_ID', 'a8'), ('BASE1_UMP_ID', 'a8'),
        ('BASE2_UMP_ID', 'a8'), ('BASE3_UMP_ID', 'a8'),
        ('LF_UMP_ID', 'a8'), ('RF_UMP_ID', 'a8'),
        ('ATTEND_PARK_CT', 'i4'), ('SCORER_RECORD_ID', 'a10'),
        ('TRANSLATOR_RECORD_ID', 'a10'), ('INPUTTER_RECORD_ID', 'a10'),
        ('INPUT_RECORD_TS', 'a10'), ('EDIT_RECORD_TS', 'a10'),
        ('METHOD_RECORD_CD', 'i1'), ('PITCHES_RECORD_CD', 'i1'),
        ('TEMP_PARK_CT', 'i1'), ('WIND_DIRECTION_PARK_CD', 'i1'),
        ('WIND_SPEED_PARK_CT', 'i1'), ('FIELD_PARK_CD', 'i1'),
        ('PRECIP_PARK_CD', 'i1'), ('SKY_PARK_CD', 'i1'),
        ('MINUTES_GAME_CT', 'i2'), ('INN_CT', 'i1'),
        ('AWAY_SCORE_CT', 'i1'), ('HOME_SCORE_CT', 'i1'),
        ('AWAY_HITS_CT', 'i1'), ('HOME_HITS_CT', 'i1'),
        ('AWAY_ERR_CT', 'i1'), ('HOME_ERR_CT', 'i1'),
        ('AWAY_LOB_CT', 'i1'), ('HOME_LOB_CT', 'i1'),
        ('WIN_PIT_ID', 'a8'), ('LOSE_PIT_ID', 'a8'),
        ('SAVE_PIT_ID', 'a8'), ('GWRBI_BAT_ID', 'a8'),
        ('AWAY_LINEUP1_BAT_ID', 'a8'), ('AWAY_LINEUP1_FLD_CD', 'i1'),
        ('AWAY_LINEUP2_BAT_ID', 'a8'), ('AWAY_LINEUP2_FLD_CD', 'i1'),
        ('AWAY_LINEUP3_BAT_ID', 'a8'), ('AWAY_LINEUP3_FLD_CD', 'i1'),
        ('AWAY_LINEUP4_BAT_ID', 'a8'), ('AWAY_LINEUP4_FLD_CD', 'i1'),
        ('AWAY_LINEUP5_BAT_ID', 'a8'), ('AWAY_LINEUP5_FLD_CD', 'i1'),
        ('AWAY_LINEUP6_BAT_ID', 'a8'), ('AWAY_LINEUP6_FLD_CD', 'i1'),
        ('AWAY_LINEUP7_BAT_ID', 'a8'), ('AWAY_LINEUP7_FLD_CD', 'i1'),
        ('AWAY_LINEUP8_BAT_ID', 'a8'), ('AWAY_LINEUP8_FLD_CD', 'i1'),
        ('AWAY_LINEUP9_BAT_ID', 'a8'), ('AWAY_LINEUP9_FLD_CD', 'i1'),
        ('HOME_LINEUP1_BAT_ID', 'a8'), ('HOME_LINEUP1_FLD_CD', 'i1'),
        ('HOME_LINEUP2_BAT_ID', 'a8'), ('HOME_LINEUP2_FLD_CD', 'i1'),
        ('HOME_LINEUP3_BAT_ID', 'a8'), ('HOME_LINEUP3_FLD_CD', 'i1'),
        ('HOME_LINEUP4_BAT_ID', 'a8'), ('HOME_LINEUP4_FLD_CD', 'i1'),
        ('HOME_LINEUP5_BAT_ID', 'a8'), ('HOME_LINEUP5_FLD_CD', 'i1'),
        ('HOME_LINEUP6_BAT_ID', 'a8'), ('HOME_LINEUP6_FLD_CD', 'i1'),
        ('HOME_LINEUP7_BAT_ID', 'a8'), ('HOME_LINEUP7_FLD_CD', 'i1'),
        ('HOME_LINEUP8_BAT_ID', 'a8'), ('HOME_LINEUP8_FLD_CD', 'i1'),
        ('HOME_LINEUP9_BAT_ID', 'a8'), ('HOME_LINEUP9_FLD_CD', 'i1'),
        ('AWAY_FINISH_PIT_ID', 'a8'), ('HOME_FINISH_PIT_ID', 'a8'),
    ]
    return np.dtype(standard_headers)

def cwevent_dtype():
    # From cwevent 0.6.0:
    #   -f flist  give list of fields to output
    #               Default is 0-6,8-9,12-13,16-17,26-40,43-45,51,58-61
    standard_headers = [
        ('GAME_ID', 'a13'), ('AWAY_TEAM_ID', 'a3'), ('INN_CT', 'i1'),
        ('BAT_HOME_ID', 'i1'), ('OUTS_CT', 'i1'), ('BALLS_CT', 'i1'),
        ('STRIKES_CT', 'i1'), ('PITCH_SEQ_TX', 'a32'), ('AWAY_SCORE_CT', 'i1'),
        ('HOME_SCORE_CT', 'i1'), ('BAT_ID', 'a8'), ('BAT_HAND_CD', 'a1'),
        ('RESP_BAT_ID', 'a8'), ('RESP_BAT_HAND_CD', 'a1'),
        ('PIT_ID', 'a8'), ('PIT_HAND_CD', 'a1'),
        ('RESP_PIT_ID', 'a8'), ('RESP_PIT_HAND_CD', 'a1'),
        ('POS2_FLD_ID', 'a8'), ('POS3_FLD_ID', 'a8'), ('POS4_FLD_ID', 'a8'),
        ('POS5_FLD_ID', 'a8'), ('POS6_FLD_ID', 'a8'), ('POS7_FLD_ID', 'a8'),
        ('POS8_FLD_ID', 'a8'), ('POS9_FLD_ID', 'a8'),
        ('BASE1_RUN_ID', 'a8'), ('BASE2_RUN_ID', 'a8'), ('BASE3_RUN_ID', 'a8'),
        ('EVENT_TX', 'a8'), ('LEADOFF_FL', 'a1'), ('PH_FL', 'a1'),
        ('BAT_FLD_CD', 'i1'), ('BAT_LINEUP_ID', 'i1'), ('EVENT_CD', 'i1'),
        ('BAT_EVENT_FL', 'a1'), ('AB_FL', 'a1'), ('H_FL', 'i1'),
        ('SH_FL', 'a1'), ('SF_FL', 'a1'), ('EVENT_OUTS_CT', 'i1'),
        ('DP_FL', 'a1'), ('TP_FL', 'a1'), ('RBI_CT', 'i1'), ('WP_FL', 'a1'),
        ('PB_FL', 'a1'), ('FLD_CD', 'i1'), ('BATTEDBALL_CD', 'a8'),
        ('BUNT_FL', 'a1'), ('FOUL_FL', 'a1'), ('BATTEDBALL_LOC_TX', 'a8'),
        ('ERR_CT', 'i1'), ('ERR1_FLD_CD', 'a8'), ('ERR1_CD', 'a1'),
        ('ERR2_FLD_CD', 'a8'), ('ERR2_CD', 'a1'), ('ERR3_FLD_CD', 'a8'),
        ('ERR3_CD', 'a1'), ('BAT_DEST_ID', 'i1'), ('RUN1_DEST_ID', 'i1'),
        ('RUN2_DEST_ID', 'i1'), ('RUN3_DEST_ID', 'i1'), ('BAT_PLAY_TX', 'a16'),
        ('RUN1_PLAY_TX', 'a16'), ('RUN2_PLAY_TX', 'a16'),
        ('RUN3_PLAY_TX', 'a16'),
        ('RUN1_SB_FL', 'a1'), ('RUN2_SB_FL', 'a1'), ('RUN3_SB_FL', 'a1'),
        ('RUN1_CS_FL', 'a1'), ('RUN2_CS_FL', 'a1'), ('RUN3_CS_FL', 'a1'),
        ('RUN1_PK_FL', 'a1'), ('RUN2_PK_FL', 'a1'), ('RUN3_PK_FL', 'a1'),
        ('RUN1_RESP_PIT_ID', 'a8'), ('RUN2_RESP_PIT_ID', 'a8'),
        ('RUN3_RESP_PIT_ID', 'a8'), ('GAME_NEW_FL', 'a1'),
        ('GAME_END_FL', 'a1'), ('PR_RUN1_FL', 'a1'), ('PR_RUN2_FL', 'a1'),
        ('PR_RUN3_FL', 'a1'), ('REMOVED_FOR_PR_RUN1_ID', 'a8'),
        ('REMOVED_FOR_PR_RUN2_ID', 'a8'), ('REMOVED_FOR_PR_RUN3_ID', 'a8'),
        ('REMOVED_FOR_PH_BAT_ID', 'a8'), ('REMOVED_FOR_PH_BAT_FLD_CD', 'a8'),
        ('PO1_FLD_CD', 'a8'), ('PO2_FLD_CD', 'a8'),
        ('PO3_FLD_CD', 'a8'), ('ASS1_FLD_CD', 'a8'), ('ASS2_FLD_CD', 'a8'),
        ('ASS3_FLD_CD', 'a8'), ('ASS4_FLD_CD', 'a8'), ('ASS5_FLD_CD', 'a8'),
        ('EVENT_ID', 'i1'),
    ]

    # Extended headers need to be parsed by looking at the column header.
    extended_headers = [
        ('HOME_TEAM_ID', 'a3'), ('BAT_TEAM_ID', 'a3'), ('FLD_TEAM_ID', 'a3'),
        ('BAT_LAST_ID', 'a8'), ('INN_NEW_FL', 'a1'), ('INN_END_FL', 'a1'),
        ('START_BAT_SCORE_CT', 'i4'), ('START_FLD_SCORE_CT', 'i4'),
        ('INN_RUNS_CT', 'i4'), ('GAME_PA_CT', 'i4'), ('INN_PA_CT', 'i4'),
        ('PA_NEW_FL', 'a1'), ('PA_TRUNC_FL', 'a1'), ('START_BASES_CD', 'a8'),
        ('END_BASES_CD', 'a8'), ('BAT_START_FL', 'a1'),
        ('RESP_BAT_START_FL', 'a1'), ('BAT_ON_DECK_ID', 'a8'),
        ('BAT_IN_HOLD_ID', 'a8'), ('PIT_START_FL', 'a1'),
        ('RESP_PIT_START_FL', 'a1'), ('RUN1_FLD_CD', 'i4'),
        ('RUN1_LINEUP_CD', 'i4'), ('RUN1_ORIGIN_EVENT_ID', 'a8'),
        ('RUN2_FLD_CD', 'i4'), ('RUN2_LINEUP_CD', 'i4'),
        ('RUN2_ORIGIN_EVENT_ID', 'a8'), ('RUN3_FLD_CD', 'i4'),
        ('RUN3_LINEUP_CD', 'i4'), ('RUN3_ORIGIN_EVENT_ID', 'a8'),
        ('RUN1_RESP_CAT_ID', 'a8'), ('RUN2_RESP_CAT_ID', 'a8'),
        ('RUN3_RESP_CAT_ID', 'a8'), ('PA_BALL_CT', 'i4'),
        ('PA_CALLED_BALL_CT', 'i4'), ('PA_INTENT_BALL_CT', 'i4'),
        ('PA_PITCHOUT_BALL_CT', 'i4'), ('PA_HITBATTER_BALL_CT', 'i4'),
        ('PA_OTHER_BALL_CT', 'i4'), ('PA_STRIKE_CT', 'i4'),
        ('PA_CALLED_STRIKE_CT', 'i4'), ('PA_SWINGMISS_STRIKE_CT', 'i4'),
        ('PA_FOUL_STRIKE_CT', 'i4'), ('PA_INPLAY_STRIKE_CT', 'i4'),
        ('PA_OTHER_STRIKE_CT', 'i4'), ('EVENT_RUNS_CT', 'i4'),
        ('FLD_ID', 'a8'), ('BASE2_FORCE_FL', 'a1'), ('BASE3_FORCE_FL', 'a1'),
        ('BASE4_FORCE_FL', 'a1'), ('BAT_SAFE_ERR_FL', 'a1'),
        ('BAT_FATE_ID', 'a8'), ('RUN1_FATE_ID', 'a8'), ('RUN2_FATE_ID', 'a8'),
        ('RUN3_FATE_ID', 'a8'), ('FATE_RUNS_CT', 'i4'), ('ASS6_FLD_CD', 'a8'),
        ('ASS7_FLD_CD', 'a8'), ('ASS8_FLD_CD', 'a8'), ('ASS9_FLD_CD', 'a8'),
        ('ASS10_FLD_CD', 'a8'), ('UNKNOWN_OUT_EXC_FL', 'a1'),
        ('UNCERTAIN_PLAY_EXC_FL', 'a1'),
    ]
    return np.dtype(standard_headers)
