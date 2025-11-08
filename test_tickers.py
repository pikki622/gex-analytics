#!/usr/bin/env python3
"""Test which tickers are available through CBOE API"""

import requests
import json
from typing import Dict, List, Tuple

def test_ticker(ticker: str) -> Tuple[bool, str, float]:
    """
    Test if a ticker is available through CBOE API
    Returns: (success, message, spot_price)
    """
    url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{ticker}.json"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if "data" in data and "options" in data["data"]:
                spot_price = data["data"].get("close", 0)
                options_count = len(data["data"]["options"])
                return True, f"✓ Found {options_count} options", spot_price
            else:
                return False, "Invalid data structure", 0
        else:
            return False, f"HTTP {response.status_code}", 0
    except requests.exceptions.Timeout:
        return False, "Timeout", 0
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)[:30]}", 0
    except json.JSONDecodeError:
        return False, "Invalid JSON", 0
    except Exception as e:
        return False, f"Error: {str(e)[:30]}", 0

def main():
    # Common index tickers to test
    tickers_to_test = [
        # Major US Indices
        ("SPX", "S&P 500 Index"),
        ("SPY", "SPDR S&P 500 ETF"),
        ("NDX", "NASDAQ-100 Index"),
        ("QQQ", "Invesco QQQ ETF"),
        ("DJX", "Dow Jones Index"),
        ("DIA", "SPDR Dow Jones ETF"),
        ("RUT", "Russell 2000 Index"),
        ("IWM", "iShares Russell 2000 ETF"),

        # Volatility Indices
        ("VIX", "CBOE Volatility Index"),
        ("VXX", "iPath S&P 500 VIX ETF"),
        ("UVXY", "ProShares Ultra VIX Short-Term"),

        # Sector ETFs
        ("XLF", "Financial Select Sector SPDR"),
        ("XLK", "Technology Select Sector SPDR"),
        ("XLE", "Energy Select Sector SPDR"),
        ("XLI", "Industrial Select Sector SPDR"),
        ("XLV", "Health Care Select Sector SPDR"),
        ("XLY", "Consumer Discretionary SPDR"),
        ("XLP", "Consumer Staples SPDR"),
        ("XLU", "Utilities Select Sector SPDR"),
        ("XLB", "Materials Select Sector SPDR"),

        # Other Popular ETFs
        ("GLD", "SPDR Gold Shares"),
        ("SLV", "iShares Silver Trust"),
        ("TLT", "iShares 20+ Year Treasury"),
        ("HYG", "iShares High Yield Corp Bond"),
        ("EEM", "iShares MSCI Emerging Markets"),
        ("EWZ", "iShares MSCI Brazil"),
        ("FXI", "iShares China Large-Cap"),
        ("IYR", "iShares U.S. Real Estate"),
        ("USO", "United States Oil Fund"),
        ("GDX", "VanEck Gold Miners ETF"),
        ("ARKK", "ARK Innovation ETF"),

        # Leveraged ETFs
        ("TQQQ", "ProShares UltraPro QQQ"),
        ("SQQQ", "ProShares UltraPro Short QQQ"),
        ("SPXU", "ProShares UltraPro Short S&P500"),
        ("UPRO", "ProShares UltraPro S&P500"),

        # International Indices
        ("EFA", "iShares MSCI EAFE ETF"),
        ("VEA", "Vanguard FTSE Developed Markets"),
        ("VWO", "Vanguard FTSE Emerging Markets"),

        # Bond ETFs
        ("AGG", "iShares Core U.S. Aggregate Bond"),
        ("BND", "Vanguard Total Bond Market"),
        ("JNK", "SPDR High Yield Bond"),
        ("LQD", "iShares Investment Grade Corp Bond"),

        # Commodity ETFs
        ("UNG", "United States Natural Gas Fund"),
        ("DBA", "Invesco DB Agriculture Fund"),
        ("DBB", "Invesco DB Base Metals Fund"),

        # CBOE Proprietary Indices
        ("CLL", "CBOE S&P 500 Call Write Index"),
        ("PUT", "CBOE S&P 500 PutWrite Index"),
        ("MXEA", "MSCI EAFE Index"),
        ("MXEF", "MSCI Emerging Markets Index"),
        ("XSP", "Mini-SPX Index"),
        ("XND", "Mini-NDX Index"),
        ("MRUT", "Mini-Russell 2000 Index")
    ]

    print("Testing CBOE Options API Availability")
    print("=" * 60)
    print(f"Testing {len(tickers_to_test)} tickers...\n")

    working_tickers = []
    failed_tickers = []

    for ticker, description in tickers_to_test:
        print(f"Testing {ticker:6s} ({description})...", end=" ")
        success, message, spot_price = test_ticker(ticker)

        if success:
            print(f"{message} | Spot: ${spot_price:.2f}")
            working_tickers.append((ticker, description, spot_price))
        else:
            print(f"✗ {message}")
            failed_tickers.append((ticker, description, message))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\n✓ WORKING TICKERS ({len(working_tickers)}):")
    print("-" * 40)
    for ticker, description, spot in working_tickers:
        print(f"  {ticker:6s} - {description:30s} (${spot:.2f})")

    print(f"\n✗ NOT AVAILABLE ({len(failed_tickers)}):")
    print("-" * 40)
    for ticker, description, error in failed_tickers:
        print(f"  {ticker:6s} - {description:30s} ({error})")

    # Create a list for the command line
    if working_tickers:
        print(f"\n📊 Available tickers for command line use:")
        print("  uv run python gammaProfileCommandLine.py [TICKER]")
        print(f"  Available: {', '.join([t[0] for t in working_tickers])}")

    return working_tickers, failed_tickers

if __name__ == "__main__":
    main()