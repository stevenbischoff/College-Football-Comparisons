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

        self.max_distance = None
        self.df_teams = None
        self.df_raw = None
        self.df_standardized = None
        self.df_transformed = None

        self.team_ids = None
        self.schools = None
        self.school = None
        self.year = None

        if 'off_def' not in st.session_state:
            st.session_state['off_def'] = 'Combined'
        elif 'off_def_radio' in st.session_state:
            st.session_state['off_def'] = st.session_state['off_def_radio']
            
        self.row_selected = False
        if 'selected_rows' in st.session_state:
            if len(st.session_state['selected_rows']) > 0:
                self.row_selected = True

        if 'n_comps' not in st.session_state:
            st.session_state['n_comps'] = 10
        elif 'n_comps_slider' in st.session_state:
            st.session_state['n_comps'] = st.session_state['n_comps_slider']

        if 'n_similar_stats' not in st.session_state:
            st.session_state['n_similar_stats'] = 10
        elif 'n_similar_stats_slider' in st.session_state:
            st.session_state['n_similar_stats'] = st.session_state['n_similar_stats_slider']

        if 'n_dissimilar_stats' not in st.session_state:
            st.session_state['n_dissimilar_stats'] = 5
        elif 'n_dissimilar_stats_slider' in st.session_state:
            st.session_state['n_dissimilar_stats'] = st.session_state['n_dissimilar_stats_slider']
        

    #@st.cache_data
    def get_comp_results(self):
        results = self.nn.kneighbors(self.df_transformed.loc[self.team_id].values.reshape(1,-1),
                                     st.session_state['n_comps']+1, return_distance=True)
        indices = results[1][0][1:]
        distances = results[0][0][1:]
        return self.df_transformed.index[indices], distances

    def comps_to_display_df(self, comps, distances):
        schools = comps.str[:-5]
        seasons = comps.str[-4:]
        sss = 1 - distances/self.max_distance # Statistical Similarity Score
        return pd.DataFrame({'Rank': range(1, st.session_state['n_comps']+1), 'School': schools,
                             'Season': seasons, 'SSS*': sss.round(4)}, index=range(1, st.session_state['n_comps']+1))

    #@st.cache_data
    def get_similar_stats(self, team_id2, pctl_threshold=15):
        stat_diffs = (self.df_standardized.loc[self.team_id, list(self.X_columns.keys())
            ] - self.df_standardized.loc[team_id2, list(self.X_columns.keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', self.team_id, 'pctl1',
                                          team_id2, 'pctl2'])
        
        for stat in stat_diffs.index[:st.session_state['n_similar_stats']]:
            pctl1 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id, stat])
            pctl2 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[team_id2, stat])
            return_df.loc[len(return_df)] = [self.X_columns[stat],
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id, stat],3)),
                                                   round(pctl1, 2),
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[team_id2, stat],3)),
                                                   round(pctl2, 2)]
        return return_df

    #@st.cache_data
    def get_different_stats(self, team_id2):
        stat_diffs = (self.df_standardized.loc[self.team_id, list(self.X_columns.keys())
            ] - self.df_standardized.loc[team_id2, list(self.X_columns.keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', self.team_id, 'pctl1',
                                          team_id2, 'pctl2'])
        for stat in stat_diffs.index[-st.session_state['n_dissimilar_stats']:]:
            pctl1 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id, stat])
            #if pctl1 < pctl_threshold or pctl1 > 100 - pctl_threshold:
            pctl2 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[team_id2, stat])
            return_df.loc[len(return_df)] = [self.X_columns[stat],
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id, stat],3)),
                                                   round(pctl1, 2),
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[team_id2, stat],3)),
                                                   round(pctl2, 2)]
        return return_df.iloc[::-1]

    def header(self):
        st.header('College Football: Most Statistically Similar FBS Teams 2004-2023')
        st.write("Select a school and a year to view the team's closest statistical comparisons")
        
    def team_selection(self):        
        left_column, mid_column, right_column = st.columns([0.4,0.4,0.2])
        with left_column:
            self.school = st.selectbox(label='School', options=self.schools, index=None)
        with mid_column:
            self.year = st.selectbox(label='Year', options=range(2004, 2024), index=None)

    def advanced_options(self):
        st.slider(label='No. of team comparisons to display', min_value=1, max_value=20,
                  value=st.session_state['n_comps'], key='n_comps_slider')
        st.slider(label='No. of similar stats to display', min_value=1, max_value=20,
                  value=st.session_state['n_similar_stats'], key='n_similar_stats_slider')
        st.slider(label='No. of dissimilar stats to display', min_value=1, max_value=20,
                  value=st.session_state['n_dissimilar_stats'], key='n_dissimilar_stats_slider')
        st.radio(label='Compare combined offense and defense?', options=['Combined', 'Offense', 'Defense'],
                 key='off_def_radio', index=self.off_def_radio_index)
        
    def display_comparisons(self):
        
        comps, distances = self.get_comp_results()
        display_df = self.comps_to_display_df(comps, distances)
                
        st.subheader(self.team_id)
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
            self.row_selected = True
            st.session_state['selected_rows'] = selection.selected_rows

        st.caption('*SSS, or Statistical Similarity Score, is a measure from 0 to 1 of the statistical similarity between two teams.')
        
    def body_left_column(self):
        self.display_comparisons()
        if st.checkbox('Show advanced options'):
            self.advanced_options()

    def body_right_column(self):
        selected_row = st.session_state['selected_rows'][0]
        team_id_comp = selected_row['School'] + ' ' + selected_row['Season']

        similar_stats_df = self.get_similar_stats(team_id_comp)
        different_stats_df = self.get_different_stats(team_id_comp)

        st.subheader('Comparison with {}'.format(team_id_comp))
        
        go = {'columnDefs': [
                {'field': 'Statistic*'},
                {'headerName': self.team_id,
                 'children': [
                 {'headerName': 'Value',
                  'field': self.team_id,
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
        
        with st.expander('Similarities:'):
            AgGrid(similar_stats_df, fit_columns_on_grid_load=True, gridOptions=go)              
    
        with st.expander('Dissimilarities:'):
            AgGrid(different_stats_df, fit_columns_on_grid_load=True, gridOptions=go)
            
        st.caption('*Statistics are per-game unless otherwise specified.')
        st.caption('**Pctl. columns give the percentile of the statistic in the entire dataset.')
        
    def body(self):
        left_column, right_column = st.columns([0.4,0.6])

        if (self.school != None) & (self.year != None):
            self.team_id = self.school + ' ' + str(self.year)
            if 'saved_team_id' in st.session_state:
                if self.team_id != st.session_state['saved_team_id']: # reset
                    st.session_state['selected_rows'] = []
                    self.row_selected = False
            st.session_state['saved_team_id'] = self.team_id
            if self.team_id in self.team_ids:
                with left_column:
                    self.body_left_column()  
                with right_column:
                    if self.row_selected:                
                        self.body_right_column()
            else:
                st.write('Sorry, comparisons for ' + self.team_id + ' are unavailable. Make another selection!')
            
    def main(self):
        # settings
        self.n_comps = st.session_state['n_comps']

        # load data
        self.max_distance = load_max_distance(st.session_state['off_def'])
        self.df_teams = load_team_data()
        self.df_raw = load_raw_data(st.session_state['off_def'])
        self.df_standardized = load_standardized_data(st.session_state['off_def'])
        self.df_transformed = load_transformed_data(st.session_state['off_def'])
        if st.session_state['off_def'] == 'Combined':
            self.X_columns = X_columns
            self.off_def_radio_index = 0
        elif st.session_state['off_def'] == 'Offense':
            self.X_columns = {**o_normal_columns, **o_advanced_columns}
            self.off_def_radio_index = 1
        elif st.session_state['off_def'] == 'Defense':
            self.X_columns = {**d_normal_columns, **d_advanced_columns}
            self.off_def_radio_index = 2

        # Preparation
        self.team_ids = self.df_transformed.index.values
        self.schools = sorted(self.df_teams['school'].unique())

        self.nn = NearestNeighbors(n_neighbors=st.session_state['n_comps']+1).fit(self.df_transformed.values)

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
def load_team_data():
    return pd.read_csv('static/fbs_teams_2004_2023.csv')

@st.cache_data
def load_raw_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/raw_team_stats_2004_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/raw_offense_team_stats_2004_2023.csv',
                           index_col='team_id')
    if data_type == 'Defense':
        return pd.read_csv('static/raw_defense_team_stats_2004_2023.csv',
                           index_col='team_id')
@st.cache_data
def load_standardized_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/standardized_team_stats_2004_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/standardized_offense_team_stats_2004_2023.csv',
                           index_col='team_id')
    if data_type == 'Defense':
        return pd.read_csv('static/standardized_defense_team_stats_2004_2023.csv',
                           index_col='team_id')

@st.cache_data
def load_transformed_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/transformed_team_stats_2004_2023.csv',
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/transformed_offense_team_stats_2004_2023.csv',
                           index_col='team_id')
    if data_type == 'Defense':
        return pd.read_csv('static/transformed_defense_team_stats_2004_2023.csv',
                           index_col='team_id')

if __name__ == '__main__':
    gui = GUI()
    gui.main()
