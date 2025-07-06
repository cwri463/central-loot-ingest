from fastapi import FastAPI, Request, HTTPException
import os, hmac, hashlib, json, asyncio
import uvicorn

app = FastAPI()
SHARED_SECRET = os.getenv("SHARED_WEBHOOK_SECRET", "dev")

def verify_sig(body: bytes, signature: str):
    mac = hmac.new(SHARED_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)

@app.post("/loot")
async def ingest(request: Request):
    body = await request.body()
    sig  = request.headers.get("X-Signature", "")

    if not verify_sig(body, sig):
        raise HTTPException(status_code=401, detail="Bad signature")

    data = json.loads(body)
    # TODO: push to Redis / write Postgres / publish in-memory queue
    print("[LOOT]", data)

    # Respond quickly so RuneLite doesn’t block
    return {"ok": True}
    
@app.get("/")
async def root():
    return {"status": "ok", "msg": "RuneLite loot-ingest service"}

# For local dev:  uvicorn ingest_webhook.main:app --reload --port 8000
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

