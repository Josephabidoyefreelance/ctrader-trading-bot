import asyncio
import datetime
import random
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="📊 Live Renko + EMA + Supertrend Web API")

# Allow frontend connections (local + Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "📊 Live Renko + EMA + Supertrend Web API is running!"}

# WebSocket endpoint for live chart
@app.websocket("/ws/chart")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("📡 Client connected to /ws/chart")
    try:
        while True:
            # Mock Renko data — you can replace this with real trading data later
            data = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "price": round(100 + random.uniform(-1.5, 1.5), 2),
                "ema": round(100 + random.uniform(-1, 1), 2),
                "supertrend": round(100 + random.uniform(-2, 2), 2)
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except Exception as e:
        print(f"❌ Client disconnected: {e}")
    finally:
        await websocket.close()
        print("🔌 Connection closed")

# To run locally:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
