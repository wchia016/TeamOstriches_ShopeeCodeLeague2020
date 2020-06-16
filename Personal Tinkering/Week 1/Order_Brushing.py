import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os

#Read Data
os.chdir('C:\\Users\\Wei Fong\\Desktop')
data = pd.read_csv('C:\\Users\\Wei Fong\\Desktop\\order_brush_order.csv')
data['event_time'] = pd.to_datetime(data['event_time'])
data.info()

#Filter out stores with 2 or less orders
store_series = data.groupby(['shopid']).size()
shops_to_check = store_series[store_series > 3]

#Sort remaining stores by chronological order
df = data[data['shopid'].isin(shops_to_check.index)]
df = df.sort_values(by='event_time')
df.set_index('event_time', inplace = True)

#Run concentrate rate check
filtered_df = df.groupby('shopid').rolling('H').count()
filtered_df['unique_user']= df.groupby('shopid').rolling('H').userid.apply(lambda x: len(np.unique(x)))
filtered_df['conc_rate'] = filtered_df['orderid'].div(filtered_df['unique_user'])

order_brush_shops = filtered_df[filtered_df['conc_rate'] >= 3].iloc[:,-1:]
order_brush_shops.reset_index('shopid',inplace=True)
event_time = order_brush_shops.index.strftime('%Y-%m-%d %H:%M:%S')
order_brush_shops.set_index(['shopid', event_time], inplace=True)

#Identify shop brushing userid
multi_index = list(order_brush_shops.index)
data = pd.read_csv('C:\\Users\\Wei Fong\\Desktop\\order_brush_order.csv')
df = data[data['shopid'].isin(shops_to_check.index)]
df = df.sort_values(by='event_time')
df.set_index(['shopid','event_time'], inplace = True)

sus_userid = df.loc[multi_index]
sus_userid.reset_index(['shopid','event_time'], inplace=True)
sus_userid['userid'] = sus_userid['userid'].astype(str)

#Clean up data of suspicious shops
result = defaultdict(list)

for i in range(len(sus_userid)):
    result[sus_userid['shopid'][i]].append(sus_userid['userid'][i])

prediction = pd.DataFrame([store_series.index, np.zeros(len(store_series), dtype=int)]).transpose()
prediction.columns = ['shopid','userid']
prediction.set_index('shopid', inplace=True)
prediction['userid'] = prediction['userid'].astype(str)

for i in sus_userid.groupby(['shopid']).size().index:
    temp = result[i]
    for j in temp:
        if len(temp) == 1:
            prediction['userid'][i] = j
        else:
            prediction['userid'][i] = '&'.join(temp)
            
compression_opts = dict(method='zip',
                        archive_name='prediction.csv')  
prediction.to_csv('out.zip', index=False,
          compression=compression_opts) 