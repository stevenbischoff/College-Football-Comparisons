import streamlit as st
#from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
#from st_aggrid.shared import GridUpdateMode
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors
import scipy.stats as stats

from load_columns import *

def get_comp_results(team_id, n_comps=10):
    results = nn.kneighbors(df_transformed.loc[team_id].values.reshape(1,-1), n_comps+1, return_distance=True)
    indices = results[1][0][1:]
    distances = results[0][0][1:]
    return df_transformed.index[indices], distances


def comps_to_display_df(comps, distances, n_comps=10):
    schools = comps.str[:-5]
    seasons = comps.str[-4:]
    sss = 1 - distances/max_distance # Statistical Similarity Score
    return pd.DataFrame({'Rank': range(1, n_comps+1), 'School': schools,
                         'Season': seasons, 'SSS*': sss.round(4)}, index=range(1, n_comps+1))


def get_similar_stats(team_id1, team_id2, n_stats=10, pctl_threshold=15):
    stat_diffs = (df_standardized.loc[team_id1, list(X_columns.keys())
        ] - df_standardized.loc[team_id2, list(X_columns.keys())]).abs().sort_values()
    return_df = pd.DataFrame(columns=['Statistic', team_id1, 'pctl1',
                                      team_id2, 'pctl2'])
    
    for stat in stat_diffs.index[:n_stats]:
        pctl1 = stats.percentileofscore(df_raw[stat], df_raw.loc[team_id1, stat])
        #if pctl1 < pctl_threshold or pctl1 > 100 - pctl_threshold:
        pctl2 = stats.percentileofscore(df_raw[stat], df_raw.loc[team_id2, stat])
        return_df.loc[len(return_df)] = [X_columns[stat],
                                               '%s' % float('%.4g' % round(df_raw.loc[team_id1, stat],3)),
                                               round(pctl1, 2),
                                               '%s' % float('%.4g' % round(df_raw.loc[team_id2, stat],3)),
                                               round(pctl2, 2)]
    return return_df

def get_different_stats(team_id1, team_id2, n_stats=5):
    stat_diffs = (df_standardized.loc[team_id1, list(X_columns.keys())
        ] - df_standardized.loc[team_id2, list(X_columns.keys())]).abs().sort_values()
    return_df = pd.DataFrame(columns=['Statistic', team_id1, 'pctl1',
                                      team_id2, 'pctl2'])
    for stat in stat_diffs.index[-n_stats:]:
        pctl1 = stats.percentileofscore(df_raw[stat], df_raw.loc[team_id1, stat])
        #if pctl1 < pctl_threshold or pctl1 > 100 - pctl_threshold:
        pctl2 = stats.percentileofscore(df_raw[stat], df_raw.loc[team_id2, stat])
        return_df.loc[len(return_df)] = [X_columns[stat],
                                               '%s' % float('%.4g' % round(df_raw.loc[team_id1, stat],3)),
                                               round(pctl1, 2),
                                               '%s' % float('%.4g' % round(df_raw.loc[team_id2, stat],3)),
                                               round(pctl2, 2)]
    return return_df.iloc[::-1]


# settings
n_comps = 10

# load data
with open('data/max_distance.txt', 'r') as f:
    max_distance = float(f.read())

team_df = pd.read_csv('data/fbs_teams_2004_2023.csv')
df_raw = pd.read_csv('data/raw_team_stats_2004_2023.csv',
                     index_col='team_id')
df_standardized = pd.read_csv('data/standardized_team_stats_2004_2023.csv',
                             index_col='team_id')
df_transformed = pd.read_csv('data/transformed_team_stats_2004_2023.csv',
                             index_col='team_id')

# Preparation
team_ids = df_transformed.index.values
schools = sorted(team_df['school'].unique())

nn = NearestNeighbors(n_neighbors=n_comps+1).fit(df_transformed)

### APP ###
st.set_page_config(layout='wide')

st.header('College Football: Most Statistically Similar FBS Teams 2004-2023')
