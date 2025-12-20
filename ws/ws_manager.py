from typing import List
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
        print(f"[WS] Клиент подключился. Активных подключений: {len(self.connections)}")

    async def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)
            print(f"[WS] Клиент отключился. Активных подключений: {len(self.connections)}")

    async def broadcast(self, message: dict):
        print(f"[WS] Рассылка сообщения: {message}")

        for ws in self.connections[:]:
            try:
                await ws.send_json(message)
            except Exception as e:
                print("[WS] Ошибка отправки сообщения:", e)
                await self.disconnect(ws)

ws_manager = WSManager()