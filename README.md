# Portfolio Copilot

A Binance Agent OS skill that turns "how's my DCA doing?" into a real
**Data & Analysis** workflow — weighted-average cost basis, market trend
context, and order-book pulse, straight from a conversation with your
agent. No terminal, no installation, no code.

## Why

I've been DCA'ing into BNB for a while, but I never actually checked
whether my buys made sense relative to the market — I just executed on
schedule. This skill closes that gap.

## How to use it (5 minutes, no coding)

**Step 1 — Connect Claude to Binance**
1. Go to [claude.ai](https://claude.ai) → **Customize** → **Connectors**
2. Click **Add custom connector**
3. Paste this URL: `https://agent.binance.com/mcp/agentic`
4. Click **Connect** and authorize with your Binance account

**Step 2 — Add this skill**
1. Still in **Customize**, go to **Skills** → **Add skill**
2. Open [`SKILL.md`](./SKILL.md) in this repo, copy its full content
3. Paste it into the skill editor and save

**Step 3 — Use it**
Start a new chat, make sure the Binance connector is active (check the
**+** menu next to the message box), then ask:

```
How's my BNB DCA doing? My last buy was $706.48 on Aug 27.
```

Or with multiple buys, for a real weighted-average cost:

```
I've bought BNB twice: $706.48 on Aug 27 and $684.60 on Sep 2, same amount each time. How's it doing?
```

**Real output from this project's own testing (Aug 27 – Sep 2, 2026):**
```
Your BNB DCA:
Buy 1: $706.48 (Aug 27)
Buy 2: $684.60 (Sep 2)
Average cost: ~$695.38 per BNB
Current price: $711.12
Result: +2.26% gain on your blended position.
```

## What it can do

- **Weighted-average cost basis** across all your declared buys — not
  just the last one
- **Market trend context** — 7-day and 30-day price comparison
- **Order-book pulse** — tells you if a move reflects real pressure or
  just thin liquidity
- **Relative strength vs. BTC** — is this asset moving on its own, or
  with the whole market
- **Draft a Binance Square post** summarizing the result, if you ask —
  always shown for approval before publishing

## What I learned testing Agent OS

- Setup takes minutes — no API keys to manage, permissions are explicit
  and revocable.
- The agent refused to guess a price when Binance's API was rate-limited,
  rather than pulling a stale number from a web search.
- Convert and Margin actions were consistently blocked on my account with
  a restricted-country/IP error, even after the margin account showed as
  activated — Spot and Futures worked every time.

## Disclaimer

Not financial advice. This is a personal tracking tool, not a trading signal.
