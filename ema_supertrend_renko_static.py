# save as: ema_supertrend_renko_static.py
import os
import pandas as pd
import pandas_ta as ta
import matplotlib
matplotlib.use('Agg')   # non-interactive backend for reliable saving
import matplotlib.pyplot as plt

# -------------------- Load Historical Data --------------------
df = pd.read_csv("EURUSD_1min.csv", parse_dates=['Date'])

# -------------------- Renko Generation --------------------
def renko_df(df, brick_size):
    df_renko = pd.DataFrame(columns=['Date','Open','High','Low','Close'])
    last_close = float(df['Close'].iloc[0])
    open_price = last_close
    for _, row in df.iterrows():
        price = float(row['Close'])
        while abs(price - last_close) >= brick_size:
            direction = 1 if price > last_close else -1
            close_price = last_close + direction * brick_size
            high = max(last_close, close_price)
            low = min(last_close, close_price)
            new_row = pd.DataFrame({
                'Date': [row['Date']],
                'Open': [open_price],
                'High': [high],
                'Low': [low],
                'Close': [close_price]
            })
            df_renko = pd.concat([df_renko, new_row], ignore_index=True)
            last_close = close_price
            open_price = last_close
    return df_renko

# -------------------- Generate Renko --------------------
brick_size = 0.0010
renko = renko_df(df, brick_size)

if renko.empty:
    raise SystemExit("No Renko bars generated. Check EURUSD_1min.csv and brick_size.")

# -------------------- Ensure numeric --------------------
renko['High'] = pd.to_numeric(renko['High'], errors='coerce')
renko['Low']  = pd.to_numeric(renko['Low'], errors='coerce')
renko['Close']= pd.to_numeric(renko['Close'], errors='coerce')

# -------------------- Indicators (short EMAs for visible signals) --------------------
renko['EMA20'] = ta.ema(renko['Close'], length=20)
renko['EMA50'] = ta.ema(renko['Close'], length=50)

# -------------------- Supertrend (dynamic column name) --------------------
st = ta.supertrend(high=renko['High'], low=renko['Low'], close=renko['Close'], length=2, multiplier=30)
if st is not None and not st.empty:
    st_col = [c for c in st.columns if "SUPERT" in c]
    if st_col:
        renko['ST'] = st[st_col[0]]
    else:
        renko['ST'] = pd.Series([None]*len(renko))
        print("Supertrend returned no SUPERT column name.")
else:
    renko['ST'] = pd.Series([None]*len(renko))
    print("Supertrend calculation failed or returned empty. Using empty ST column.")

# -------------------- Signals --------------------
signals = []
for i in range(1, len(renko)):
    if pd.isna(renko['ST'].iloc[i-1]) or pd.isna(renko['EMA20'].iloc[i-1]) or pd.isna(renko['EMA50'].iloc[i-1]):
        signals.append('HOLD')
        continue

    buy = (renko['ST'].iloc[i-1] < renko['Close'].iloc[i-1]) and \
          (renko['EMA20'].iloc[i-1] > renko['EMA50'].iloc[i-1]) and \
          (renko['Low'].iloc[i-1] < renko['EMA50'].iloc[i-1]) and \
          (renko['Close'].iloc[i] > renko['Open'].iloc[i])

    sell = (renko['ST'].iloc[i-1] > renko['Close'].iloc[i-1]) and \
           (renko['EMA20'].iloc[i-1] < renko['EMA50'].iloc[i-1]) and \
           (renko['High'].iloc[i-1] > renko['EMA50'].iloc[i-1]) and \
           (renko['Close'].iloc[i] < renko['Open'].iloc[i])

    if buy:
        signals.append('BUY')
    elif sell:
        signals.append('SELL')
    else:
        signals.append('HOLD')

renko['Signal'] = ['HOLD'] + signals

# -------------------- Plot and save PNG --------------------
plt.figure(figsize=(12,6))
plt.plot(renko['Close'], label='Renko Close')
plt.plot(renko['EMA20'], label='EMA20')
plt.plot(renko['EMA50'], label='EMA50')
plt.scatter(renko.index[renko['Signal']=='BUY'], renko['Close'][renko['Signal']=='BUY'], marker='^', s=100, label='BUY', zorder=5)
plt.scatter(renko.index[renko['Signal']=='SELL'], renko['Close'][renko['Signal']=='SELL'], marker='v', s=100, label='SELL', zorder=5)
plt.title("Renko + EMA + Supertrend Signals (static)")
plt.xlabel("Bars")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()

outfn = "renko_signals.png"
plt.savefig(outfn)
plt.close()

print(f"Chart saved to: {os.path.abspath(outfn)}")

# Try to open automatically (Windows)
try:
    os.startfile(outfn)
except Exception:
    print("Could not open image automatically. Open the file manually.")
