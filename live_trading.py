# live_trading.py
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from email import message
import backtrader as bt
from ccxtbt import CCXTStore, CCXTFeed
import pytz
from GMT_30_strategy_02 import HeikinAshiStrategy

import TGnotify
import pandas as pd
import api_config
import os
import json
import time
import datetime as dt
import asyncio
from tabulate import tabulate
from trade_list_analyzer import trade_list
import csv
from backtrader.feeds import GenericCSVData
from data_feed import BinanceFuturesData

# Settings
target_coin = 'GMT'
base_currency = 'USDT'
symbol = target_coin + base_currency
timeframe = bt.TimeFrame.Minutes
compression = 5  # For live trading, you typically want to use smaller timeframes

# Notifier
tg_chat_id = api_config.TG_BOT_ID
tg_bot_api = api_config.TG_BOT_API
notifier = TGnotify.TG_Notifier(tg_bot_api, tg_chat_id)

# Create a new backtrader instance
cerebro = bt.Cerebro(quicknotify=True, runonce=False)

# Add your strategy
cerebro.addstrategy(HeikinAshiStrategy,)

# Add the analyzers we are interested in
cerebro.addobserver(bt.observers.DrawDown, plot=False)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(trade_list, _name='trade_list')

# absolute dir the script is in
script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, '../params.json')
with open('.\params.json', 'r') as f:
    params = json.load(f)

# Create a CCXTStore and Data Feed
config = {'apiKey': params["binance"]["apikey"],
          'secret': params["binance"]["secret"],
          'enableRateLimit': True,
          'nonce': lambda: str(int(time.time() * 1000)), 
          'type': 'swap',        
          }

store = CCXTStore(exchange='binanceusdm', currency=base_currency, config=config, retries=5) #, debug=True) #, sandbox=True)
# store.exchange.setSandboxMode(True)

broker_mapping = {
    'order_types': {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop-loss', #stop-loss for kraken, stop for bitmex
        bt.Order.StopLimit: 'stop limit'
    },
    'mappings':{
        'closed_order':{
            'key': 'status',
            'value':'closed'
        },
        'canceled_order':{
            'key': 'status',
            'value':'canceled'
        }
    }
}

broker = store.getbroker()
cerebro.setbroker(broker)
cerebro.broker.setcommission(leverage=10.0) 

# # Set the starting cash and commission
# starting_cash = 100
# cerebro.broker.setcash(starting_cash)
# cerebro.broker.setcommission(
#     automargin=True,         
#     leverage=10.0, 
#     commission=0.0004, 
#     commtype=bt.CommInfoBase.COMM_PERC,
#     stocklike=True,
# )  

server_time = store.exchange.fetch_time()
local_time = time.time() * 1000  # convert to milliseconds
time_difference = round(server_time - local_time)
print(f"Time difference between local machine and Binance server: {time_difference} ms")
asyncio.run(notifier.send_message(
    f"BOT STARTED!\n"
    f"\n"
    f"Time difference between local machine and Binance server: {time_difference} ms\n"))


t = time.time()

# create a timezone object for your timezone
kiev_tz = pytz.timezone('Europe/Kiev')
loc_time = dt.datetime.fromtimestamp(t).astimezone(tz=kiev_tz)
hist_start_date = loc_time - dt.timedelta(hours=24)
dataname = (f'{target_coin}/{base_currency}')

data_feed = store.getdata(dataname=symbol, name=dataname, #from_date=hist_start_date, 
                        timeframe=timeframe, compression=compression, ohlcv_limit=1000,
                        tz=kiev_tz, drop_newest=True)  # 

# Add the data to the cerebro engine
cerebro.adddata(data_feed)

# Add resampling
data1 = cerebro.replaydata(data_feed, timeframe=bt.TimeFrame.Minutes, compression=30, name='data1')

# Initialize strategySummary as an empty DataFrame
strategySummary = pd.DataFrame()

try:
    # Run the strategy
    strat = cerebro.run(quicknotify=True, runonce=False, tradehistory=True)[0]
    tradeanalyzer = strat.analyzers.tradeanalyzer.get_analysis()
    sqn = strat.analyzers.sqn.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trade_list = strat.analyzers.trade_list.get_analysis()

    stats0 = pd.DataFrame(tradeanalyzer, index=[0])
    stats1 = pd.DataFrame(sqn, index=[0])
    stats2 = pd.DataFrame(returns, index=[0])
    stats3 = pd.DataFrame(drawdown, index=[0])
    stats4 = pd.DataFrame(trade_list, index=[0])
    all_stats = [stats0,stats1,stats2,stats3,stats4]

    strategySummary = pd.concat(all_stats, axis=1)
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    # This code will be executed whether an exception occurs or not
    strategySummary.to_csv('all_stats.csv')

    # Print out the trade list
    print (tabulate(trade_list, headers="keys", tablefmt="psql", missingval="?"))
    print()
    print()

    # Closing the notifier connections
    asyncio.run(notifier.close())

    cerebro.plot()



