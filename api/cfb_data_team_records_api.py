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
        api_records = api_instance.get_team_records(year=year)
    except ApiException as e:
        print("Exception when calling GameApi->get_games: %s\n" % e)

    
    df = pd.DataFrame.from_records([record.to_dict() for record in api_records])[['team','year','total']]
    df = df.join(pd.json_normalize(df['total'])).drop('total', axis='columns')    

    df_list.append(df)
    
df_tot = pd.concat(df_list).reset_index(drop=True)

df_tot['team_id'] = df_tot['team'] + ' ' + df_tot['year'].astype(str)

df_tot['record_string'] = df_tot['wins'].astype(str)+'-'+df_tot['losses'].astype(str)+'-'+df_tot['ties'].astype(str)

def strip_zero_ties(record_string):
    parts = record_string.split('-')
    if parts[2] == '0':
        return '-'.join(parts[:2])
    return record_string

df_tot['record_string'] = df_tot['record_string'].apply(strip_zero_ties)
df_tot = df_tot[['team_id', 'record_string']]

df_tot.to_csv('../static/team_records_{}_{}.csv'.format(first_year, last_year),
              index=False)
