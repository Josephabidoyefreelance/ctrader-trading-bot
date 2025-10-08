import asyncio
import datetime
import pandas as pd
import pandas_ta as ta
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="📊 cTrader EMA + Supertrend Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def renko_df(df, brick_size=0.001):
    df_renko = pd.DataFrame(columns=['Date','Open','High','Low','Close'])
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
                'Date':[row['Date']],
                'Open':[open_price],
                'High':[high],
                'Low':[low],
                'Close':[close_price]
            })
            df_renko = pd.concat([df_renko, new_row], ignore_index=True)
            last_close = close_price
            open_price = last_close
    return df_renko

# Preload CSV once
df = pd.read_csv("EURUSD_1min.csv", parse_dates=['Date'])
renko = renko_df(df)
renko['EMA100'] = ta.ema(renko['Close'], length=100)
renko['EMA300'] = ta.ema(renko['Close'], length=300)
st = ta.supertrend(renko['High'], renko['Low'], renko['Close'], length=2, multiplier=30)
renko['ST'] = st[st.columns[-1]]

# Generate signals
def get_signals():
    signals = []
    for i in range(301, len(renko)):
        prev = renko.iloc[i-1]
        curr = renko.iloc[i]

        # Buy
        if curr['ST'] < curr['Close'] and prev['EMA100'] > prev['EMA300'] and prev['Low'] < prev['EMA300'] and curr['Close'] > curr['Open']:
            signals.append({"type":"BUY","price":curr['Close'],"time":str(curr['Date'])})
        # Sell
        elif curr['ST'] > curr['Close'] and prev['EMA100'] < prev['EMA300'] and prev['High'] > prev['EMA300'] and curr['Close'] < curr['Open']:
            signals.append({"type":"SELL","price":curr['Close'],"time":str(curr['Date'])})
    return signals

@app.websocket("/ws/chart")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 WebSocket Connected")
    i = 301
    try:
        while True:
            if i >= len(renko):
                i = 301  # loop for demo
            prev = renko.iloc[i-1]
            curr = renko.iloc[i]

            # Determine signal
            signal = ""
            if curr['ST'] < curr['Close'] and prev['EMA100'] > prev['EMA300'] and prev['Low'] < prev['EMA300'] and curr['Close'] > curr['Open']:
                signal = "BUY"
            elif curr['ST'] > curr['Close'] and prev['EMA100'] < prev['EMA300'] and prev['High'] > prev['EMA300'] and curr['Close'] < curr['Open']:
                signal = "SELL"

            data = {
                "timestamp": str(curr['Date']),
                "price": float(curr['Close']),
                "ema100": float(curr['EMA100']),
                "ema300": float(curr['EMA300']),
                "supertrend": float(curr['ST']),
                "signal": signal
            }

            await websocket.send_json(data)
            i += 1
            await asyncio.sleep(1)
    except Exception as e:
        print("❌ Client disconnected:", e)
    finally:
        await websocket.close()
