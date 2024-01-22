import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors
import scipy.stats as stats

from load_columns import *

@st.cache_data
def load_max_distance():
    with open('static/max_distance.txt', 'r') as f:
        return float(f.read())
        
@st.cache_data
def load_team_df():
    return pd.read_csv('static/fbs_teams_2004_2023.csv')

@st.cache_data
def load_raw_data():
    return pd.read_csv('static/raw_team_stats_2004_2023.csv',
                       index_col='team_id')
@st.cache_data
def load_standardized_data():
    return pd.read_csv('static/standardized_team_stats_2004_2023.csv',
                       index_col='team_id')

@st.cache_data
def load_transformed_data():
    return pd.read_csv('static/transformed_team_stats_2004_2023.csv',
                       index_col='team_id')

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
max_distance = load_max_distance()
team_df = load_team_data()
df_raw = load_raw_data()
df_standardized = load_standardized_data()
df_transformed = load_transformed_data()

# Preparation
team_ids = df_transformed.index.values
schools = sorted(team_df['school'].unique())

nn = NearestNeighbors(n_neighbors=n_comps+1).fit(df_transformed)

### APP ###
st.set_page_config(layout='wide')

st.header('College Football: Most Statistically Similar FBS Teams 2004-2023')
st.write("Select a school and a year to view the team's closest statistical comparisons")
left_column, mid_column, right_column = st.columns([0.4,0.4,0.2])
with left_column:
    school = st.selectbox(label='School', options=schools, index=None)
with mid_column:
    year = st.selectbox(label='Year', options=range(2004, 2024), index=None)

left_column, right_column = st.columns([0.4,0.6])

if (school != None) & (year != None):
    team_id = school + ' ' + str(year)
    if team_id in team_ids:
        comps, distances = get_comp_results(team_id, n_comps)
        display_df = comps_to_display_df(comps, distances, n_comps)
        with left_column:
            st.subheader(team_id)
            st.write('Select a row for a detailed comparison!')
            
            builder = GridOptionsBuilder.from_dataframe(
                display_df, enableRowGroup=True, enableValue=True
                )
            builder.configure_selection('single')
            builder.configure_default_column(resizable=False)
            builder.configure_column('Rank', width=50)
            builder.configure_column('Season', width=130)
            builder.configure_column('SSS*', width=130)
            go = builder.build()
            

            selection = AgGrid(display_df, fit_columns_on_grid_load=True,
                   enable_enterprise_modules=True, gridOptions=go, update_mode=GridUpdateMode.MODEL_CHANGED)

            st.caption('*SSS, or Statistical Similarity Score, is a measure from 0 to 1 of the statistical similarity between two teams.')

            if st.checkbox('Show advanced options'):
                st.write('PLACEHOLDER')
        with right_column:
            if len(selection.selected_rows) > 0:                
                selected_row = selection.selected_rows[0]
                team_id_comp = selected_row['School'] + ' ' + selected_row['Season']

                similar_stats_df = get_similar_stats(team_id, team_id_comp)
                different_stats_df = get_different_stats(team_id, team_id_comp)

                st.subheader('Comparison with {}'.format(team_id_comp))
                
                st.write('Similarities:*')

                builder1 = GridOptionsBuilder.from_dataframe(
                    similar_stats_df,
                    enableValue=True, enableRowGroup=True
                    )
                builder1.configure_selection('single')
                builder1.configure_grid_options(columnDefs=[
                        {'field': 'Statistic'},
                        {'headerName': team_id,
                         'children': [
                         {'field': team_id},
                         {'field': 'pctl1',
                          'width': 100,
                          'type': 'rightAligned'}
                         ]},
                        {'headerName': team_id_comp,
                         'children': [
                         {'field': team_id_comp},
                         {'field': 'pctl2'}
                         ]}])
                go1 = {'columnDefs': [
                        {'field': 'Statistic'},
                        {'headerName': team_id,
                         'children': [
                         {'headerName': 'Value',
                          'field': team_id,
                          'width': 100,
                          'type': 'rightAligned'},
                         {'headerName': 'Pctl.**',
                          'field': 'pctl1',
                          'width': 100,
                          'type': 'rightAligned'}
                         ],},
                        {'headerName': team_id_comp,
                         'children': [
                         {'headerName': 'Value',
                          'field': team_id_comp,
                          'width': 100,
                          'type': 'rightAligned'},
                         {'headerName': 'Pctl.',
                          'field': 'pctl2',
                          'width': 100,
                          'type': 'rightAligned'}
                         ]}]}
                #builder1.configure_default_column(resizable=False)
                #builder1.configure_columns([team_id, 'pctl1'], props={'headerName': team_id})
                #builder1.configure_columns([team_id_comp, 'pctl2'], props={'headerName': team_id_comp})
                #builder1.configure_column(team_id, headerName=team_id)
                #builder1.configure_column('pctl1', width=100, headerName=team_id)
                #builder1.configure_column('pctl2', width=100)
                #go1 = builder1.build()

                selection1 = AgGrid(similar_stats_df, fit_columns_on_grid_load=True, gridOptions=go1,
                                    enable_enterprise_modules=True, update_mode=GridUpdateMode.MODEL_CHANGED,
                                    rowSelection='single')
                
                st.caption('*Statistics are per-game unless otherwise specified.')
                st.caption('**The percentile of the statistic in the entire dataset')
                
                st.write('Dissimilarities:')
                
                AgGrid(different_stats_df, fit_columns_on_grid_load=True, gridOptions=go1)
                if len(selection1.selected_rows) > 0:
                    #st.write(selection1.column_state)
                    st.write(builder1.__dict__)
    else:
        st.write('Sorry, comparisons for ' + team_id + ' are unavailable. Make another selection!')
#elif year != None:
 #   st.write('Select a school in the sidebar to view the closest statistical comparisons')
#elif school != None:
 #   st.write('Select a year in the sidebar to view the closest statistical comparisons')
#else:
 #   st.write('Select a school and a year in the sidebar to view the closest statistical comparisons')
