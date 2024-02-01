import pandas as pd
from sklearn.preprocessing import StandardScaler
from load_columns import *

def main():
    first_year = 2014
    last_year = 2023

    df_raw = pd.read_csv('static/raw_team_stats_{}_{}.csv'.format(first_year, last_year),
                         index_col='team_id')

    ss = StandardScaler()
    df_standardized = pd.DataFrame(ss.fit_transform(df_raw),
                                   index=df_raw.index, columns=df_raw.columns)

    # All
    df_standardized[df_standardized.index.str[-4:].astype(int) >= 2014 # !!! With bad advanced data < 2014
                    ].to_csv('static/standardized_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_standardized[list({**o_normal_columns, **d_normal_columns, **other_columns}.keys())
                ].to_csv('static/standardized_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

    # Offense
    df_standardized[df_standardized.index.str[-4:].astype(int) >= 2014 # !!! With bad advanced data < 2014
                    ][list({**o_normal_columns, **o_advanced_columns}.keys())
                ].to_csv('static/standardized_offense_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_standardized[list(o_normal_columns.keys())
                ].to_csv('static/standardized_offense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))
    # Defense
    df_standardized[df_standardized.index.str[-4:].astype(int) >= 2014 # !!! With bad advanced data < 2014
                    ][list({**d_normal_columns, **d_advanced_columns}.keys())
                ].to_csv('static/standardized_defense_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_standardized[list(d_normal_columns.keys())
                ].to_csv('static/standardized_defense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

if __name__ == '__main__':
    main()
