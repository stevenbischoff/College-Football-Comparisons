import pandas as pd
import cfbd
from cfbd.rest import ApiException

from config import *

first_year = 2004
last_year = 2011

df_list = []
for year in range(first_year, last_year+1):
    print(year)

    api_instance = cfbd.DrivesApi(cfbd.ApiClient(configuration))
    try:
        api_drives = api_instance.get_drives(
            year=year
            )
    except ApiException as e:
        print("Exception when calling DrivesApi->get_drives: %s\n" % e)

    df = pd.DataFrame([drive.to_dict() for drive in api_drives])
    df['season'] = year
    df_list.append(df)

df_drives = pd.concat(df_list).reset_index(drop=True)

# Manipluate ToP
df_drives[['start_minute','start_second']] = pd.DataFrame.from_records(df_drives['start_time'])
df_drives[['end_minute','end_second']] = pd.DataFrame.from_records(df_drives['end_time'])

df_drives['start_time_temp'] = (4 - df_drives['start_period'])*900 + (df_drives['start_minute']*60 + df_drives['start_second'])
df_drives['end_time_temp'] = (4 - df_drives['end_period'])*900 + (df_drives['end_minute']*60 + df_drives['end_second'])
df_drives['duration'] = df_drives['start_time_temp'] - df_drives['end_time_temp']

df_drives.loc[df_drives['duration'] < 0, 'duration'] = 0  

# Save
df_drives.to_csv('static/drives_{}_{}.csv'.format(first_year, last_year), index=False)
