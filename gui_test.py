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

        if 'off_def' not in st.session_state:
            st.session_state['off_def'] = 'Combined'
        if 'adv' not in st.session_state:
            st.session_state['adv'] = True
        set_data_type()
        if 'n_comps' not in st.session_state:
            st.session_state['n_comps'] = 8
        if 'n_similar_stats' not in st.session_state:
            st.session_state['n_similar_stats'] = 8
        if 'n_dissimilar_stats' not in st.session_state:
            st.session_state['n_dissimilar_stats'] = 5

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
    def get_similar_stats(self):
        stat_diffs = (self.df_standardized.loc[self.team_id, list(self.X_columns.keys())
            ] - self.df_standardized.loc[self.team_id_comp, list(self.X_columns.keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', self.team_id, 'pctl1',
                                          self.team_id_comp, 'pctl2'])
        
        for stat in stat_diffs.index[:st.session_state['n_similar_stats']]:
            pctl1 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id, stat])
            pctl2 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id_comp, stat])
            return_df.loc[len(return_df)] = [self.X_columns[stat],
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id, stat],3)),
                                                   round(pctl1, 2),
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id_comp, stat],3)),
                                                   round(pctl2, 2)]
        return return_df

    #@st.cache_data
    def get_different_stats(self):
        stat_diffs = (self.df_standardized.loc[self.team_id, list(self.X_columns.keys())
            ] - self.df_standardized.loc[self.team_id_comp, list(self.X_columns.keys())]).abs().sort_values()
        return_df = pd.DataFrame(columns=['Statistic*', self.team_id, 'pctl1',
                                          self.team_id_comp, 'pctl2'])
        for stat in stat_diffs.index[-st.session_state['n_dissimilar_stats']:]:
            pctl1 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id, stat])
            pctl2 = stats.percentileofscore(self.df_raw[stat], self.df_raw.loc[self.team_id_comp, stat])
            return_df.loc[len(return_df)] = [self.X_columns[stat],
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id, stat],3)),
                                                   round(pctl1, 2),
                                                   '%s' % float('%.4g' % round(self.df_raw.loc[self.team_id_comp, stat],3)),
                                                   round(pctl2, 2)]
        return return_df.iloc[::-1]
    
    def header(self):
        st.header('College Football: Most Statistically Similar FBS Teams 2014-2023')
        st.write("Select a school and a year to view the team's closest statistical comparisons")
        
    def team_selection(self):        
        left_column, mid_column, right_column = st.columns([0.4,0.4,0.2])
        with left_column:
            self.school = st.selectbox(label='**School**', options=self.schools, index=None,
                                       placeholder='Choose a school')
        with mid_column:
            self.year = st.selectbox(label='**Year**', options=self.years, index=None,
                                    placeholder='Choose a year')

    def display_comparisons(self):
        
        comps, distances = self.get_comp_results()
        display_df = self.comps_to_display_df(comps, distances)

        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = self.team_id
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = self.school + ' Offense ' + str(self.year)
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = self.school + ' Defense ' + str(self.year)
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

    def advanced_options(self):
        with st.expander('**Advanced Options**'):
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
                
            
    def body_left_column(self):
        if self.team_id in self.team_ids:
            self.display_comparisons()
        self.advanced_options()
            
    def body(self):
        left_column, right_column = st.columns([0.4, 0.6])

        if (self.school != None) & (self.year != None): # if team selected
            self.team_id = self.school + ' ' + str(self.year)

            with left_column:
                self.body_left_column()
        else:
            with left_column:
                self.advanced_options()
           
    def main(self):

        # load data
        self.max_distance = load_max_distance(st.session_state['data_type'])
        self.df_teams = load_team_data()
        self.df_raw = load_raw_data(st.session_state['data_type'])
        self.df_standardized = load_standardized_data(st.session_state['data_type'])
        self.df_transformed = load_transformed_data(st.session_state['data_type'])
        if st.session_state['data_type'].startswith('Combined'):
            if st.session_state['data_type'] == 'Combined No Adv':
                self.X_columns = {**o_normal_columns, **d_normal_columns, **other_columns}
            else:
                self.X_columns = X_columns
            self.off_def_radio_index = 2
        elif st.session_state['data_type'].startswith('Offense'):
            if st.session_state['data_type'] == 'Offense No Adv':
                self.X_columns = o_normal_columns
            else:
                self.X_columns = {**o_normal_columns, **o_advanced_columns}
            self.off_def_radio_index = 0
        elif st.session_state['data_type'].startswith('Defense'):
            if st.session_state['data_type'] == 'Defense No Adv':
                self.X_columns = d_normal_columns
            else:
                self.X_columns = {**d_normal_columns, **d_advanced_columns}
            self.off_def_radio_index = 1

        # Preparation
        self.team_ids = self.df_transformed.index.values
        self.schools = sorted(self.df_transformed.index.str[:-5].unique())
        self.years = sorted(self.df_transformed.index.str[-4:].unique())

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
