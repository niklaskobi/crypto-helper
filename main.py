# This is a sample Python script.
import math

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import pandas as pd
import datetime

# Map asset-name to pair-name
currency_map = {
    'ADA.S': 'ADAEUR',
    'DOT.S': 'DOTEUR',
    'ETH2': 'XETHZEUR'
}
begin_ts = '1609455600'  # Thu Dec 31 2020 23:00:00, get epoch from: https://currentmillis.com/
result_path = 'data/result.csv'
ledger_data_path = 'data/ledgers.csv'
def read_csv(path):
    data_from_csv = pd.read_csv(path)
    # convert date-string into time-object
    data_from_csv['time'] = pd.to_datetime(data_from_csv['time'])
    return data_from_csv


def get_prepared_kraken_data(path):
    """ Read csv from the given path and prepare it for further actions """

    df = read_csv(path)
    # remove unused columns
    df.drop(['txid', 'refid', 'subtype', 'aclass', 'balance'], axis=1)
    # leave only 'staking' raws
    df = df.drop(df[df.type != 'staking'].index)
    # convert date string to epochs
    df['epoch'] = df['time'].astype('int64') // 1e9
    # add column with day begin ts
    df['day_start_epoch'] = df['time'].round('D').astype('int64') // 1e9
    # add column with currency pair
    df['pair'] = [currency_map.get(stak_cur) for stak_cur in df['asset']]
    # convert to numerical values
    df['epoch'] = df['epoch'].astype('int64')
    df['amount'] = df['amount'].astype('float')
    df['day_start_epoch'] = df['day_start_epoch'].astype('int64')
    # set options for output
    pd.set_option('display.max_columns', None)
    pd.set_option('float_format', '{:f}'.format)
    # get the earliest date (might be useful later)
    # start_ts = df.nsmallest(1, ['day_start_epoch']).iloc[0]['day_start_epoch']
    return df


def get_pair(pair, begin_ts, interval_sec=1440):
    """ Returns a prices from kraken-api for given pair, begin-ts and interval,
    returns dictionary with day-begin-ts and volume-weighted average price """

    req = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval_sec}&since={begin_ts}"
    response = requests.get(req)

    if response.json()["error"]:
        raise RuntimeError(f"Request price data from 'kraken' failed: {response.json()['error']}")
    else:
        # result is array of tick data arrays [int <time>, string <open>, string <high>, string <low>, string <close>,
        # string <vwap>, string <volume>, int <count>]
        result = response.json()["result"]
        # we need only time and vwap (The volume-weighted average price)
        tmp = [(block[0], block[5]) for block in result[pair]]
        d = dict(tmp)
        return d


# Function to add
def add(price_dict, ts, pair):
    try:
        return price_dict[pair][ts]
    except KeyError:
        return None


def fill_price_data(price_dict, transactions):
    """ Calculate and fill vwap- and euro-values into the dataframe """

    df = transactions
    df['vwap'] = [add(price_dict, row[0], row[1]) for row in zip(df['day_start_epoch'], df['pair'])]
    df.loc[df['vwap'] == df['vwap'], 'euro'] = df['amount'].astype(float) * df['vwap'].astype(float)
    return df


def get_prices():
    """ Aggregate price-data for all currency pairs """

    price_data = {}

    for pair in currency_map.values():
        price_data[pair] = get_pair(pair, begin_ts)

    return price_data


def test_sum():
    test_transactions = get_prepared_kraken_data('data/test_ledgers.csv')
    test_data = fill_price_data(prices, test_transactions)
    assert test_data['euro'].sum() == 86.7737888, "Should be 86.7737888"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(f"Getting price data for: {list(currency_map.keys())} since {datetime.datetime.utcfromtimestamp(int(begin_ts))} (UTC).")
    prices = get_prices()
    test_sum()
    print(f"Test passed")
    transactions = get_prepared_kraken_data(ledger_data_path)
    data = fill_price_data(prices, transactions)
    data.to_csv(result_path, index=False, columns=['time', 'txid', 'asset', 'amount', 'pair', 'vwap', 'euro'])
    # for test with default ledgers total sum should be: 86.7737888
    print(f"Total sum in euro: {data['euro'].sum()}")
    print(f"Result is saved in {result_path}")
