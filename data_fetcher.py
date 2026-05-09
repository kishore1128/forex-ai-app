import os
import pandas as pd
import requests
from urllib.parse import urlencode
import yfinance as yf

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

# ---------------------------------------------------
# API KEY

def _get_api_key():

    return os.getenv(
        "ALPHA_VANTAGE_API_KEY"
    )

# ---------------------------------------------------
# FOREX CHECK

def _use_yfinance(symbol):

    return len(symbol) == 6

# ---------------------------------------------------
# FETCH OHLC

def fetch_ohlc(
    symbol,
    interval="5m",
    outputsize="compact"
):

    # ---------------------------------------------------
    # FOREX DATA VIA YFINANCE

    if _use_yfinance(symbol):

        try:

            ticker = (
                f"{symbol.upper()}=X"
            )

            interval_map = {
                "1min": "1m",
                "5min": "5m",
                "15min": "15m",
                "30min": "30m",
                "60min": "60m"
            }

            yf_interval = interval_map.get(
                interval,
                "5m"
            )

            data = yf.download(
                ticker,
                period="7d",
                interval=yf_interval,
                progress=False,
                auto_adjust=False
            )

            if data.empty:

                # fallback retry

                data = yf.download(
                    ticker,
                    period="1mo",
                    interval="1h",
                    progress=False,
                    auto_adjust=False
                )

            if data.empty:

                raise RuntimeError(
                    f"No data returned for {ticker}"
                )

            # Fix multi index issue

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                data.columns = (
                    data.columns
                    .get_level_values(0)
                )

            df = data.reset_index()

            rename_map = {
                "Datetime": "timestamp",
                "Date": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }

            df.rename(
                columns=rename_map,
                inplace=True
            )

            required_cols = [
                "timestamp",
                "open",
                "high",
                "low",
                "close"
            ]

            for col in required_cols:

                if col not in df.columns:

                    raise RuntimeError(
                        f"Missing column: {col}"
                    )

            if "volume" not in df.columns:

                df["volume"] = 0

            numeric_cols = [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            for col in numeric_cols:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            df.dropna(inplace=True)

            df.reset_index(
                drop=True,
                inplace=True
            )

            return df

        except Exception as e:

            raise RuntimeError(
                f"Forex fetch failed: {e}"
            )

    # ---------------------------------------------------
    # STOCK DATA VIA ALPHA VANTAGE

    api_key = _get_api_key()

    if not api_key:

        raise RuntimeError(
            "Alpha Vantage API key not set."
        )

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": outputsize,
        "datatype": "json",
    }

    url = (
        f"{ALPHA_VANTAGE_URL}?"
        f"{urlencode(params)}"
    )

    resp = requests.get(
        url,
        timeout=30
    )

    resp.raise_for_status()

    data = resp.json()

    key = "Time Series (Daily)"

    if key not in data:

        raise RuntimeError(
            f"Unexpected response: {data}"
        )

    rows = []

    for ts, vals in data[key].items():

        rows.append({
            "timestamp": pd.to_datetime(ts),
            "open": float(vals["1. open"]),
            "high": float(vals["2. high"]),
            "low": float(vals["3. low"]),
            "close": float(vals["4. close"]),
            "volume": float(
                vals.get(
                    "5. volume",
                    0.0
                )
            ),
        })

    df = pd.DataFrame(rows)

    df.sort_values(
        "timestamp",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df
