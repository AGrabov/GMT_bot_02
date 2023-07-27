# live_trading.py
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from email import message
from pickletools import optimize
import subprocess
import backtrader as bt
from ccxtbt import CCXTStore
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
import argparse


# Settings
target_coin = 'GMT'
base_currency = 'USDT'
symbol = target_coin + base_currency
timeframe = bt.TimeFrame.Minutes
compression = 5  # For live trading, you typically want to use smaller timeframes
optimized = False

# Notifier
tg_chat_id = api_config.TG_BOT_ID
tg_bot_api = api_config.TG_BOT_API
notifier = TGnotify.TG_Notifier(tg_bot_api, tg_chat_id)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run live trading with the optimized "best_params".')
parser.add_argument('--optimized', type=bool, default=False, help='Whether to use optimized parameters')

if optimized:
    # At the beginning of the script
    try:
        with open('best_params.json', 'r') as f:
            best_params = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading best parameters: {e}")
        asyncio.run(notifier.send_message(f"Error loading best parameters: {e}"))
        # Use the default parameters from the strategy
        best_params = (
            HeikinAshiStrategy.params.fast_ema,
            HeikinAshiStrategy.params.slow_ema,
            HeikinAshiStrategy.params.hma_length,
            HeikinAshiStrategy.params.atr_period,
            HeikinAshiStrategy.params.atr_threshold,
            HeikinAshiStrategy.params.dmi_length,            
            HeikinAshiStrategy.params.dmi_threshold,
            HeikinAshiStrategy.params.cmo_period,
            HeikinAshiStrategy.params.cmo_threshold,
            HeikinAshiStrategy.params.volume_factor_perc,
            HeikinAshiStrategy.params.ta_threshold,
            HeikinAshiStrategy.params.mfi_period,
            HeikinAshiStrategy.params.mfi_level,
            HeikinAshiStrategy.params.mfi_smooth,
            HeikinAshiStrategy.params.sl_percent,
            HeikinAshiStrategy.params.kama_period,
            HeikinAshiStrategy.params.dma_period,
            HeikinAshiStrategy.params.dma_gainlimit,
            HeikinAshiStrategy.params.dma_hperiod,
            HeikinAshiStrategy.params.fast_ad,
            HeikinAshiStrategy.params.slow_ad,
            HeikinAshiStrategy.params.fastk_period,
            HeikinAshiStrategy.params.fastd_period,
            HeikinAshiStrategy.params.fastd_matype,
            HeikinAshiStrategy.params.mama_fastlimit,
            HeikinAshiStrategy.params.mama_slowlimit,
            HeikinAshiStrategy.params.apo_fast,
            HeikinAshiStrategy.params.apo_slow,
            HeikinAshiStrategy.params.apo_matype,
        )  # Retrieve default values from the strategy class

else:
    # Use the default parameters from the strategy
        best_params = (
            HeikinAshiStrategy.params.fast_ema,
            HeikinAshiStrategy.params.slow_ema,
            HeikinAshiStrategy.params.hma_length,
            HeikinAshiStrategy.params.atr_period,
            HeikinAshiStrategy.params.atr_threshold,
            HeikinAshiStrategy.params.dmi_length,            
            HeikinAshiStrategy.params.dmi_threshold,
            HeikinAshiStrategy.params.cmo_period,
            HeikinAshiStrategy.params.cmo_threshold,
            HeikinAshiStrategy.params.volume_factor_perc,
            HeikinAshiStrategy.params.ta_threshold,
            HeikinAshiStrategy.params.mfi_period,
            HeikinAshiStrategy.params.mfi_level,
            HeikinAshiStrategy.params.mfi_smooth,
            HeikinAshiStrategy.params.sl_percent,
            HeikinAshiStrategy.params.kama_period,
            HeikinAshiStrategy.params.dma_period,
            HeikinAshiStrategy.params.dma_gainlimit,
            HeikinAshiStrategy.params.dma_hperiod,
            HeikinAshiStrategy.params.fast_ad,
            HeikinAshiStrategy.params.slow_ad,
            HeikinAshiStrategy.params.fastk_period,
            HeikinAshiStrategy.params.fastd_period,
            HeikinAshiStrategy.params.fastd_matype,
            HeikinAshiStrategy.params.mama_fastlimit,
            HeikinAshiStrategy.params.mama_slowlimit,
            HeikinAshiStrategy.params.apo_fast,
            HeikinAshiStrategy.params.apo_slow,
            HeikinAshiStrategy.params.apo_matype,
        )  # Retrieve default values from the strategy class

# Create a new backtrader instance
cerebro = bt.Cerebro(quicknotify=True, runonce=False)

# Add your strategy
cerebro.addstrategy(HeikinAshiStrategy,
        fast_ema=best_params[0],
        slow_ema=best_params[1],
        hma_length=best_params[2],
        atr_period=best_params[3],
        atr_threshold=best_params[4],
        dmi_length=best_params[5],        
        dmi_threshold=best_params[6],
        cmo_period=best_params[7],
        cmo_threshold=best_params[8],
        volume_factor_perc=best_params[9],
        ta_threshold=best_params[10],
        mfi_period=best_params[11],
        mfi_level=best_params[12],
        mfi_smooth=best_params[13],
        sl_percent=best_params[14],
        kama_period=best_params[15],
        dma_period=best_params[16],
        dma_gainlimit=best_params[17],
        dma_hperiod=best_params[18],
        fast_ad=best_params[19],
        slow_ad=best_params[20],
        fastk_period=best_params[21],
        fastd_period=best_params[22],
        fastd_matype=best_params[23],
        mama_fastlimit=best_params[24],
        mama_slowlimit=best_params[25],
        apo_fast=best_params[26],
        apo_slow=best_params[27],
        apo_matype=best_params[28],    

    )   

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
    f"STARTING LIVE TRADING!\n"
    f"\n"
    f"Time difference with Binance server: {time_difference} ms"))


# create a timezone object for your timezone
kiev_tz = pytz.timezone('Europe/Kiev')
t = time.time()
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
    tradelist = strat.analyzers.trade_list.get_analysis()

    stats0 = pd.DataFrame(tradeanalyzer, index=[0])
    stats1 = pd.DataFrame(sqn, index=[0])
    stats2 = pd.DataFrame(returns, index=[0])
    stats3 = pd.DataFrame(drawdown, index=[0])
    # stats4 = pd.DataFrame(tradelist, index=[0])
    all_stats = [stats0,stats1,stats2,stats3] #,stats4]

    strategySummary = pd.concat(all_stats, axis=1)

except (KeyboardInterrupt, SystemExit, StopIteration, InterruptedError):
    print("Interrupted by user")
    asyncio.run(notifier.send_message(f"LIVE TRADING STOPTED!\n"
                                      f"___________________________\n"
                                      f"Interrupted by user"))
    
except (subprocess.CalledProcessError, subprocess.TimeoutExpired, subprocess.SubprocessError):
    print("Strategy execution timed out")
    asyncio.run(notifier.send_message(f"LIVE TRADING STOPTED!\n"
                                      f"___________________________\n"
                                      f"Strategy execution stopped"))
    
finally:
    # This code will be executed whether an exception occurs or not
    strategySummary.to_csv('all_stats.csv')

    # Print out the trade list
    print (tabulate(trade_list, headers="keys", tablefmt="pipe", missingval="?"))
    print()
    print()

    # Closing the notifier connections
    asyncio.run(notifier.close())

    cerebro.plot()
