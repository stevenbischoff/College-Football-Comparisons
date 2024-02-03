import streamlit as st
import pandas as pd
import pickle

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
