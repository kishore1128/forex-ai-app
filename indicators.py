import pandas as pd
import numpy as np

# ---------------------------------------------------
# RSI

def rsi(close, period=14):

    delta = close.diff()

    gain = (
        delta.where(delta > 0, 0)
    ).rolling(period).mean()

    loss = (
        -delta.where(delta < 0, 0)
    ).rolling(period).mean()

    rs = gain / loss

    return 100 - (
        100 / (1 + rs)
    )

# ---------------------------------------------------
# EMA

def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()

# ---------------------------------------------------
# SMA

def sma(series, period):

    return series.rolling(
        window=period
    ).mean()

# ---------------------------------------------------
# MACD

def macd(
    close,
    fast=12,
    slow=26,
    signal=9
):

    ema_fast = ema(close, fast)

    ema_slow = ema(close, slow)

    macd_line = (
        ema_fast - ema_slow
    )

    signal_line = ema(
        macd_line,
        signal
    )

    hist = (
        macd_line - signal_line
    )

    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "hist": hist
    })

# ---------------------------------------------------
# BOLLINGER BANDS

def bollinger_bands(
    close,
    period=20,
    stddev=2
):

    middle = sma(close, period)

    std = close.rolling(
        period
    ).std()

    upper = (
        middle + stddev * std
    )

    lower = (
        middle - stddev * std
    )

    return pd.DataFrame({
        "upper": upper,
        "middle": middle,
        "lower": lower
    })

# ---------------------------------------------------
# VWAP

def vwap(df):

    price = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    cum_vol_price = (
        price * df["volume"]
    ).cumsum()

    cum_vol = (
        df["volume"]
    ).cumsum()

    return cum_vol_price / cum_vol.replace(
        0,
        np.nan
    )

# ---------------------------------------------------
# PIVOT POINTS

def pivot_points(df):

    high = df["high"].iloc[-1]

    low = df["low"].iloc[-1]

    close = df["close"].iloc[-1]

    pp = (
        high + low + close
    ) / 3

    r1 = 2 * pp - low

    s1 = 2 * pp - high

    r2 = pp + (
        high - low
    )

    s2 = pp - (
        high - low
    )

    return {
        "PP": pp,
        "R1": r1,
        "S1": s1,
        "R2": r2,
        "S2": s2
    }