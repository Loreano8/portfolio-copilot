---
name: portfolio-copilot
description: A Binance Agent OS skill for DCA and portfolio health checks — weighted-average cost basis, market trend, order-book context, dip/breakout signal, DCA scheduling, and optional scheduled-buy execution (manual or opt-in auto mode). Use whenever the user asks "how's my [asset] DCA doing", wants a portfolio health check, gives you a list of buys and asks for their real average cost, or asks to set up/execute their recurring DCA buys.
---

# Portfolio Copilot

A reusable skill for Binance Agent OS. When loaded, it teaches the agent
how to answer one question properly — *"is my DCA holding up?"* — with a
real weighted-average cost basis and market context, not just a single
price comparison.

## When to use this skill

- User asks "how's my [asset] DCA doing"
- User gives a list of buys (price, date, amount) and wants their real
  average cost or gain/loss
- User asks for a portfolio health check or market-context comparison

## Remembering things across sessions

The first time a user gives you their buys for an asset, save them (price,
date, amount) to memory. On later requests, if they just ask "how's my
[asset] DCA doing" without repeating the numbers, use what's saved instead
of asking again. If they mention a new buy, add it rather than replacing
the list. If nothing is saved yet, ask once for the full buy history.

Also save, if the user provides them: their DCA cadence (for check D),
any dip-alert threshold (for check E), and the highest price observed so
far (for check F, update this automatically each time a new high appears —
no need to ask the user for it).

## Core workflow

1. **Get the buys.** Use what's saved in memory, or collect price, date,
   and amount for each buy if this is the first time — don't assume only
   the most recent one matters.

2. **Compute the weighted-average cost basis yourself:**
   ```
   weighted_avg = sum(price_i * amount_i) / sum(amount_i)
   ```

3. **Fetch live data via the Binance MCP Server.** Use `spot.tickerPrice`
   for the current price and `spot.klines` for 7-day and 30-day history.
   Call each symbol separately — a single batched call with multiple
   symbols can be rejected by the API depending on formatting; one call
   per symbol is more reliable.

4. **Compute** % change vs weighted-average cost, $ P&L, and whether the
   current price is above/below its own recent trend.

5. **Give a plain-language verdict**, calibrated to the size of the move
   (small: within ~3% — flat/normal noise; moderate: 3–10% — clear
   direction, still normal; large: >10% — flagged clearly, still not advice).

6. **Always close with a one-line disclaimer** — this is portfolio math,
   not financial advice.

## Enhanced checks

These use the same Binance MCP Server market-data access as the core
workflow — no extra tools required beyond what's already connected.

### A. Order-book pulse
When a move is large enough to be worth explaining, call `spot.depth` and
note whether the book looks like a normal spread or is visibly
thin/imbalanced — this tells the user whether a dip reflects real selling
pressure or just low liquidity at that moment.

### B. Relative strength vs. the market
Fetch BTC's % change over the same window (`spot.ticker24hr` and
`spot.klines` for BTCUSDT) and compare. A DCA position that's down 3%
while BTC is down 8% is a very different story than one down 3% while
BTC is flat — say which one it is.

### C. Publish the digest (if the `square-post` skill is available)
If the user asks to share the result, offer to turn the report into a
short Binance Square post — headline number, verdict, one-line context.
Always show the draft and get explicit confirmation before publishing.

### D. DCA schedule reminder
If the user tells you their DCA cadence (e.g. "I buy every 2 weeks"), save
it to memory alongside their buys. On each check, compute days since the
last buy and say plainly whether today is on-schedule, early, or overdue
for their next buy — a scheduling fact, not a suggestion to act. If no
cadence is saved, skip this section rather than guessing one.

### E. Dip-threshold flag
If the user sets a threshold (e.g. "flag me if it drops more than 10% from
my last buy"), save it. On each check, state clearly whether the current
price has crossed that threshold — "crossed" or "not crossed," with the
exact number. This is a factual threshold check, not a buy/sell signal;
never follow it with a recommendation, only the fact.

### F. All-time-high tracking and drawdown
Track the highest price observed for the asset across checks (store it in
memory, update it if a new high is seen). Report the current drawdown from
that high (`(current - high) / high * 100`) alongside the drawdown from
the user's own cost basis — these are two different numbers and both are
useful: one shows market context, the other shows personal P&L.

### G. Dip vs. breakout signal
Compute a 20-period simple moving average from `spot.klines` (choose a
consistent interval, e.g. daily). Classify the current price as a
**dip** if it's more than ~1.5% below the SMA and the 24h change isn't a
sharp drop (worse than -8%); as **extended/breakout** if it's more than
~1.5% above the SMA, or flag a sharp drop separately if 24h change is
worse than -8%. Report this as a descriptive classification only — never
follow it with a buy/sell instruction.

### H. Real balance cross-check (if Account scope is available)
Optionally check the asset's actual free balance in the Agentic
sub-account and compare it to the sum of the user's declared buy amounts.
If they don't match, say so plainly (could mean a sale, an internal
transfer, or a buy that wasn't mentioned) rather than silently trusting
either number over the other.

### I. Volatility context
Using the last 7 days of `spot.klines`, compute each day's high-low range
as a % of price, and average it. Compare today's move to that average —
say whether today's move is typical or larger than the asset's recent
normal range.

### J. Portfolio-wide view (multi-asset)
If the user tracks more than one asset, also report a combined total:
overall $ P&L across all tracked assets, and which one moved the most
today. Skip this section entirely if only one asset is tracked.

### K. Funding-rate context (if the asset has a futures market)
Note the current funding rate's sign and rough magnitude as market
context — persistently positive funding suggests long-heavy positioning,
persistently negative suggests the opposite. Present this as context only,
never as a trading signal.

### L. Time in position
Report how many days have passed since the user's first buy of the asset
— simple date-difference context, useful for framing how "young" or
"seasoned" the position is.

### M. Scheduled buy — propose and execute (manual mode, default)
When check D shows today is a scheduled DCA day, offer to place the buy.
Restate the exact order (symbol, amount, order type — market) and wait
for explicit confirmation in a separate message before calling
`spot.newOrder`. Never place the order in the same turn as the proposal.

### N. Auto-execute mode (opt-in only, explicit standing authorization)
Only enable this if the user unambiguously says something like "execute
my scheduled DCA buys automatically, don't ask me each time." Before
turning it on:

1. Restate the exact terms — asset, fixed $ amount per buy, cadence — and
   get the user's confirmation on this restatement. This one confirmation
   is the only gate; there is no separate confirmation per future buy.
2. Save the authorization and its exact terms to memory.

Once enabled, on each scheduled day (including inside an unattended
Routine run with no human present):
- Execute the buy automatically using **only** the exact saved terms —
  never a different amount, asset, or cadence than what was confirmed.
- Always report what happened (filled amount, price, new balance) — never
  execute silently without a record the user can see later.
- If the sub-account balance is insufficient, skip the buy and report
  that plainly rather than partially filling or guessing an amount.
- Every report produced while auto-mode is active should state clearly
  that auto-buy is ON, so it's never silently forgotten.
- The user can revoke this at any time by saying so ("stop auto-buying",
  "back to asking me first") — treat that as immediate and unconditional.
- Never use this authorization for anything beyond the exact confirmed
  scheduled buy — no Convert, no Margin, no other symbol, no size increase.

## Example

**User (first time):** "I've bought BNB twice: \$706.48 on Aug 27 and
\$684.60 on Sep 2, same amount each time. How's it doing, and is this dip
BNB-specific or market-wide?"

**Agent should:**
1. Save both buys to memory.
2. Compute weighted avg: (706.48 + 684.60) / 2 = \$695.54
3. Fetch current BNBUSDT price + 7d/30d trend via `spot.tickerPrice` /
   `spot.klines`
4. Fetch BTC's % change over the same window (relative strength check)
5. Report: weighted avg cost, current price, % change, \$ P&L, trend note,
   relative-strength note, one-line verdict, disclaimer

**User (later session):** "How's my BNB DCA doing?"

**Agent should:** use the saved buys instead of asking again, and repeat
steps 3–5 above.

## Notes from real-world testing

- Binance's API can rate-limit; if it does, don't fall back to a stale web
  search for a price — say so and offer to retry, rather than guessing.
- A batched price request for multiple symbols in one call can fail with
  an "Illegal characters" error depending on how it's formatted — retrying
  as separate calls per symbol resolves it. This ran successfully as a
  scheduled Claude Code Routine, which retried automatically and still
  produced a correct report.
- Convert and Margin actions can be blocked by account/region restrictions
  independent of anything the user did wrong — explain plainly rather than
  retrying silently if this comes up in a related request.
- Core and enhanced checks A/B only need **Market data** (read) and
  optionally **Account** scopes — no Trade or Transfer scope required.
- Check C depends on the `square-post` skill being available in the
  user's session — if it isn't, skip that section rather than failing
  the whole response.
- Checks D, E, and F are opt-in — only run them once the user has given
  the relevant input (cadence, threshold). Never invent a schedule or
  threshold on the user's behalf.
- Check H needs Account scope; check K only applies to assets with a
  futures market. Skip either silently if not applicable rather than
  erroring.
- Check J only makes sense once more than one asset is being tracked —
  don't force a "portfolio view" for a single-asset check.
- Checks M and N require Trade scope, unlike every other check in this
  skill. M and N are the only checks that ever move real funds — treat
  them with the same discipline the rest of this skill applies to
  everything else: restate before acting, and for N, never act outside
  the exact terms the user confirmed.
- This skill requires no installation beyond pasting it into Claude's
  Skills settings — no terminal, no Node.js, no extra setup. It also
  works unattended as a Claude Code Routine (schedule trigger, Binance
  connector attached) for a fully automated daily check.
