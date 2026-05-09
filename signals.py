def generate_signal(indicators):

    bullish = 0

    bearish = 0

    rsi = indicators.get("RSI", 50)

    macd = indicators.get("MACD", {})

    macd_value = macd.get("macd", 0)

    signal_value = macd.get("signal", 0)

    ema9 = indicators.get("EMA_9", 0)

    ema21 = indicators.get("EMA_21", 0)

    price = indicators.get("price", 0)

    # RSI

    if rsi < 30:
        bullish += 1

    elif rsi > 70:
        bearish += 1

    # MACD

    if macd_value > signal_value:
        bullish += 1

    elif macd_value < signal_value:
        bearish += 1

    # EMA

    if ema9 > ema21:
        bullish += 1

    else:
        bearish += 1

    # Price Trend

    if price > ema21:
        bullish += 1

    else:
        bearish += 1

    # Final Signal

    if bullish >= 3:
        return "BUY"

    if bearish >= 3:
        return "SELL"

    return "HOLD"