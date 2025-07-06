from fastapi import FastAPI, Request, HTTPException
import os, hmac, hashlib, json, asyncpg, asyncio
from typing import Any, Dict
from db import get_pool, init_db
from scoring import score

app = FastAPI()
SECRET = os.getenv("SHARED_WEBHOOK_SECRET", "dev")

def verify_sig(body: bytes, sig: str) -> bool:
    mac = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"status": "ok", "msg": "RuneLite loot-ingest service"}

@app.post("/loot")
async def ingest(request: Request):
    body = await request.body()
    sig  = request.headers.get("X-Signature", "")
    if not verify_sig(body, sig):
        raise HTTPException(status_code=401, detail="Bad signature")

    data: Dict[str, Any] = json.loads(body)
    player   = data["player"]
    npc_id   = data["data"]["npcId"]
    plugin_ts= data["time"]

    pool = await get_pool()
    async with pool.acquire() as con:
        for item in data["data"]["items"]:
            item_id = item["id"]
            qty     = item["qty"]
            pts     = score(item_id, qty)
            await con.execute(
                """INSERT INTO loot_events
                   (player,npc_id,item_id,qty,points,plugin_ts)
                   VALUES ($1,$2,$3,$4,$5,to_timestamp($6))""",
                player, npc_id, item_id, qty, pts, plugin_ts/1000
            )
    return {"ok": True}
