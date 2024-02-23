"""
This module gathers the relevant data from where it's been stored after API
access, cleans it a bit, transforms it to get end-of-season per-game stats,
and then stores it as "raw" dataframes.
Should be cleaned up

Author: Steve Bischoff
"""
import pandas as pd
from sklearn.impute import SimpleImputer
from load_columns import *

pd.options.mode.chained_assignment = None

# LOOK AT
# In the similar/dissimilar charts, don't display stats with significant imputation (?)

def main():
    first_year = 2014 # 2014 is first year advanced stats are good. 2004 otherwise (except ToP)
    last_year = 2023

    ### Teams
    team_df = pd.read_csv('static/fbs_teams_{}_{}.csv'.format(first_year, last_year))
    team_df = team_df[team_df['season'] >= first_year].reset_index(drop=True)

    ### Game Info
    games_df = pd.read_csv('static/game_info_{}_{}.csv'.format(first_year, last_year), low_memory=False)
    games_df = games_df[games_df['season'] >= first_year].reset_index(drop=True)
    games_df['home_team_id'] = games_df['home_team'] + ' ' + games_df['season'].astype(str)
    games_df['away_team_id'] = games_df['away_team'] + ' ' + games_df['season'].astype(str)

    ### Game Stats
    game_stats_df = pd.DataFrame()
    for year in range(first_year, last_year+1):
        game_stats_df_year = pd.read_csv('static/team_game_stats_{}.csv'.format(year), low_memory=False)
        last_reg_week = game_stats_df_year.loc[game_stats_df_year['season_type']=='regular', 'week'].max()
        game_stats_df_year.loc[game_stats_df_year['season_type']=='postseason', 'week'] += last_reg_week
        game_stats_df = pd.concat([game_stats_df, game_stats_df_year]).reset_index(drop=True)

    game_stats_df['team_id'] = game_stats_df['team'] + ' ' + game_stats_df['season'].astype(str)
    game_stats_df = game_stats_df.set_index('team_id', drop=True)

    # Extract percent stats from string columns
    game_stats_df = game_stats_df[~game_stats_df['fourthDownEff'].isna()] # dropping rows
    game_stats_df[['passingCompletions', 'passingAttempts']] = game_stats_df[
        'completionAttempts'].str.split('-', expand=True).astype('int')
    game_stats_df[['thirdDownConversions', 'thirdDownAttempts']] = game_stats_df[
        'thirdDownEff'].str.replace('--','-').str.split('-', expand=True).astype('int')
    game_stats_df[['fourthDownConversions', 'fourthDownAttempts']] = game_stats_df[
        'fourthDownEff'].str.replace('--','-').str.split('-', expand=True).astype('int')
    game_stats_df = game_stats_df.drop(columns=['completionAttempts', 'thirdDownEff', 'fourthDownEff'])

    # Add opponent stats
    suffix = '_opp'
    numeric_cols = list(game_stats_df.select_dtypes(include='number'))
    numeric_cols = [col for col in numeric_cols if col not in ['game_id','season', 'week']]
    total_game_stats_df = game_stats_df.join(game_stats_df.groupby('game_id')[numeric_cols].sum(), 
                                             on='game_id', how='left', rsuffix=suffix)
    for col in numeric_cols:
        col_opp = col + suffix
        total_game_stats_df[col_opp] = total_game_stats_df[col_opp] - total_game_stats_df[col]

    numeric_cols.extend([col + suffix for col in numeric_cols])

    total_game_stats_df = total_game_stats_df.dropna(axis=1, thresh=(len(total_game_stats_df)-90)) # dropping columns
    total_game_stats_df['games'] = 1
    numeric_cols = list(total_game_stats_df.select_dtypes(include='number'))
    numeric_cols = [col for col in numeric_cols if col not in ['game_id','season','week']]

    # Impute NAs
    si = SimpleImputer()
    total_game_stats_df[numeric_cols] = si.fit_transform(total_game_stats_df[numeric_cols])

    # Sum over season stats
    sum_df = total_game_stats_df.sort_values('week').groupby(['team_id'])[numeric_cols].apply(
        lambda x: x.expanding().sum())
    sum_df.index = sum_df.index.droplevel(1)

    # Get end-of-season total stats
    last_week_list = []
    for team_id in sum_df.index.unique():
        if team_id in team_df['team_id'].values:
            team_season_df = sum_df.loc[team_id]
            #if len(team_season_df) < 5:
                #   continue
            last_week_list.append(team_season_df[team_season_df['games']==team_season_df['games'].max()])
                
    last_sum_df = pd.concat(last_week_list)

    # Calculate end-of-season per-game stats
    for col in numeric_cols:
        if col != 'games':
            last_sum_df[col + '/game'] = last_sum_df[col]/last_sum_df['games']

    # Get Opponent (defense) stats
    opp_df = last_sum_df[last_sum_df.columns[last_sum_df.columns.str.contains('_opp')]]

    # Calculate some additional stats
    opp_df['rushingPct_opp'] = opp_df['rushingAttempts_opp/game']/(
        opp_df['rushingAttempts_opp/game'] + opp_df['passingAttempts_opp/game'])
    opp_df['rushingYardsPct_opp'] = opp_df['rushingYards_opp/game']/opp_df['totalYards_opp/game']
    opp_df['completionPct_opp'] = opp_df['passingCompletions_opp/game']/opp_df['passingAttempts_opp/game']
    opp_df['rushingYards/attempt_opp'] = opp_df['rushingYards_opp/game']/opp_df['rushingAttempts_opp/game']
    opp_df['passingYards/attempt_opp'] = opp_df['netPassingYards_opp/game']/opp_df['passingAttempts_opp/game']
    opp_df['passingYards/completion_opp'] = opp_df['netPassingYards_opp/game']/opp_df['passingCompletions_opp/game']
    opp_df['thirdDownPct_opp'] = opp_df['thirdDownConversions_opp/game']/opp_df['thirdDownAttempts_opp/game']
    opp_df['fourthDownPct_opp'] = opp_df['fourthDownConversions_opp/game']/opp_df['fourthDownAttempts_opp/game']

    ##### Drives #####
    # To fix possessionTime 2004-2011

    """drives_df = pd.read_csv('static/drives_2004_2011.csv')

    drives_df['offense_team_id'] = drives_df['offense'] + ' ' + drives_df['season'].astype(str)
    drives_df['defense_team_id'] = drives_df['defense'] + ' ' + drives_df['season'].astype(str)

    team_ToP_means = pd.DataFrame(drives_df.groupby('offense_team_id')['duration'].sum(
        )/drives_df.groupby(['offense_team_id'])['game_id'].unique().str.len())
    print(team_ToP_means)"""

    ##### Season Stats #####
    season_df = pd.read_csv('static/team_season_stats_{}_{}.csv'.format(first_year, last_year))
    season_df = season_df[season_df['season'] >= first_year].reset_index(drop=True)

    season_df['team_id'] = season_df['team'] + ' ' + season_df['season'].astype(str)
    season_df = pd.pivot_table(season_df, index=['team_id'],
                               columns=['stat_name'], values=['stat_value'])
    season_df.columns = season_df.columns.droplevel()

    # Drop bad data
    season_df = season_df.dropna(subset='rushingAttempts')
    season_df = season_df[season_df['games']<17] # Florida A&M 2004 is weird
    season_df = season_df[season_df['firstDowns']>0] # 2008 Western Kentucky
    season_df = season_df[season_df['possessionTime'] > 6000] # 2007 Western Kentucky
    season_df = season_df[season_df['games']>6] # All 2020 short COVID seasons

    # Get points and wins data from Game Info
    season_df['points'] = None
    season_df['wins'] = None
    for team_id, row in season_df.iterrows():
        
        home_games = games_df.loc[games_df['home_team_id']==team_id]
        away_games = games_df.loc[games_df['away_team_id']==team_id]
        
        team_home_points = home_games['home_points'].sum()
        team_away_points = away_games['away_points'].sum()
        team_total_points = team_home_points + team_away_points    
        season_df.loc[team_id, 'points'] = team_total_points
        
        home_wins = len(home_games[home_games['home_points'] > home_games['away_points']])
        away_wins = len(away_games[away_games['away_points'] > away_games['home_points']])
        total_wins = home_wins + away_wins
        season_df.loc[team_id, 'wins'] = total_wins 

    # Calculate per-game stats
    for col in season_df.columns:
        if col != 'games':
            season_df[col + '/game'] = season_df[col]/season_df['games']

    # Impute NAs
    season_df[season_df.columns] = si.fit_transform(season_df)

    # Impute 0s where required
    si1 = SimpleImputer(missing_values=0)
    season_df.loc[season_df['penalties'] <= 20, ['penalties', 'penalties/game']] = 0
    season_df[['passingTDs','passingTDs/game','penalties','penalties/game']] = si1.fit_transform(
        season_df[['passingTDs','passingTDs/game','penalties','penalties/game']])

    # Get per-game stats
    pg_df = season_df[[col for col in season_df.columns if '/game' in col]]

    # Get possessionTime from drives data
    """pg_df = pd.merge(pg_df, team_ToP_means, how='left', left_index=True, right_index=True)
    pg_df.loc[pg_df.index.str[-4:].astype(int)<= 2011, 'possessionTime/game'] = pg_df.loc[
        pg_df.index.str[-4:].astype(int)<= 2011, 0]
    # Get Possession Time to a rate
    pg_df['possessionTime/game'] /= 3600
    pg_df = pg_df.drop(columns=0)"""

    # Calculate some additional stats
    pg_df['rushingPct'] = pg_df['rushingAttempts/game']/(pg_df['rushingAttempts/game'] + pg_df['passAttempts/game'])
    pg_df['rushingYardsPct'] = pg_df['rushingYards/game']/pg_df['totalYards/game']
    pg_df['completionPct'] = pg_df['passCompletions/game']/pg_df['passAttempts/game']
    pg_df['rushingYards/attempt'] = pg_df['rushingYards/game']/pg_df['rushingAttempts/game']
    pg_df['passingYards/attempt'] = pg_df['netPassingYards/game']/pg_df['passAttempts/game']
    pg_df['passingYards/completion'] = pg_df['netPassingYards/game']/pg_df['passCompletions/game']
    pg_df['thirdDownPct'] = pg_df['thirdDownConversions/game']/pg_df['thirdDowns/game']
    pg_df['fourthDownPct'] = pg_df['fourthDownConversions/game']/pg_df['fourthDowns/game']

    pg_df['possessionTime/game'] /= 3600

    ##### Advanced Stats #####
    advanced_stats_df = pd.read_csv('static/team_advanced_season_stats_{}_{}.csv'.format(first_year, last_year))
    advanced_stats_df = advanced_stats_df[advanced_stats_df['season'] >= first_year].reset_index(drop=True)

    advanced_stats_df['team_id'] = advanced_stats_df['team'] + ' ' + advanced_stats_df['season'].astype(str)
    advanced_stats_df = advanced_stats_df.set_index(['team_id'])

    # limit to 2014-2023 FBS teams
    advanced_stats_df = advanced_stats_df.loc[advanced_stats_df.index.isin(team_df['team_id'])]

    # some teams have advanced stats from few games in earlier seasons
    # minimum plays was 45*8 = 360
    #advanced_stats_df = advanced_stats_df[advanced_stats_df['o_plays']>advanced_stats_df['o_plays'].min()*6.67]
    # Use only if going back to 2004

    # Calculate some additional stats
    advanced_stats_df['o_plays/drive'] = advanced_stats_df['o_plays']/advanced_stats_df['o_drives']
    advanced_stats_df['d_plays/drive'] = advanced_stats_df['d_plays']/advanced_stats_df['d_drives']
    advanced_stats_df['o_field_position_average_start'] = 100 - advanced_stats_df['o_field_position_average_start']
    advanced_stats_df['d_field_position_average_start'] = 100 - advanced_stats_df['d_field_position_average_start']

    ### Join and store
    df_combined = pg_df.join(advanced_stats_df, how='inner').drop(columns=['team', 'season', 'conference'])
    df_combined = df_combined.join(opp_df, how='inner')

    # All
    df_combined[list(X_columns.keys())].to_csv('static/raw_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_combined[list({**o_normal_columns, **d_normal_columns, **other_columns}.keys())
                ].to_csv('static/raw_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))
    # Offense
    df_combined[list({**o_normal_columns, **o_advanced_columns}.keys())
                ].to_csv('static/raw_offense_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_combined[list(o_normal_columns.keys())
                ].to_csv('static/raw_offense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))
    # Defense
    df_combined[list({**d_normal_columns, **d_advanced_columns}.keys())
                ].to_csv('static/raw_defense_team_stats_{}_{}.csv'.format(first_year, last_year))
    df_combined[list(d_normal_columns.keys())
                ].to_csv('static/raw_defense_no_adv_team_stats_{}_{}.csv'.format(first_year, last_year))

if __name__ == '__main__':
    main()
