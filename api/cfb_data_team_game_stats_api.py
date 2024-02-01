import pandas as pd
import numpy as np
from cfbd.rest import ApiException

from config import *

def preprocess_data(api_games, year, week, season_type, df_list, df_season_list):
    
    game_ids = [game.to_dict()['id'] for game in api_games for _ in (0,1)]
    df = pd.DataFrame([game.to_dict()['teams'][i] for game in api_games for i in (0,1)])
    
    df_week_list = [pd.DataFrame(
        np.array([stat['stat'] for stat in df['stats'].iloc[i]]).reshape(1,-1),
        columns=[stat['category'] for stat in df['stats'].iloc[i]]) for i in range(len(df))]

    try:
        df1 = pd.concat(df_week_list).reset_index(drop=True)
    except:
        print(season_type + str(week))
        return
    
    df1[['team','home_away','points']] = df[['school','home_away','points']]
    df1['game_id'] = game_ids
    df1['season'] = year
    df1['week'] = week
    df1['season_type'] = season_type
    
    df_list.append(df1)
    df_season_list.append(df1)

first_year = 2014
last_year = 2014

df_list = []
for year in range(first_year, last_year+1):
    print(year)
    df_season_list = []

    season_type = 'regular'
    for week in range(1, 17):

        api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
        try:
            api_games = api_instance.get_team_game_stats(year=year, week=week,
                                                         season_type=season_type)
        except ApiException as e:
            print("Exception when calling GameApi->get_games: %s\n" % e)

        preprocess_data(api_games, year, week, season_type, df_list, df_season_list)

    season_type = 'postseason'
    for week in range(1, 4):

        api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
        try:
            api_games = api_instance.get_team_game_stats(year=year, week=week,
                                                         season_type=season_type)
        except ApiException as e:
            print("Exception when calling GameApi->get_games: %s\n" % e)

        preprocess_data(api_games, year, week, season_type, df_list, df_season_list)
        
    df_season_tot = pd.concat(df_season_list).reset_index(drop=True)
    df_season_tot.to_csv('../static/team_game_stats_{}.csv'.format(year),
              index=False)         
