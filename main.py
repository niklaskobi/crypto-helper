# This is a sample Python script.
import math

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import pandas as pd
import numpy as np


# Limitations:
# Data must have a period of 1 year max.
# Days are rounded up, so 2021-01-01 11:45 -> 2021-01-01 00:00, 2021-01-01 12:45 -> 2021-01-02 00:00


def read_csv(path):
    data = pd.read_csv(path)
    # convert date-string into time-object
    data['time'] = pd.to_datetime(data['time'])
    return data


# example: filter_columns_label(columns=['A', 'B', 'C', 'D'], df)
def filterout_columns(columns, data):
    return data.drop(columns, axis=1)


currency_map = {
    'ADA.S': 'ADAEUR',
    'DOT.S': 'DOTEUR',
    'ETH2': 'ETHEUR'
}


def get_prepared_kraken_data(path):
    df = read_csv(path)
    # leave only 'staking' raws
    df = df.drop(df[df.type != 'staking'].index)
    # convert date string to epochs
    df['epoch'] = df['time'].astype('int64') // 1e9
    df['epoch'] = df['epoch'].astype('int64')
    # convert amount to int
    df['amount'] = df['amount'].astype('float')
    # add column with day begin ts
    df['day_start_epoch'] = df['time'].round('D').astype('int64') // 1e9
    df['day_start_epoch'] = df['day_start_epoch'].astype('int64')
    # add column with currency pair
    df['pair'] = [currency_map.get(stak_cur) for stak_cur in df['asset']]
    # remove some columns
    df = filterout_columns(['txid', 'refid', 'subtype', 'aclass', 'balance'], df)
    # show all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('float_format', '{:f}'.format)
    # get the earliest date
    start_ts = df.nsmallest(1, ['day_start_epoch']).iloc[0]['day_start_epoch']
    # print(start_ts)
    return df


def merge_data_and_price():
    data = get_prepared_kraken_data('data/ledgers.csv')


def get_price_data(pair, begin_ts, interval_sec=1440):
    req = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval_sec}&since={begin_ts}"
    response = requests.get(req)

    if response.json()["error"]:
        raise RuntimeError(f"Request price data from 'kraken' failed: {response.json()['error']}")
    else:
        # result is array of tick data arrays [int <time>, string <open>, string <high>, string <low>, string <close>,
        # string <vwap>, string <volume>, int <count>]
        result = response.json()["result"]
        # we need only time and vwap (The volume-weighted average price)
        tmp = [[block[0], block[5]] for block in result[pair]]
        df = pd.DataFrame(tmp, columns=['day_start_epoch', 'vwap'])
        df['day_start_epoch'] = df['day_start_epoch'].astype('int64')
        df['vwap'] = df['vwap'].astype('float')
        df['pair'] = pair
        return df


def add_pair(pair, begin_ts, transactions):
    price = get_price_data(pair=pair, begin_ts=begin_ts)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    price_ada = get_price_data(pair='ADAEUR', begin_ts='1609455600')
    transactions = get_prepared_kraken_data('data/ledgers.csv')

    # Solution with merge is cool, but works only for 1 pair
    aggr = pd.merge(transactions, price_ada, how="left", left_on=["day_start_epoch", "pair"], right_on=["day_start_epoch", "pair"])
    aggr.loc[aggr['vwap'] == aggr['vwap'], 'euro'] = aggr['amount'] * aggr['vwap']


    print(aggr)
    aggr.to_csv('result.csv')
