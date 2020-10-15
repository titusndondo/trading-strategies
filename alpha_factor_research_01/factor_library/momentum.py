import pandas as pd
import numpy as np
import ta

## Momentum indicators

def momentum(open = None, high = None, low = None, close = None, volume = None,
            lags = [4, 7, 10, 20]):
    mom = pd.DataFrame()
    for i in lags:
        out = close.shift(2) / close.shift(i) - 1
        out.name = f"mom_2_{i}"
        mom = pd.concat([mom, out], axis = 1)
    return mom

# awesome oscillator
def ao(open = None, high = None, low = None, close = None, volume = None,
    s = 3, len = 9):
    ao = ta.momentum.AwesomeOscillatorIndicator(
        high, low, s = s, len = len).ao() 
    return ao

# kama indicator, normalised
def kamaCrossOver(open = None, high = None, low = None, close = None, volume = None,
                n = 10, pow1 = 2, pow2 = 30):
    
    """
    Try pow1 = 2 to 5 for smoothing the indicator even further, may improve result
    """
    
    kamashort = ta.momentum.KAMAIndicator(close, n = n, pow1 = pow1, pow2 = pow2).kama()
    cross_over = close.sub(kamashort).div(close) * -1
    cross_over.name = 'kama_cross_over'
    return cross_over
    
# roc indicator
def rocIndicator(open = None, high = None, low = None, close = None, volume = None,
                n = 4):
    roc = ta.momentum.ROCIndicator(close, n = n).roc() * -1
    return roc

# reletive strength index
def rsi(open = open, high = None, low = None, close = None, volume = None,
    n = 5):
    rsi = ta.momentum.RSIIndicator(close, n = n).rsi()
    rsi.name = 'rsi'
    return rsi * -1

def tsi(open = None, high = None, low = None, close = None, volume = None,
    r = 9, s = 5):
    tsi = ta.momentum.TSIIndicator(close, r = r, s = s).tsi() 
    tsi.name = 'tsi'
    return tsi * -1

# stochastic oscilator
def stochOscillator(open = open, high = None, low = None, close = None, volume = None,
                    n = 14, m = 3, slow = None):
    
    lowest_low = low.rolling(window = n).min()
    highest_high = high.rolling(window = n).max()
    
    percentK = (close - lowest_low)/(highest_high - lowest_low) * 100
    percentD = ta.trend.sma(percentK, periods = m)
    signal = percentD.sub(percentK)
    signal.name = 'fast_stoch_osc'
    
    if not slow:
        return signal
    elif slow:
        slow_percentK = ta.trend.sma(percentK, periods = m)
        slow_percentD = ta.trend.sma(slow_percentK, periods = m)
        slow_signal = slow_percentD.sub(slow_percentK)
        slow_signal.name = 'slow_stoch_osc'
        return slow_signal

def uo(open = None, high = None, low = None, close = None, volume = None,
    s = 7, m = 14, len = 28, ws = 4, wm = 2, wl = 1):
    uo = ta.momentum.UltimateOscillator(
        high, low, close, s = s, m = m, len = len, ws = ws, wm = wm, wl = wl).uo() * -1
    return uo

def williamsR(open = None, high = None, low = None, close = None, volume = None,
    lbp = 14):
    wr = ta.momentum.WilliamsRIndicator(
        high, low, close, lbp = lbp).wr() * -1
    return wr