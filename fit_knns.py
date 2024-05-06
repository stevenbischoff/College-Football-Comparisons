"""
This module ...

Author: Steve Bischoff
"""
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors

from load_columns import *

# Globals
FIRST_YEAR = 2014 # 2014 is first year advanced stats are good. 2004 otherwise (except ToP)
LAST_YEAR = 2023

def main():
    ### All
    ## Adv
    df_transformed = pd.read_csv('static/transformed_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values) # 21 for max # of teams to display (20) + 1
    # Save
    with open('static/models/knn.pkl', 'wb') as f:
        pickle.dump(nn, f)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values)
    # Save
    with open('static/models/knn_no_adv.pkl', 'wb') as f:
        pickle.dump(nn, f)

    ### Offense
    ## Adv
    df_transformed = pd.read_csv('static/transformed_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values)
    # Save
    with open('static/models/knn_offense.pkl', 'wb') as f:
        pickle.dump(nn, f)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values)
    # Save
    with open('static/models/knn_offense_no_adv.pkl', 'wb') as f:
        pickle.dump(nn, f)

    ### Defense
    ## Adv
    df_transformed = pd.read_csv('static/transformed_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values)
    # Save
    with open('static/models/knn_defense.pkl', 'wb') as f:
        pickle.dump(nn, f)

    ## No Adv
    df_transformed = pd.read_csv('static/transformed_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                                 index_col='team_id')
    # Fit KNN
    nn = NearestNeighbors(n_neighbors=21).fit(df_transformed.values)
    # Save
    with open('static/models/knn_defense_no_adv.pkl', 'wb') as f:
        pickle.dump(nn, f)

if __name__ == '__main__':
    main()
