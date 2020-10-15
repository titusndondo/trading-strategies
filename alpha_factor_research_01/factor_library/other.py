import pandas as pd
import numpy as np
import ta  
    
def nDifference(open = None, high = None, low = None, close = None, volume = None,
            lags = range(0, 10)):
    diffs = pd.DataFrame()
    for i in lags:
        out = close.shift(i).diff()
        out.name = f"close_diff_{i}"
        diffs = pd.concat([diffs, out], axis = 1)
    return diffs * -1