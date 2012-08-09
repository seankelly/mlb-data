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

