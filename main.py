"""Command‑line interface for the Forex analysis agent.

Usage example::

    python -m forex_agent.main --symbol EURUSD --interval 60min
"""
import argparse
import os
from dotenv import load_dotenv
from engine import analyze_symbol


def main():
    parser = argparse.ArgumentParser(description="Forex analysis agent")
    parser.add_argument("--symbol", required=True, help="Ticker symbol, e.g., EURUSD")
    parser.add_argument("--interval", default="60min", help="Alpha Vantage interval (1min,5min,15min,30min,60min)")
    parser.add_argument("--outputsize", default="compact", choices=["compact", "full"], help="Number of data points to fetch")
    args = parser.parse_args()

    # Load API key from .env (if present)
    load_dotenv()

    result = analyze_symbol(args.symbol, interval=args.interval, outputsize=args.outputsize)
    # Pretty‑print the structured output
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
