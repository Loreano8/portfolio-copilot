#!/usr/bin/env python3
"""
BNB DCA Guardian — standalone version.

Replicates the Agent OS "how's my DCA doing" check using Binance's
public REST API (no API key required — this only reads public market data).

Usage:
    python dca_guardian.py --last-buy-price 706.48 --symbol BNBUSDT
"""

import argparse
import sys
import requests

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"


def get_current_price(symbol: str) -> float:
    resp = requests.get(BINANCE_TICKER_URL, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return float(data["price"])


def verdict(change_pct: float) -> str:
    if change_pct >= 5:
        return "Comfortably in the green — your last buy is looking good."
    if change_pct >= 0:
        return "Roughly flat to slightly up — nothing dramatic either way."
    if change_pct >= -5:
        return "Slightly underwater since your last buy — nothing dramatic, just a normal short-term dip."
    return "Meaningfully underwater — worth knowing before your next buy, not a reason to panic."


def main():
    parser = argparse.ArgumentParser(description="Check your BNB (or any pair) DCA health.")
    parser.add_argument("--last-buy-price", type=float, required=True,
                         help="The price you paid on your last buy, e.g. 706.48")
    parser.add_argument("--symbol", type=str, default="BNBUSDT",
                         help="Trading pair symbol, default BNBUSDT")
    args = parser.parse_args()

    try:
        current_price = get_current_price(args.symbol)
    except requests.RequestException as e:
        print(f"Could not fetch live price from Binance: {e}", file=sys.stderr)
        sys.exit(1)

    change_pct = (current_price - args.last_buy_price) / args.last_buy_price * 100

    print(f"Last buy: ${args.last_buy_price:.2f}")
    print(f"Current spot ({args.symbol}): ${current_price:.2f}")
    print(f"Change: {change_pct:+.2f}%")
    print(f"Verdict: {verdict(change_pct)}")


if __name__ == "__main__":
    main()
