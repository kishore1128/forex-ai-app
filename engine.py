"""Engine that ties together data fetching, indicators, and pattern detection."""

import pandas as pd

from data_fetcher import fetch_ohlc

from indicators import (
    rsi,
    macd,
    ema,
    sma,
    bollinger_bands,
    vwap,
    pivot_points,
)

from patterns import (
    is_engulfing,
    is_doji,
    is_hammer,
    is_shooting_star,
)

from signals import generate_signal

from confidence import score as confidence_score


def analyze_symbol(
    symbol: str,
    interval: str = "60min",
    outputsize: str = "compact"
) -> dict:

    df = fetch_ohlc(
        symbol,
        interval=interval,
        outputsize=outputsize
    )

    indicators = {

        "RSI": round(
            float(rsi(df['close']).iloc[-1]),
            2
        ),

        "MACD": {

            "macd": round(
                float(
                    macd(df['close']).iloc[-1, 0]
                ),
                2
            ),

            "signal": round(
                float(
                    macd(df['close']).iloc[-1, 1]
                ),
                2
            ),
        },

        "EMA_9": round(
            float(
                ema(df['close'], 9).iloc[-1]
            ),
            2
        ),

        "EMA_21": round(
            float(
                ema(df['close'], 21).iloc[-1]
            ),
            2
        ),

        "EMA_50": round(
            float(
                ema(df['close'], 50).iloc[-1]
            ),
            2
        ),

        "EMA_200": round(
            float(
                ema(df['close'], 200).iloc[-1]
            ),
            2
        ),

        "SMA_20": round(
            float(
                sma(df['close'], 20).iloc[-1]
            ),
            2
        ),

        "BollingerUpper": round(
            float(
                bollinger_bands(
                    df['close']
                ).iloc[-1, 0]
            ),
            4
        ),

        "BollingerLower": round(
            float(
                bollinger_bands(
                    df['close']
                ).iloc[-1, 2]
            ),
            4
        ),

        "VWAP": round(
            float(vwap(df).iloc[-1]),
            4
        ),
    }

    sr = pivot_points(df)

    indicators.update({

        f"SR_{k}": round(v, 4)

        for k, v in sr.items()
    })

    patterns = {

        "Engulfing": bool(
            is_engulfing(df)
        ),

        "Doji": bool(
            is_doji(df)
        ),

        "Hammer": bool(
            is_hammer(df)
        ),

        "ShootingStar": bool(
            is_shooting_star(df)
        ),
    }

    indicators["patterns"] = patterns

    trend = (

        "Bullish"

        if indicators["EMA_9"]
        > indicators["EMA_21"]
        > indicators["EMA_50"]

        else "Bearish"
    )

    trade_signal = generate_signal(
        indicators
    )

    confidence, ai_label = confidence_score(
        indicators
    )

    result = {

        "symbol": symbol,

        "interval": interval,

        "timestamp": df[
            'timestamp'
        ].iloc[-1].isoformat(),

        "price": round(
            float(
                df['close'].iloc[-1]
            ),
            5
        ),

        "trend": trend,

        "signal": trade_signal,

        "confidence": confidence,

        "ai_label": ai_label,

        "indicators": indicators,

        "patterns": patterns,

        "raw_df": df.to_dict(
            orient="records"
        ),
    }

    return result