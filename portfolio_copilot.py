#!/usr/bin/env python3
"""
BNB Portfolio Copilot (v2) — a Data & Analysis agent for Binance Agent OS.

What it does, beyond a single-point DCA check:
  1. Computes a real weighted-average cost basis across ALL your declared buys
     (not just "last buy") — grouped per asset, so it works for a whole portfolio.
  2. Pulls 7-day and 30-day moving averages via Binance's public klines endpoint,
     so you know if the current price is above/below its recent trend, not just
     "up or down since I bought."
  3. Works for any symbol(s), not just BNB — driven entirely by positions.json.
  4. Only pushes a Telegram alert when the move crosses a threshold you set —
     avoids notification spam, and is what turns this from "a script I run"
     into "a workflow that runs itself."

Setup:
    cp positions.example.json positions.json
    # edit positions.json with your real buys
    pip install requests

Run:
    python portfolio_copilot.py

Optional — enable Telegram alerts:
    export TELEGRAM_BOT_TOKEN="..."
    export TELEGRAM_CHAT_ID="..."
    python portfolio_copilot.py
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime

import requests

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def load_positions(path: str = "positions.json") -> dict:
    if not os.path.exists(path):
        print(f"No {path} found. Copy positions.example.json to {path} and fill in your buys.",
              file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)


def get_current_price(symbol: str) -> float:
    resp = requests.get(BINANCE_TICKER_URL, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["price"])


def get_moving_average(symbol: str, days: int) -> float:
    """Average close price over the last `days` daily candles."""
    resp = requests.get(
        BINANCE_KLINES_URL,
        params={"symbol": symbol, "interval": "1d", "limit": days},
        timeout=10,
    )
    resp.raise_for_status()
    candles = resp.json()
    closes = [float(c[4]) for c in candles]
    return sum(closes) / len(closes) if closes else 0.0


def weighted_avg_cost(buys: list) -> tuple:
    """Returns (weighted_avg_price, total_amount, total_cost)."""
    total_cost = sum(b["buy_price"] * b["amount"] for b in buys)
    total_amount = sum(b["amount"] for b in buys)
    avg_price = total_cost / total_amount if total_amount else 0.0
    return avg_price, total_amount, total_cost


def verdict(change_pct: float) -> str:
    if change_pct >= 10:
        return "Strongly in the green — well above your average cost."
    if change_pct >= 3:
        return "Comfortably in the green."
    if change_pct >= -3:
        return "Roughly flat — nothing dramatic either way."
    if change_pct >= -10:
        return "Underwater, but within normal short-term noise."
    return "Meaningfully underwater — worth noting before your next buy, not a reason to panic."


def trend_note(current: float, avg_7d: float, avg_30d: float) -> str:
    vs_7d = (current - avg_7d) / avg_7d * 100
    vs_30d = (current - avg_30d) / avg_30d * 100
    if vs_7d > 0 and vs_30d > 0:
        return f"Trading above both its 7d ({vs_7d:+.1f}%) and 30d ({vs_30d:+.1f}%) average — short-term strength."
    if vs_7d < 0 and vs_30d < 0:
        return f"Below both its 7d ({vs_7d:+.1f}%) and 30d ({vs_30d:+.1f}%) average — short-term weakness."
    return f"Mixed signal — {vs_7d:+.1f}% vs 7d avg, {vs_30d:+.1f}% vs 30d avg."


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return  # Telegram not configured — silently skip, still print to console
    try:
        requests.post(
            TELEGRAM_API_URL.format(token=token),
            data={"chat_id": chat_id, "text": message},
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"Telegram send failed (non-fatal): {e}", file=sys.stderr)


def main():
    config = load_positions()
    threshold = config.get("alert_threshold_pct", 3.0)

    by_symbol = defaultdict(list)
    for pos in config["positions"]:
        by_symbol[pos["symbol"]].append(pos)

    report_lines = [f"Portfolio Copilot — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"]
    alerts = []

    for symbol, buys in by_symbol.items():
        try:
            current = get_current_price(symbol)
            avg_7d = get_moving_average(symbol, 7)
            avg_30d = get_moving_average(symbol, 30)
        except requests.RequestException as e:
            print(f"Skipping {symbol} — couldn't fetch data: {e}", file=sys.stderr)
            continue

        avg_cost, total_amount, total_cost = weighted_avg_cost(buys)
        change_pct = (current - avg_cost) / avg_cost * 100
        current_value = current * total_amount
        pnl = current_value - total_cost

        report_lines.append(f"\n{symbol}")
        report_lines.append(f"  Weighted avg cost: ${avg_cost:.2f}  (across {len(buys)} buy(s))")
        report_lines.append(f"  Current price: ${current:.2f}")
        report_lines.append(f"  Change vs avg cost: {change_pct:+.2f}%  (P&L: ${pnl:+.2f})")
        report_lines.append(f"  {trend_note(current, avg_7d, avg_30d)}")
        report_lines.append(f"  Verdict: {verdict(change_pct)}")

        if abs(change_pct) >= threshold:
            alerts.append(f"{symbol}: {change_pct:+.2f}% vs your avg cost — {verdict(change_pct)}")

    report = "\n".join(report_lines)
    print(report)

    if alerts:
        send_telegram("Portfolio Copilot alert:\n" + "\n".join(alerts))


if __name__ == "__main__":
    main()
