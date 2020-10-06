import pandas as pd
import numpy as np
import ta

## Volatility Indicators
# bbands
def bbands(open = None, high = None, low = None, close = None, volume = None,
            n = 20, ndev = 2):
    bbands = ta.volatility\
        .BollingerBands(close, n = n, ndev = ndev)
    perc_b = bbands.bollinger_pband()
    hband_ind = bbands.bollinger_hband_indicator()
    lband_ind = bbands.bollinger_lband_indicator()
    bollinger_wband = bbands.bollinger_wband()
    
    return pd.concat(
        [hband_ind, lband_ind, perc_b, bollinger_wband], #
        axis = 1)

# Average true range
def atr(open = None, high = None, low = None, close = None, volume = None,
            n = 14):
    atr = ta.volatility.AverageTrueRange(high, low, close, n = n)
    atr = atr.average_true_range().div(close).mul(100)
    atr.name = 'atr'
    return atr

# Dochian channel
def dc(open = None, high = None, low = None, close = None, volume = None,
            n = 20):
    dc = ta.volatility.DonchianChannel(high, low, close, n = n)
    perc_b = dc.donchian_channel_pband()
    band_width = dc.donchian_channel_wband()

    return pd.concat([band_width, perc_b], axis = 1)

# Keltner Channel
def kc(open = None, high = None, low = None, close = None, volume = None,
            n = 20, n_atr = 10):
    kc = ta.volatility.KeltnerChannel(high, low, close, n = n, n_atr = n_atr)
    perc_b = kc.keltner_channel_pband()
    hband_ind = kc.keltner_channel_hband_indicator()
    lband_ind = kc.keltner_channel_lband_indicator()
    kc_wband = kc.keltner_channel_wband()
    
    return pd.concat(
        [hband_ind, lband_ind, perc_b, kc_wband], #
        axis = 1)