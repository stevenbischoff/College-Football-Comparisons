import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import pickle

from load_columns import *

def get_n_components(pca):
    ev = pca.explained_variance_ratio_
    cum_ev = np.cumsum(ev)
    n_components = len(cum_ev) - len(cum_ev[cum_ev >= 0.9]) + 1
    return n_components

def get_transformed_df(n_components, df):
    pcamax = PCA(n_components=df.shape[1])
    X_n_components = pcamax.fit_transform(df)[:,:n_components]
    df_transformed = pd.DataFrame(X_n_components, index=df.index)
    return df_transformed

first_year = 2004
last_year = 2023

df_standardized = pd.read_csv('static/standardized_team_stats_{}_{}.csv'.format(first_year, last_year),
                              index_col='team_id')

### All
df = df_standardized[list(X_columns.keys())]
# Fit PCA
pca = PCA().fit(df)
# Select number of components (90% explained variance)
n_components = get_n_components(pca)
print('All Components:', n_components)
# Apply transformation and selection first n components
df_transformed = get_transformed_df(n_components, df)
print(df_transformed.loc['Notre Dame 2012'])
# Store transformed data
df_transformed.to_csv('static/transformed_team_stats_{}_{}.csv'.format(first_year, last_year))

### Offense
df = df_standardized[list(o_normal_columns.keys())+list(o_advanced_columns.keys())]
# Fit PCA
pca = PCA().fit(df)
# Select number of components (90% explained variance)
n_components = get_n_components(pca)
print('Offense Components:', n_components)
# Apply transformation and selection first n components
df_transformed = get_transformed_df(n_components, df)
print(df_transformed.loc['Notre Dame 2012'])
# Store transformed data
df_transformed.to_csv('static/transformed_offense_team_stats_{}_{}.csv'.format(first_year, last_year))

### Defense
df = df_standardized[list(d_normal_columns.keys())+list(d_advanced_columns.keys())]
# Fit PCA
pca = PCA().fit(df)
# Select number of components (90% explained variance)
n_components = get_n_components(pca)
print('Defense Components:', n_components)
# Apply transformation and selection first n components
df_transformed = get_transformed_df(n_components, df)
print(df_transformed.loc['Notre Dame 2012'])
# Store transformed data
df_transformed.to_csv('static/transformed_defense_team_stats_{}_{}.csv'.format(first_year, last_year))
