import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle

team_df = pd.read_csv('static/fbs_teams_2004_2023.csv')
team_ids = team_df['team_id'].values
distance_dict = {}

### ALL
df_transformed = pd.read_csv('static/transformed_team_stats_2004_2023.csv',
                             index_col='team_id')
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
distance_dict['Combined'] = max_distance
print('All:', max_distance)

### Offense
df_transformed = pd.read_csv('static/transformed_offense_team_stats_2004_2023.csv',
                             index_col='team_id')
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
distance_dict['Offense'] = max_distance
print('Offense:', max_distance)

### Defense
df_transformed = pd.read_csv('static/transformed_defense_team_stats_2004_2023.csv',
                             index_col='team_id')
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
distance_dict['Defense'] = max_distance
print('Defense:', max_distance)

with open('static/max_distance.pkl', 'wb') as f:
    pickle.dump(distance_dict, f)

