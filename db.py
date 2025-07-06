import os, asyncpg, asyncio, textwrap

DB_URL = os.getenv("DATABASE_URL")

_pool: asyncpg.Pool | None = None

async def get_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(DB_URL)
    return _pool

CREATE_SQL = textwrap.dedent("""
CREATE TABLE IF NOT EXISTS loot_events (
    id           bigserial PRIMARY KEY,
    player       text    NOT NULL,
    npc_id       int     NOT NULL,
    item_id      int     NOT NULL,
    qty          int     NOT NULL,
    points       int     NOT NULL,
    plugin_ts    timestamptz NOT NULL,
    received_ts  timestamptz DEFAULT now()
);
""")

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute(CREATE_SQL)
