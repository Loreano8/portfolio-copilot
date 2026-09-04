# Portfolio Copilot

A Binance Agent OS skill built around one real habit: DCA'ing into BNB.
At its core, it's a **Data & Analysis** workflow — weighted-average cost
basis, market trend, order-book and volatility context — with an optional
layer that can also propose or (if you explicitly opt in) execute your
scheduled DCA buys.

## Why

I've been DCA'ing into BNB for a while, but I never actually checked
whether my buys made sense relative to the market — I just executed on
schedule. This skill closes that gap, and optionally closes the loop
entirely by handling the scheduled buy itself, always under an explicit
confirmation model.

## How to use it (5 minutes, no coding)

**Step 1 — Connect Claude to Binance**
1. Go to [claude.ai](https://claude.ai) → **Customize** → **Connectors**
2. Click **Add custom connector**
3. Paste this URL: `https://agent.binance.com/mcp/agentic`
4. Click **Connect** and authorize with your Binance account
5. If you want the optional buy-execution features, make sure the
   **Trade** scope is granted, not just Market data / Account — everything
   else in this skill only ever needs read access.

**Step 2 — Add this skill**
1. Still in **Customize**, go to **Skills** → **Add skill**
2. Open [`SKILL.md`](./SKILL.md) in this repo, copy its full content
3. Paste it into the skill editor and save

**Step 3 — Use it**
Start a new chat, make sure the Binance connector is active (check the
**+** menu next to the message box), then ask:

```
I've bought BNB twice: $706.48 on Aug 27 and $684.60 on Sep 2, same amount each time. How's it doing?
```

Once your buys are saved, later checks can just be:
```
How's my BNB DCA doing?
```

**Real output from this project's own testing (Aug 27 – Sep 3, 2026):**
```
Weighted avg cost: $695.54/BNB (Aug 27 @ $706.48, Sep 2 @ $684.60)
Current price: $720.77
P&L: +$25.23/BNB → +3.63%
24h: BNB +5.04%, BTC +4.99% — broad market move, not BNB-specific
Verdict: healthy, mild gain — normal range, nothing alarming.
```

## What it can do

**Analysis (read-only, no Trade scope needed):**
- Weighted-average cost basis across all your declared buys
- Market trend — 7-day and 30-day context, plus a dip/breakout signal
  based on a moving average
- Order-book pulse — real pressure vs. thin liquidity
- Relative strength vs. BTC — is this asset moving on its own, or with
  the whole market
- Volatility context — is today's move typical or unusual for this asset
- All-time-high tracking and drawdown
- Time in position
- Multi-asset portfolio view, if you track more than one asset
- Funding-rate context, for assets with a futures market
- Real balance cross-check against your declared buys (needs Account scope)
- Draft a Binance Square post summarizing the result, shown for approval
  before publishing

**Scheduling and execution (opt-in, needs Trade scope):**
- DCA schedule reminder — tells you if today is on-schedule, early, or
  overdue for your next buy
- Dip-threshold flag — states plainly if a price drop you defined has
  been crossed, as a fact, never as advice
- Scheduled-buy proposal — restates the exact order and waits for your
  explicit confirmation before placing it
- Optional auto-execute mode — only activates if you explicitly authorize
  a fixed asset, amount, and cadence; every run reports what happened,
  and you can revoke it at any time by asking

## Automation

This skill also works unattended as a **Claude Code Routine** — a native,
no-code scheduling feature (claude.ai/code/routines). Attach the Binance
connector, set a daily schedule, and it runs the same analysis on its own,
in the cloud, with no one at the keyboard. Tested and working — it
recovered on its own from a formatting error on a batched price request
by retrying per-symbol, and still produced a correct report.

## What I learned testing Agent OS

- Setup takes minutes — permissions are explicit and revocable.
- The agent refused to guess a price when Binance's API was rate-limited,
  rather than pulling a stale number from a web search.
- Convert and Margin actions were consistently blocked on my account with
  a restricted-country/IP error, even after the margin account showed as
  activated — Spot and Futures worked every time.

## Disclaimer

Not financial advice. The analysis features are portfolio math, not a
trading signal. The optional execution features place real orders with
real funds once you explicitly confirm or authorize them — review the
terms carefully before opting into auto-execute mode.
