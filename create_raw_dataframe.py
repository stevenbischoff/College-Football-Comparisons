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

# Globals
FIRST_YEAR = 2014 # 2014 is first year advanced stats are good. 2004 otherwise (except ToP)
LAST_YEAR = 2023
SUFFIX = '_opp'

si_na = SimpleImputer()
si_zero = SimpleImputer(missing_values=0)

def process_game_stats_df():

    # Compile game_stats_df from year csv's
    game_stats_df = pd.DataFrame()
    for year in range(FIRST_YEAR, LAST_YEAR+1):
        game_stats_df_year = pd.read_csv('static/team_game_stats_{}.csv'.format(year), low_memory=False)
        last_reg_week = game_stats_df_year.loc[game_stats_df_year['season_type']=='regular', 'week'].max()
        game_stats_df_year.loc[game_stats_df_year['season_type']=='postseason', 'week'] += last_reg_week
        game_stats_df = pd.concat([game_stats_df, game_stats_df_year]).reset_index(drop=True)

    # Create team_id column, set index
    game_stats_df['team_id'] = game_stats_df['team'] + ' ' + game_stats_df['season'].astype(str)
    game_stats_df = game_stats_df.set_index('team_id', drop=True)
    # Drop Akron, Buffalo 2022. Many NA values
    game_stats_df = game_stats_df[~game_stats_df['fourthDownEff'].isna()]
    # Create integer columns from strings
    game_stats_df[['passingCompletions', 'passingAttempts']] = game_stats_df[
        'completionAttempts'].str.split('-', expand=True).astype('int')
    game_stats_df[['thirdDownConversions', 'thirdDownAttempts']] = game_stats_df[
        'thirdDownEff'].str.replace('--','-').str.split('-', expand=True).astype('int')
    game_stats_df[['fourthDownConversions', 'fourthDownAttempts']] = game_stats_df[
        'fourthDownEff'].str.replace('--','-').str.split('-', expand=True).astype('int')
    game_stats_df = game_stats_df.drop(columns=['completionAttempts', 'thirdDownEff', 'fourthDownEff'])

    return game_stats_df

def process_total_game_stats_df(game_stats_df, numeric_cols): # game_stats_df with opponent (defensive) stats

    total_game_stats_df = game_stats_df.join(game_stats_df.groupby('game_id')[numeric_cols].sum(), 
                                             on='game_id', how='left', rsuffix=SUFFIX)
    for col in numeric_cols:
        col_opp = col + SUFFIX
        total_game_stats_df[col_opp] = total_game_stats_df[col_opp] - total_game_stats_df[col]

    # Drop columns with many NA values
    total_game_stats_df = total_game_stats_df.dropna(axis=1, thresh=(len(total_game_stats_df)-90))
    # Prepare to sum season stats and divide by # of games
    total_game_stats_df['games'] = 1

    return total_game_stats_df

def process_games_df():
    # Load data
    games_df = pd.read_csv('static/game_info_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR), low_memory=False)
    games_df = games_df[games_df['season'] >= FIRST_YEAR].reset_index(drop=True)
    # Create team_id columns
    games_df['home_team_id'] = games_df['home_team'] + ' ' + games_df['season'].astype(str)
    games_df['away_team_id'] = games_df['away_team'] + ' ' + games_df['season'].astype(str)
    return games_df

def process_team_df():    
    team_df = pd.read_csv('static/fbs_teams_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    team_df = team_df[team_df['season'] >= FIRST_YEAR].reset_index(drop=True)
    return team_df

def process_opp_df(): # calls process_game_stats_df(), process_total_game_stats_df()

    game_stats_df = process_game_stats_df()

    # Create initial numeric columns    
    numeric_cols = list(game_stats_df.select_dtypes(include='number'))
    numeric_cols = [col for col in numeric_cols if col not in ['game_id','season', 'week']]

    total_game_stats_df = process_total_game_stats_df(game_stats_df, numeric_cols)    

    # Extend numeric columns (with '_opp')
    numeric_cols.extend([col + SUFFIX for col in numeric_cols])
    numeric_cols = list(total_game_stats_df.select_dtypes(include='number'))
    numeric_cols = [col for col in numeric_cols if col not in ['game_id','season','week']]

    # Impute NAs to total_game_stats_df
    total_game_stats_df[numeric_cols] = si_na.fit_transform(total_game_stats_df[numeric_cols])

    # Sum over season stats
    sum_df = total_game_stats_df.sort_values('week').groupby(['team_id'])[numeric_cols].apply(
        lambda x: x.expanding().sum())
    sum_df.index = sum_df.index.droplevel(1)

    # Get end-of-season total stats
    last_week_list = []
    for team_id in sum_df.index.unique():
        if team_id in team_ids:
            team_season_df = sum_df.loc[team_id]
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

    return opp_df

def process_pg_df(): # calls: process_games_df()

    games_df = process_games_df() # used to add point data
    
    # Load data
    season_df = pd.read_csv('static/team_season_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    season_df = season_df[season_df['season'] >= FIRST_YEAR].reset_index(drop=True)
    # Add team_id
    season_df['team_id'] = season_df['team'] + ' ' + season_df['season'].astype(str)
    # Pivot season_df, making 'stat_name' values the new columns
    season_df = pd.pivot_table(season_df, index=['team_id'], columns=['stat_name'], values=['stat_value'])
    season_df.columns = season_df.columns.droplevel()

    # Drop short 2020 COVID seasons
    season_df = season_df[season_df['games'] > 6] # All 

    # Get points data from games_df
    season_df['points'] = None
    for team_id, row in season_df.iterrows():
        
        home_games = games_df.loc[games_df['home_team_id']==team_id]
        away_games = games_df.loc[games_df['away_team_id']==team_id]
        
        team_home_points = home_games['home_points'].sum()
        team_away_points = away_games['away_points'].sum()
        team_total_points = team_home_points + team_away_points    
        season_df.loc[team_id, 'points'] = team_total_points

    # Calculate per-game stats
    for col in season_df.columns:
        if col != 'games':
            season_df[col + '/game'] = season_df[col]/season_df['games']

    # Impute NAs
    season_df[season_df.columns] = si_na.fit_transform(season_df)

    # Impute 0s where required
    season_df.loc[season_df['penalties'] <= 20, ['penalties', 'penalties/game']] = 0
    season_df[['passingTDs','passingTDs/game','penalties','penalties/game']] = si_zero.fit_transform(
        season_df[['passingTDs','passingTDs/game','penalties','penalties/game']])

    # Get per-game stats
    pg_df = season_df[[col for col in season_df.columns if '/game' in col]]

    # Calculate some additional stats
    pg_df['rushingPct'] = pg_df['rushingAttempts/game']/(pg_df['rushingAttempts/game'] + pg_df['passAttempts/game'])
    pg_df['rushingYardsPct'] = pg_df['rushingYards/game']/pg_df['totalYards/game']
    pg_df['completionPct'] = pg_df['passCompletions/game']/pg_df['passAttempts/game']
    pg_df['rushingYards/attempt'] = pg_df['rushingYards/game']/pg_df['rushingAttempts/game']
    pg_df['passingYards/attempt'] = pg_df['netPassingYards/game']/pg_df['passAttempts/game']
    pg_df['passingYards/completion'] = pg_df['netPassingYards/game']/pg_df['passCompletions/game']
    pg_df['thirdDownPct'] = pg_df['thirdDownConversions/game']/pg_df['thirdDowns/game']
    pg_df['fourthDownPct'] = pg_df['fourthDownConversions/game']/pg_df['fourthDowns/game']
    # Possession time in seconds/game to ratio
    pg_df['possessionTime/game'] /= 3600

    return pg_df

def process_advanced_stats_df():
    # Load data
    advanced_stats_df = pd.read_csv('static/team_advanced_season_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    # Create team_id
    advanced_stats_df['team_id'] = advanced_stats_df['team'] + ' ' + advanced_stats_df['season'].astype(str)
    advanced_stats_df = advanced_stats_df.set_index(['team_id'])
    # limit to 2014-2023 FBS teams
    advanced_stats_df = advanced_stats_df.loc[advanced_stats_df.index.isin(team_ids)]
    # Calculate some additional stats
    advanced_stats_df['o_plays/drive'] = advanced_stats_df['o_plays']/advanced_stats_df['o_drives']
    advanced_stats_df['d_plays/drive'] = advanced_stats_df['d_plays']/advanced_stats_df['d_drives']
    advanced_stats_df['o_field_position_average_start'] = 100 - advanced_stats_df['o_field_position_average_start']
    advanced_stats_df['d_field_position_average_start'] = 100 - advanced_stats_df['d_field_position_average_start']

    return advanced_stats_df
    
def main():

    ## Auxiliary dataset
    team_df = process_team_df()
    global team_ids # used in opp, advanced functions to identify FBS teams in year range
    team_ids = team_df['team_id'].values    

    ## Primary datasets
    opp_df = process_opp_df()
    pg_df = process_pg_df()   
    advanced_stats_df = process_advanced_stats_df()
   
    ## Join and store primary datasets using keys from load_columns
    df_combined = pg_df.join(advanced_stats_df, how='inner').drop(columns=['team', 'season', 'conference'])
    df_combined = df_combined.join(opp_df, how='inner')

    # All
    df_combined[list(X_columns.keys())].to_csv('static/raw_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_combined[list({**o_normal_columns, **d_normal_columns, **other_columns}.keys())
                ].to_csv('static/raw_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    # Offense
    df_combined[list({**o_normal_columns, **o_advanced_columns}.keys())
                ].to_csv('static/raw_offense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_combined[list(o_normal_columns.keys())
                ].to_csv('static/raw_offense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    # Defense
    df_combined[list({**d_normal_columns, **d_advanced_columns}.keys())
                ].to_csv('static/raw_defense_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))
    df_combined[list(d_normal_columns.keys())
                ].to_csv('static/raw_defense_no_adv_team_stats_{}_{}.csv'.format(FIRST_YEAR, LAST_YEAR))

if __name__ == '__main__':
    main()
