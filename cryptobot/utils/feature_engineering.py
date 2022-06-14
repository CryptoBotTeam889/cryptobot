import pandas as pd
import pandas_ta as ta

"""
Uses pandas_ta library
"""


def ema_metric(df, close_series, interval=10):
    """
    Returns df with the EMA column with name EMA_interval
    Where:
    EMA = Exponential Moving Average
    interval = 10 (default). Most used intervals (10, 20, 50, 200) depends on
    the time frame of the data, smaller intervals are more suitable for shorter
    time frames
    """
    df[f"EMA_{interval}"] = df.ta.ema(interval, close=close_series)
    return df


def rsi_metric(df, close_series, interval=14):
    """
    Returns df with the RSI column with name RSI_interval
    Where:
    RSI = Relative Strength Index
    interval = 14 (default)
    """
    df[f"RSI_{interval}"] = df.ta.rsi(interval, close=close_series)
    return df


def adx_dmp_dmn_metric(df, high_series, low_series, close_series, interval=14):
    """
    Returns df with the ADX, DMP and DMN column with name ADX_interval, DMP_interval, DMN_interval
    Where:
    ADX = Average directional movement index
    DMP = Directional Movement Index Positive
    DMN = Directional Movement Index Negative

    interval = 14 (default)
    """
    aux_df = df.ta.adx(interval, high=high_series, low=low_series, close=close_series)

    df[f"ADX_{interval}"] = aux_df[f"ADX_{interval}"]
    df[f"DMP_{interval}"] = aux_df[f"DMP_{interval}"]
    df[f"DMN_{interval}"] = aux_df[f"DMN_{interval}"]
    return df


def atr_metric(df, high_series, low_series, close_series, interval=14):
    """
    Returns df with the ATR column with name ADX_interval
    Where:
    ATR = Average True Range

    interval = 14 (default)
    """
    df[f"ATR_{interval}"] = df.ta.atr(
        interval, high=high_series, low=low_series, close=close_series
    )
    return df


def add_metrics(df):
    """
    Add EMA, RSI, ADX, DMP, DMN, ATR metrics to dataframe
    """
    df = ema_metric(df, df["close"], 10)
    df = ema_metric(df, df["close"], 50)
    df = ema_metric(
        df, df["close"], 200
    )  # if we change this value, we need to change the slice before returning the dataframe
    df = rsi_metric(df, df["close"], 14)
    df = adx_dmp_dmn_metric(df, df["high"], df["low"], df["close"], 14)
    df = atr_metric(df, df["high"], df["low"], df["close"], 14)
    return df
