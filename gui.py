import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import pickle
from sklearn.neighbors import NearestNeighbors
import scipy.stats as stats
import copy

from load_columns import *

class GUI:
    def __init__(self):
        st.set_page_config(layout='wide')
        self.set_session_state()

    def set_session_state(self):
        if 'off_def' not in st.session_state:
            st.session_state['off_def'] = 'Combined'

        if 'adv' not in st.session_state:
            st.session_state['adv'] = True

        set_data_type()

        if 'row_selected' not in st.session_state:
            st.session_state['row_selected'] = False
            st.session_state['selected_rows'] = []

        if 'n_comps' not in st.session_state:
            st.session_state['n_comps'] = 8

        if 'n_similar_stats' not in st.session_state:
            st.session_state['n_similar_stats'] = 8

        if 'n_dissimilar_stats' not in st.session_state:
            st.session_state['n_dissimilar_stats'] = 5        

    #@st.cache_data
    def get_comp_results(self):
        results = self.nn.kneighbors(st.session_state['df_transformed'].loc[st.session_state.team_id].values.reshape(1,-1),
                                     st.session_state['n_comps']+1, return_distance=True)
        indices = results[1][0][1:]
        distances = results[0][0][1:]
        return st.session_state['df_transformed'].index[indices], distances

    def comps_to_display_df(self, comps, distances):
        schools = comps.str[:-5]
        seasons = comps.str[-4:]
        sss = 1 - distances/st.session_state['max_distance'] # Statistical Similarity Score
        return pd.DataFrame({'Rank': range(1, st.session_state['n_comps']+1), 'School': schools,
                             'Season': seasons, 'SSS*': sss.round(4)}, index=range(1, st.session_state['n_comps']+1))

    #@st.cache_data
    def get_similar_stats(self, pctl_threshold=15):
        stat_diffs = (st.session_state['df_standardized'].loc[st.session_state['team_id'], list(st.session_state['X_columns'].keys())
            ] - st.session_state['df_standardized'].loc[st.session_state['team_id_comp'], list(st.session_state['X_columns'].keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', st.session_state['team_id'], 'pctl1',
                                          st.session_state['team_id_comp'], 'pctl2'])

        counter = 0
        for stat in stat_diffs.index:
            if counter >= st.session_state['n_similar_stats']:
                break
            pctl1 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id'], stat])
            if pctl1 < pctl_threshold or pctl1 > 100 - pctl_threshold: 
                pctl2 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat])
                if abs(pctl1 - pctl2) <= 8: 
                    return_df.loc[counter] = [st.session_state['X_columns'][stat],
                                              '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id'], stat],3)),
                                              round(pctl1, 2),
                                              '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],3)),
                                              round(pctl2, 2)]
                    counter += 1
        for stat in stat_diffs.index:
            if counter >= st.session_state['n_similar_stats']:
                break
            if stat in return_df['Statistic*'].values:
                continue
            pctl1 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id'], stat])
            pctl2 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat])
            return_df.loc[counter] = [st.session_state['X_columns'][stat],
                                      '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id'], stat],3)),
                                      round(pctl1, 2),
                                      '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],3)),
                                      round(pctl2, 2)]
            counter += 1
        return return_df

    #@st.cache_data
    def get_different_stats(self):
        stat_diffs = (st.session_state['df_standardized'].loc[st.session_state['team_id'], list(st.session_state['X_columns'].keys())
            ] - st.session_state['df_standardized'].loc[st.session_state['team_id_comp'], list(st.session_state['X_columns'].keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', st.session_state['team_id'], 'pctl1',
                                          st.session_state['team_id_comp'], 'pctl2'])
        for stat in stat_diffs.index[-st.session_state['n_dissimilar_stats']:]:
            pctl1 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id'], stat])
            pctl2 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat])
            return_df.loc[len(return_df)] = [st.session_state['X_columns'][stat],
                                                   '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id'], stat],3)),
                                                   round(pctl1, 2),
                                                   '%s' % float('%.4g' % round(st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],3)),
                                                   round(pctl2, 2)]
        return return_df.iloc[::-1]

    def header(self):
        st.header('College Football: Statistically Similar FBS Teams 2014-2023')
        st.write("Select a school and a year to view the team's closest statistical comparisons")
        
    def team_selection(self):        
        left_column, mid_column, right_column = st.columns([0.2,0.2,0.6])
        with left_column:
            st.selectbox(label='**School**', options=st.session_state['schools'], index=None,
                         placeholder='Choose a school', key='school_selectbox')
            st.session_state['school'] = st.session_state['school_selectbox']
        with mid_column:
            st.session_state['year'] = st.selectbox(label='**Year**', options=st.session_state['years'], index=None,
                                     placeholder='Choose a year', key='year_selectbox')        

    def advanced_options(self):
        with st.expander('**Settings**'):
            left_column, right_column = st.columns(2)
            with left_column:
                st.slider(label='No. of team comparisons to display', min_value=1, max_value=20,
                          value=st.session_state['n_comps'], key='n_comps_slider',
                          on_change=change_n_comps_slider)
                st.slider(label='No. of similar stats to display', min_value=1, max_value=20,
                          value=st.session_state['n_similar_stats'], key='n_similar_stats_slider',
                          on_change=change_n_similar_stats_slider)
                st.slider(label='No. of dissimilar stats to display', min_value=1, max_value=20,
                          value=st.session_state['n_dissimilar_stats'], key='n_dissimilar_stats_slider',
                          on_change=change_n_dissimilar_stats_slider)
            with right_column:
                st.radio(label='Compare offense, defense, or combined?', options=['Offense', 'Defense', 'Combined'],
                     key='off_def_radio', index=self.off_def_radio_index,
                         on_change=change_off_def_radio)
                st.toggle(label='Include Advanced Stats', value=st.session_state['adv'], key='adv_toggle',
                          on_change=change_adv_toggle) # SET TO TRUE IF ADV. PROBLEM FIXED
                st.write('Advanced stat explanations: https://collegefootballdata.com/glossary')
        
    def display_comparisons(self):
        
        comps, distances = self.get_comp_results()
        display_df = self.comps_to_display_df(comps, distances)

        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id']
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school'] + ' Offense ' + str(st.session_state['year'])
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school'] + ' Defense ' + str(st.session_state['year'])
        st.subheader(subheader_string)
        
        st.write('Select a row for a detailed comparison!')
        
        builder = GridOptionsBuilder.from_dataframe(
            display_df, enableRowGroup=True, enableValue=True
            )
        builder.configure_selection('single')
        builder.configure_default_column(resizable=False)
        builder.configure_column('Rank', headerName='', width=50)
        builder.configure_column('Season', width=130)
        builder.configure_column('SSS*', width=130)
        go = builder.build()
        
        selection = AgGrid(display_df, fit_columns_on_grid_load=True,
               enable_enterprise_modules=True, gridOptions=go, update_mode=GridUpdateMode.MODEL_CHANGED)       
        if len(selection.selected_rows) > 0:
            st.session_state['row_selected'] = True
            st.session_state['selected_rows'] = selection.selected_rows

        st.caption('*SSS, or Statistical Similarity Score, is a measure from 0 to 1 of the statistical similarity between two teams.')
        
    def body_left_column(self):
        if st.session_state['team_id'] in st.session_state['team_ids']:
            self.display_comparisons()
        self.advanced_options()

    def body_right_column(self):
        selected_row = st.session_state['selected_rows'][0]
        st.session_state['school_comp'] = selected_row['School']
        st.session_state['year_comp'] = selected_row['Season']
        st.session_state['team_id_comp'] = st.session_state['school_comp'] + ' ' + st.session_state['year_comp']

        similar_stats_df = self.get_similar_stats()
        different_stats_df = self.get_different_stats()

        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id_comp']
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school_comp'] + ' Offense ' + str(st.session_state['year_comp'])
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school_comp'] + ' Defense ' + str(st.session_state['year_comp'])

        st.subheader('Comparison with {}'.format(subheader_string))
        
        go = {'columnDefs': [
                {'field': 'Statistic*'},
                {'headerName': st.session_state['team_id'],
                 'children': [
                 {'headerName': 'Value',
                  'field': st.session_state['team_id'],
                  'width': 100,
                  'type': 'rightAligned'},
                 {'headerName': 'Pctl.**',
                  'field': 'pctl1',
                  'width': 100,
                  'type': 'rightAligned'}
                 ],},
                {'headerName': st.session_state['team_id_comp'],
                 'children': [
                 {'headerName': 'Value',
                  'field': st.session_state['team_id_comp'],
                  'width': 100,
                  'type': 'rightAligned'},
                 {'headerName': 'Pctl.',
                  'field': 'pctl2',
                  'width': 100,
                  'type': 'rightAligned'}
                 ]}]}
        
        with st.expander('**Similarities**', expanded=True):
            AgGrid(similar_stats_df, fit_columns_on_grid_load=True, gridOptions=go)              
    
        with st.expander('**Dissimilarities**'):
            AgGrid(different_stats_df, fit_columns_on_grid_load=True, gridOptions=go)
            
        st.caption('*Statistics are per-game unless otherwise specified.')
        st.caption('**Pctl. columns give the percentile of the statistic across all years in the dataset.')
        
    def body(self):
        left_column, right_column = st.columns([0.4, 0.6])

        if (st.session_state['school'] != None) & (st.session_state['year'] != None): # if team selected
            st.session_state['team_id'] = st.session_state['school'] + ' ' + str(st.session_state['year'])
            if 'saved_team_id' in st.session_state:
                if st.session_state['team_id'] != st.session_state['saved_team_id']: # reset
                    st.session_state['selected_rows'] = []
                    st.session_state['row_selected'] = False
            st.session_state['saved_team_id'] = st.session_state['team_id']
            with left_column:
                self.body_left_column()
            if st.session_state['team_id'] in st.session_state['team_ids']:
                with right_column:
                    if st.session_state['row_selected']:                
                        self.body_right_column()
            else: # if st.session_state['team_id'] not in st.session_state['team_ids']
                st.write('Sorry, comparisons for ' + st.session_state['team_id'] + ' are unavailable. Make another selection!')
        else:
            with left_column:
                self.advanced_options()
            
    def main(self):
        # load data
        st.session_state['max_distance'] = load_max_distance(st.session_state['data_type'])
        st.session_state['df_raw'] = load_raw_data(st.session_state['data_type'])
        st.session_state['df_standardized'] = load_standardized_data(st.session_state['data_type'])
        st.session_state['df_transformed'] = load_transformed_data(st.session_state['data_type'])
        if st.session_state['data_type'].startswith('Combined'):
            if st.session_state['data_type'] == 'Combined No Adv':
                st.session_state['X_columns'] = {**o_normal_columns, **d_normal_columns, **other_columns}
            else:
                st.session_state['X_columns'] = X_columns
            self.off_def_radio_index = 2
        elif st.session_state['data_type'].startswith('Offense'):
            if st.session_state['data_type'] == 'Offense No Adv':
                st.session_state['X_columns'] = o_normal_columns
            else:
                st.session_state['X_columns'] = {**o_normal_columns, **o_advanced_columns}
            self.off_def_radio_index = 0
        elif st.session_state['data_type'].startswith('Defense'):
            if st.session_state['data_type'] == 'Defense No Adv':
                st.session_state['X_columns'] = d_normal_columns
            else:
                st.session_state['X_columns'] = {**d_normal_columns, **d_advanced_columns}
            self.off_def_radio_index = 1

        # Preparation
        st.session_state['team_ids'] = st.session_state['df_transformed'].index.values
        st.session_state['schools'] = sorted(st.session_state['df_transformed'].index.str[:-5].unique())
        st.session_state['years'] = sorted(st.session_state['df_transformed'].index.str[-4:].unique(), reverse=True)

        self.nn = NearestNeighbors(n_neighbors=st.session_state['n_comps']+1).fit(st.session_state['df_transformed'].values)

        ### APP ###
        st.markdown("""
            <style>
            [data-testid=stVerticalBlock]{
                gap: 0.5rem;
                padding-top: 0rem;
            }
            [data-testid=header]{
                gap: 0rem;
                padding-top: 0rem;
            }
            </style>
            """, unsafe_allow_html=True)

        self.header()
        self.team_selection()
        self.body()
        
        
@st.cache_data
def load_max_distance(data_type):
    with open('static/max_distance.pkl', 'rb') as f:
        distance_dict = pickle.load(f)
        return distance_dict[data_type]

@st.cache_data
def load_raw_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/raw_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/raw_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/raw_offense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/raw_offense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/raw_defense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/raw_defense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    
@st.cache_data
def load_standardized_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/standardized_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/standardized_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/standardized_offense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/standardized_offense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/standardized_defense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/standardized_defense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')

@st.cache_data
def load_transformed_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/transformed_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/transformed_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/transformed_offense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/transformed_offense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/transformed_defense_team_stats_2014_2023.csv',
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/transformed_defense_no_adv_team_stats_2014_2023.csv',
                           index_col='team_id')

def change_n_comps_slider():
    st.session_state['n_comps'] = st.session_state['n_comps_slider']

def change_n_similar_stats_slider():
    st.session_state['n_similar_stats'] = st.session_state['n_similar_stats_slider']

def change_n_dissimilar_stats_slider():
    st.session_state['n_dissimilar_stats'] = st.session_state['n_dissimilar_stats_slider']

def change_off_def_radio():
    st.session_state['off_def'] = st.session_state['off_def_radio']
    set_data_type()

def change_adv_toggle():
    st.session_state['adv'] = st.session_state['adv_toggle']
    set_data_type()

def set_data_type():
    if st.session_state['adv']:
        st.session_state['data_type'] = st.session_state['off_def']
    else:
        st.session_state['data_type'] = st.session_state['off_def'] + ' No Adv'
    
if __name__ == '__main__':
    gui = GUI()
    gui.main()
