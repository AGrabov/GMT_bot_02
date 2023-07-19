# data_feed.py

import ccxt
import pandas as pd
import backtrader as bt
from datetime import datetime
import pytz

class BinanceFuturesData(bt.feeds.PandasData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def fetch_data(cls, symbol, startdate, enddate, binance_timeframe):
        exchange = ccxt.binanceusdm({
            'rateLimit': 1200,
            'enableRateLimit': True,
        })
        exchange.load_markets()

        if enddate is None:
            enddate = datetime.now()

        timeframe_minutes = {
                '1m': 1,
                '3m': 3,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '2h': 120,
                '4h': 240,
                '1d': 1440,
            }

        # Convert startdate and enddate to timezone-aware datetime objects, if they aren't already
        if not pd.to_datetime(startdate).tzinfo:
            startdate = pd.to_datetime(startdate).tz_localize('UTC')
        else:
            startdate = pd.to_datetime(startdate)

        if not pd.to_datetime(enddate).tzinfo:
            enddate = pd.to_datetime(enddate).tz_localize('UTC')
        else:
            enddate = pd.to_datetime(enddate)

        timeframe_str = binance_timeframe
        all_data = []

        start_date = startdate  # Use the timezone-aware startdate

        while True:
            since = int(start_date.timestamp() * 1000)
            ohlcv = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe_str,
                since=since,
                limit=None,
            )

            if len(ohlcv) == 0:
                break

            df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms', utc=True)
            df.set_index('datetime', inplace=True)
            all_data.append(df)

            start_date = df.index[-1] + pd.Timedelta(minutes=timeframe_minutes[timeframe_str])

            if start_date > enddate:  # Use the timezone-aware enddate
                break

        df = pd.concat(all_data).sort_index()
        df = df.loc[startdate:enddate]  # Use the timezone-aware startdate and enddate for slicing
        df = df[~df.index.duplicated(keep='first')]  # Drop potential duplicates
        
        return df
