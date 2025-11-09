#!/usr/bin/env python3
"""
Generate gamma exposure charts for all available index tickers
Saves charts as PNG files for report generation
"""

import pandas as pd
import numpy as np
import scipy
from scipy.stats import norm
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from datetime import datetime, timedelta, date
import requests
import os
import sys

pd.options.display.float_format = '{:,.4f}'.format

# Black-Scholes European-Options Gamma
def calcGammaEx(S, K, vol, T, r, q, optType, OI):
    if T == 0 or vol == 0:
        return 0

    dp = (np.log(S/K) + (r - q + 0.5*vol**2)*T) / (vol*np.sqrt(T))
    dm = dp - vol*np.sqrt(T)

    if optType == 'call':
        gamma = np.exp(-q*T) * norm.pdf(dp) / (S * vol * np.sqrt(T))
        # 10bps (0.1%) moves
        return OI * 100 * S * S * 0.001 * gamma
    else:
        gamma = K * np.exp(-r*T) * norm.pdf(dm) / (S * S * vol * np.sqrt(T))
        # 10bps (0.1%) moves
        return OI * 100 * S * S * 0.001 * gamma

def isThirdFriday(d):
    return d.weekday() == 4 and 15 <= d.day <= 21

def process_ticker(index, output_dir="charts"):
    """Process a single ticker and save charts"""

    print(f"\n{'='*60}")
    print(f"📈 Processing {index}...")
    print(f"{'='*60}")

    try:
        # Get options data
        response = requests.get(url=f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{index}.json", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch data for {index}: HTTP {response.status_code}")
            return None

        options = response.json()

        # Get Index Spot Price
        spotPrice = options["data"]["close"]
        print(f"✓ {index} Spot Price: ${spotPrice:.2f}")
        fromStrike = 0.8 * spotPrice
        toStrike = 1.2 * spotPrice

        # Get Today's Date
        todayDate = date.today()

        # Get Options Data
        data_df = pd.DataFrame(options["data"]["options"])

        data_df['CallPut'] = data_df['option'].str.slice(start=-9,stop=-8)
        data_df['ExpirationDate'] = data_df['option'].str.slice(start=-15,stop=-9)
        data_df['ExpirationDate'] = pd.to_datetime(data_df['ExpirationDate'], format='%y%m%d')
        data_df['Strike'] = data_df['option'].str.slice(start=-8,stop=-3)
        data_df['Strike'] = data_df['Strike'].str.lstrip('0')

        data_df_calls = data_df.loc[data_df['CallPut'] == "C"]
        data_df_puts = data_df.loc[data_df['CallPut'] == "P"]
        data_df_calls = data_df_calls.reset_index(drop=True)
        data_df_puts = data_df_puts.reset_index(drop=True)

        df = data_df_calls[['ExpirationDate','option','last_trade_price','change','bid','ask','volume','iv','delta','gamma','open_interest','Strike']]
        df_puts = data_df_puts[['ExpirationDate','option','last_trade_price','change','bid','ask','volume','iv','delta','gamma','open_interest','Strike']]
        df_puts.columns = ['put_exp','put_option','put_last_trade_price','put_change','put_bid','put_ask','put_volume','put_iv','put_delta','put_gamma','put_open_interest','put_strike']

        df = pd.concat([df, df_puts], axis=1)

        df['check'] = np.where((df['ExpirationDate'] == df['put_exp']) & (df['Strike'] == df['put_strike']), 0, 1)

        if df['check'].sum() != 0:
            print(f"❌ PUT CALL MERGE FAILED for {index}")
            return None

        df.drop(['put_exp', 'put_strike', 'check'], axis=1, inplace=True)

        print(f"✓ Processing {len(df)} option pairs...")

        df.columns = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol',
                      'CallIV','CallDelta','CallGamma','CallOpenInt','StrikePrice','Puts','PutLastSale',
                      'PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']

        df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], format='%a %b %d %Y')
        df['ExpirationDate'] = df['ExpirationDate'] + timedelta(hours=16)
        df['StrikePrice'] = df['StrikePrice'].astype(float)
        df['CallIV'] = df['CallIV'].astype(float)
        df['PutIV'] = df['PutIV'].astype(float)
        df['CallGamma'] = df['CallGamma'].astype(float)
        df['PutGamma'] = df['PutGamma'].astype(float)
        df['CallOpenInt'] = df['CallOpenInt'].astype(float)
        df['PutOpenInt'] = df['PutOpenInt'].astype(float)

        # CALCULATE SPOT GAMMA
        df['CallGEX'] = df['CallGamma'] * df['CallOpenInt'] * 100 * spotPrice * spotPrice * 0.001
        df['PutGEX'] = df['PutGamma'] * df['PutOpenInt'] * 100 * spotPrice * spotPrice * 0.001 * -1

        df['TotalGamma'] = (df.CallGEX + df.PutGEX) / 10**9
        dfAgg = df.groupby(['StrikePrice']).sum(numeric_only=True)
        strikes = dfAgg.index.values

        # CALCULATE GAMMA PROFILE
        levels = np.linspace(fromStrike, toStrike, 30)

        df['daysTillExp'] = [1/262 if (np.busday_count(todayDate, x.date())) == 0 \
                                  else np.busday_count(todayDate, x.date())/262 for x in df.ExpirationDate]

        nextExpiry = df['ExpirationDate'].min()

        df['IsThirdFriday'] = [isThirdFriday(x) for x in df.ExpirationDate]
        thirdFridays = df.loc[df['IsThirdFriday'] == True]
        nextMonthlyExp = thirdFridays['ExpirationDate'].min() if len(thirdFridays) > 0 else nextExpiry

        totalGamma = []
        totalGammaExNext = []
        totalGammaExFri = []

        for level in levels:
            df['callGammaEx'] = df.apply(lambda row : calcGammaEx(level, row['StrikePrice'], row['CallIV'],
                                                                  row['daysTillExp'], 0, 0, "call", row['CallOpenInt']), axis = 1)

            df['putGammaEx'] = df.apply(lambda row : calcGammaEx(level, row['StrikePrice'], row['PutIV'],
                                                                 row['daysTillExp'], 0, 0, "put", row['PutOpenInt']), axis = 1)

            totalGamma.append(df['callGammaEx'].sum() - df['putGammaEx'].sum())

            exNxt = df.loc[df['ExpirationDate'] != nextExpiry]
            totalGammaExNext.append(exNxt['callGammaEx'].sum() - exNxt['putGammaEx'].sum())

            exFri = df.loc[df['ExpirationDate'] != nextMonthlyExp]
            totalGammaExFri.append(exFri['callGammaEx'].sum() - exFri['putGammaEx'].sum())

        totalGamma = np.array(totalGamma) / 10**9
        totalGammaExNext = np.array(totalGammaExNext) / 10**9
        totalGammaExFri = np.array(totalGammaExFri) / 10**9

        # Find Gamma Flip Point
        zeroCrossIdx = np.where(np.diff(np.sign(totalGamma)))[0]

        if len(zeroCrossIdx) > 0:
            negGamma = totalGamma[zeroCrossIdx]
            posGamma = totalGamma[zeroCrossIdx+1]
            negStrike = levels[zeroCrossIdx]
            posStrike = levels[zeroCrossIdx+1]
            zeroGamma = posStrike - ((posStrike - negStrike) * posGamma/(posGamma-negGamma))
            zeroGamma = zeroGamma[0]
        else:
            zeroGamma = 0

        # CREATE 2x3 GRID OF ALL CHARTS (INCLUDING TABLE)
        fig = plt.figure(figsize=(20, 12), constrained_layout=True)
        # Determine overall risk level for title
        total_gamma = df['TotalGamma'].sum()
        risk_emoji = '🔴' if abs(total_gamma) > 0.2 else '🟡' if abs(total_gamma) > 0.05 else '🟢'

        fig.suptitle(f'{risk_emoji} Gamma Exposure Analysis - {index} - {todayDate.strftime("%d %b %Y")}', fontsize=16, fontweight='bold')

        # Create grid spec for 2x3 layout
        gs = fig.add_gridspec(2, 3)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[0, 2])
        ax4 = fig.add_subplot(gs[1, 0])
        ax5 = fig.add_subplot(gs[1, 1:])  # Table spans 2 columns

        # Chart 1: Total Gamma Exposure
        ax1.grid(True, alpha=0.3)
        ax1.bar(strikes, dfAgg['TotalGamma'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure", color='steelblue')
        ax1.set_xlim([fromStrike, toStrike])
        ax1.set_title(f"Total Gamma: ${df['TotalGamma'].sum():.2f} Bn per 10bps (0.1%) {index} Move", fontweight="bold", fontsize=12)
        ax1.set_xlabel('Strike', fontweight="bold")
        ax1.set_ylabel('Spot Gamma Exposure ($ billions/10bps move)', fontweight="bold")
        ax1.axvline(x=spotPrice, color='r', lw=1.5, label=f"{index} Spot: ${spotPrice:,.0f}")
        ax1.legend(loc='best')

        # Chart 2: Open Interest Distribution
        ax2.grid(True, alpha=0.3)
        ax2.bar(strikes, dfAgg['CallOpenInt'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Call OI", color='green', alpha=0.7)
        ax2.bar(strikes, -1 * dfAgg['PutOpenInt'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Put OI", color='red', alpha=0.7)
        ax2.set_xlim([fromStrike, toStrike])
        ax2.set_title(f"Total Open Interest for {index}", fontweight="bold", fontsize=12)
        ax2.set_xlabel('Strike', fontweight="bold")
        ax2.set_ylabel('Open Interest (number of contracts)', fontweight="bold")
        ax2.axvline(x=spotPrice, color='r', lw=1.5, label=f"{index} Spot: ${spotPrice:,.0f}")
        ax2.axhline(y=0, color='black', lw=0.5)
        ax2.legend(loc='best')

        # Chart 3: Gamma by Type
        ax3.grid(True, alpha=0.3)
        ax3.bar(strikes, dfAgg['CallGEX'].to_numpy() / 10**9, width=6, linewidth=0.1, edgecolor='k', label="Call Gamma", color='green', alpha=0.7)
        ax3.bar(strikes, dfAgg['PutGEX'].to_numpy() / 10**9, width=6, linewidth=0.1, edgecolor='k', label="Put Gamma", color='red', alpha=0.7)
        ax3.set_xlim([fromStrike, toStrike])
        ax3.set_title(f"Gamma by Type: ${df['TotalGamma'].sum():.2f} Bn per 10bps (0.1%) {index} Move", fontweight="bold", fontsize=12)
        ax3.set_xlabel('Strike', fontweight="bold")
        ax3.set_ylabel('Spot Gamma Exposure ($ billions/10bps move)', fontweight="bold")
        ax3.axvline(x=spotPrice, color='r', lw=1.5, label=f"{index} Spot: ${spotPrice:,.0f}")
        ax3.axhline(y=0, color='black', lw=0.5)
        ax3.legend(loc='best')

        # Chart 4: Gamma Profile
        ax4.grid(True, alpha=0.3)
        ax4.plot(levels, totalGamma, label="All Expiries", linewidth=2, color='blue')
        ax4.plot(levels, totalGammaExNext, label="Ex-Next Expiry", linewidth=1.5, color='orange', linestyle='--')
        ax4.plot(levels, totalGammaExFri, label="Ex-Next Monthly Expiry", linewidth=1.5, color='purple', linestyle=':')
        ax4.set_title(f"Gamma Exposure Profile - {index}", fontweight="bold", fontsize=12)
        ax4.set_xlabel('Index Price', fontweight="bold")
        ax4.set_ylabel('Gamma Exposure ($ billions/10bps move)', fontweight="bold")
        ax4.axvline(x=spotPrice, color='r', lw=1.5, label=f"{index} Spot: ${spotPrice:,.0f}")
        if zeroGamma != 0:
            ax4.axvline(x=zeroGamma, color='g', lw=1.5, label=f"Gamma Flip: ${zeroGamma:,.0f}")
        ax4.axhline(y=0, color='grey', lw=1)
        ax4.set_xlim([fromStrike, toStrike])

        trans = ax4.get_xaxis_transform()
        if zeroGamma != 0:
            ax4.fill_between([fromStrike, zeroGamma], min(totalGamma), max(totalGamma),
                             facecolor='red', alpha=0.1, transform=trans)
            ax4.fill_between([zeroGamma, toStrike], min(totalGamma), max(totalGamma),
                             facecolor='green', alpha=0.1, transform=trans)

        ax4.legend(loc='best', fontsize=9)

        # Chart 5: Gamma Exposure Table for Different Move Sizes
        ax5.axis('tight')
        ax5.axis('off')

        # Calculate gamma for different basis point moves
        move_sizes = [1, 5, 10, 25, 50, 100, 200, 300, 400, 500]

        # Calculate total gamma at current spot for each move size
        current_total_gamma = df['TotalGamma'].sum()  # This is already for 10bps

        # Create table data
        table_data = []
        headers = ['Move Size', 'Gamma ($Bn)', '% of Spot', 'Notional ($Bn)']

        # Estimate ADTV based on typical volumes for indices
        # These are rough estimates - actual ADTV varies
        adtv_estimates = {
            'SPX': 250,  # $250Bn typical SPX futures/options notional
            'NDX': 100,  # $100Bn typical NDX
            'RUT': 50,   # $50Bn typical RUT
            'VIX': 30,   # $30Bn VIX products
            'DJX': 10,   # $10Bn DJX
            'XSP': 20,   # $20Bn mini-SPX
            'XND': 10,   # $10Bn mini-NDX
            'MRUT': 5,   # $5Bn mini-RUT
            'MXEA': 5,   # $5Bn MXEA
            'MXEF': 5    # $5Bn MXEF
        }

        adtv = adtv_estimates.get(index, 10)  # Default to $10Bn if not found

        for bps in move_sizes:
            # Scale gamma from 10bps base
            gamma_for_move = current_total_gamma * (bps / 10)
            pct_move = bps / 100  # Convert bps to percentage
            notional = abs(gamma_for_move)

            # Format the row
            if bps < 100:
                move_label = f"{bps}bps"
            else:
                move_label = f"{bps/100:.0f}%"

            # Add ADTV context for significant moves
            adtv_context = ""
            if notional > 0:
                adtv_ratio = notional / adtv
                if adtv_ratio >= 0.1:  # If more than 10% of ADTV
                    adtv_context = f" ({adtv_ratio:.1f}x ADTV)"

            table_data.append([
                move_label,
                f"${gamma_for_move:+.2f}",
                f"{pct_move:.2f}%",
                f"${notional:.2f}{adtv_context}"
            ])

        # Create the table
        table = ax5.table(cellText=table_data,
                         colLabels=headers,
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.15, 0.2, 0.15, 0.35])

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        # Style the header
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Enhanced color coding with risk-based visual hierarchy
        for i in range(1, len(table_data) + 1):
            gamma_val = float(table_data[i-1][1].replace('$', '').replace('+', ''))
            adtv_ratio = float(table_data[i-1][3].split('(')[1].split('x')[0]) if '(' in table_data[i-1][3] else 0

            # Color intensity based on risk level (magnitude + ADTV impact)
            if abs(gamma_val) > 10 or adtv_ratio > 0.5:  # CRITICAL RISK
                color = '#ff4444' if gamma_val < 0 else '#44ff44'
                table[(i, 1)].set_text_props(weight='bold')
                table[(i, 3)].set_text_props(weight='bold')
            elif abs(gamma_val) > 5 or adtv_ratio > 0.3:  # HIGH RISK
                color = '#ff9999' if gamma_val < 0 else '#99ff99'
            elif abs(gamma_val) > 2 or adtv_ratio > 0.1:  # MEDIUM RISK
                color = '#ffcccc' if gamma_val < 0 else '#ccffcc'
            else:  # LOW RISK
                color = '#f9f9f9'

            for j in range(len(headers)):
                table[(i, j)].set_facecolor(color)

        # Add title and context
        ax5.set_title(f'Gamma Exposure by Move Size (Est. 20D ADTV: ${adtv}Bn)',
                     fontweight='bold', fontsize=12, pad=20)

        # Add explanatory text
        explanation = (f"Negative gamma = Dealers sell into weakness, buy into strength (amplifies moves)\n"
                      f"Positive gamma = Dealers buy into weakness, sell into strength (dampens moves)\n"
                      f"Current Gamma Flip: ${zeroGamma:,.0f}" if zeroGamma != 0 else "")

        if explanation:
            ax5.text(0.5, -0.1, explanation, transform=ax5.transAxes,
                    ha='center', fontsize=9, style='italic')

        # Save the figure
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{output_dir}/{index}_gamma_analysis.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()

        print(f"✓ Charts saved to {filename}")

        # Calculate ADTV context
        adtv_estimates = {
            'SPX': 250, 'NDX': 100, 'RUT': 50, 'VIX': 30,
            'DJX': 10, 'XSP': 20, 'XND': 10, 'MRUT': 5,
            'MXEA': 5, 'MXEF': 5
        }
        adtv = adtv_estimates.get(index, 10)
        total_gamma_bn = df['TotalGamma'].sum()
        adtv_pct = (abs(total_gamma_bn) / adtv) * 100 if adtv > 0 else 0

        # Print gamma exposure with ADTV context
        print(f"\n💰 Total Gamma Exposure: ${total_gamma_bn:.2f}Bn per 10bps move ({adtv_pct:.1f}% of 20D ADTV)")
        if zeroGamma != 0:
            distance_to_flip = ((zeroGamma - spotPrice) / spotPrice) * 100
            print(f"🎯 Gamma Flip at: ${zeroGamma:.2f} ({distance_to_flip:+.2f}% from spot)")

        # Return summary statistics
        return {
            'ticker': index,
            'spot_price': spotPrice,
            'total_gamma': total_gamma_bn,
            'gamma_flip': zeroGamma if zeroGamma != 0 else None,
            'adtv': adtv,
            'adtv_pct': adtv_pct,
            'filename': filename
        }

    except Exception as e:
        print(f"❌ Error processing {index}: {str(e)}")
        return None

def main():
    # List of all working tickers
    tickers = [
        ("SPX", "S&P 500 Index"),
        ("NDX", "NASDAQ-100 Index"),
        ("DJX", "Dow Jones Index"),
        ("RUT", "Russell 2000 Index"),
        ("VIX", "CBOE Volatility Index"),
        ("MXEA", "MSCI EAFE Index"),
        ("MXEF", "MSCI Emerging Markets Index"),
        ("XSP", "Mini-SPX Index"),
        ("XND", "Mini-NDX Index"),
        ("MRUT", "Mini-Russell 2000 Index")
    ]

    print("="*60)
    print("GAMMA EXPOSURE ANALYSIS - ALL INDEX TICKERS")
    print(f"Date: {date.today().strftime('%B %d, %Y')}")
    print("="*60)

    results = []

    for ticker, description in tickers:
        result = process_ticker(ticker)
        if result:
            result['description'] = description
            results.append(result)

    # Create summary report with visual hierarchy
    print("\n" + "="*60)
    print("📊 GAMMA EXPOSURE SUMMARY REPORT")
    print("="*60)

    if results:
        summary_df = pd.DataFrame(results)
        summary_df = summary_df[['ticker', 'description', 'spot_price', 'total_gamma', 'gamma_flip', 'adtv', 'adtv_pct']]

        # Add ADTV-contextualized gamma column
        summary_df['gamma_with_adtv'] = summary_df.apply(
            lambda row: f"${row['total_gamma']:.2f}Bn ({row['adtv_pct']:.1f}% ADTV)",
            axis=1
        )

        # Add risk indicators and market state
        def get_risk_indicator(gamma_value, adtv_pct):
            """Assign risk level based on gamma magnitude and ADTV impact"""
            abs_gamma = abs(gamma_value)
            if abs_gamma > 0.2 or adtv_pct > 10:  # High gamma or high ADTV impact
                return '🔴'  # High risk
            elif abs_gamma > 0.05 or adtv_pct > 5:
                return '🟡'  # Medium risk
            else:
                return '🟢'  # Low risk

        def get_market_state(gamma_value, spot, flip):
            """Determine market state from gamma and flip point"""
            if pd.isna(flip) or flip == 0:
                return '➖'  # No clear flip
            elif spot < flip:
                return '📉'  # Below flip (negative gamma zone)
            else:
                return '📈'  # Above flip (positive gamma zone)

        # Add indicators
        summary_df['Risk'] = summary_df.apply(lambda row: get_risk_indicator(row['total_gamma'], row['adtv_pct']), axis=1)
        summary_df['State'] = summary_df.apply(
            lambda row: get_market_state(row['total_gamma'], row['spot_price'], row['gamma_flip']),
            axis=1
        )

        # Reorder columns for better visual hierarchy with ADTV context
        summary_df = summary_df[['Risk', 'State', 'ticker', 'description', 'spot_price', 'gamma_with_adtv', 'gamma_flip']]
        summary_df.columns = ['Risk', 'State', 'Ticker', 'Description', 'Spot Price', 'Gamma (Bn/10bps + ADTV%)', 'Gamma Flip']

        # Print enhanced summary
        print("\n🎯 KEY INDICATORS:")
        print("  Risk Levels: 🔴 High | 🟡 Medium | 🟢 Low")
        print("  Market State: 📈 Above Flip (Positive Gamma) | 📉 Below Flip (Negative Gamma)")
        print("\n" + summary_df.to_string(index=False))

        # Save enhanced summary to CSV
        summary_df.to_csv('charts/summary.csv', index=False)
        print(f"\n✅ Summary saved to charts/summary.csv")
        print(f"✅ All charts saved to charts/ directory")

        # Print critical alerts
        high_risk = summary_df[summary_df['Risk'] == '🔴']
        if not high_risk.empty:
            print(f"\n⚠️  HIGH RISK ALERTS:")
            for _, row in high_risk.iterrows():
                print(f"   • {row['Ticker']}: {row['Gamma (Bn/10bps + ADTV%)']}")

    return results

if __name__ == "__main__":
    results = main()