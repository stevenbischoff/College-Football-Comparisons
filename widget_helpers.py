"""
This module contains helper functions for gui.py that update st.session_state
for various user interactions with the app.

Author: Steve Bischoff
"""
import streamlit as st

def change_n_comparisons_slider():
    """Used in GUI.settings_expander() -> left_column -> Slider 1"""
    st.session_state['n_comparisons'] = st.session_state['n_comparisons_slider']

def change_n_similar_stats_slider():
    """Used in GUI.settings_expander() -> left_column -> Slider 2"""
    st.session_state['n_similar_stats'] = st.session_state['n_similar_stats_slider']

def change_n_dissimilar_stats_slider():
    """Used in GUI.settings_expander() -> left_column -> Slider 3"""
    st.session_state['n_dissimilar_stats'] = st.session_state['n_dissimilar_stats_slider']

def change_off_def_radio():
    """Used in GUI.settings_expander() -> right_column -> Radio 1"""
    st.session_state['off_def'] = st.session_state['off_def_radio']
    set_data_type()

def change_adv_toggle():
    """Used in GUI.settings_expander() -> right_column -> Toggle 1"""
    st.session_state['adv'] = st.session_state['adv_toggle']
    set_data_type()

def set_data_type():
    """Used in GUI.set_data_type()"""
    if st.session_state['adv']:
        st.session_state['data_type'] = st.session_state['off_def']
    else:
        st.session_state['data_type'] = st.session_state['off_def'] + ' No Adv'
