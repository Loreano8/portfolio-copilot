# BNB Portfolio Copilot 🛡️📊

An AI agent, built on **Binance Agent OS**, that turns "how's my DCA doing?"
into a real **Data & Analysis** workflow: weighted-average cost basis,
market trend context, and automated daily alerts — no manual checking required.

## Why

I've been DCA'ing into BNB for a while, but I never actually checked whether
my buys made sense relative to the market — I just executed on schedule.
This project closes that gap, and does it the way Binance's own Agent OS
page describes "Track Your Portfolio": balances, positions, and market
movements, tracked in real time, within limits I set.

## What it does

- **Weighted-average cost basis** across *all* your declared buys per asset
  (not just your last one) — the number that actually matters for a real
  DCA strategy.
- **Market trend context** — compares the current price to its 7-day and
  30-day moving averages via Binance's public klines endpoint, so you know
  if you're buying into strength or weakness, not just up/down since your
  own buy.
- **Multi-asset** — works for any symbol(s) you track, driven by a simple
  `positions.json` file.
- **Automated daily alerts** — a GitHub Actions workflow runs the check
  every day and pushes a Telegram message, but *only* when the move crosses
  a threshold you set. No spam, no manual checking.

## How it works

### 1. As an Agent OS conversation (no code)

Connect Claude (or ChatGPT) to Binance via Agent OS:

```
claude mcp add binance-mcp-server --transport http https://agent.binance.com/mcp/agentic
```

(Or via claude.ai → Customize → Connectors → Add custom connector →
`https://agent.binance.com/mcp/agentic`)

Then ask:

```
How's my BNB DCA doing? My last buy was $706.48 on Aug 27.
```

**Real output from this project's own testing (Aug 27 – Sep 2, 2026):**

```
Last buy: $706.48 (Aug 27)
Current spot: $689.34
Change: -2.43%
Verdict: Slightly underwater since your last buy — nothing dramatic, just a normal short-term dip.
```

### 2. As a standalone, automated agent (the real workflow)

`portfolio_copilot.py` runs the same logic — plus weighted cost basis and
trend context — using Binance's public REST API. No API key, no LLM
required for the check itself.

```bash
cp positions.example.json positions.json
# edit positions.json with your real buys
pip install requests
python portfolio_copilot.py
```

**Set it to run itself, every day, automatically:**

1. Fork/push this repo to your own GitHub account.
2. Add two repo secrets (Settings → Secrets and variables → Actions):
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
3. The included workflow (`.github/workflows/daily-check.yml`) runs every
   day at 08:00 UTC and pushes a Telegram alert if any position moves past
   your `alert_threshold_pct`.

That's the difference between "a prompt I remember to run" and an agent
that actually watches the market for me.

## What I actually learned building this (from a full week testing Agent OS)

- Setup takes minutes — no API keys to manage on the chat side, permissions
  are explicit and revocable.
- The agent refused to guess a price when Binance's API was rate-limited,
  rather than pulling a stale number from a web search. Small thing, but
  it's the difference between a tool you can trust and one that just
  sounds confident.
- Convert and Margin actions were consistently blocked on my account with
  a restricted-country/IP error, even after the margin account showed as
  activated — Spot and Futures worked every time. Worth knowing if your
  use case depends on those specific products.
- Agent OS conversations can't run on a schedule by themselves — that's
  exactly why this repo exists as a standalone, automatable script.

## Files

- `portfolio_copilot.py` — the real workflow: weighted cost basis, trend
  analysis, multi-asset, Telegram alerts
- `positions.example.json` — copy to `positions.json` and fill in your buys
- `agent_prompt.md` — the Agent OS prompt template for the chat version
- `.github/workflows/daily-check.yml` — runs the check automatically, every day

## Disclaimer

Not financial advice. This is a personal tracking tool, not a trading signal.
