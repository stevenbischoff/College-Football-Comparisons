import pandas as pd
import cfbd
from cfbd.rest import ApiException

from config import *

division = 'fbs'

first_year = 2014
last_year = 2023
df_list = []
for year in range(first_year, last_year+1):
    print(year)
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    
    try:
        api_games = api_instance.get_games(year=year, division=division,
                                           season_type='regular')
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    df_reg = pd.DataFrame.from_records([game.to_dict() for game in api_games])
    df_reg['season_type'] = 'regular'

    try:
        api_games = api_instance.get_games(year=year, division=division,
                                           season_type='postseason')
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    df_post = pd.DataFrame.from_records([game.to_dict() for game in api_games])
    df_post['season_type'] = 'postseason'

    df = pd.concat([df_reg, df_post]).reset_index(drop=True)

    df_list.append(df)
    
df_tot = pd.concat(df_list).reset_index(drop=True)
df_tot.to_csv('../static/game_info_{}_{}.csv'.format(first_year, last_year),
              index=False)
