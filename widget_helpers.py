import streamlit as st

def change_n_comparisons_slider():
    st.session_state['n_comparisons'] = st.session_state['n_comparisons_slider']

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
