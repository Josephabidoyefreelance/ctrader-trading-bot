import pandas as pd
import pandas_ta as ta
import matplotlib
matplotlib.use('TkAgg')  # GUI backend for live chart
import matplotlib.pyplot as plt
import time
import os

# -------------------- Load Historical Data --------------------
df = pd.read_csv("EURUSD_1min.csv", parse_dates=['Date'])

# -------------------- Renko Function --------------------
def renko_df(df, brick_size):
    df_renko = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close'])
    last_close = df['Close'].iloc[0]
    open_price = last_close
    for i, row in df.iterrows():
        price = row['Close']
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
brick_size = 0.001
renko_full = renko_df(df, brick_size)

if not os.path.exists("charts"):
    os.makedirs("charts")

# -------------------- Live Simulation --------------------
print("🚀 Starting live Renko simulation...")

plt.ion()  # interactive mode ON
fig, ax = plt.subplots(figsize=(12, 6))
plt.show(block=False)
plt.pause(2)  # allow GUI window to appear

for i in range(300, len(renko_full)):
    renko = renko_full.iloc[:i].copy()
    renko['EMA100'] = ta.ema(renko['Close'], length=100)
    renko['EMA300'] = ta.ema(renko['Close'], length=300)

    st = ta.supertrend(renko['High'], renko['Low'], renko['Close'], length=2, multiplier=30)
    if st is not None and not st.empty:
        st_col = [col for col in st.columns if "SUPERT" in col][0]
        renko['ST'] = st[st_col]
    else:
        renko['ST'] = pd.Series([None] * len(renko))

    # Signal generation
    if i > 301 and not pd.isna(renko['ST'].iloc[-2]):
        buy = (renko['ST'].iloc[-2] < renko['Close'].iloc[-2]) and \
              (renko['EMA100'].iloc[-2] > renko['EMA300'].iloc[-2]) and \
              (renko['Low'].iloc[-2] < renko['EMA300'].iloc[-2]) and \
              (renko['Close'].iloc[-1] > renko['Open'].iloc[-1])
        sell = (renko['ST'].iloc[-2] > renko['Close'].iloc[-2]) and \
               (renko['EMA100'].iloc[-2] < renko['EMA300'].iloc[-2]) and \
               (renko['High'].iloc[-2] > renko['EMA300'].iloc[-2]) and \
               (renko['Close'].iloc[-1] < renko['Open'].iloc[-1])
        if buy:
            print(f"🟢 BUY @ {renko['Close'].iloc[-1]:.5f} | {renko['Date'].iloc[-1]}")
        elif sell:
            print(f"🔴 SELL @ {renko['Close'].iloc[-1]:.5f} | {renko['Date'].iloc[-1]}")

    # --- Plot update ---
    ax.clear()
    ax.plot(renko['Close'], label='Renko Close', color='blue')
    ax.plot(renko['EMA100'], label='EMA100', color='orange')
    ax.plot(renko['EMA300'], label='EMA300', color='red')
    if 'ST' in renko.columns:
        ax.plot(renko['ST'], label='Supertrend', color='green', linestyle='--', alpha=0.6)
    ax.set_title(f"📈 Live EMA + Supertrend Simulation ({i}/{len(renko_full)})")
    ax.legend(loc='upper left')
    plt.pause(0.5)  # <— slower so it updates visibly

print("✅ Live Renko playback complete!")

# keep window open after loop
plt.ioff()
plt.show(block=True)
input("Press Enter to close the chart...")
