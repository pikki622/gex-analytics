# Frequently Asked Questions

## Quick Answers to Common Questions

### General Questions

**Q: What exactly does this tool do?**
A: It calculates and visualizes how much stock/futures market makers need to buy or sell at different price levels. This helps predict volatility and identify support/resistance levels.

**Q: How accurate is this analysis?**
A: Gamma levels are about 70-80% reliable as support/resistance. They work best in normal market conditions and less well during major news events.

**Q: Do I need to understand options to use this?**
A: No! The tool gives you actionable levels. Just know:
- Below gamma flip = expect bigger moves
- Above gamma flip = expect calmer market

### Data Questions

**Q: Why can't I use SPY, QQQ, or other ETFs?**
A: CBOE restricts free API access to indices only. ETF options data requires a paid subscription ($380-2000+/month).

**Q: How delayed is the data?**
A: 15 minutes. For real-time data, you need a CBOE subscription.

**Q: Why do the charts take time to generate?**
A: The tool fetches data for thousands of option contracts, calculates gamma for each, then generates visualizations. This typically takes 10-30 seconds.

### Trading Questions

**Q: Should I trade based solely on gamma levels?**
A: No. Gamma analysis is one tool among many. Combine it with:
- Technical analysis
- Market sentiment
- News/fundamentals
- Your risk management rules

**Q: What's the most important thing to watch?**
A: The gamma flip point. It's where market behavior changes from volatile to calm (or vice versa).

**Q: Which index should I focus on?**
A: SPX (S&P 500) has the most gamma and drives overall market behavior. Start there.

### Technical Questions

**Q: What's the difference between the two scripts?**
- `gammaProfileCommandLine.py`: Shows gamma per 1% move, charts appear one at a time
- `gammaProfileCommandLine10bps.py`: Shows gamma per 0.1% move, all charts in a grid, includes ADTV table (recommended)

**Q: Can I backtest these gamma levels?**
A: Not with this tool currently. Historical gamma tracking is planned for Phase 4 of development.

**Q: How often should I run the analysis?**
A:
- Day traders: Every 1-2 hours
- Swing traders: Once at market open
- Position traders: Daily or when approaching key levels

### Troubleshooting

**Q: "Module not found" error**
A: Run `uv sync` to install dependencies. If using pip, ensure you've activated your virtual environment.

**Q: Charts aren't displaying**
A:
- Ensure matplotlib is installed: `pip install matplotlib`
- On Mac, you may need: `brew install python-tk`
- On Linux: `sudo apt-get install python3-tk`

**Q: API returns 403 error**
A: You're trying to access an ETF (like SPY). Use index tickers only: SPX, NDX, RUT, VIX, etc.

### Understanding the Output

**Q: What does negative gamma mean in the report?**
A: When gamma is negative, market makers amplify price moves. They sell when prices drop and buy when prices rise, making moves bigger.

**Q: Why are there different lines on the gamma profile chart?**
A:
- Blue line: Total gamma across all expirations
- Orange dashed: Gamma excluding next expiration
- Purple dotted: Gamma excluding monthly expiration
This shows how gamma will change after options expire.

**Q: What's ADTV and why does it matter?**
A: Average Daily Trading Volume. It shows if dealer hedging will significantly impact the market:
- < 10% ADTV: Minimal impact
- 10-30% ADTV: Noticeable impact
- > 30% ADTV: Major impact expected

### Advanced Questions

**Q: How is gamma calculated?**
A: Using the Black-Scholes formula with market implied volatility. See the [technical documentation](terminology.md#greek-letters-explained) for the exact formula.

**Q: Why do 0DTE options matter so much?**
A: Options expiring today have extreme gamma. Small price moves force huge hedging flows, creating volatility.

**Q: Can I modify the code for my needs?**
A: Yes! The code is open source (MIT license). Feel free to fork and modify. We welcome pull requests for improvements.

---

## Still Have Questions?

- Check the [Terminology Guide](terminology.md) for detailed explanations
- Open an [issue on GitHub](https://github.com/pikki622/gex-analytics/issues)
- Review the [Implementation Plan](../IMPLEMENTATION_PLAN.md) to see if your feature request is already planned

---

[← Back to README](../README.md)