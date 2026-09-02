# BNB DCA Guardian 🛡️

A tiny AI agent, built on **Binance Agent OS**, that answers one question honestly:

> "Is my last BNB DCA buy holding up?"

## Why

I've been DCA'ing into BNB for a while, but I never actually checked whether my buys made sense relative to the market — I just executed on schedule. This project turns that blind spot into a one-line health check, built on top of Binance Agent OS (MCP).

## How it works

There are two ways to run this — they use the exact same logic:

### 1. As an Agent OS conversation (no code)

Connect Claude (or ChatGPT) to Binance via Agent OS:

```
claude mcp add binance-mcp-server --transport http https://agent.binance.com/mcp/agentic
```

(Or via claude.ai → Customize → Connectors → Add custom connector → `https://agent.binance.com/mcp/agentic`)

Then set up the recurring check once:

```
Set up a recurring check for me: whenever I ask "how's my BNB DCA doing",
compare my last buy price to the current BNB spot price and give me a
gain/loss percentage plus a one-line verdict.
```

From then on, just ask:

```
How's my BNB DCA doing? My last buy was $706.48 on Aug 27.
```

**Real output from this repo's own testing (Aug 27–Sep 1, 2026):**

```
Last buy: $706.48 (Aug 27)
Current spot: $689.34
Change: -2.43%
Verdict: Slightly underwater since your last buy — nothing dramatic, just a normal short-term dip.
```

### 2. As a standalone script (no AI, no API key needed)

`dca_guardian.py` replicates the same check using Binance's public REST API — useful if you want this to run in a cron job, a Telegram bot, or anywhere without an LLM in the loop.

```bash
pip install requests
python dca_guardian.py --last-buy-price 706.48 --symbol BNBUSDT
```

## What I actually learned building this (from a full week testing Agent OS)

- Setup takes minutes — no API keys to manage, permissions are explicit and revocable.
- The agent refused to guess a price when Binance's API was rate-limited, rather than pulling a stale number from a web search. Small thing, but it's the difference between a tool you can trust and one that just sounds confident.
- Convert and Margin actions were consistently blocked on my account with a restricted-country/IP error, even though Spot and Futures worked every time. Worth knowing if your use case depends on those specific products.
- The "recurring check" isn't a true background job — Agent OS can't ping you on a schedule on its own. It's a saved prompt pattern you re-run, not a cron job. `dca_guardian.py` in this repo is the fix if you want actual automation.

## Files

- `dca_guardian.py` — standalone Python version of the check
- `agent_prompt.md` — the exact Agent OS prompt template used above

## Disclaimer

Not financial advice. This is a personal tracking tool, not a trading signal.
