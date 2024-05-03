"""
This module finds the maximum distance between two points in each PCA-
transformed dataset. These max distances are stored and used to calculate
Statistical Similarity Scores (see the README).

Author: Steve Bischoff
"""
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle

# Globals
FIRST_YEAR = 2014
LAST_YEAR = 2023

def get_max_distance(df_transformed, team_ids):
    """
    This function gets the max distance in df_transformed between two teams in
    team_ids. It uses the sklearn NearestNeighbors class to calculate distances.
    Args:
        df_transformed: PCA-transformed dataframe
        team_ids: iterable, members in the df_transformed index
    """
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
    return max_distance

def main():

    team_df = pd.read_csv('static/fbs_teams_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    team_ids = team_df['team_id'].values
    distance_dict = {}

    ### ALL
    ## Adv
    df_transformed = pd.read_csv('static/transformed_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    max_distance = get_max_distance(df_transformed, team_ids)
    distance_dict['Combined'] = max_distance
    print('Combined:', max_distance)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    distance_dict['Combined No Adv'] = get_max_distance(df_transformed, team_ids)
    print('Combined No Adv:', max_distance)

    ### Offense
    ## Adv
    df_transformed = pd.read_csv('static/transformed_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    max_distance = get_max_distance(df_transformed, team_ids)
    distance_dict['Offense'] = max_distance
    print('Offense:', max_distance)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    max_distance = get_max_distance(df_transformed, team_ids)
    distance_dict['Offense No Adv'] = max_distance
    print('Offense No Adv:', max_distance)

    ### Defense
    ## Adv
    df_transformed = pd.read_csv('static/transformed_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    max_distance = get_max_distance(df_transformed, team_ids)
    distance_dict['Defense'] = max_distance
    print('Defense:', max_distance)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    max_distance = get_max_distance(df_transformed, team_ids)
    distance_dict['Defense No Adv'] = max_distance
    print('Defense No Adv:', max_distance)

    with open('static/max_distance.pkl', 'wb') as f:
        pickle.dump(distance_dict, f)

if __name__ == '__main__':
    main()
