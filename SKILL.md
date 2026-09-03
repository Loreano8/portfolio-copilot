---
name: portfolio-copilot
description: A Binance Agent OS skill for DCA and portfolio health checks — weighted-average cost basis, market trend, order-book context, and optional Square publishing. Use whenever the user asks "how's my [asset] DCA doing", wants a portfolio health check, or gives you a list of buys and asks for their real average cost.
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

## Core workflow

1. **Collect the buys.** Ask for price, date, and amount for each buy if
   not already given — don't assume only the most recent one matters.

2. **Compute the weighted-average cost basis yourself:**
   ```
   weighted_avg = sum(price_i * amount_i) / sum(amount_i)
   ```

3. **Fetch live data via the Binance MCP Server:**
   - Current spot price
   - 7-day and 30-day price context (candlestick/kline history)

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
When a move is large enough to be worth explaining, pull the order book
and note whether it looks like a normal spread or a visibly thin/imbalanced
book — this tells the user whether a dip reflects real selling pressure or
just low liquidity at that moment.

### B. Relative strength vs. the market
Fetch BTC's % change over the same window and compare. A DCA position that's
down 3% while BTC is down 8% is a very different story than one down 3%
while BTC is flat — say which one it is.

### C. Publish the digest (if the `square-post` skill is available)
If the user asks to share the result, offer to turn the report into a
short Binance Square post — headline number, verdict, one-line context.
Always show the draft and get explicit confirmation before publishing.

## Example

**User:** "I've bought BNB twice: \$706.48 on Aug 27 and \$684.60 on Sep 2,
same amount each time. How's it doing, and is this dip BNB-specific or
market-wide?"

**Agent should:**
1. Compute weighted avg: (706.48 + 684.60) / 2 = \$695.54
2. Fetch current BNBUSDT price + 7d/30d trend via Binance MCP
3. Fetch BTC's % change over the same window (relative strength check)
4. Report: weighted avg cost, current price, % change, \$ P&L, trend note,
   relative-strength note, one-line verdict, disclaimer

## Notes from real-world testing

- Binance's API can rate-limit; if it does, don't fall back to a stale web
  search for a price — say so and offer to retry, rather than guessing.
- Convert and Margin actions can be blocked by account/region restrictions
  independent of anything the user did wrong — explain plainly rather than
  retrying silently if this comes up in a related request.
- Core and enhanced checks A/B only need **Market data** (read) and
  optionally **Account** scopes — no Trade or Transfer scope required.
- Check C depends on the `square-post` skill being available in the
  user's session — if it isn't, skip that section rather than failing
  the whole response.
- This skill requires no installation beyond pasting it into Claude's
  Skills settings — no terminal, no Node.js, no extra setup.
