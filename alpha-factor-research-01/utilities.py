import pandas as pd
import numpy as np
from alphalens import utils, performance, plotting
import matplotlib.pyplot as plt
import seaborn as sns

def getIndicator(
    datas,
    indicator,
    filter = 'QTradeable',
    trailing_volume_n = 200, 
    *args, **kwargs):


    factor_df = pd.DataFrame()
    for symbol, data in datas.items():
        if len(data) > trailing_volume_n:
            data = data.copy()

            open = data['open']
            high = data['high']
            low = data['low']
            close = data['close']
            volume = data['volume']
#             adj_close = data['adj_close']


            factor = indicator(
                open = open,
                high = high,
                low = low,
                close = close,
                volume = volume,
                *args, **kwargs
            )

            out = pd.DataFrame(factor)
            # factor_names = out.columns
            out['symbol'] = symbol
            out.index.name = 'date'
            out = out.reset_index()\
                  .set_index(['date', 'symbol'])

            if filter == 'QTradeable':

                def getTrailingVolume(
                    close, volume, symbol, n = trailing_volume_n):

                    volume = data['volume']
                    dollar_volume = volume.mul(close)

                    trailing_dollar_volume = \
                        dollar_volume.rolling(
                            window = n).median()
                    trailing_dollar_volume.name = \
                        'trailing_dollar_volume'

                    trailing_dollar_volume = \
                        pd.DataFrame(trailing_dollar_volume)

                    trailing_dollar_volume['symbol'] = symbol

                    trailing_dollar_volume = \
                        trailing_dollar_volume.\
                        reset_index()\
                        .set_index(['date', 'symbol'])

                    return trailing_dollar_volume

                def getPricing(close, symbol):
                    prices = pd.DataFrame(close)
                    prices['symbol'] = symbol
                    prices = prices.reset_index()\
                        .set_index(['date', 'symbol'])

                    return prices

                # volume filter
                trailing_dollar_volume = \
                    getTrailingVolume(close, volume, symbol)

                # price filter
                prices = getPricing(close, symbol)

                out = pd.concat(
                    [out, trailing_dollar_volume, prices], 
                    axis = 1)

                QTradeableStocks_median_dollar_volume = 2500000
                exchange_rate = 16.56
                minimum_dollar_volume = \
                    QTradeableStocks_median_dollar_volume * exchange_rate

                QTradeableStocks_minimun_price = 5
                minimum_price = \
                    QTradeableStocks_minimun_price * exchange_rate

                volume_mask = out['trailing_dollar_volume'] > \
                    minimum_dollar_volume
                price_mask = out['close'] > minimum_price

                out = out[volume_mask & price_mask].drop(['trailing_dollar_volume', 'close'], axis = 1)

            factor_df = pd.concat([factor_df, out])#.unstack().asfreq('C').stack()
    return factor_df

def getPrices(
    trainPrices, 
    symbols, 
    at_open = False):

    prices_data = pd.DataFrame()
    for symbol, data in trainPrices.items():
        if symbol in symbols:
            if not at_open:
                out = data['close']
            else:
                out = data['open'].shift(-1)
            out.name = symbol
            prices_data = pd.concat([prices_data, out], axis = 1)
    prices_data.index = pd.to_datetime(prices_data.index)
    return prices_data.asfreq('C')


def addGroupingFactor(
    factor_data, 
    group_data):

    _groups = group_data['factor_quantile']
    _groups.name = 'group'
    factor_data_w_group = pd.concat([factor_data, _groups], axis = 1).dropna()
    return factor_data_w_group

def getCleanFactor(
    indicator, 
    forward_returns, 
    quantiles = None, 
    max_loss = 0.35):

    """
    Modified alphalens get_clean_factor function
    """
    
    out = pd.DataFrame()
    for symbol in pd.Series(forward_returns.index.get_level_values('asset')).unique():
        factor_name = indicator.columns[0]
        
        if quantiles:

            data = pd.concat(
                [
                    forward_returns[forward_returns.index.get_level_values('asset').isin([symbol])], 
                    indicator[indicator.index.get_level_values('symbol').isin([symbol])]
                ], 
                axis = 1).dropna(subset = ['event'])
            
            data[factor_name].fillna(method = 'ffill', inplace = True)
            data = data[['1D', factor_name]].dropna()
        
        else:
            data = pd.concat(
                [
                    forward_returns[forward_returns.index.get_level_values('asset').isin([symbol])], 
                    indicator[indicator.index.get_level_values('symbol').isin([symbol])]
                ], 
                axis = 1).dropna(subset = ['event'])
            
            data[factor_name].fillna(method = 'ffill', inplace = True)
            data['factor_quantile'].fillna(method = 'ffill', inplace = True)
            data = data[['1D', factor_name, 'factor_quantile']].dropna()

        data.index.set_names(['date', 'asset'], inplace = True)

        out = pd.concat([out, data])
    
    if quantiles:
        factor_ = out.rename(columns = {factor_name:'factor'})['factor']
        factor_data = utils\
            .get_clean_factor(
                    factor_, 
                    forward_returns = out[['1D']], 
                    quantiles = quantiles,
                    max_loss=max_loss)
    else:
        factor_data = out
    
    return factor_data

def getForwardReturns(datas):

    """
    Modified version of alphalens get_forward_returns
    """

    forward_returns = pd.DataFrame()
    for symbol, data in datas.items():
        data = data.copy()
        out = data[['open']].shift(-1)
        out['event'] = data['event']
        out['t1'] = data['t1']
        out['t1'].fillna(method = 'ffill', inplace = True)
        out = out.reset_index()
        out = out[out['date'] <= out['t1']]
        out['open'] = out['open'].pct_change(periods = 1).shift(-1)
        out['asset'] = symbol
        out = out[out['date'] != out['t1']].set_index(['date', 'asset'])
        out.rename(columns = {'open':'1D'}, inplace = True)
        forward_returns = pd.concat([forward_returns, out])
    forward_returns.sort_index(level = 'date', inplace = True)
    
    return forward_returns

def InformationTable(factor_data):

    """
    alphalens plot information table
    """

    ic = performance.factor_information_coefficient(factor_data)

    return plotting.plot_information_table(ic)

def plotFactorQuantileBars(
    factor_data, 
    demeaned = True, 
    by_group = False, 
    group_adjust = False):
    
    mean_quant_ret, std_quantile_ = \
        performance.mean_return_by_quantile(
        factor_data,
        demeaned = demeaned,
        by_group = by_group,
        group_adjust = group_adjust)

    mean_quant_rateret = \
            mean_quant_ret\
                .apply(
        utils.rate_of_return, 
        axis = 0,
        base_period = mean_quant_ret.columns[0])
    
    plotting.plot_quantile_returns_bar(mean_quant_rateret,
                                   by_group = by_group,
                                   ylim_percentiles = None)
    plt.show()

def plotCumulativeReturns(
    factor_data, 
    p = '1D', 
    demeaned = True, 
    group_adjust = False, 
    figsize = (16, 8)):

    factor_returns = performance.factor_returns(
        factor_data, 
        demeaned = demeaned, 
        group_adjust = group_adjust)

    fig = plt.figure(figsize = figsize)
    title = \
        'Factor weighted LONG/SHORT portfolio cumulative returns'
    plotting.plot_cumulative_returns(
        factor_returns[p],
        period = p)
    plt.show()

def plotQuantileCumulativeReturns(
    factor_data, 
    p = '1D',
    demeaned = True,
    by_date = True,
    by_group = False,
    group_adjust = False,
    figsize = (16, 8)):
    
    mean_quant_ret_bydate, std_quant_daily = \
            performance.mean_return_by_quantile(
                             factor_data,
                             demeaned = demeaned,
                             by_date = by_date,
                             by_group = by_group,
                             group_adjust = group_adjust)

    fig = plt.figure(figsize = figsize)
    cumulative_quantile_returns = \
        mean_quant_ret_bydate\
        .groupby(level = ['factor_quantile', 'date'])\
        .sum()[p]
    
    plotting.plot_cumulative_returns_by_quantile(
        cumulative_quantile_returns,
        period = p)
    plt.show()