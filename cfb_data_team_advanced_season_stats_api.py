import pandas as pd
import cfbd
from cfbd.rest import ApiException

from config import *

first_year = 2004
last_year = 2023
df_list = []
for year in range(first_year, last_year+1):
    print(year)

    api_instance = cfbd.StatsApi(cfbd.ApiClient(configuration))
    try:
        api_teams = api_instance.get_advanced_team_season_stats(
            year=year
            )
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    df = pd.DataFrame([team.to_dict() for team in api_teams])
    df_list.append(df)

df = pd.concat(df_list).reset_index(drop=True)

offense = pd.DataFrame(df['offense'].to_dict()).T
defense = pd.DataFrame(df['defense'].to_dict()).T

for col in offense.columns:
    try:
        offense['o_'+col] = pd.to_numeric(offense[col])
    except:
        col_df = pd.DataFrame(offense[col].to_dict()).T
        col_df.columns = ['o_'+col+'_'+subcol for subcol in col_df.columns]

        offense = pd.concat([offense, col_df], axis=1)

    offense = offense.drop(columns=[col])

for col in defense.columns:
    try:
        defense['d_'+col] = pd.to_numeric(defense[col])
    except:
        col_df = pd.DataFrame(defense[col].to_dict()).T
        col_df.columns = ['d_'+col+'_'+subcol for subcol in col_df.columns]

        defense = pd.concat([defense, col_df], axis=1)

    defense = defense.drop(columns=[col])

df = pd.concat([pd.concat([df, offense], axis=1), defense], axis=1)
df = df.drop(columns=['offense','defense'])
    
df.to_csv('static/team_advanced_season_stats_{}_{}.csv'.format(first_year, last_year),
          index=False)
