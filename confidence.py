"""
Confidence scoring and AI recommendation mapping.

The function receives the full indicator dictionary and returns:
- confidence → integer 0-100
- ai_label → Strong Buy / Buy / Hold / Sell / Strong Sell
"""

from typing import Tuple, Dict


def safe_number(value, default=0.0):
    """Guard against None / NaN."""
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def score(indicators: Dict) -> Tuple[int, str]:

    bullish = 0
    bearish = 0

    # ------------------------------------------------ RSI

    rsi = safe_number(indicators.get("RSI"))

    if rsi < 30:
        bullish += 1

    elif rsi > 70:
        bearish += 1

    # ------------------------------------------------ MACD

    macd = safe_number(
        indicators.get("MACD", {}).get("macd")
    )

    signal = safe_number(
        indicators.get("MACD", {}).get("signal")
    )

    if macd > signal:
        bullish += 1

    elif macd < signal:
        bearish += 1

    # ------------------------------------------------ EMA TREND

    ema9 = safe_number(indicators.get("EMA_9"))
    ema21 = safe_number(indicators.get("EMA_21"))
    ema50 = safe_number(indicators.get("EMA_50"))
    ema200 = safe_number(indicators.get("EMA_200"))

    if ema9 > ema21:
        bullish += 1
    else:
        bearish += 1

    if ema21 > ema50:
        bullish += 1
    else:
        bearish += 1

    if ema50 > ema200:
        bullish += 1
    else:
        bearish += 1

    # ------------------------------------------------ STRONG TREND

    if ema9 > ema21 > ema50 > ema200:
        bullish += 1

    elif ema9 < ema21 < ema50 < ema200:
        bearish += 1

    # ------------------------------------------------ PRICE VS EMA

    price = safe_number(indicators.get("price"))

    if price > ema21:
        bullish += 1

    elif price < ema21:
        bearish += 1

    # ------------------------------------------------ PATTERNS

    patterns = indicators.get("patterns", {})

    if any(
        patterns.get(p)
        for p in ("Engulfing", "Hammer")
    ):
        bullish += 1

    if any(
        patterns.get(p)
        for p in ("ShootingStar",)
    ):
        bearish += 1

    # ------------------------------------------------ FINAL SCORE

    total = bullish + bearish

    if total == 0:
        confidence = 50

    else:
        confidence = int(
            (max(bullish, bearish) / total) * 100
        )

    # ------------------------------------------------ LABEL

    if bullish > bearish:
        direction = "BUY"

    elif bearish > bullish:
        direction = "SELL"

    else:
        direction = "HOLD"

    if confidence >= 85:
        ai_label = f"Strong {direction.title()}"

    elif confidence >= 65:
        ai_label = direction.title()

    else:
        ai_label = "Hold"

    return confidence, ai_label