import streamlit as st
st.set_page_config(layout='wide')
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from st_aggrid.shared import GridUpdateMode

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import scipy.stats as stats

from load_columns import *
import data_loaders
import widget_helpers

class GUI:
    def __init__(self):
        self.set_session_state()

    def set_session_state(self):
        if 'off_def' not in st.session_state:
            st.session_state['off_def'] = 'Combined'

        if 'adv' not in st.session_state:
            st.session_state['adv'] = True

        widget_helpers.set_data_type()

        if 'row_selected' not in st.session_state:
            st.session_state['row_selected'] = False
            st.session_state['selected_rows'] = []

        if 'n_comparisons' not in st.session_state:
            st.session_state['n_comparisons'] = 8

        if 'n_similar_stats' not in st.session_state:
            st.session_state['n_similar_stats'] = 8

        if 'n_dissimilar_stats' not in st.session_state:
            st.session_state['n_dissimilar_stats'] = 5        

    def get_comparison_results(self):
        results = self.nn.kneighbors(st.session_state['df_transformed'].loc[st.session_state.team_id].values.reshape(1,-1),
                                     st.session_state['n_comparisons']+1, return_distance=True)
        indices = results[1][0][1:]
        distances = results[0][0][1:]
        return st.session_state['df_transformed'].index[indices], distances

    def comparisons_to_display_df(self, comparisons, distances):
        schools = comparisons.str[:-5]
        seasons = comparisons.str[-4:]
        sss = 1 - distances/st.session_state['max_distance'] # Statistical Similarity Score
        return pd.DataFrame({'Rank': range(1, st.session_state['n_comparisons']+1), 'School': schools,
                             'Season': seasons, 'SSS*': sss.round(4)}, index=range(1, st.session_state['n_comparisons']+1))

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
        left_column, mid_column, right_column = st.columns([0.2, 0.2, 0.6])
        with left_column:
            st.selectbox(label='**School**', options=st.session_state['schools'], index=None,
                         placeholder='Choose a school', key='school_selectbox')
            st.session_state['school'] = st.session_state['school_selectbox']
        with mid_column:
            st.session_state['year'] = st.selectbox(label='**Year**', options=st.session_state['years'], index=None,
                                     placeholder='Choose a year', key='year_selectbox')        

    def settings_expander(self):
        with st.expander('**Settings**'):
            left_column, right_column = st.columns(2)
            with left_column: # Display settings
                st.slider(label='No. of team comparisons to display', min_value=1, max_value=20,
                          value=st.session_state['n_comparisons'], key='n_comparisons_slider',
                          on_change=widget_helpers.change_n_comparisons_slider)
                st.slider(label='No. of similar stats to display', min_value=1, max_value=20,
                          value=st.session_state['n_similar_stats'], key='n_similar_stats_slider',
                          on_change=widget_helpers.change_n_similar_stats_slider)
                st.slider(label='No. of dissimilar stats to display', min_value=1, max_value=20,
                          value=st.session_state['n_dissimilar_stats'], key='n_dissimilar_stats_slider',
                          on_change=widget_helpers.change_n_dissimilar_stats_slider)
            with right_column: # Data settings
                st.radio(label='Compare offense, defense, or combined?', options=['Offense', 'Defense', 'Combined'],
                     key='off_def_radio', index=self.off_def_radio_index,
                         on_change=widget_helpers.change_off_def_radio)
                st.toggle(label='Include Advanced Stats', value=st.session_state['adv'], key='adv_toggle',
                          on_change=widget_helpers.change_adv_toggle)
                st.write('Advanced stat explanations: https://collegefootballdata.com/glossary')

    def comparisons_header(self):
        # Team ( / Offense / Defense)
        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id']
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school'] + ' Offense ' + str(st.session_state['year'])
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school'] + ' Defense ' + str(st.session_state['year'])
        st.subheader(subheader_string)
        # User instructions
        st.write('Select a row for a detailed comparison!')

    def comparisons_grid(self):
        # Get the closest comparisons to team_id
        comparisons, distances = self.get_comparison_results()
        display_df = self.comparisons_to_display_df(comparisons, distances)
        # Grid options
        builder = GridOptionsBuilder.from_dataframe(
            display_df, enableRowGroup=True, enableValue=True
            )
        builder.configure_selection('single')
        builder.configure_default_column(resizable=False)
        builder.configure_column('Rank', headerName='', width=50)
        builder.configure_column('Season', width=130)
        builder.configure_column('SSS*', width=130)
        go = builder.build()
        # Display grid
        selection = AgGrid(display_df, fit_columns_on_grid_load=True,
                           enable_enterprise_modules=False,
                           gridOptions=go, update_mode=GridUpdateMode.MODEL_CHANGED)
        # On row selection
        if len(selection.selected_rows) > 0:
            st.session_state['row_selected'] = True
            st.session_state['selected_rows'] = selection.selected_rows
        # Footnote
        st.caption('*SSS, or Statistical Similarity Score, is a measure from 0 to 1 of the statistical similarity between two teams.')
        
    def display_comparisons(self):
        self.comparisons_header()
        self.comparisons_grid()        
        
    def body_left_column(self):
        if st.session_state['team_id'] in st.session_state['team_ids']: # If valid team_id selected
            self.display_comparisons()
        self.settings_expander()

    def stats_header(self):
        # Comparison team ( / Offense / Defense)
        if st.session_state['data_type'].startswith('Combined'):
            subheader_string = st.session_state['team_id_comp']
        elif st.session_state['data_type'].startswith('Offense'):
            subheader_string = st.session_state['school_comp'] + ' Offense ' + str(st.session_state['year_comp'])
        elif st.session_state['data_type'].startswith('Defense'):
            subheader_string = st.session_state['school_comp'] + ' Defense ' + str(st.session_state['year_comp'])
        st.subheader('Comparison with {}'.format(subheader_string))
        
    def body_right_column(self):
        # Change settings to fit selection
        selected_row = st.session_state['selected_rows'][0]
        st.session_state['school_comp'] = selected_row['School']
        st.session_state['year_comp'] = selected_row['Season']
        st.session_state['team_id_comp'] = st.session_state['school_comp'] + ' ' + st.session_state['year_comp']
        # Get similar / dissimilar statistics
        similar_stats_df = self.get_similar_stats()
        different_stats_df = self.get_different_stats()
        
        self.stats_header()
        # Grid options
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
                 ]},
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
        # Similar stats expander
        with st.expander('**Similarities**', expanded=True):
            AgGrid(similar_stats_df, fit_columns_on_grid_load=True, 
                           enable_enterprise_modules=False, gridOptions=go)              
        # Dissimilar stats expander
        with st.expander('**Dissimilarities**'):
            AgGrid(different_stats_df, fit_columns_on_grid_load=True, 
                           enable_enterprise_modules=False, gridOptions=go)
        # Footnotes    
        st.caption('*Statistics are per-game unless otherwise specified.')
        st.caption('**Pctl. columns give the percentile of the statistic across all years in the dataset.')
        
    def body(self):
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
        st.session_state['max_distance'] = data_loaders.load_max_distance(st.session_state['data_type'])
        st.session_state['df_raw'] = data_loaders.load_raw_data(st.session_state['data_type'])
        st.session_state['df_standardized'] = data_loaders.load_standardized_data(st.session_state['data_type'])
        st.session_state['df_transformed'] = data_loaders.load_transformed_data(st.session_state['data_type'])
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
        # Style settings
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
        # Run app
        self.header()
        self.team_selection()
        self.body()
    
if __name__ == '__main__':
    gui = GUI()
    gui.main()
