from typing import List, Dict
from engine import analyze_symbol

def scan_symbols(symbols: List[str], interval: str = "60min", outputsize: str = "compact") -> Dict[str, dict]:

    results = {}

    for sym in symbols:
        try:
            results[sym.upper()] = analyze_symbol(
                sym.upper(),
                interval=interval,
                outputsize=outputsize
            )
        except Exception as exc:
            results[sym.upper()] = {
                "error": str(exc),
                "symbol": sym.upper()
            }

    return results