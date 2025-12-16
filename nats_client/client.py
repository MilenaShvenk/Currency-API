import json
import nats
from config import NATS_URL, NATS_SUBJECT
from ws.ws_manager import ws_manager

async def init_nats(app):
    nc = await nats.connect(NATS_URL)
    app.state.nc = nc

    async def handler(msg):
        try:
            data = json.loads(msg.data.decode())
        except json.JSONDecodeError:
            data = msg.data.decode()

        print("[NATS]", data)

        await ws_manager.broadcast({
            "event": "nats_event",
            "data": data
        })

    await nc.subscribe(NATS_SUBJECT, cb=handler)
