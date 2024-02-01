import pandas as pd
import numpy as np
from cfbd.rest import ApiException

from config import *
    
first_year = 2014
last_year = 2023

df_list = []
for year in range(first_year, last_year+1):
    print(year)
    df_season_list = []

    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    try:
        api_teams = api_instance.get_team_records(year=year)
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    df_temp = pd.DataFrame.from_records([team.to_dict() for team in api_teams])
    df = pd.concat([df_temp[['team','year']], df_temp['total'].apply(pd.Series)], axis=1)

    df_list.append(df)

df_records_tot = pd.concat(df_list).reset_index(drop=True)
df_records_tot['team_id'] = df_records_tot['team'] + ' ' + df_records_tot['year'].astype(str)
df_records_tot.to_csv('static/team_records_{}_{}.csv'.format(first_year, last_year),
                      index=False)
