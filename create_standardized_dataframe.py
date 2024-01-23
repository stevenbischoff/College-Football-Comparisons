import pandas as pd
from sklearn.preprocessing import StandardScaler
from load_columns import *

first_year = 2004
last_year = 2023

df_raw = pd.read_csv('static/raw_team_stats_{}_{}.csv'.format(first_year, last_year),
                     index_col='team_id')

ss = StandardScaler()
df_standardized = pd.DataFrame(ss.fit_transform(df_raw),
                               index=df_raw.index, columns=df_raw.columns)

# All
df_standardized.to_csv('static/standardized_team_stats_{}_{}.csv'.format(first_year, last_year))
# Offense
df_standardized[list(o_normal_columns.keys())+list(o_advanced_columns.keys())
            ].to_csv('static/standardized_offense_team_stats_{}_{}.csv'.format(first_year, last_year))
# Defense
df_standardized[list(d_normal_columns.keys())+list(d_advanced_columns.keys())
            ].to_csv('static/standardized_defense_team_stats_{}_{}.csv'.format(first_year, last_year))
