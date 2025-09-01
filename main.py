import asyncio
import json
import datetime
import asyncpg
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

DB_DSN = "postgresql://user:password@localhost:5432/lt_fault"
MQTT_HOST = "localhost"

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Postgres connection pool
    app.state.pool = await asyncpg.create_pool(dsn=DB_DSN)

    # Active websocket connections
    app.state.ws_clients = set()

    # MQTT setup
    client = mqtt.Client()

    def on_connect(c, u, f, rc):
        c.subscribe("telemetry/#")

    def on_message(c, u, msg):
        try:
            data = json.loads(msg.payload.decode())
        except Exception:
            return
        asyncio.run_coroutine_threadsafe(
            broadcast_and_store(data), asyncio.get_event_loop()
        )

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, 1883, 60)

    app.state.mqtt = client
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(client.loop_forever))


async def broadcast_and_store(d: dict):
    # Notify all websocket clients
    for ws in list(app.state.ws_clients):
        try:
            await ws.send_json({"type": "telemetry", "data": d})
        except Exception:
            try:
                app.state.ws_clients.remove(ws)
            except Exception:
                pass

    # Store in Postgres
    ts = datetime.datetime.fromtimestamp(
        d["ts"] / 1000.0, tz=datetime.timezone.utc
    )
    q = """
    INSERT INTO telemetry(
        ts, panel_id, line_id, v_rms, i_rms, pf, thd_est, status, fault_prob
    )
    VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)
    """
    async with app.state.pool.acquire() as con:
        await con.execute(
            q,
            ts,
            d["panelId"],
            d["lineId"],
            d.get("v_rms"),
            d.get("i_rms"),
            d.get("pf"),
            d.get("thd_est"),
            d.get("status"),
            d.get("fault_prob"),
        )


@app.get("/api/line-status")
async def line_status(panelId: str, lineId: int, limit: int = 1):
    q = """
    SELECT ts, v_rms, i_rms, pf, thd_est, status, fault_prob
    FROM telemetry
    WHERE panel_id=$1 AND line_id=$2
    ORDER BY ts DESC
    LIMIT $3
    """
    async with app.state.pool.acquire() as con:
        rows = await con.fetch(q, panelId, lineId, limit)
    return {"panelId": panelId, "lineId": lineId, "data": [dict(r) for r in rows]}


@app.post("/api/isolate/{lineId}")
async def isolate(lineId: int, reason: str = "software_fault"):
    topic = f"command/isolate/{lineId}"
    payload = {"reason": reason, "issued_by": "backend_api"}
    app.state.mqtt.publish(topic, json.dumps(payload))
    return {"status": "ok", "lineId": lineId, "action": "isolate", "reason": reason}


@app.post("/api/reset/{lineId}")
async def reset(lineId: int, reason: str = "manual_reset"):
    topic = f"command/reset/{lineId}"
    payload = {"reason": reason, "issued_by": "backend_api"}
    app.state.mqtt.publish(topic, json.dumps(payload))
    return {"status": "ok", "lineId": lineId, "action": "reset", "reason": reason}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    app.state.ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        app.state.ws_clients.remove(ws)
