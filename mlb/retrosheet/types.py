"""
Module to define numpy dtypes for Chadwick's output from parsing
Retrosheet data.
"""

import numpy as np

def cwgame_game_dtype():
    standard_headers = [
        ('GAME_ID', 'a13'), ('GAME_DT', 'a6'), ('GAME_CT', 'i4'),
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
        ('METHOD_RECORD_CD', 'i4'), ('PITCHES_RECORD_CD', 'i4'),
        ('TEMP_PARK_CT', 'i4'), ('WIND_DIRECTION_PARK_CD', 'i4'),
        ('WIND_SPEED_PARK_CT', 'i4'), ('FIELD_PARK_CD', 'i4'),
        ('PRECIP_PARK_CD', 'i4'), ('SKY_PARK_CD', 'i4'),
        ('MINUTES_GAME_CT', 'i4'), ('INN_CT', 'i4'),
        ('AWAY_SCORE_CT', 'i4'), ('HOME_SCORE_CT', 'i4'),
        ('AWAY_HITS_CT', 'i4'), ('HOME_HITS_CT', 'i4'),
        ('AWAY_ERR_CT', 'i4'), ('HOME_ERR_CT', 'i4'),
        ('AWAY_LOB_CT', 'i4'), ('HOME_LOB_CT', 'i4'),
        ('WIN_PIT_ID', 'a8'), ('LOSE_PIT_ID', 'a8'),
        ('SAVE_PIT_ID', 'a8'), ('GWRBI_BAT_ID', 'a8'),
        ('AWAY_LINEUP1_BAT_ID', 'a8'), ('AWAY_LINEUP1_FLD_CD', 'i4'),
        ('AWAY_LINEUP2_BAT_ID', 'a8'), ('AWAY_LINEUP2_FLD_CD', 'i4'),
        ('AWAY_LINEUP3_BAT_ID', 'a8'), ('AWAY_LINEUP3_FLD_CD', 'i4'),
        ('AWAY_LINEUP4_BAT_ID', 'a8'), ('AWAY_LINEUP4_FLD_CD', 'i4'),
        ('AWAY_LINEUP5_BAT_ID', 'a8'), ('AWAY_LINEUP5_FLD_CD', 'i4'),
        ('AWAY_LINEUP6_BAT_ID', 'a8'), ('AWAY_LINEUP6_FLD_CD', 'i4'),
        ('AWAY_LINEUP7_BAT_ID', 'a8'), ('AWAY_LINEUP7_FLD_CD', 'i4'),
        ('AWAY_LINEUP8_BAT_ID', 'a8'), ('AWAY_LINEUP8_FLD_CD', 'i4'),
        ('AWAY_LINEUP9_BAT_ID', 'a8'), ('AWAY_LINEUP9_FLD_CD', 'i4'),
        ('HOME_LINEUP1_BAT_ID', 'a8'), ('HOME_LINEUP1_FLD_CD', 'i4'),
        ('HOME_LINEUP2_BAT_ID', 'a8'), ('HOME_LINEUP2_FLD_CD', 'i4'),
        ('HOME_LINEUP3_BAT_ID', 'a8'), ('HOME_LINEUP3_FLD_CD', 'i4'),
        ('HOME_LINEUP4_BAT_ID', 'a8'), ('HOME_LINEUP4_FLD_CD', 'i4'),
        ('HOME_LINEUP5_BAT_ID', 'a8'), ('HOME_LINEUP5_FLD_CD', 'i4'),
        ('HOME_LINEUP6_BAT_ID', 'a8'), ('HOME_LINEUP6_FLD_CD', 'i4'),
        ('HOME_LINEUP7_BAT_ID', 'a8'), ('HOME_LINEUP7_FLD_CD', 'i4'),
        ('HOME_LINEUP8_BAT_ID', 'a8'), ('HOME_LINEUP8_FLD_CD', 'i4'),
        ('HOME_LINEUP9_BAT_ID', 'a8'), ('HOME_LINEUP9_FLD_CD', 'i4'),
        ('AWAY_FINISH_PIT_ID', 'a8'), ('HOME_FINISH_PIT_ID', 'a8'),
    ]
    return np.dtype(standard_headers)

def cwevent_event_dtype():
    # From cwevent 0.6.0:
    #   -f flist  give list of fields to output
    #               Default is 0-6,8-9,12-13,16-17,26-40,43-45,51,58-61
    standard_headers = [
        ('GAME_ID', 'a8'), ('AWAY_TEAM_ID', 'a3'), ('INN_CT', 'i4'),
        ('BAT_HOME_ID', 'a8'), ('OUTS_CT', 'i4'), ('BALLS_CT', 'i4'),
        ('STRIKES_CT', 'i4'), ('PITCH_SEQ_TX', 'a32'), ('AWAY_SCORE_CT', 'i4'),
        ('HOME_SCORE_CT', 'i4'), ('BAT_ID', 'a8'), ('BAT_HAND_CD', 'a1'),
        ('RESP_BAT_ID', 'a8'), ('RESP_BAT_HAND_CD', 'a1'),
        ('PIT_ID', 'a8'), ('PIT_HAND_CD', 'a1'),
        ('RESP_PIT_ID', 'a8'), ('RESP_PIT_HAND_CD', 'a1'),
        ('POS2_FLD_ID', 'a8'), ('POS3_FLD_ID', 'a8'), ('POS4_FLD_ID', 'a8'),
        ('POS5_FLD_ID', 'a8'), ('POS6_FLD_ID', 'a8'), ('POS7_FLD_ID', 'a8'),
        ('POS8_FLD_ID', 'a8'), ('POS9_FLD_ID', 'a8'),
        ('BASE1_RUN_ID', 'a8'), ('BASE2_RUN_ID', 'a8'), ('BASE3_RUN_ID', 'a8'),
        ('EVENT_TX', 'a8'), ('LEADOFF_FL', 'a1'), ('PH_FL', 'a1'),
        ('BAT_FLD_CD', 'i4'), ('BAT_LINEUP_ID', 'i4'), ('EVENT_CD', 'i4'),
        ('BAT_EVENT_FL', 'a1'), ('AB_FL', 'a1'), ('H_FL', 'a1'),
        ('SH_FL', 'a1'), ('SF_FL', 'a1'), ('EVENT_OUTS_CT', 'i4'),
        ('DP_FL', 'a1'), ('TP_FL', 'a1'), ('RBI_CT', 'i4'), ('WP_FL', 'a1'),
        ('PB_FL', 'a1'), ('FLD_CD', 'i4'), ('BATTEDBALL_CD', 'a8'),
        ('BUNT_FL', 'a1'), ('FOUL_FL', 'a1'), ('BATTEDBALL_LOC_TX', 'a8'),
        ('ERR_CT', 'i4'), ('ERR1_FLD_CD', 'a8'), ('ERR1_CD', 'a1'),
        ('ERR2_FLD_CD', 'a8'), ('ERR2_CD', 'a1'), ('ERR3_FLD_CD', 'a8'),
        ('ERR3_CD', 'a1'), ('BAT_DEST_ID', 'i4'), ('RUN1_DEST_ID', 'i4'),
        ('RUN2_DEST_ID', 'i4'), ('RUN3_DEST_ID', 'i4'), ('BAT_PLAY_TX', 'a16'),
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
        ('EVENT_ID', 'i4'),
    ]
    return np.dtype(standard_headers)
