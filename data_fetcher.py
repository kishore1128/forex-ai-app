import os
import pandas as pd
import requests
from urllib.parse import urlencode
import yfinance as yf

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

def _get_api_key():
    return os.getenv("ALPHA_VANTAGE_API_KEY")

def _use_yfinance(symbol: str):
    return len(symbol) == 6

def fetch_ohlc(symbol: str, interval: str = "60min", outputsize: str = "compact"):

    # ---------- FOREX via yfinance ----------
    if _use_yfinance(symbol):

        ticker = f"{symbol.upper()}=X"

        yf_interval = interval.replace("min", "m")

        data = yf.download(
            tickers=ticker,
            period="7d",
            interval=yf_interval,
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            raise RuntimeError(f"No data returned for {ticker}")

        # Remove multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        df = data.reset_index()

        # Rename columns
        rename_map = {
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }

        df.rename(columns=rename_map, inplace=True)

        # Select needed columns
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        # Convert to numeric
        numeric_cols = ["open", "high", "low", "close", "volume"]

        for col in numeric_cols:
            df[col] = df[col].astype(float)

        df.dropna(inplace=True)

        df.reset_index(drop=True, inplace=True)

        return df

    # ---------- STOCKS via Alpha Vantage ----------
    api_key = _get_api_key()

    if not api_key:
        raise RuntimeError("Alpha Vantage API key not set.")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": outputsize,
        "datatype": "json",
    }

    url = f"{ALPHA_VANTAGE_URL}?{urlencode(params)}"

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    data = resp.json()

    key = "Time Series (Daily)"

    if key not in data:
        raise RuntimeError(f"Unexpected response format: {data}")

    rows = []

    for ts, vals in data[key].items():
        rows.append({
            "timestamp": pd.to_datetime(ts),
            "open": float(vals["1. open"]),
            "high": float(vals["2. high"]),
            "low": float(vals["3. low"]),
            "close": float(vals["4. close"]),
            "volume": float(vals.get("5. volume", 0.0)),
        })

    df = pd.DataFrame(rows)

    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df