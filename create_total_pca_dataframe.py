import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import pickle

from load_columns import *

first_year = 2004
last_year = 2023

df_standardized = pd.read_csv('data/standardized_team_stats_{}_{}.csv'.format(first_year, last_year),
                              index_col='team_id')

df = df_standardized[list(X_columns.keys())]

print(df.loc['Notre Dame 2012', ['points/game', 'points_opp/game']])
# Fit PCA
pca = PCA().fit(df)

# Select number of components (90% explained variance)
ev = pca.explained_variance_ratio_
cum_ev = np.cumsum(ev)
n_components = len(cum_ev) - len(cum_ev[cum_ev >= 0.9]) + 1
print('Components:', n_components)

# Apply transformation and selection first n components
pcamax = PCA(n_components=len(list(X_columns.keys())))
X_n_components = pcamax.fit_transform(df)[:,:n_components]
df_transformed = pd.DataFrame(X_n_components, index=df.index)
print(df_transformed.loc['Notre Dame 2012'])

# Store transformed data
df_transformed.to_csv('data/transformed_team_stats_{}_{}.csv'.format(first_year, last_year))
