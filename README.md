# Forex Analysis Agent

A lightweight Python tool that pulls Forex (FX) price data from **Alpha Vantage**, calculates a suite of technical indicators, detects common candlestick patterns, and outputs a structured JSON payload ready for downstream trading‑signal logic.

## Features
- Fetches intraday FX OHLCV data (intervals: 1 min, 5 min, 15 min, 30 min, 60 min) using the free Alpha Vantage API.
- Computes RSI, MACD, EMA (9, 21, 50, 200), SMA, Bollinger Bands, VWAP, pivot‑point based support/resistance, and more.
- Detects bullish/bearish engulfing, doji, hammer, shooting‑star patterns on the latest candle.
- Simple trend inference based on EMA hierarchy.
- CLI interface (`python -m forex_agent.main`) with environment‑based API‑key handling.

## Setup
1. **Create a virtual environment** (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate   # on Windows
   # or source venv/bin/activate on Unix
   ```
2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```
   > Note: `ta-lib` requires the native TA‑Lib library. If installation fails, you can switch to the pure‑Python fallback `pandas‑ta` by editing `indicators.py` (the code already falls back automatically).
3. **Provide your Alpha Vantage API key**:
   - Copy `.env.example` to `.env` and replace `YOUR_ALPHA_VANTAGE_API_KEY` with your key.
   - Or set the environment variable `ALPHAVANTAGE_API_KEY` directly.

## Usage
```bash
python -m forex_agent.main --symbol EURUSD --interval 60min
```
Example output (pretty‑printed JSON):
```json
{
  "symbol": "EURUSD",
  "interval": "60min",
  "timestamp": "2024-10-31T15:00:00",
  "price": 1.08457,
  "trend": "Bullish",
  "indicators": {
    "RSI": 62.3,
    "MACD": {"macd": 0.0012, "signal": -0.0005},
    "EMA_9": 1.0842,
    "EMA_21": 1.0839,
    "EMA_50": 1.0825,
    "EMA_200": 1.0780,
    "SMA_20": 1.0830,
    "BollingerUpper": 1.0875,
    "BollingerLower": 1.0785,
    "VWAP": 1.0840,
    "SR_PP": 1.0842,
    "SR_R1": 1.0864,
    "SR_S1": 1.0820,
    "SR_R2": 1.0885,
    "SR_S2": 1.0799
  },
  "patterns": {
    "Engulfing": false,
    "Doji": false,
    "Hammer": true,
    "ShootingStar": false
  }
}
```

## Testing
```bash
pip install pytest responses
pytest -q
```
Unit tests are placed under `forex_agent/tests/` (add your own as needed).

## License
MIT – feel free to extend or adapt this code for your own trading workflows.
