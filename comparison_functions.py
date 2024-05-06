import pandas as pd
import scipy.stats as stats
import streamlit as st

def get_comparison_results(nn):
    results = nn.kneighbors(st.session_state['df_transformed'].loc[st.session_state['team_id']].values.reshape(1,-1),
                            n_neighbors=st.session_state['n_comparisons']+1, # +1 since team_id is returned as closest with dist. 0
                            return_distance=True)
    indices = results[1][0][1:]
    distances = results[0][0][1:]
    return st.session_state['df_transformed'].index[indices], distances


def comparisons_to_display_df(comparisons, distances):
    schools = comparisons.str[:-5]
    seasons = comparisons.str[-4:]
    records = st.session_state['team_records'].loc[comparisons, 'record_string'].values
    sss = 1 - distances/st.session_state['max_distance'] # Statistical Similarity Score
    df = pd.DataFrame({'Rank': range(1, st.session_state['n_comparisons']+1),
                       'School': schools,
                       'Season': seasons,
                       'Record': records,
                       'SSS*': sss.round(4)},
                      index=range(1, st.session_state['n_comparisons']+1))
    return df


def get_similar_stats(pctl_threshold=15):
    stat_diffs = (st.session_state['df_standardized'].loc[st.session_state['team_id'], list(st.session_state['X_columns'].keys())
        ] - st.session_state['df_standardized'].loc[st.session_state['team_id_comp'], list(st.session_state['X_columns'].keys())]).abs().sort_values()
    return_df = pd.DataFrame(
        columns=['Statistic*', st.session_state['team_id'], 'pctl1', st.session_state['team_id_comp'], 'pctl2'])
    # Get "interesting" (i.e. extreme) similarities first
    counter = 0
    for stat in stat_diffs.index:
        if counter >= st.session_state['n_similar_stats']:
            break
        pctl1 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id'], stat])
        if pctl1 < pctl_threshold or pctl1 > 100 - pctl_threshold: 
            pctl2 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat])
            if abs(pctl1 - pctl2) <= 8: 
                return_df.loc[counter] = [st.session_state['X_columns'][stat],
                                          st.session_state['df_raw'].loc[st.session_state['team_id'], stat],
                                          round(pctl1, 2),
                                          st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],
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
                                  st.session_state['df_raw'].loc[st.session_state['team_id'], stat],
                                  round(pctl1, 2),
                                  st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],
                                  round(pctl2, 2)]
        counter += 1

    return_df.set_index('Statistic*', inplace=True)
    return return_df


def get_dissimilar_stats():
    stat_diffs = (st.session_state['df_standardized'].loc[st.session_state['team_id'], list(st.session_state['X_columns'].keys())
        ] - st.session_state['df_standardized'].loc[st.session_state['team_id_comp'], list(st.session_state['X_columns'].keys())]).abs().sort_values()
    return_df = pd.DataFrame(
        columns=['Statistic*', st.session_state['team_id'], 'pctl1', st.session_state['team_id_comp'], 'pctl2'])
    for stat in stat_diffs.index[-st.session_state['n_dissimilar_stats']:]:
        pctl1 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id'], stat])
        pctl2 = stats.percentileofscore(st.session_state['df_raw'][stat], st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat])
        return_df.loc[len(return_df)] = [st.session_state['X_columns'][stat],
                                         st.session_state['df_raw'].loc[st.session_state['team_id'], stat],
                                         round(pctl1, 2),
                                         st.session_state['df_raw'].loc[st.session_state['team_id_comp'], stat],
                                         round(pctl2, 2)]
        
    return_df.set_index('Statistic*', inplace=True)
    return return_df.iloc[::-1]
