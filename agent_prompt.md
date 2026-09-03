# Agent OS Prompt Template — Portfolio Copilot

## One-time setup (run once per conversation/agent)

```
Set up a recurring check for me: whenever I ask "how's my portfolio doing",
take my declared buys for one or more assets, compute the weighted-average
cost basis per asset, compare it to the current spot price, and give me a
gain/loss percentage plus a one-line verdict for each.
```

## Daily/weekly use — single asset

```
How's my BNB DCA doing? My last buy was $<PRICE> on <DATE>.
```

## Daily/weekly use — multiple buys, real weighted cost basis

```
I've bought BNB twice: $706.48 on Aug 27 and $684.60 on Sep 2, same amount
each time. What's my real weighted-average cost, and how does it compare
to the current spot price?
```

## Variant — generic, any asset or portfolio

```
Here are my buys for <ASSET>: <list of price/date/amount>.
Compute my weighted-average cost, compare it to current spot, and also
tell me if the price is trading above or below its 7-day and 30-day
average — I want context, not just a single comparison point.
```

## Notes from real testing

- Works reliably with Spot market data.
- If Binance's API is rate-limited, a well-behaved agent should refuse to
  guess from a stale web search rather than give you a wrong number.
- Agent OS conversations aren't a background job — they can't ping you on
  a schedule by themselves. For real automation (daily checks, alerts),
  use `portfolio_copilot.py` + the included GitHub Actions workflow, which
  runs on its own and pushes a Telegram alert only when a move crosses
  your threshold.
