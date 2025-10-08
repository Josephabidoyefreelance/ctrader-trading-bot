import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

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

brick_size = 0.0010  # example for EURUSD 10 pips
renko = renko_df(df, brick_size)

# -------------------- Indicators --------------------
renko['High'] = pd.to_numeric(renko['High'])
renko['Low'] = pd.to_numeric(renko['Low'])
renko['Close'] = pd.to_numeric(renko['Close'])

# Use shorter EMAs for testing so signals appear
renko['EMA20'] = ta.ema(renko['Close'], length=20)
renko['EMA50'] = ta.ema(renko['Close'], length=50)

# Supertrend safely
st = ta.supertrend(high=renko['High'], low=renko['Low'], close=renko['Close'], length=2, multiplier=30)
if st is not None:
    st_col = [col for col in st.columns if "SUPERT" in col][0]
    renko['ST'] = st[st_col]
else:
    renko['ST'] = pd.Series([None]*len(renko))
    print("Supertrend calculation failed. Using empty ST column.")

# -------------------- Signals --------------------
signals = []
for i in range(1,len(renko)):
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

# -------------------- Plot and Save --------------------
plt.figure(figsize=(12,6))
plt.plot(renko['Close'], label='Renko Close', color='blue')
plt.plot(renko['EMA20'], label='EMA20', color='orange')
plt.plot(renko['EMA50'], label='EMA50', color='purple')
plt.scatter(renko.index[renko['Signal']=='BUY'], renko['Close'][renko['Signal']=='BUY'], marker='^', color='g', s=100, label='BUY Signal')
plt.scatter(renko.index[renko['Signal']=='SELL'], renko['Close'][renko['Signal']=='SELL'], marker='v', color='r', s=100, label='SELL Signal')
plt.title("Renko Chart with EMA & Supertrend Signals")
plt.xlabel("Bars")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()
plt.savefig("renko_signals.png")
plt.close()
print("Chart saved as renko_signals.png with BUY/SELL signals.")
