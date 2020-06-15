import numpy as np
import pandas as pd
import multiprocessing as mp
from datetime import datetime
from collections import defaultdict
import os

#Read Data
os.chdir('C:\\Users\\Wei Fong\\Desktop')
df = pd.read_csv('C:\\Users\\Wei Fong\\Desktop\\order_brush_order.csv')
df['event_time'] = pd.to_datetime(df['event_time'])
df.info()

#Filter out stores with 2 or less orders
store_ser = df.groupby(['shopid']).size()
shops_to_check = store_ser[store_ser > 3]

#Sort remaining stores by chronological order
df = df[df['shopid'].isin(shops_to_check.index)]
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
df = pd.read_csv('C:\\Users\\Wei Fong\\Desktop\\order_brush_order.csv')
df = df[df['shopid'].isin(shops_to_check.index)]
df = df.sort_values(by='event_time')
df.set_index(['shopid','event_time'], inplace = True)

sus_userid = df.loc[multi_index]
sus_userid.reset_index(['shopid','event_time'], inplace=True)
sus_userid['shopid'] = sus_userid['shopid'].astype(str)
sus_userid['userid'] = sus_userid['userid'].astype(str)

#Clean up data of suspicious shops
result = defaultdict(list)

for i in range(len(sus_userid)):
    result[sus_userid['shopid'][i]].append(sus_userid['userid'][i])



