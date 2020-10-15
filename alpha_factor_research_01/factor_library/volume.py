import pandas as pd
import numpy as np
import ta

## Volume Indicator
def mfi(open = None, high = None, low = None, close = None, volume = None,
    n = 12):
    mfi = ta.volume.MFIIndicator(
            high, low, close, volume, n = n)\
            .money_flow_index()
    mfi.name = 'mfi'
    return mfi

def adi(open = None, high = None, low = None, close = None, volume = None):
    adii = ta.volume.AccDistIndexIndicator(high, low, close, volume)
    adi = adii.acc_dist_index()

    adi[np.isinf(adi)] = np.nan
    adi.fillna(method = 'ffill', inplace = True)
    
    return adi

def cmf(open = None, high = None, low = None, close = None, volume = None):
    cmf = ta.volume.ChaikinMoneyFlowIndicator(high, low, close, volume)
    cmf = cmf.chaikin_money_flow()
    
    return cmf

def eom(open = None, high = None, low = None, close = None, volume = None,
    n = 14):
    eom = ta.volume.EaseOfMovementIndicator(high, low, volume, n = n).ease_of_movement()
    sma_eom = ta.volume.EaseOfMovementIndicator(high, low, volume, n = n).sma_ease_of_movement()
    
    return pd.concat([eom, sma_eom], axis = 1)

def fii(open = None, high = None, low = None, close = None, volume = None,
        n = 13):
    fii = ta.volume.ForceIndexIndicator(close, volume, n = n).force_index()
    return fii

def nvi(open = None, high = None, low = None, close = None, volume = None):
    nvi = ta.volume.NegativeVolumeIndexIndicator(close, volume).negative_volume_index()
    return nvi

def obv(open = None, high = None, low = None, close = None, volume = None):
    obv = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    return obv

def vpti(open = None, high = None, low = None, close = None, volume = None):
    vpti = ta.volume.VolumePriceTrendIndicator(close, volume).volume_price_trend()
    return vpti

def vwap(open = None, high = None, low = None, close = None, volume = None,
        n = 14):
    vwap = ta.volume.VolumeWeightedAveragePrice(high, low, close, volume, n = n)\
            .volume_weighted_average_price()
    return vwap

def getVolumeOsc(open = None, high = None, low = None, close = None, volume = None,
                periods = 20):
    vol_sma = ta.trend.ema(volume, periods = periods)
    vol_sma.name = 'volume_oscillator20'
    return vol_sma