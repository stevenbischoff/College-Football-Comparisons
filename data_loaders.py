"""
This module contains helper functions for gui.py that load and cache the
dataframes required to calculate SSS and display similar stats.
 - load_records
 - load_max_distance
 - load_raw_data
 - load_standardized_data
 - load_transformed_data
Besides load_records, each function takes a data_type argument that is one of
these 6 strings:
Combined, Combined No Adv, Offense, Offense No Adv, Defense, Defense No Adv

Author: Steve Bischoff
"""
import streamlit as st
import pandas as pd
import pickle

# Globals
FIRST_YEAR = 2014
LAST_YEAR = 2023


@st.cache_data
def load_records():
    return pd.read_csv('static/team_records_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                index_col='team_id')


@st.cache_data
def load_max_distance(data_type):
    with open('static/max_distance.pkl', 'rb') as f:
        distance_dict = pickle.load(f)
        return distance_dict[data_type]

    
@st.cache_data
def load_raw_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/raw_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/raw_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/raw_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/raw_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/raw_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/raw_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')

   
@st.cache_data
def load_standardized_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/standardized_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/standardized_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/standardized_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/standardized_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/standardized_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/standardized_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')


@st.cache_data
def load_transformed_data(data_type):
    if data_type == 'Combined':
        return pd.read_csv('static/transformed_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Combined No Adv':
        return pd.read_csv('static/transformed_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense':
        return pd.read_csv('static/transformed_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Offense No Adv':
        return pd.read_csv('static/transformed_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense':
        return pd.read_csv('static/transformed_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')
    elif data_type == 'Defense No Adv':
        return pd.read_csv('static/transformed_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR),
                           index_col='team_id')


@st.cache_data
def load_knn(data_type):
    if data_type == 'Combined':
        with open('static/models/knn.pkl', 'rb') as f:
            nn = pickle.load(f)
    elif data_type == 'Combined No Adv':
        with open('static/models/knn_no_adv.pkl', 'rb') as f:
            nn = pickle.load(f)
    elif data_type == 'Offense':
        with open('static/models/knn_offense.pkl', 'rb') as f:
            nn = pickle.load(f)
    elif data_type == 'Offense No Adv':
        with open('static/models/knn_offense_no_adv.pkl', 'rb') as f:
            nn = pickle.load(f)
    elif data_type == 'Defense':
        with open('static/models/knn_defense.pkl', 'rb') as f:
            nn = pickle.load(f)
    elif data_type == 'Defense No Adv':
        with open('static/models/knn_defense_no_adv.pkl', 'rb') as f:
            nn = pickle.load(f)
    return nn

