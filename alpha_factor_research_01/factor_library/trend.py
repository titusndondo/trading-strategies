import pandas as pd
import numpy as np
import ta

## Trend Indicators
def macdDiff(open = None, high = None, low = None, close = None, volume = None,
            n_slow = 26, n_fast = 12, n_sign = 9):
    Macd = ta.trend.MACD(
        close, n_slow = n_slow, n_fast = n_fast, n_sign = n_sign)
    
    # macd = Macd.macd()
    # macd_signal = Macd.macd_signal()
    macd_diff = Macd.macd_diff() 
    return macd_diff