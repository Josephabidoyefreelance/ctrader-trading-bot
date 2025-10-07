from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
import datetime

app = FastAPI()

# Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend domain when ready
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "📊 Live Renko + EMA + Supertrend Web API is running!"}

# Live WebSocket endpoint
@app.websocket("/ws/chart")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # simulate a random price update
        new_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "price": round(100 + random.uniform(-2, 2), 2)
        }
        await websocket.send_json(new_data)
        await asyncio.sleep(2)  # every 2 seconds
