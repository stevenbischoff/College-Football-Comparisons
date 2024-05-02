"""
This module runs the app through the GUI class.
Accessed by streamlit.

Author: Steve Bischoff
"""
import streamlit as st
st.set_page_config(layout='wide')
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode

import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.neighbors import NearestNeighbors

from load_columns import *
import comparison_functions as cf
import data_loaders as dl
import style_functions as sf
import widget_helpers as wh

# Set app style
sf.set_markdown_style()

class GUI:
    
    def __init__(self):
        self.set_session_state()


    def set_session_state(self):
        if 'off_def' not in st.session_state:
            st.session_state['off_def'] = 'Combined'

        if 'adv' not in st.session_state:
            st.session_state['adv'] = True

        wh.set_data_type()

        if 'row_selected' not in st.session_state:
            st.session_state['row_selected'] = False
            st.session_state['selected_rows'] = []
        if 'n_comparisons' not in st.session_state:
            st.session_state['n_comparisons'] = 8
        if 'n_similar_stats' not in st.session_state:
            st.session_state['n_similar_stats'] = 8
        if 'n_dissimilar_stats' not in st.session_state:
            st.session_state['n_dissimilar_stats'] = 6               


    def header(self): # Parent: self.main()
        st.header('College Football: Statistically Similar FBS Teams 2014-2023')
        st.write("Select a school and a year to view the team's closest statistical comparisons.")

        
    def team_selection(self): # Parent: self.main()       
        left_column, mid_column, right_column = st.columns([0.2, 0.2, 0.6])
        with left_column:
            st.selectbox(label='**School**',
                         options=st.session_state['schools'],
                         index=None,
                         placeholder='Choose a school',
                         key='school_selectbox')
            st.session_state['school'] = st.session_state['school_selectbox']
        with mid_column:
            st.session_state['year'] = st.selectbox(label='**Year**',
                                                    options=st.session_state['years'],
                                                    index=None,
                                                    placeholder='Choose a year',
                                                    key='year_selectbox')        


    def settings_expander(self): # Parent: self.body_left_column()
        with st.expander('**Settings**'):
            left_column, right_column = st.columns(2)
            with left_column: # Display settings
                st.slider(label='\# of team comparisons',
                          min_value=1, max_value=20,
                          value=st.session_state['n_comparisons'],
                          key='n_comparisons_slider',
                          on_change=wh.change_n_comparisons_slider)
                st.slider(label='\# of similar stats',
                          min_value=1, max_value=20,
                          value=st.session_state['n_similar_stats'],
                          key='n_similar_stats_slider',
                          on_change=wh.change_n_similar_stats_slider)
                st.slider(label='\# of dissimilar stats',
                          min_value=1, max_value=20,
                          value=st.session_state['n_dissimilar_stats'],
                          key='n_dissimilar_stats_slider',
                          on_change=wh.change_n_dissimilar_stats_slider)
            with right_column: # Data settings
                st.radio(label='Compare offense, defense, or combined?',
                         options=['Offense', 'Defense', 'Combined'],
                         key='off_def_radio',
                         index=self.off_def_radio_index,
                         on_change=wh.change_off_def_radio)
                st.toggle(label='Include Advanced Stats',
                          value=st.session_state['adv'],
                          key='adv_toggle',
                          on_change=wh.change_adv_toggle)
                st.write('Advanced stat explanations: https://collegefootballdata.com/glossary')


    def comparisons_header(self):  # Parent: self.display_comparisons()
        # Get team record
        record_string = '('+st.session_state['team_records'].loc[st.session_state['team_id']].item()+')'
        # Team ( / Offense / Defense)
        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id']+' '+record_string
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school']+' Offense '+str(st.session_state['year'])+' '+record_string
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school']+' Defense '+str(st.session_state['year'])+' '+record_string
        st.subheader(subheader_string)
        # User instructions
        st.write('Select a row for a detailed comparison!')


    def comparisons_grid(self): # Parent: self.display_comparisons()
        # Get the closest comparisons to team_id
        comparisons, distances = cf.get_comparison_results(self.nn)
        # Prepare dataframe for AgGrid
        display_df = cf.comparisons_to_display_df(comparisons, distances) 
        # Set grid options
        builder = GridOptionsBuilder.from_dataframe(display_df, enableRowGroup=True, enableValue=True)
        builder.configure_selection('single')
        builder.configure_default_column(resizable=False)
        builder.configure_column('Rank', headerName='', width=50)
        builder.configure_column('Season', width=130)
        builder.configure_column('SSS*', width=130)
        go = builder.build()
        # Display grid
        selection = AgGrid(display_df,
                           fit_columns_on_grid_load=True,
                           enable_enterprise_modules=False,
                           gridOptions=go,
                           update_mode=GridUpdateMode.MODEL_CHANGED)
        # On row selection
        if len(selection.selected_rows) > 0:
            st.session_state['row_selected'] = True
            st.session_state['selected_rows'] = selection.selected_rows
        # Footnote
        st.caption('*SSS, or Statistical Similarity Score, is a measure from 0 to 1 of the statistical similarity between two teams. See the README: https://github.com/stevenbischoff/College-Football-Comparisons/tree/main')

        
    def display_comparisons(self): # Parent: self.body_left_column()
        self.comparisons_header()
        self.comparisons_grid()        

        
    def body_left_column(self): # Parent: self.body()
        if st.session_state['team_id'] in st.session_state['team_ids']: # If valid team_id selected
            self.display_comparisons()
        self.settings_expander()


    def stats_header(self): # Parent: self.body_right_column()
        # Get team_comp record
        record_string = '('+st.session_state['team_records'].loc[st.session_state['team_id_comp']].item()+')'
        # Comparison team ( / Offense / Defense)
        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id_comp'] + ' ' + record_string
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school_comp'] + ' Offense ' + str(st.session_state['year_comp']) + ' ' + record_string
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school_comp'] + ' Defense ' + str(st.session_state['year_comp']) + ' ' + record_string
        st.subheader('Comparison with {}'.format(subheader_string))


    def similar_stats_expander(self, similar_stats_df): # Parent: self.body_right_column()
        with st.expander('**Similarities**', expanded=True):
            # Similar offensive stats
            o_similar_stats_df = similar_stats_df[similar_stats_df.index.isin(
                list(o_normal_columns.values()) + list(o_advanced_columns.values()) + list(other_columns.values()))]
            if len(o_similar_stats_df) > 0:
                o_html = sf.stats_df_to_html(o_similar_stats_df, high_bad, uuid='1').replace('Statistic*', 'Off. Statistic*')
                st.write(o_html, unsafe_allow_html=True)
            # Similar defensive stats
            d_similar_stats_df = similar_stats_df[similar_stats_df.index.isin(
                list(d_normal_columns.values()) + list(d_advanced_columns.values()))]
            if len(d_similar_stats_df) > 0:
                d_html = sf.stats_df_to_html(d_similar_stats_df, high_bad, uuid='2').replace('Statistic*', 'Def. Statistic*')
                st.write(d_html, unsafe_allow_html=True)
            st.write('') # Empty space


    def dissimilar_stats_expander(self, dissimilar_stats_df): # Parent: self.body_right_column()
        with st.expander('**Dissimilarities**'):
            # Dissimilar offensive stats
            o_dissimilar_stats_df = dissimilar_stats_df[dissimilar_stats_df.index.isin(
                list(o_normal_columns.values()) + list(o_advanced_columns.values()) + list(other_columns.values()))]
            if len(o_dissimilar_stats_df) > 0:
                o_dis_html = sf.stats_df_to_html(o_dissimilar_stats_df, high_bad, uuid='3').replace('Statistic*', 'Off. Statistic*')
                st.write(o_dis_html, unsafe_allow_html=True)
            # Dissimilar defensive stats
            d_dissimilar_stats_df = dissimilar_stats_df[dissimilar_stats_df.index.isin(
                list(d_normal_columns.values()) + list(d_advanced_columns.values()))]
            if len(d_dissimilar_stats_df) > 0:
                d_dis_html = sf.stats_df_to_html(d_dissimilar_stats_df, high_bad, uuid='4').replace('Statistic*', 'Def. Statistic*')
                st.write(d_dis_html, unsafe_allow_html=True)
            st.write('') # Empty space


    def color_legend(self): # Parent: self.body_right_column()
        fig, ax = plt.subplots(figsize=(2, 0.06))
        norm = Normalize(vmin=0, vmax=1)
        cb = ColorbarBase(ax, cmap='RdBu', norm=norm, orientation='horizontal')
        cb.set_ticks([0,1])
        cb.set_ticklabels(['Bad', 'Good***'])
        cb.ax.tick_params(labelsize=4, size=0)
        st.pyplot(fig, use_container_width=False)

        
    def body_right_column(self): # Parent: self.body()
        # Change settings to fit selection
        selected_row = st.session_state['selected_rows'][0]
        st.session_state['school_comp'] = selected_row['School']
        st.session_state['year_comp'] = selected_row['Season']
        st.session_state['team_id_comp'] = st.session_state['school_comp'] + ' ' + st.session_state['year_comp']
        # Get similar / dissimilar statistics
        similar_stats_df = cf.get_similar_stats() 
        dissimilar_stats_df = cf.get_dissimilar_stats()
        # Display components
        self.stats_header()      
        self.similar_stats_expander(similar_stats_df)       
        self.dissimilar_stats_expander(dissimilar_stats_df)
        self.color_legend()
        # Display footnotes
        st.caption('*Statistics are per-game unless otherwise specified.')
        st.caption('**Pctl. columns give the percentile of the statistic across all teams in the dataset.')
        st.caption("***Color labels don't apply well for some stats (e.g. Rushing Yards / Total Yards).")

        
    def body(self): # Parent: self.main()
        left_column, right_column = st.columns([0.4, 0.6])

        if (st.session_state['school'] != None) & (st.session_state['year'] != None): # If team_id selected
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
            else: # If team_id not in st.session_state['team_ids']
                st.write('Sorry, comparisons for ' + st.session_state['team_id'] + ' are unavailable. Make another selection!')
        else: # If team_id not selected
            with left_column:
                self.settings_expander()

            
    def main(self):
        # Load data
        st.session_state['max_distance'] = dl.load_max_distance(st.session_state['data_type'])
        st.session_state['df_raw'] = dl.load_raw_data(st.session_state['data_type'])
        st.session_state['df_standardized'] = dl.load_standardized_data(st.session_state['data_type'])
        st.session_state['df_transformed'] = dl.load_transformed_data(st.session_state['data_type'])
        st.session_state['team_records'] = dl.load_records()
        # Set columns given data type
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
        # Set team_ids, schools, and years
        st.session_state['team_ids'] = st.session_state['df_transformed'].index.values
        st.session_state['schools'] = sorted(st.session_state['df_transformed'].index.str[:-5].unique())
        st.session_state['years'] = sorted(st.session_state['df_transformed'].index.str[-4:].unique(), reverse=True)
        # Fit Nearest Neighbors
        self.nn = NearestNeighbors(n_neighbors=st.session_state['n_comparisons']+1).fit(st.session_state['df_transformed'].values)
        # Run app
        self.header()
        self.team_selection()
        self.body()
    
if __name__ == '__main__':
    gui = GUI()
    gui.main()
