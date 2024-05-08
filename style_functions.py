import streamlit as st

import copy
import pandas as pd

def set_markdown_style():
    st.markdown(f"""
        <style>
            .appview-container .main .block-container{{
                padding-top: 1rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }}
            [data-testid=stVerticalBlock]{{
                gap: 0.4rem;
                padding-top: 0rem;
            }}
            [data-testid=header]{{
                gap: 0rem;
                padding-top: 0rem;
            }}
        </style>""",
        unsafe_allow_html=True,
    )

def stats_df_to_html(stats_df, high_bad, uuid='1'):
    arrays = [[st.session_state['team_id']]*2 + [st.session_state['team_id_comp']]*2,
              ['Value', 'Pctl.**']*2]
    stats_df.columns = pd.MultiIndex.from_arrays(arrays)
    stats_df.reset_index(inplace=True)

    team_ids_gmap = copy.deepcopy(stats_df)
    team_ids_gmap.loc[team_ids_gmap[('Statistic*',)].isin(high_bad), (st.session_state['team_id'], 'Pctl.**')] = \
        100 - team_ids_gmap.loc[team_ids_gmap[('Statistic*',)].isin(high_bad), (st.session_state['team_id'], 'Pctl.**')]
    team_ids_gmap.loc[team_ids_gmap[('Statistic*',)].isin(high_bad), (st.session_state['team_id_comp'], 'Pctl.**')] = \
        100 - team_ids_gmap.loc[team_ids_gmap[('Statistic*',)].isin(high_bad), (st.session_state['team_id_comp'], 'Pctl.**')]
    
    stats_df = stats_df.style \
               .set_uuid(uuid) \
               .format(precision=2) \
               .set_properties(subset=[(st.session_state['team_id'], 'Value'), (st.session_state['team_id'], 'Pctl.**'),
                                       (st.session_state['team_id_comp'], 'Value'), (st.session_state['team_id_comp'], 'Pctl.**')],
                               **{'text-align': 'right'}) \
               .background_gradient(
                    'RdBu',
                    subset=[(st.session_state['team_id'], 'Pctl.**')],
                    gmap = team_ids_gmap[(st.session_state['team_id'], 'Pctl.**')],
                    vmin=0, vmax=100
                    ) \
                .background_gradient(
                    'RdBu',
                    subset=[(st.session_state['team_id_comp'], 'Pctl.**')],
                    gmap = team_ids_gmap[(st.session_state['team_id_comp'], 'Pctl.**')],
                    vmin=0, vmax=100
                    ) \
                .background_gradient(
                    'RdBu',
                    subset=[(st.session_state['team_id'], 'Value')],
                    gmap = team_ids_gmap[(st.session_state['team_id'], 'Pctl.**')],
                    vmin=0, vmax=100
                    ) \
                .background_gradient(
                    'RdBu',
                    subset=[(st.session_state['team_id_comp'], 'Value')],
                    gmap = team_ids_gmap[(st.session_state['team_id_comp'], 'Pctl.**')],
                    vmin=0, vmax=100
                    ) \
                .hide()

    html = stats_df.to_html(index=False, bold_rows=False)
    html = html.replace('<table', '<table style="font-size: 10pt; width: 100%; margin-bottom: 8px;"') \
        .replace('<td', '<td style="padding:2px 8px;"') \
        .replace('<th id="T_'+uuid+'_level0_col0"', '<th id="T_'+uuid+'_level0_col0" style="width: 38%"') \
        .replace('<th id="T_'+uuid+'_level0_col1"', '<th id="T_'+uuid+'_level0_col1" style="width: 31%; text-align:right"') \
        .replace('<th id="T_'+uuid+'_level0_col3"', '<th id="T_'+uuid+'_level0_col3" style="width: 31%; text-align:right"')

    for i in range(1, 5): # right-align subheader labels
        html = html.replace('<th id="T_'+uuid+'_level1_col{}"'.format(i),  '<th id="T_'+uuid+'_level1_col{}" style="text-align:right"'.format(i))

    return html
