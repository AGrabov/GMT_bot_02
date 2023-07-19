# indicators\heikin_patterns_01.py

import backtrader as bt
from matplotlib.pyplot import plot

class HeikinPatterns(bt.Indicator): 
    lines = ('signal', 'stop_signal',)   
        
    def __init__(self):
        
        self.ha = bt.indicators.HeikinAshi(self.data, plot=False)
        
        self.ha_close = self.ha.lines.ha_close
        self.ha_open = self.ha.lines.ha_open
        self.ha_high = self.ha.lines.ha_high
        self.ha_low = self.ha.lines.ha_low 
        # self.lines.myline = self.ha_close - self.ha_open

    def is_falling_star(self, index=0):
        condition1 = self.ha_close[0] < self.ha_open[0]
        condition2 = (self.ha_open[0] - self.ha_low[0] > 2 * (self.ha_close[0] - self.ha_open[0]))
        condition3 = (self.ha_close[0] - self.ha_low[0]) < (self.ha_high[0] - self.ha_close[0])
        is_falling_star = condition1 and condition2 and condition3
        return is_falling_star
    
    def bullish_engulfing(self, index=0):
        condition1 = self.ha_close[0] > self.ha_open[-1]
        condition2 = (self.ha_open[0] < self.ha_close[-1])
        condition3 = self.ha_close[0] > (self.ha_open[0] + (self.ha_open[-1] - self.ha_close[-1]))
        bullish_engulfing = condition1 and condition2 and condition3
        return bullish_engulfing
    
    def bearish_engulfing(self, index=0):
        condition1 = self.ha_close[0] < self.ha_open[-1]
        condition2 = (self.ha_open[0] > self.ha_close[-1])
        condition3 = self.ha_close[0] < (self.ha_open[0] - (self.ha_close[-1] - self.ha_open[-1]))
        bearish_engulfing = condition1 and condition2 and condition3
        return bearish_engulfing
 
    def bullish_harami(self, index=0):
        condition1 = self.ha_open[-1] > self.ha_close[-1]
        condition2 = (self.ha_open[0] < self.ha_close[0])
        condition3 = self.ha_close[0] <= self.ha_open[-1]
        condition4 = self.ha_close[-1] <= self.ha_open[0]
        condition5 = (self.ha_close[0] - self.ha_open[0]) < (self.ha_open[-1] - self.ha_close[-1]) 
        bullish_harami = condition1 and condition2 and condition3 and condition4 and condition5
        return bullish_harami

    def bearish_harami(self, index=0):
        condition1 = self.ha_open[-1] < self.ha_close[-1]
        condition2 = self.ha_open[0] > self.ha_close[0]
        condition3 = self.ha_close[-1] >= self.ha_open[0]
        condition4 = self.ha_close[0] >= self.ha_open[-1]
        condition5 = (self.ha_open[0] - self.ha_close[0]) > (self.ha_close[-1] - self.ha_open[-1]) 
        bearish_harami = condition1 and condition2 and condition3 and condition4 and condition5
        return bearish_harami
    
    def bullish_hammer(self, index=0):
        сondition1 = self.ha_close[0] > self.ha_open[0]
        сondition2 = self.ha_close[0] > (self.ha_high[0] + self.ha_low[0]) / 2
        сondition3 = (self.ha_high[0] - self.ha_low[0]) > 2 * (self.ha_open[0] - self.ha_close[0])
        сondition4 = (self.ha_close[0] - self.ha_open[0]) <= 0.2 * (self.ha_high[0] - self.ha_low[0])
        bullish_hammer = сondition1 and сondition2 and сondition3 and сondition4
        return bullish_hammer

    def bearish_hanging_man(self, index=0):
        condition1 = self.ha_close[0] < self.ha_open[0]
        condition2 = self.ha_close[0] < (self.ha_high[0] + self.ha_low[0]) / 2
        condition3 = (self.ha_high[0] - self.ha_low[0]) >= 2 * (self.ha_open[0] - self.ha_close[0])
        condition4 = (self.ha_open[0] - self.ha_close[0]) <= 0.1 * (self.ha_high[0] - self.ha_low[0])
        bearish_hanging_man = condition1 and condition2 and condition3 and condition4
        return bearish_hanging_man

    def inside_bar(self, index=0):
        condition1 = self.ha_high[0] < self.ha_high[-1]
        condition2 = self.ha_low[0] > self.ha_low[-1]
        inside_bar = condition1 and condition2
        return inside_bar

    def doji(self, index=0):
        doji = abs(self.ha_close[0] - self.ha_open[0]) <= 0.1 * (self.ha_high[0] - self.ha_low[0])
        return doji

    def morning_star(self, index=0):
        condition1 = self.ha_close[-2] < self.ha_open[-2]
        condition2 = self.ha_close[-1] < self.ha_open[-1]
        condition3 = self.ha_close[0] > self.ha_open[0]
        condition4 = self.ha_close[0] > self.ha_close[-2]
        condition5 = self.ha_open[0] < self.ha_open[-2]
        morning_star = condition1 and condition2 and condition3 and condition4 and condition5
        return morning_star
    
    def evening_star(self, index=0):
        condition1 = self.ha_close[-2] > self.ha_open[-2]
        condition2 = self.ha_close[-1] > self.ha_open[-1]
        condition3 = self.ha_close[0] < self.ha_open[0]
        condition4 = self.ha_close[0] < self.ha_close[-2]
        condition5 = self.ha_open[0] > self.ha_open[-2]
        evening_star = condition1 and condition2 and condition3 and condition4 and condition5
        return evening_star
    
    def bullish_pattern(self):
        bullish_pattern = (self.bullish_engulfing() or self.bullish_hammer() or self.bullish_harami() or self.morning_star())
        return bullish_pattern
    
    def bearish_pattern(self):
        bearish_pattern = (self.bearish_engulfing() or self.bearish_hanging_man() or self.evening_star() or self.bearish_harami())
        return bearish_pattern
    
    def pattern_buy1(self):        
        condition1 = (self.bullish_hammer(-1) or self.bullish_hammer() or 
                      self.morning_star() or self.morning_star(-1) or 
                      self.bullish_harami() or self.bullish_harami(-1))
        condition2 = (self.bullish_engulfing())  
        condition3 = (self.doji() or self.doji(-1))   #self.inside_bar() or self.inside_bar(-1) or 
        pattern_buy1 = (condition1 and condition2) #and not condition3
        return pattern_buy1
    
    def pattern_sell1(self):
        condition1 = (self.evening_star(-1) or self.bearish_harami(-1) or self.is_falling_star(-1))
        condition2 = self.bearish_engulfing()
        condition3 = (self.inside_bar() or self.inside_bar(-1) or self.doji() or self.doji(-1)) # or 
        pattern_sell1 = (condition1 and condition2) and not condition3
        return pattern_sell1

    def pattern_buy2(self):        
        condition1 = (self.ha_close[0] > self.ha_open[0]) and self.bullish_engulfing()
        condition2 = (self.bullish_hammer() or                  
                      self.bullish_harami() or
                      self.morning_star() or self.morning_star(-1))
        # condition3 = self.bearish_pattern()
        pattern_buy2 = (condition1 and condition2)
        return pattern_buy2
    
    def pattern_sell2(self):
        condition1 = (self.ha_close[0] < self.ha_open[0])
        condition2 = (self.bearish_engulfing() or 
                      self.bearish_hanging_man() or 
                      self.bearish_harami()) and \
                     (self.is_falling_star() or self.evening_star())
        condition3 = (self.inside_bar() or self.inside_bar(-1)) #) # or self.doji()) #) # or self.bullish_pattern())
        pattern_sell2 = (condition1 and condition2) and not condition3
        return pattern_sell2

   
    def pattern_buy3(self):        
        condition1 = ((self.ha_close[0] - self.ha_open[0]) > (self.ha_close[-1] - self.ha_open[-1])) and \
                      (self.ha_high[0] > self.ha_high[-1]) and (self.ha_low[0] > self.ha_low[-1]) 
        # condition2 = (self.ha_open[0] - self.ha_low[0]) <= 0.05 * (self.ha_high[0] - self.ha_low[0]) and \
        #               (self.ha_close[0] - self.ha_open[0]) >= (self.ha_high[0] - self.ha_low[0]) / 2
        condition2 = (self.ha_open[0] <= self.ha_low[0]) and (self.ha_open[-1] <= self.ha_low[-1])
        condition3 = (self.ha_close[0] > self.ha_open[0]) and (self.ha_close[-1] > self.ha_open[-1])
        condition4 = ((self.ha_close[0] - self.ha_open[0]) > ((self.ha_high[0] - self.ha_low[0]) / 2))
        condition5 = (self.doji() or self.inside_bar()) or (self.doji(-1) or self.inside_bar(-1)) or self.bearish_pattern()
        pattern_buy3 = (condition1 and condition2 and condition3 and condition4) and not condition5
        return pattern_buy3
    
    def pattern_sell3(self):
        condition1 = ((self.ha_open[0] - self.ha_close[0]) > (self.ha_open[-1] - self.ha_close[-1])) and \
                      (self.ha_high[0] < self.ha_high[-1]) and (self.ha_low[0] < self.ha_low[-1])
        # condition2 = (self.ha_high[0] - self.ha_open[0]) <= 0.05 * (self.ha_high[0] - self.ha_low[0]) and \
        #               (self.ha_open[0] - self.ha_close[0]) >= (self.ha_high[0] - self.ha_low[0]) / 2
        condition2 = (self.ha_high[0] <= self.ha_open[0]) and (self.ha_high[-1] <= self.ha_open[-1])
        condition3 = (self.ha_open[0] > self.ha_close[0]) #and (self.ha_open[-1] > self.ha_close[-1])
        condition4 = ((self.ha_open[0] - self.ha_close[0]) > ((self.ha_high[0] - self.ha_low[0]) / 2))
        condition5 = (self.doji() or self.inside_bar()) or (self.doji(-1) or self.inside_bar(-1)) or self.bullish_pattern()
        pattern_sell3 = (condition1 and condition2 and condition3 and condition4) and not condition5
        return pattern_sell3
    
    def pattern_buy4(self):
        condition1 = (self.ha_open[0] < self.ha_close[0]) and (self.ha_open[-1] < self.ha_close[-1])
        condition2 = (self.ha_close[0] - self.ha_open[0]) > (self.ha_high[0] - self.ha_low[0]) / 2
        condition3 = ((self.ha_high[-1] - self.ha_low[-1]) - abs(self.ha_close[-1] - self.ha_open[-1])) > abs(self.ha_close[-1] - self.ha_open[-1])
        # condition4 = (self.ha_open[0] - self.ha_low[0]) <= 0.05 * (self.ha_high[0] - self.ha_low[0])
        condition4 = (self.ha_open[0] == self.ha_low[0]) and (self.ha_open[-2] < self.ha_close[-2])
        condition5 = (self.ha_open[0] > self.ha_open[-1]) and (self.ha_high[0] > self.ha_high[-1]) and (self.ha_low[0] > self.ha_low[-1])
        condition6 = (self.ha_open[-1] > self.ha_open[-2]) and (self.ha_high[-1] > self.ha_high[-2])
        condition7 = (self.ha_close[0] - self.ha_open[0]) > (self.ha_close[-1] - self.ha_open[-1])
        pattern_buy4 = (condition1 and condition2 and condition3 and condition4 and condition5 and condition6 and condition7)
        return pattern_buy4
    
    def pattern_buy5(self):        
        condition1 = ((self.ha_close[0] > self.ha_open[0]) and (self.ha_close[-1] < self.ha_open[-1]) and (self.ha_close[-2] < self.ha_open[-2]))
        condition2 = (self.ha_open[0] - self.ha_low[0]) < (self.ha_high[0] - self.ha_close[0])
        condition3 = (self.ha_high[0] > self.ha_high[-1])        
        condition5 = (self.doji() or self.inside_bar())
        pattern_buy5 = (condition1 and condition2 and condition3) and not condition5
        return pattern_buy5

    
    def pattern_buy_all(self):
        return self.pattern_buy1() or self.pattern_buy2() or self.pattern_buy3() or self.pattern_buy4()
    
    def pattern_sell_all(self):
        return self.pattern_sell1() or self.pattern_sell2() or self.pattern_sell3()
    
    def pattern_stop_buy1(self):
        condition1 = (self.ha_close[0] < self.ha_open[0])
        condition2 = (self.bearish_engulfing() or self.bearish_harami() or self.bearish_hanging_man())
        condition3 = (self.doji(-1) or self.doji()) #and (self.inside_bar(-1) or self.inside_bar(-2))
        pattern_stop_buy1 = condition1 and condition2 and condition3
        return pattern_stop_buy1
    
    def pattern_stop_sell1(self):
        condition1 = (self.ha_close[0] > self.ha_open[0])
        condition2 = (self.bullish_engulfing() or self.bullish_harami() or self.bullish_hammer())
        condition3 = (self.doji(-1) or self.doji()) # and (self.inside_bar(-1) or self.inside_bar(-2))
        pattern_stop_sell1 = condition1 and condition2 and condition3
        return pattern_stop_sell1    
    
    
    def pattern_stop_buy2(self):
        condition1 = (self.ha_close[0] < self.ha_open[0])
        condition2 = ((self.ha_high[0] < self.ha_high[-1]) and (self.ha_low[0] < self.ha_low[-1])) or self.doji()
        condition3 = self.evening_star()
        pattern_stop_buy2 = condition1 and condition2 and condition3
        return pattern_stop_buy2
    
    def pattern_stop_sell2(self):
        condition1 = (self.ha_close[0] > self.ha_open[0])
        condition2 = ((self.ha_high[0] > self.ha_high[-1]) and (self.ha_low[0] > self.ha_low[-1])) or self.doji()
        condition3 = self.morning_star()
        pattern_stop_sell2 = condition1 and condition2 and condition3
        return pattern_stop_sell2

    def pattern_stop_buy3(self):
        condition1 = (self.ha_close[0] < self.ha_open[0])
        condition2 = self.bearish_hanging_man(-1)
        pattern_stop_buy3 = condition1 and condition2
        return pattern_stop_buy3
    
    
    def pattern_buy_signal(self):
        condition1 = (self.pattern_buy2() or self.pattern_buy1()) # or (self.pattern_buy3() and self.pattern_buy4() and self.pattern_buy5()) 
        condition2 = (self.bearish_pattern()) # or self.pattern_sell_all())
        pattern_buy_signal = condition1 and not condition2
        return pattern_buy_signal
    
    def pattern_sell_signal(self):
        condition1 = (self.pattern_sell2()) # or self.pattern_sell2()) #or self.pattern_sell3()  
        condition2 = (self.bullish_pattern() ) # or self.pattern_buy_all())
        pattern_sell_signal = condition1 and not condition2
        return pattern_sell_signal
    
    def pattern_stopBuy_signal(self):
        condition1 = (self.pattern_stop_buy1() and self.pattern_stop_buy2())# or self.pattern_stop_buy3()
        condition2 = (self.bullish_pattern() or self.pattern_buy_signal())
        pattern_stopBuy_signal = condition1 and not condition2
        return pattern_stopBuy_signal
    
    def pattern_stopSell_signal(self):
        condition1 = (self.pattern_stop_sell1() and self.pattern_stop_sell2())
        condition2 = (self.bearish_pattern() or self.pattern_sell_signal())
        pattern_stopSell_signal = condition1 and not condition2
        return pattern_stopSell_signal
       
    def next(self):
        if len(self.data) < 5:
            return      
        if self.pattern_buy_signal() == 1:
            self.lines.signal[0] = 1
        elif self.pattern_sell_signal() == 1:
            self.lines.signal[0] = -1
        else:
            self.lines.signal[0] = 0
        
        if self.pattern_stopBuy_signal() == 1:
            self.lines.stop_signal[0] = 1
        elif self.pattern_stopSell_signal() == 1:
            self.lines.stop_signal[0] = -1
        else:
            self.lines.stop_signal[0] = 0