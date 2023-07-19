# indicators\ta_patterns_02.py

import backtrader as bt
from matplotlib.pyplot import plot
import numpy as np
from collections import deque

class CustomIndicator(bt.Indicator):
    lines = ('custom_indicator',)
    plotinfo = dict(plot=False)  # Do not plot 'custom_indicator'

    def __init__(self, pattern, data, penetration=None, buffer_length=3):
        self.pattern = pattern
        self.data = data
        self.penetration = penetration
        self.buffer = deque(maxlen=buffer_length)
        super().__init__()

        # Call the TA-Lib function with the data
        if self.penetration is not None:
            self.pattern_value = self.pattern(self.data.open, self.data.high, self.data.low, self.data.close, penetration=self.penetration)
        else:
            self.pattern_value = self.pattern(self.data.open, self.data.high, self.data.low, self.data.close)

    def next(self):
        # Assign the latest result to the line object if it's not NaN
        if not np.isnan(self.pattern_value[-1]) :
            self.lines.custom_indicator[0] = self.pattern_value[-1]
            self.buffer.append(self.lines.custom_indicator[0])  # Add the value to the buffer
            # if (self.pattern_value[-1] != 0):
            #     # Print the recognized pattern and its value
            #     print(f"{bt.num2date(self.data.datetime[0])}\t pattern: {self.pattern.__name__}, Value: {self.lines.custom_indicator[0]}")

    def get_buffer_sum(self):
        return sum(self.buffer)

class TaPatterns(bt.Indicator):
    lines = ('signal',)

    params = dict(
        patterns=[(bt.talib.CDLTRISTAR, None),
                (bt.talib.CDLTHRUSTING, None),
                (bt.talib.CDLTASUKIGAP, None),
                (bt.talib.CDLTAKURI, None),
                (bt.talib.CDLSTICKSANDWICH, None),
                (bt.talib.CDLSTALLEDPATTERN, None),
                (bt.talib.CDLSPINNINGTOP, None),
                (bt.talib.CDLSHORTLINE, None),
                (bt.talib.CDLSHOOTINGSTAR, None),
                (bt.talib.CDLSEPARATINGLINES, None),
                (bt.talib.CDLRICKSHAWMAN, None),                
                (bt.talib.CDLONNECK, None),
                (bt.talib.CDLMORNINGSTAR, 0.5),
                (bt.talib.CDLMORNINGDOJISTAR, 0.5),
                (bt.talib.CDLMATHOLD, 0.75),
                (bt.talib.CDLMATCHINGLOW, None),
                (bt.talib.CDLMARUBOZU, None),
                (bt.talib.CDLLONGLINE, None),
                (bt.talib.CDLLONGLEGGEDDOJI, None),
                (bt.talib.CDLLADDERBOTTOM, None),
                (bt.talib.CDLKICKINGBYLENGTH, None),                
                (bt.talib.CDLINNECK, None),
                (bt.talib.CDLHOMINGPIGEON, None),
                (bt.talib.CDLHIKKAKEMOD, None),
                (bt.talib.CDLHIKKAKE, None),
                (bt.talib.CDLHIGHWAVE, None),
                (bt.talib.CDLHARAMICROSS, None),
                (bt.talib.CDLHARAMI, None),
                (bt.talib.CDLHANGINGMAN, None),
                (bt.talib.CDLGRAVESTONEDOJI, None),
                (bt.talib.CDLGAPSIDESIDEWHITE, None),
                (bt.talib.CDLGAPSIDESIDEWHITE, None),
                (bt.talib.CDLEVENINGSTAR, 0.5),
                (bt.talib.CDLEVENINGDOJISTAR, 0.5),                
                (bt.talib.CDLDRAGONFLYDOJI, None),
                (bt.talib.CDLDOJISTAR, None),
                (bt.talib.CDLDOJI, None),
                (bt.talib.CDLDARKCLOUDCOVER, 0.75),
                (bt.talib.CDLCOUNTERATTACK, None),
                (bt.talib.CDLCONCEALBABYSWALL, None),
                (bt.talib.CDLCLOSINGMARUBOZU, None),
                (bt.talib.CDLBREAKAWAY, None),
                (bt.talib.CDLBELTHOLD, None),
                (bt.talib.CDLADVANCEBLOCK, None),
                (bt.talib.CDLABANDONEDBABY, 0.5)],        
        threshold=0
    )

    def __init__(self):
        super().__init__()
        self.patterns = [CustomIndicator(pattern=pattern, data=self.data, penetration=penetration) for pattern, penetration in self.params.patterns]

        self.kicking = bt.talib.CDLKICKING(self.data.open, self.data.high, self.data.low, self.data.close)
        self.hammer = bt.talib.CDLHAMMER(self.data.open, self.data.high, self.data.low, self.data.close)
        self.piercing = bt.talib.CDLPIERCING(self.data.open, self.data.high, self.data.low, self.data.close)
        self.engulfing = bt.talib.CDLENGULFING(self.data.open, self.data.high, self.data.low, self.data.close)
        self.inv_hammer = bt.talib.CDLINVERTEDHAMMER(self.data.open, self.data.high, self.data.low, self.data.close)


    def next(self):
        # Sum up the actual pattern values
        self.lines.signal[0] = sum(ci.get_buffer_sum() for ci in self.patterns)
        # if self.lines.signal[0] != 0:
        #     print(f"Signal: {self.lines.signal[0]}")

    def strong_buy(self):
        return self.kicking[0] == 100 or \
               self.hammer[0] == 100 or \
               self.piercing[0] == 100 or \
               self.engulfing[0] == 100 or \
               self.inv_hammer[0] == 100
    
    def strong_sell(self):
        return self.kicking[0] == -100 or \
               self.hammer[0] == -100 or \
               self.piercing[0] == -100 or \
               self.engulfing[0] == -100 or \
               self.inv_hammer[0] == -100

    def signal_buy(self):
        return (self.lines.signal[0] > self.params.threshold) or self.strong_buy()
    
    def signal_sell(self):
        return (self.lines.signal[0] < -self.params.threshold) or self.strong_sell()
    
    def signal_stop_buy(self):
        return (self.lines.signal[0] < 0) or self.strong_sell()
    
    def signal_stop_sell(self):
        return (self.lines.signal[0] > 0) or self.strong_buy()



