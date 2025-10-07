import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import time
import os

# -------------------- Load Historical Data --------------------
df = pd.read_csv("EURUSD_1min.csv", parse_dates=['Date'])

# -------------------- Renko Generation --------------------
def renko_df(df, brick_size):
    df_renko = pd.DataFrame(columns=['Date','Open','High','Low','Close'])
    last_close = df['Close'].iloc[0]
    open_price = last_close
    for i,row in df.iterrows():
        price = row['Close']
        while abs(price - last_close) >= brick_size:
            direction = 1 if price > last_close else -1
            close_price = last_close + direction * brick_size
            high = max(last_close, close_price)
            low = min(last_close, close_price)
            df_renko = pd.concat([df_renko, pd.DataFrame({'Date':[row['Date']],
                                                           'Open':[open_price],
                                                           'High':[high],
                                                           'Low':[low],
                                                           'Close':[close_price]})], ignore_index=True)
            last_close = close_price
            open_price = last_close
    return df_renko

brick_size = 0.0010
renko = renko_df(df, brick_size)

# -------------------- Indicators --------------------
renko['High'] = pd.to_numeric(renko['High'])
renko['Low'] = pd.to_numeric(renko['Low'])
renko['Close'] = pd.to_numeric(renko['Close'])

# Short EMAs for testing
renko['EMA20'] = ta.ema(renko['Close'], length=20)
renko['EMA50'] = ta.ema(renko['Close'], length=50)

# Supertrend
st = ta.supertrend(high=renko['High'], low=renko['Low'], close=renko['Close'], length=2, multiplier=30)
if st is not None:
    st_col = [col for col in st.columns if "SUPERT" in col][0]
    renko['ST'] = st[st_col]
else:
    renko['ST'] = pd.Series([None]*len(renko))
    print("Supertrend calculation failed. Using empty ST column.")

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

# -------------------- Pseudo Live Plotting --------------------
plt.ion()  # interactive mode
fig, ax = plt.subplots(figsize=(12,6))

for i in range(len(renko)):
    ax.clear()
    ax.plot(renko['Close'][:i+1], color='blue', label='Renko Close')
    ax.plot(renko['EMA20'][:i+1], color='orange', label='EMA20')
    ax.plot(renko['EMA50'][:i+1], color='purple', label='EMA50')
    
    # Plot BUY/SELL signals up to current bar
    buy_idx = renko.index[:i+1][renko['Signal'][:i+1]=='BUY']
    sell_idx = renko.index[:i+1][renko['Signal'][:i+1]=='SELL']
    ax.scatter(buy_idx, renko['Close'][buy_idx], marker='^', color='g', s=100, label='BUY Signal')
    ax.scatter(sell_idx, renko['Close'][sell_idx], marker='v', color='r', s=100, label='SELL Signal')
    
    ax.set_title("Renko Chart with EMA & Supertrend Signals (Pseudo Live)")
    ax.set_xlabel("Bars")
    ax.set_ylabel("Price")
    ax.legend()
    plt.pause(0.05)  # speed of the pseudo live update

plt.ioff()
plt.savefig("renko_signals_live.png")
plt.show()
print("Dynamic chart saved as renko_signals_live.png")
