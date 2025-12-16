from ws_manager import ws_manager
from fastapi import WebSocket, WebSocketDisconnect

async def websocket_currencies(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)
