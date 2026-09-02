# Agent OS Prompt Template — BNB DCA Guardian

## One-time setup (run once per conversation/agent)

```
Set up a recurring check for me: whenever I ask "how's my BNB DCA doing",
compare my last buy price to the current BNB spot price and give me a
gain/loss percentage plus a one-line verdict.
```

## Daily/weekly use

```
How's my BNB DCA doing? My last buy was $<PRICE> on <DATE>.
```

## Variant — generic, any asset

```
How's my <ASSET> DCA doing? My last buy was $<PRICE> on <DATE>.
Compare it to the current spot price, give me the gain/loss %, and a
one-line verdict — no financial advice, just the numbers and a plain
read of them.
```

## Notes from real testing

- Works reliably with Spot market data.
- If Binance's API is rate-limited, a well-behaved agent should refuse to
  guess from a stale web search rather than give you a wrong number.
- This is a saved prompt, not a background job — Agent OS agents can't
  ping you on a schedule by themselves (see `dca_guardian.py` for a
  script-based alternative that can be cron'd).
