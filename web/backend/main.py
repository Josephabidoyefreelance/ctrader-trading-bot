from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pandas_ta as ta
import asyncio
import json

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- WebSocket for live updates --------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    df = pd.read_csv("EURUSD_1min.csv", parse_dates=["Date"])

    async for i in stream_renko_data(df, websocket):
        pass

async def stream_renko_data(df, websocket):
    import random, time

    df = df.tail(400)  # just simulate last few rows
    for i in range(100, len(df)):
        renko_slice = df.iloc[:i].copy()

        renko_slice['EMA100'] = ta.ema(renko_slice['Close'], length=100)
        renko_slice['EMA300'] = ta.ema(renko_slice['Close'], length=300)
        st = ta.supertrend(renko_slice['High'], renko_slice['Low'], renko_slice['Close'], length=2, multiplier=30)

        if st is not None:
            st_col = [col for col in st.columns if "SUPERT" in col][0]
            renko_slice['ST'] = st[st_col]
        else:
            renko_slice['ST'] = pd.Series([None]*len(renko_slice))

        # Generate fake signal (BUY/SELL/HOLD)
        signal = random.choice(["BUY", "SELL", "HOLD"])
        payload = {
            "time": str(df["Date"].iloc[i]),
            "close": float(df["Close"].iloc[i]),
            "signal": signal
        }
        await websocket.send_text(json.dumps(payload))
        await asyncio.sleep(0.5)  # simulate live tick updates

# -------------------- Root route --------------------
@app.get("/")
async def root():
    return {"message": "📊 Live Renko + EMA + Supertrend Web API is running!"}
