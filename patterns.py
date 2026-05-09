"""Candlestick pattern detection utilities.

Only a subset of patterns is implemented for brevity; additional patterns can be added later.
"""
import pandas as pd


def _last_candle(df: pd.DataFrame):
    return df.iloc[-1]


def is_engulfing(df: pd.DataFrame) -> bool:
    """Detect bullish or bearish engulfing on the last two candles.
    Returns True if a bullish engulfing (green body engulfs previous red) **or** bearish engulfing.
    """
    if len(df) < 2:
        return False
    prev, cur = df.iloc[-2], df.iloc[-1]
    # bullish engulfing
    if cur['close'] > cur['open'] and prev['close'] < prev['open']:
        return cur['open'] <= prev['close'] and cur['close'] >= prev['open']
    # bearish engulfing
    if cur['close'] < cur['open'] and prev['close'] > prev['open']:
        return cur['open'] >= prev['close'] and cur['close'] <= prev['open']
    return False


def is_doji(df: pd.DataFrame, tolerance: float = 0.001) -> bool:
    """Doji when open and close are nearly equal.
    tolerance is relative to the candle's range.
    """
    if len(df) == 0:
        return False
    c = _last_candle(df)
    range_ = c['high'] - c['low']
    if range_ == 0:
        return False
    return abs(c['close'] - c['open']) / range_ <= tolerance


def is_hammer(df: pd.DataFrame) -> bool:
    """Hammer / inverted hammer detection for the last candle.
    Classic hammer: small body, long lower shadow, short upper shadow.
    """
    if len(df) == 0:
        return False
    c = _last_candle(df)
    body = abs(c['close'] - c['open'])
    lower = c['open'] - c['low'] if c['close'] >= c['open'] else c['close'] - c['low']
    upper = c['high'] - c['close'] if c['close'] >= c['open'] else c['high'] - c['open']
    return body * 2 < lower and upper < body * 0.5


def is_shooting_star(df: pd.DataFrame) -> bool:
    """Shooting star detection – opposite of hammer."""
    if len(df) == 0:
        return False
    c = _last_candle(df)
    body = abs(c['close'] - c['open'])
    upper = c['high'] - c['close'] if c['close'] >= c['open'] else c['high'] - c['open']
    lower = c['open'] - c['low'] if c['close'] >= c['open'] else c['close'] - c['low']
    return body * 2 < upper and lower < body * 0.5

# Additional patterns (morning/evening star, pin bar, inside bar) can be added similarly.
