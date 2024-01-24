import pandas as pd
from cfbd.rest import ApiException

from config import *

first_year = 2004
last_year = 2023

df_list = []
for year in range(first_year, last_year+1):
    print(year)
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
    try:
        api_teams = api_instance.get_fbs_teams(year=year)
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    df = pd.DataFrame([team.to_dict() for team in api_teams])[['id','school']]
    df['season'] = year

    df_list.append(df)

df_tot = pd.concat(df_list).reset_index(drop=True)
df_tot['team_id'] = df_tot['school'] + ' ' + df_tot['season'].astype(str)
df_tot.to_csv('static/fbs_teams_{}_{}.csv'.format(first_year, last_year),
              index=False)
