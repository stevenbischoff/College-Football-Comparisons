import pandas as pd
from sklearn.neighbors import NearestNeighbors

team_df = pd.read_csv('data/fbs_teams_2004_2023.csv')
df_transformed = pd.read_csv('data/transformed_team_stats_2004_2023.csv',
                             index_col='team_id')

team_ids = team_df['team_id'].values

n_comps = len(df_transformed)
nn = NearestNeighbors(n_neighbors=n_comps).fit(df_transformed.values)

max_distance = 0
for team_id in team_ids:
    try:
        indices = nn.kneighbors(df_transformed.loc[team_id].values.reshape(1,-1),
                                n_comps, return_distance=True)
    except:
        continue
    max_team_distance = indices[0][0].max()
    max_distance = max(max_distance, max_team_distance)

with open('data/max_distance.txt', 'w') as f:
    f.write(str(max_distance))
