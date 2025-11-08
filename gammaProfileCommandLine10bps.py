import pandas as pd
import numpy as np
import scipy
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import requests
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
        # Changed from 0.01 to 0.001 for 10bps (0.1%) moves
        return OI * 100 * S * S * 0.001 * gamma
    else: # Gamma is same for calls and puts. This is just to cross-check
        gamma = K * np.exp(-r*T) * norm.pdf(dm) / (S * S * vol * np.sqrt(T))
        # Changed from 0.01 to 0.001 for 10bps (0.1%) moves
        return OI * 100 * S * S * 0.001 * gamma

def isThirdFriday(d):
    return d.weekday() == 4 and 15 <= d.day <= 21

index = sys.argv[1]

# Get options data
response = requests.get(url="https://cdn.cboe.com/api/global/delayed_quotes/options/_" + index + ".json")
options = response.json()

# Get Index Spot Price
spotPrice = options["data"]["close"]
print(f"{index} Spot Price: ${spotPrice:.2f}")
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
    print("PUT CALL MERGE FAILED - OPTIONS ARE MISMATCHED.")
    exit()

df.drop(['put_exp', 'put_strike', 'check'], axis=1, inplace=True)

print(f"Processing {len(df)} option pairs...")

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


# ---=== CALCULATE SPOT GAMMA ===---
# Gamma Exposure = Unit Gamma * Open Interest * Contract Size * Spot Price
# Changed to 10bps (0.1%) moves instead of 100bps (1%) moves
df['CallGEX'] = df['CallGamma'] * df['CallOpenInt'] * 100 * spotPrice * spotPrice * 0.001
df['PutGEX'] = df['PutGamma'] * df['PutOpenInt'] * 100 * spotPrice * spotPrice * 0.001 * -1

df['TotalGamma'] = (df.CallGEX + df.PutGEX) / 10**9
dfAgg = df.groupby(['StrikePrice']).sum(numeric_only=True)
strikes = dfAgg.index.values

# ---=== CALCULATE GAMMA PROFILE ===---
levels = np.linspace(fromStrike, toStrike, 30)

# For 0DTE options, I'm setting DTE = 1 day, otherwise they get excluded
df['daysTillExp'] = [1/262 if (np.busday_count(todayDate, x.date())) == 0 \
                          else np.busday_count(todayDate, x.date())/262 for x in df.ExpirationDate]

nextExpiry = df['ExpirationDate'].min()

df['IsThirdFriday'] = [isThirdFriday(x) for x in df.ExpirationDate]
thirdFridays = df.loc[df['IsThirdFriday'] == True]
nextMonthlyExp = thirdFridays['ExpirationDate'].min()

totalGamma = []
totalGammaExNext = []
totalGammaExFri = []

# For each spot level, calc gamma exposure at that point
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
    zeroGamma = 0  # No flip point found

# ---=== CREATE 2x2 GRID OF ALL CHARTS ===---
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(f'Gamma Exposure Analysis - {index} - {todayDate.strftime("%d %b %Y")}', fontsize=16, fontweight='bold')

# Chart 1: Total Gamma Exposure (Top Left)
ax1.grid(True, alpha=0.3)
ax1.bar(strikes, dfAgg['TotalGamma'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure", color='steelblue')
ax1.set_xlim([fromStrike, toStrike])
ax1.set_title(f"Total Gamma: ${df['TotalGamma'].sum():.2f} Bn per 10bps (0.1%) {index} Move", fontweight="bold", fontsize=12)
ax1.set_xlabel('Strike', fontweight="bold")
ax1.set_ylabel('Spot Gamma Exposure ($ billions/10bps move)', fontweight="bold")
ax1.axvline(x=spotPrice, color='r', lw=1.5, label=f"{index} Spot: ${spotPrice:,.0f}")
ax1.legend(loc='best')

# Chart 2: Open Interest by Calls and Puts (Top Right)
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

# Chart 3: Gamma by Calls and Puts (Bottom Left)
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

# Chart 4: Gamma Exposure Profile (Bottom Right)
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

# Add shaded regions for positive/negative gamma
trans = ax4.get_xaxis_transform()
if zeroGamma != 0:
    ax4.fill_between([fromStrike, zeroGamma], min(totalGamma), max(totalGamma),
                     facecolor='red', alpha=0.1, transform=trans, label='Negative Gamma Zone')
    ax4.fill_between([zeroGamma, toStrike], min(totalGamma), max(totalGamma),
                     facecolor='green', alpha=0.1, transform=trans, label='Positive Gamma Zone')

ax4.legend(loc='best', fontsize=9)

# Adjust layout and display
plt.tight_layout()
plt.show()

print(f"\n✅ Analysis complete for {index}")
print(f"   Total Gamma: ${df['TotalGamma'].sum():.2f}B per 10bps move")
if zeroGamma != 0:
    print(f"   Gamma Flip: ${zeroGamma:,.0f}")
print(f"   Current Spot: ${spotPrice:,.0f}")