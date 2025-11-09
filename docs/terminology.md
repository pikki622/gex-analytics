# Gamma Exposure Glossary & Terminology Guide

## Table of Contents
- [Core Concepts](#core-concepts)
- [Greek Letters Explained](#greek-letters-explained)
- [Market Mechanics](#market-mechanics)
- [Technical Terms](#technical-terms)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Decision Trees](#decision-trees)

---

## Core Concepts

### Gamma Exposure (GEX)
**Technical**: The rate of change of delta with respect to the underlying price, multiplied by open interest and contract multiplier.

**Plain English**: How many shares/contracts market makers need to buy or sell when the price moves. Think of it as "hedging pressure" - the bigger the number, the more trading that happens automatically.

**Example**: If SPX has +$15Bn gamma exposure for a 1% move, dealers need to trade $15 billion worth of stock/futures if SPX moves 1%.

### Gamma Flip Point
**Technical**: The price level where net gamma exposure crosses from positive to negative or vice versa.

**Plain English**: The "personality change" price. Above this price, the market is calm (dealers stabilize it). Below this price, the market gets wild (dealers make moves bigger).

**Real Example**:
- SPX at $6,700 (below flip at $6,770) = 🔴 Volatile market
- SPX rallies to $6,780 (above flip) = 🟢 Calm market

### Negative Gamma Zone
**Technical**: Price region where dealers' net gamma exposure is negative, requiring them to sell into declines and buy into rallies.

**Plain English**: The "gasoline on fire" zone. When prices drop, automatic selling makes them drop more. When prices rise, automatic buying makes them rise more.

**What it means for you**:
- ✅ Good for: Trend following, momentum trading
- ❌ Bad for: Buying dips, selling rallies
- ⚠️ Expect: Larger moves than normal

### Positive Gamma Zone
**Technical**: Price region where dealers' net gamma exposure is positive, requiring them to buy into declines and sell into rallies.

**Plain English**: The "shock absorber" zone. The market has built-in brakes - when it tries to fall, automatic buying supports it. When it tries to rally, automatic selling caps it.

**What it means for you**:
- ✅ Good for: Range trading, selling options premium
- ❌ Bad for: Breakout trading
- ⚠️ Expect: Prices to revert to the mean

---

## Greek Letters Explained

### Delta (Δ)
**Technical**: The rate of change of option price with respect to underlying price.

**Plain English**: How much an option's value changes when the stock moves $1. Delta of 0.50 means the option gains $0.50 when stock gains $1.

### Gamma (Γ)
**Technical**: The rate of change of delta with respect to underlying price.

**Plain English**: How fast delta changes. High gamma means the option becomes much more sensitive to stock moves very quickly. It's the "acceleration" of option prices.

### Theta (Θ)
**Technical**: The rate of time decay of option value.

**Plain English**: How much money an option loses each day just from time passing. Like ice cream melting - it loses value even if nothing else changes.

### Vega (ν)
**Technical**: The sensitivity of option price to changes in implied volatility.

**Plain English**: How much an option's price changes when fear/uncertainty in the market changes. Higher fear = higher option prices.

---

## Market Mechanics

### Market Maker / Dealer
**Who they are**: Large financial institutions (Citadel, Susquehanna, etc.) that provide liquidity by constantly buying and selling options.

**What they do**:
- Sell options to traders who want them
- Stay "neutral" by hedging with stock/futures
- Make money from the bid-ask spread, not direction

**Why it matters**: Their hedging creates the gamma flows we track. They're like a giant robot trader that must buy/sell based on math, not opinion.

### Delta Hedging
**Technical**: The practice of offsetting option delta exposure with underlying shares.

**Plain English**: When a dealer sells a call option, they buy stock to stay neutral. If the stock goes up, they buy more. If it goes down, they sell some. This constant rebalancing is what creates gamma flows.

**Example**:
1. Dealer sells 100 call options (delta = 0.5 each)
2. Must buy 5,000 shares to hedge (100 × 100 × 0.5)
3. Stock rises, delta becomes 0.6
4. Must buy 1,000 more shares (100 × 100 × 0.1)

### ADTV (Average Daily Trading Volume)
**Technical**: 20-day average of daily trading volume in dollar terms.

**Plain English**: How much normally trades in a day. We compare gamma flows to this to understand if dealer hedging will significantly impact the market.

**Why it matters**:
- Gamma flow = 5% of ADTV → Barely noticeable
- Gamma flow = 30% of ADTV → Major market impact
- Gamma flow > 50% of ADTV → Potential for extreme moves

### Open Interest (OI)
**Technical**: The total number of outstanding option contracts that haven't been closed.

**Plain English**: How many "bets" are currently active in the options market. High OI at a strike price creates a "magnet" effect - prices tend to gravitate toward big OI strikes.

---

## Technical Terms

### 0DTE (Zero Days to Expiration)
**What it is**: Options expiring the same day.

**Why it matters**: These have extreme gamma - small moves create huge hedging flows. They're like nitroglycerin for markets.

### Pin Risk / Pinning
**Technical**: The tendency for stock prices to gravitate toward strikes with high open interest near expiration.

**Plain English**: Big option positions act like magnets for stock prices. If there's huge OI at $6,750, the price often "sticks" near there on expiration day.

### Implied Volatility (IV)
**Technical**: The market's expectation of future volatility derived from option prices.

**Plain English**: How much the market thinks the stock will move. High IV = expecting big moves. It's the market's "fear gauge."

### Realized Volatility
**Technical**: The actual historical volatility of the underlying.

**Plain English**: How much the stock actually moved (vs. what options predicted). If realized < implied, option sellers win.

### bps (Basis Points)
**What it is**: 1 basis point = 0.01% = 0.0001

**Examples**:
- 10bps = 0.1% move
- 100bps = 1% move
- 500bps = 5% move

**Usage**: SPX moving from $6,700 to $6,707 = 10bps move

---

## Frequently Asked Questions

### Q: Why is positive gamma number but negative gamma zone confusing?

**A**: This is industry convention that trips everyone up!

- **+$1.5Bn gamma** = The number is positive (dealers are long gamma)
- **"Negative gamma zone"** = The EFFECT on market (below flip point)

Think of it this way:
- The NUMBER tells you dealer positioning
- The ZONE tells you market behavior

### Q: How accurate are gamma flip points?

**A**: About 70-80% reliable as support/resistance levels. They work best when:
- Large gamma magnitude (> $1Bn for SPX)
- Clear flip point (not multiple crossings)
- Normal market conditions (not during major news)

### Q: Why do dealers have to hedge?

**A**: Regulations and risk management require them to stay "market neutral." They're not allowed to make directional bets with client positions. Think of them as forced traders - they MUST hedge whether they want to or not.

### Q: What's more important - spot gamma or the flip point?

**A**: Both matter, but differently:
- **Spot gamma** → How volatile TODAY will be
- **Flip point** → Where behavior CHANGES

If you're day trading, spot gamma matters more. If you're swing trading, the flip point is your key level.

### Q: Can gamma exposure predict market direction?

**A**: No, gamma doesn't predict direction - it predicts CHARACTER:
- Negative gamma = Trending market (amplified moves)
- Positive gamma = Rangebound market (dampened moves)

Direction comes from other factors (news, flows, sentiment).

---

## Decision Trees

### "Should I Trade Today?" Decision Tree

```
Current Gamma State?
├─ NEGATIVE GAMMA ZONE
│  ├─ Day Trading?
│  │  ├─ YES → Use momentum strategies, tight stops
│  │  └─ NO → Consider sitting out (high risk)
│  └─ Swing Trading?
│     ├─ Trending Market? → Go with trend
│     └─ Choppy Market? → Avoid (whipsaws likely)
│
└─ POSITIVE GAMMA ZONE
   ├─ Day Trading?
   │  ├─ YES → Fade extremes, mean reversion works
   │  └─ NO → Good for selling premium
   └─ Swing Trading?
      ├─ Near Support? → Good buying opportunity
      └─ Near Resistance? → Consider selling/shorting
```

### Position Sizing Based on Gamma

```
What's the Gamma Magnitude?
├─ EXTREME (>$2Bn SPX)
│  └─ Reduce size by 40-50%
├─ HIGH ($1-2Bn SPX)
│  └─ Reduce size by 25-35%
├─ MODERATE ($0.5-1Bn SPX)
│  └─ Normal position size
└─ LOW (<$0.5Bn SPX)
   └─ Can increase size by 20%

Are we near flip point?
├─ YES (within 0.5%)
│  └─ Reduce size additional 20% (regime change risk)
└─ NO
   └─ Use gamma-based sizing above
```

### Stop Loss Placement Guide

```
Current Market State?
├─ NEGATIVE GAMMA
│  ├─ With Trend
│  │  └─ Tight stops (0.5-0.8% for SPX)
│  └─ Against Trend
│     └─ Wide stops (1.5-2% for SPX) or avoid
│
└─ POSITIVE GAMMA
   ├─ At Range Extreme
   │  └─ Tight stops (0.3-0.5% for SPX)
   └─ Mid-Range
      └─ Normal stops (0.8-1% for SPX)
```

---

## Quick Reference Card

### 🔴 Red Flags (High Risk)
- Negative gamma > $1Bn
- Just crossed below flip point
- Gamma increasing rapidly
- Multiple indices negative
- Near 0DTE expiration

### 🟢 Green Lights (Lower Risk)
- Positive gamma zone
- Far from flip point
- Decreasing gamma magnitude
- After large expiration
- Low IV environment

### 📊 Key Levels to Watch Daily
1. **Gamma flip point** - Where behavior changes
2. **Current spot gamma** - Today's volatility expectation
3. **Distance to flip** - Risk of regime change
4. **Major OI strikes** - Potential pin levels
5. **Next expiration** - When gamma resets

---

## Glossary Updates

This document is a living guide. For updates or clarifications, please submit a PR or open an issue on GitHub.

*Last Updated: November 2024*

---

[← Back to README](../README.md) | [View Implementation Plan →](../IMPLEMENTATION_PLAN.md)