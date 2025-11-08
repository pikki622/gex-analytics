# Gamma Exposure (GEX) Profile Analysis Tool

A Python tool that analyzes options market gamma exposure for major indices, providing insights into market maker positioning and potential support/resistance levels.

## Table of Contents
- [How It Works](#how-it-works)
- [Key Concepts](#key-concepts)
- [Code Architecture](#code-architecture)
- [Available Tickers](#available-tickers)
- [Usage](#usage)
- [Output Charts](#output-charts)

## How It Works

This tool fetches real-time options data from CBOE (Chicago Board Options Exchange) and calculates the gamma exposure of market makers at different price levels. This helps identify:
- Where market makers need to hedge (buy/sell underlying)
- Potential support and resistance levels
- The "gamma flip" point where hedging behavior changes

### Workflow

1. **Data Fetching** (lines 32-34)
   - Connects to CBOE's delayed quotes API
   - Downloads complete options chain for the specified index
   - Extracts current spot price

2. **Data Processing** (lines 46-87)
   - Parses option symbols to extract strike prices and expiration dates
   - Separates calls and puts
   - Merges data into a unified DataFrame
   - Converts data types for calculations

3. **Gamma Calculations** (lines 90-98)
   - Calculates spot gamma exposure for each strike
   - Formula: `GEX = Unit Gamma × Open Interest × 100 × Spot² × 0.01`
   - Puts have negative gamma exposure (market makers are short puts)

4. **Gamma Profile Generation** (lines 138-173)
   - Simulates gamma at different spot prices
   - Uses Black-Scholes model for theoretical gamma values
   - Identifies the "gamma flip" point (zero gamma crossing)

5. **Visualization** (lines 100-206)
   - Generates 4 interactive charts showing different aspects of gamma exposure

## Key Concepts

### Gamma Exposure (GEX)
Gamma exposure represents the amount of shares market makers must buy or sell to maintain delta neutrality when the underlying price moves 1%.

- **Positive Gamma**: Market makers dampen volatility (buy dips, sell rallies)
- **Negative Gamma**: Market makers amplify volatility (sell dips, buy rallies)
- **Zero Gamma (Flip Point)**: Transition between stabilizing and destabilizing hedging flows

### Black-Scholes Gamma Calculation
The `calcGammaEx` function (lines 13-25) implements the Black-Scholes gamma formula:

```python
gamma = exp(-q*T) * norm.pdf(d1) / (S * vol * sqrt(T))
```

Where:
- `S`: Spot price
- `K`: Strike price
- `vol`: Implied volatility
- `T`: Time to expiration
- `r`: Risk-free rate (set to 0)
- `q`: Dividend yield (set to 0)

### Days to Expiration Handling
- Business days are calculated excluding weekends (line 142-143)
- 0DTE options are set to 1/262 year to avoid division by zero
- Monthly options are identified by third Friday detection (lines 27-29, 147-149)

## Code Architecture

### Main Components

1. **Option Greeks Calculator** (`calcGammaEx`)
   - Pure Black-Scholes implementation
   - Handles edge cases (zero time/volatility)
   - Returns dollar gamma exposure

2. **Data Parser**
   - Extracts components from CBOE option symbols
   - Format: `INDEX YYMMDD C/P STRIKE`
   - Example: `SPX241108C05500` = SPX Nov 8, 2024 Call at 5500

3. **Aggregation Engine**
   - Groups by strike price
   - Sums total gamma across all expirations
   - Handles "ex-next expiry" calculations

4. **Visualization Module**
   - 4 distinct chart types
   - Interactive matplotlib plots
   - Color-coded regions (red = negative gamma, green = positive)

## Available Tickers

The tool works with CBOE-listed index options through their free API. ETF options require a paid subscription.

### ✅ Working Tickers (Free Access)

| Ticker | Description | Current Spot Price |
|--------|-------------|-------------------|
| **SPX** | S&P 500 Index | ~$6,728 |
| **NDX** | NASDAQ-100 Index | ~$25,059 |
| **DJX** | Dow Jones Index (1/100th scale) | ~$469 |
| **RUT** | Russell 2000 Index | ~$2,432 |
| **VIX** | CBOE Volatility Index | ~$19 |
| **MXEA** | MSCI EAFE Index | ~$2,774 |
| **MXEF** | MSCI Emerging Markets Index | ~$1,381 |
| **XSP** | Mini-SPX Index (1/10th SPX) | ~$672 |
| **XND** | Mini-NDX Index (1/100th NDX) | ~$251 |
| **MRUT** | Mini-Russell 2000 Index (1/10th RUT) | ~$243 |

### ❌ Unavailable Without Subscription

ETF options (SPY, QQQ, IWM, etc.) return HTTP 403 errors and require a CBOE DataShop subscription ($380-2000+/month).

## Usage

### Setup with uv Package Manager

```bash
# Initialize project (already done)
uv init --no-readme

# Install dependencies
uv sync

# Run the original 1% gamma script
uv run python gammaProfileCommandLine.py SPX

# Run the 10bps (0.1%) gamma script with grid layout
uv run python gammaProfileCommandLine10bps.py NDX
```

### Available Scripts

1. **gammaProfileCommandLine.py** - Original version
   - Calculates gamma per 1% (100bps) move
   - Shows charts one at a time (close to see next)

2. **gammaProfileCommandLine10bps.py** - Enhanced version
   - Calculates gamma per 0.1% (10bps) move
   - Displays all 4 charts in a single grid
   - Better for precise hedging analysis

3. **test_tickers.py** - Ticker availability tester
   - Tests which tickers work with the API
   - Provides current spot prices

### Example Commands

```bash
# Analyze S&P 500 gamma (1% moves)
uv run python gammaProfileCommandLine.py SPX

# Analyze NASDAQ-100 gamma (10bps moves, grid view)
uv run python gammaProfileCommandLine10bps.py NDX

# Test all available tickers
uv run python test_tickers.py
```

## Output Charts

The tool generates 4 comprehensive visualizations:

### Chart 1: Total Gamma Exposure
- Bar chart showing net gamma at each strike price
- Helps identify key support/resistance levels
- Positive bars = net long gamma, Negative = net short gamma

### Chart 2: Open Interest Distribution
- Shows call OI above zero, put OI below zero
- Identifies where most options positions are concentrated
- Large OI strikes often act as "magnets" for price

### Chart 3: Gamma by Type (Calls vs Puts)
- Separates call gamma (positive) from put gamma (negative)
- Shows which side dominates at each strike
- Useful for understanding directional hedging flows

### Chart 4: Gamma Exposure Profile
- Line chart showing gamma across different spot prices
- Identifies the "gamma flip" point (zero crossing)
- Shows ex-next expiry and ex-monthly expiry profiles
- Red shading = negative gamma zone (volatility amplifying)
- Green shading = positive gamma zone (volatility dampening)

## Interpretation Guide

### Key Metrics
- **Total Gamma**: Net $ exposure market makers must hedge per 1% or 0.1% move
- **Gamma Flip**: Price where market maker hedging behavior reverses
- **Negative Gamma**: Below flip point, dealers sell into weakness, buy into strength
- **Positive Gamma**: Above flip point, dealers buy into weakness, sell into strength

### Trading Implications
- Large positive gamma = Lower volatility expected (dampening effect)
- Large negative gamma = Higher volatility expected (amplifying effect)
- Gamma flip point often acts as pivot level for intraday price action
- High OI strikes can act as support/resistance due to pinning effects

## Requirements

- Python 3.8+
- pandas, numpy, scipy, matplotlib, requests
- uv package manager (recommended) or pip

## Data Source

Options data is sourced from CBOE's delayed quotes API (15-minute delay). Real-time data requires CBOE subscription.