import backtrader as bt

class MyPivotPoint(bt.Indicator):
    lines = ('pp', 's1', 's2', 'r1', 'r2')
    plotinfo = dict(subplot=False)  # Plot on the same subplot as the data

    def __init__(self):
        self.ha = bt.indicators.HeikinAshi(self.data, plot=False)        
        self.ha.plotlines.ha_high._plotskip=True 
        self.ha.plotlines.ha_low._plotskip=True
        self.ha.plotlines.ha_open._plotskip=True
        self.ha.plotlines.ha_close._plotskip=True

        self.addminperiod(2)

        # Initialize the variables
        self.current_day = None  # Initialize as None
        self.prev_data_high = None
        self.prev_data_low = None
        self.prev_data_close = None
        self.first_call = True  # Flag to indicate the first call to next

    def next(self):        
        
        # Check if we're on a new day
        if self.data.datetime.date(0) != self.current_day:
            # We have a new day, so calculate the PivotPoint indicator
            # using the complete OHLC values from the previous day
            if self.data_high is not None and self.data_low is not None and self.data_close is not None:
                self.lines.pp[0] = (self.data_high + self.data_low + self.data_close) / 3
                self.lines.s1[0] = 2.0 * self.lines.pp[0] - self.data_high
                self.lines.s2[0] = self.lines.pp[0] - (self.data_high - self.data_low)
                self.lines.r1[0] = 2.0 * self.lines.pp[0] - self.data_low
                self.lines.r2[0] = self.lines.pp[0] + (self.data_high - self.data_low)

            # Update the current day to the new day
            self.current_day = self.data.datetime.date(0)

            # Reset the OHLC values for the new day
            self.data_high = self.data.high[0]
            self.data_low = self.data.low[0]
            self.data_close = self.data.close[0]
        else:
            # We're still on the same day, so update the OHLC values
            self.data_high = max(self.data_high, self.data.high[0])
            self.data_low = min(self.data_low, self.data.low[0])
            self.data_close = self.data.close[0]

            self.lines.pp[0] = self.lines.pp[-1]
            self.lines.s1[0] = self.lines.s1[-1]
            self.lines.s2[0] = self.lines.s2[-1]
            self.lines.r1[0] = self.lines.r1[-1]
            self.lines.r2[0] = self.lines.r2[-1]

        # if self.lines.pp[0] != self.lines.pp[-1]:
        #     # Print the values of the lines
        #     print(f'pp: {self.lines.pp[0]:.4f}, s1: {self.lines.s1[0]:.4f}, s2: {self.lines.s2[0]:.4f}, r1: {self.lines.r1[0]:.4f}, r2: {self.lines.r2[0]:.4f}')


    def buy(self):
        pivot_buy1 = (self.ha.lines.ha_close[0] > self.lines.s1[0]) and \
                     (self.ha.lines.ha_close[-1] < self.lines.s1[0]) and \
                     (self.ha.lines.ha_close[-2] >= self.lines.s1[0]) and \
                     (self.ha.lines.ha_close[-3] >= self.lines.s1[0]) and \
                     (self.ha.lines.ha_close[-1] < self.ha.lines.ha_close[0])
        
        pivot_buy2 = (self.ha.lines.ha_close[0] > self.lines.s2[0]) and \
                     (self.ha.lines.ha_close[-1] < self.lines.s2[0]) and \
                     (self.ha.lines.ha_close[-2] >= self.lines.s2[0])
        buy = (pivot_buy1 or pivot_buy2)       
        return buy    
        
    def sell(self):
        pivot_sell1 = ((self.ha.lines.ha_close[0] < self.lines.r1[0]) and
                       (self.ha.lines.ha_close[-1] > self.lines.r1[0]) and
                       (self.ha.lines.ha_close[-2] <= self.lines.r1[0]) and 
                       (self.ha.lines.ha_close[-3] <= self.lines.r1[0]))
        pivot_sell2 = ((self.ha.lines.ha_close[0] < self.lines.r2[0]) and
                       (self.ha.lines.ha_close[-1] > self.lines.r2[0]) and 
                       (self.ha.lines.ha_close[-2] <= self.lines.r2[0]))  
        sell = (pivot_sell1 or pivot_sell2)      
        return sell       
    
    def stop_buy(self):
        return ((self.ha.lines.ha_close[0] < self.lines.r1[0]) and
                (self.ha.lines.ha_close[-1] > self.lines.r1[0]) and
                (self.ha.lines.ha_close[-2] > self.lines.r1[0]))        
    
    def stop_sell(self):
        return ((self.ha.lines.ha_close[0] > self.lines.s1[0]) and
                (self.ha.lines.ha_close[-1] < self.lines.s1[0]) and
                (self.ha.lines.ha_close[-2] < self.lines.s1[0])) 