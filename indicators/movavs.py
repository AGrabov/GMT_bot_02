import backtrader as bt
import talib

class MovAverages(bt.Indicator):
    lines = ('signal', 'stop_signal',)
    params = dict(
        fast_ema = 9,                
        slow_ema = 19,
        hma_length = 20,
        kama_period = 29, 
        dma_period = 17, 
        dma_gainlimit = 50,
        dma_hperiod = 11,
    )

    def __init__(self):
        # EMAs signals
        self.fma = bt.talib.EMA(self.data, timeperiod=self.params.fast_ema, plot=False)
        self.sma = bt.talib.EMA(self.data, timeperiod=self.params.slow_ema, plot=False)

        self.ema2_cross = bt.ind.CrossOver(self.fma, self.sma, plot=False)
        self.ema_cross = bt.ind.CrossOver(self.data, self.sma, plot=False)
        self.ema_buy1 = (self.ema2_cross == 1)
        self.ema_sell1 = (self.ema2_cross == -1)
        self.ema_buy2 = (self.ema_cross == 1)
        self.ema_sell2 = (self.ema_cross == -1)
        self.ema_buy = bt.Or(self.ema_buy1, self.ema_buy2)
        self.ema_sell = bt.Or(self.ema_sell1, self.ema_sell2)
        
        # Hull moving average
        self.hma = bt.indicators.HullMovingAverage(self.data, period=self.params.hma_length).lines.hma        
        self.hma_cross = bt.ind.CrossOver(self.data, self.hma, plot=False)
        self.hma_cross.plotinfo.plotname = 'HMA cross'
        self.hma_buy1 = (self.hma_cross == 1)
        self.hma_sell1 = (self.hma_cross == -1)        

        # # Hull movav Oscillator
        # self.hmo = bt.indicators.HullMovingAverageOscillator(self.data, period=self.params.hma_length)
        # self.hmo_buy1 = (self.hmo.hma > 0.0)
        # self.hmo_sell1 = (self.hmo.hma < 0.0)

        # Dickson Moving Average
        self.dma = bt.indicators.DMA(self.data, 
                                     period=self.params.dma_period, 
                                     gainlimit=self.params.dma_gainlimit, 
                                     hperiod=self.params.dma_hperiod, 
                                     plot=False
                                     )
        self.dma_cross = bt.ind.CrossOver(self.data, self.dma, plot=False)
        self.dma_cross.plotinfo.plotname = 'DMA cross'
        
        self.dma_buy = (self.dma_cross == 1)
        self.dma_sell = (self.dma_cross == -1)

        self.hma_dma_cross = bt.ind.CrossOver(self.dma, self.hma, plot=False)
        self.dma_cross.plotinfo.plotname = 'DMA and HMA crossover'

        self.dma_hma_buy = (self.hma_dma_cross == 1)
        self.dma_hma_sell = (self.hma_dma_cross == -1)
        

        # KAMA
        self.kama = bt.talib.KAMA(self.data, timeperiod=self.params.kama_period)
        self.kama_cross = bt.ind.CrossOver(self.data, self.kama.real, plot=False)

        self.kama_buy1 =  (self.kama_cross == 1)
        self.kama_sell1 =  (self.kama_cross == -1)      

    def hma_buy(self):  
        hma_buy1 = self.hma_buy1[0]      
        hma_buy2 = ((self.hma[-4] > self.hma[-3]) and 
                    (self.hma[-3] >= self.hma[-2]) and 
                    (self.hma[-2] <= self.hma[-1]) and
                    (self.hma[-1] < self.hma[0]))        
        return (hma_buy1 or hma_buy2)
    
    def hma_sell(self):    
        hma_sell1 = self.hma_sell1[0]    
        hma_sell2 = ((self.hma[-4] < self.hma[-3]) and 
                     (self.hma[-3] <= self.hma[-2]) and 
                     (self.hma[-2] >= self.hma[-1]) and
                     (self.hma[-1] > self.hma[0]))
        
        return (hma_sell1 or hma_sell2) 

    def kama_buy(self):
        kama_buy1 = self.kama_buy1[0]
        kama_buy2 = ((self.kama[-4] > self.kama[-3]) and 
                     (self.kama[-3] >= self.kama[-2]) and 
                     (self.kama[-2] <= self.kama[-1]) and
                     (self.kama[-1] < self.kama[0]))
        return (kama_buy1 or kama_buy2)
    
    def kama_sell(self):
        kama_sell1 = self.kama_sell1[0]
        kama_sell2 = ((self.kama[-4] < self.kama[-3]) and 
                      (self.kama[-3] <= self.kama[-2]) and 
                      (self.kama[-2] >= self.kama[-1]) and
                      (self.kama[-1] > self.kama[0]))
        return (kama_sell1 or kama_sell2)
    
    def movav_buy(self):        
        ema = (self.ema_buy[0] or self.ema_buy[-1])
        dma = (self.dma_buy[0] or self.dma_buy[-1])
        hma = (self.hma_buy() or self.hma_buy1[-1])
        kama = (self.kama_buy() or self.kama_buy1[-1])        
        movav_buy = ema and hma and (dma or kama)
        return movav_buy
    
    def movav_sell(self):
        ema = (self.ema_sell[0] or self.ema_sell[-1])
        dma = (self.dma_sell[0] or self.dma_sell[-1])
        hma = (self.hma_sell() or self.hma_sell1[-1])
        kama = (self.kama_sell() or self.kama_sell1[-1])         
        movav_sell = ema and hma and (dma or kama)
        return movav_sell
    
    def movav_stop_buy(self):
        ema = (self.ema_sell[0])
        dma = (self.dma_sell[0])
        hma = (self.hma_sell1[0])
        kama = (self.kama_sell())        
        movav_stop_buy = (ema and hma)# and (dma or kama))
        return movav_stop_buy

    def movav_stop_sell(self):        
        ema = (self.ema_buy[0])
        dma = (self.dma_buy[0])
        hma = (self.hma_buy1[0])
        kama = (self.kama_buy())        
        movav_stop_sell = (ema and hma) # and (dma or kama))
        return movav_stop_sell

    def next(self):
        if len(self.data) < 5:
            return      
        if (self.movav_buy() == 1):
            self.lines.signal[0] = 1
        elif (self.movav_sell() == 1):
            self.lines.signal[0] = -1
        else:
            self.lines.signal[0] = 0
        
        if (self.movav_stop_buy() == 1):
            self.lines.stop_signal[0] = 1
        elif (self.movav_stop_sell() == 1):
            self.lines.stop_signal[0] = -1
        else:
            self.lines.stop_signal[0] = 0
        