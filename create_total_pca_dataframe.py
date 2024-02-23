"""
This module loads each dataset created by create_standardized_dataframe.py,
transforms the features using PCA, selects just enough features to explain
90% of the variance, and saves the results.

Author: Steve Bischoff
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import pickle

from load_columns import *

def get_n_components(pca, threshold=0.9):
    """
    Gets the number of components that explains an input ratio of total variance in the data
    Args:
        pca: A trained sklearn PCA object
        threshold: float in [0,1], the ratio of total variance the n_components should explain
    Returns:
        n_components: int
    """
    ev = pca.explained_variance_ratio_
    cum_ev = np.cumsum(ev)
    n_components = len(cum_ev) - len(cum_ev[cum_ev >= threshold]) + 1
    return n_components

def get_transformed_df(df, n_components):
    """
    Fits an sklearn PCA object to a dataframe and returns the first n principal components
    Args:
        df: input dataset compatible with sklearn.PCA
        n_components: int, the number of principal components to keep
    Returns:
        df_transformed: DataFrame, first n components of the transformed data
    """
    pcamax = PCA(n_components=df.shape[1])
    X_n_components = pcamax.fit_transform(df)[:,:n_components]
    df_transformed = pd.DataFrame(X_n_components, index=df.index)
    return df_transformed

def main():
    first_year = 2014 # 2014 is first year advanced stats are good. 2004 otherwise (except ToP)
    last_year = 2023

    ### All
    ## Adv
    df_standardized = pd.read_csv('static/standardized_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list(X_columns.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('All Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_team_stats_{}_{}.csv'.format(first_year, last_year))

    ## No Adv
    df_standardized = pd.read_csv('static/standardized_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list({**o_normal_columns, **d_normal_columns, **other_columns}.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('No Adv. Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

    ### Offense
    ## Adv
    df_standardized = pd.read_csv('static/standardized_offense_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list({**o_normal_columns, **o_advanced_columns}.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('Offense Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_offense_team_stats_{}_{}.csv'.format(first_year, last_year))

    ## No Adv
    df_standardized = pd.read_csv('static/standardized_offense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list(o_normal_columns.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('Offense No Adv. Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_offense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

    ### Defense
    ## Adv
    df_standardized = pd.read_csv('static/standardized_defense_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list({**d_normal_columns, **d_advanced_columns}.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('Defense Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_defense_team_stats_{}_{}.csv'.format(first_year, last_year))

    ## No Adv
    df_standardized = pd.read_csv('static/standardized_defense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year),
                                  index_col='team_id')
    df = df_standardized[list(d_normal_columns.keys())]
    # Fit PCA
    pca = PCA().fit(df)
    # Select number of components (90% explained variance)
    n_components = get_n_components(pca)
    print('Defense No Adv. Components:', n_components)
    # Apply transformation and selection first n components
    df_transformed = get_transformed_df(df, n_components)
    # Store transformed data
    df_transformed.to_csv('static/transformed_defense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

if __name__ == '__main__':
    main()    
