"""
This module loads each dataset created by create_raw_dataframe.py, standardizes each column,
and saves the results.

Author: Steve Bischoff
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from load_columns import *

# Globals
FIRST_YEAR = 2014
LAST_YEAR = 2023

def main():
    
    df_raw = pd.read_csv('static/raw_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                         index_col='team_id')

    ss = StandardScaler()
    df_standardized = pd.DataFrame(ss.fit_transform(df_raw),
                                   index=df_raw.index, columns=df_raw.columns)

    # All
    df_standardized.to_csv('static/standardized_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_standardized[list({**o_normal_columns, **d_normal_columns, **other_columns}.keys())].to_csv(
        'static/standardized_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))

    # Offense
    df_standardized[
        list({**o_normal_columns, **o_advanced_columns}.keys())].to_csv(
        'static/standardized_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_standardized[list(o_normal_columns.keys())].to_csv(
        'static/standardized_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    # Defense
    df_standardized[list({**d_normal_columns, **d_advanced_columns}.keys())].to_csv(
        'static/standardized_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_standardized[list(d_normal_columns.keys())].to_csv(
        'static/standardized_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))

if __name__ == '__main__':
    main()
