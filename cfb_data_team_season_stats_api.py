import pandas as pd
from cfbd.rest import ApiException

from config import *

first_year = 2014
last_year = 2023

df_list = []
for year in range(first_year, last_year+1): # 2001 first possible, 2004 first good
    print(year)
    api_instance = cfbd.StatsApi(cfbd.ApiClient(configuration))
    try:
        api_stats = api_instance.get_team_season_stats(year=year)
    except ApiException as e:
        print("Exception when calling StatsApi->get_team_season_stats: %s\n" % e)

    df = pd.DataFrame.from_records([stat.to_dict() for stat in api_stats])

    df_list.append(df)

df_tot = pd.concat(df_list).reset_index(drop=True)
df_tot.to_csv('static/team_season_stats_{}_{}.csv'.format(first_year, last_year),
              index=False)
          
