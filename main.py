import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from db.database import engine
from api.currencies import router as currency_router
from ws.ws_manager import ws_manager
from nats_client.client import init_nats
from tasks.currency_tasks import update_currencies_periodically


app = FastAPI(title="Currency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start:.4f}"
    return response

app.include_router(currency_router)


@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)


@app.post("/tasks/run")
async def run_task():
    asyncio.create_task(update_currencies_periodically(app))
    return {"status": "started"}

@app.on_event("startup")
async def startup():
    print("[APP] Запуск приложения")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        print("[DB] Таблицы базы данных готовы")

    await init_nats(app)

    print("[TASK] Запуск фоновой задачи обновления валют")
    asyncio.create_task(update_currencies_periodically(app))
