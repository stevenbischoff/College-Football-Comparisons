import pandas as pd
from sklearn.preprocessing import StandardScaler

first_year = 2004
last_year = 2023

df_raw = pd.read_csv('data/raw_team_stats_{}_{}.csv'.format(first_year, last_year),
                     index_col='team_id')

ss = StandardScaler()
df_standardized = pd.DataFrame(ss.fit_transform(df_raw),
                               index=df_raw.index, columns=df_raw.columns)

df_standardized.to_csv('data/standardized_team_stats_{}_{}.csv'.format(first_year, last_year))
