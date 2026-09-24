"""Blocking vs non-blocking: when does `async def` actually help?

FastAPI runs every endpoint in ONE of two ways:
* `async def`  -> on the event loop. Fast, but while it BLOCKS (time.sleep,
                  requests.get, a sync DB driver) NOTHING else can run.
* `def`        -> in a thread pool (about 40 threads). Blocking is OK there.

Three endpoints that each "wait" 1 second:
    /async-good    async def + await asyncio.sleep(1)   -> the loop keeps serving others
    /sync-ok       def + time.sleep(1)                   -> runs in a thread, fine
    /async-bad     async def + time.sleep(1)             -> freezes the WHOLE server

Run `python load_test.py` (next to this file): it fires 10 requests at the
same time at each endpoint, in-process, and prints how long they took.
    async-good ~1 s   sync-ok ~1 s   async-bad ~10 s !

Rule: use `async def` only when everything you wait for inside is awaited.
Otherwise use plain `def`.
"""

import asyncio
import time

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get('/async-good')
async def async_good() -> dict[str, str]:
    await asyncio.sleep(1)  # pretend: await an async DB query or HTTP call
    return {'endpoint': 'async-good'}


@app.get('/sync-ok')
def sync_ok() -> dict[str, str]:
    time.sleep(1)  # pretend: a blocking library call -- fine in a thread
    return {'endpoint': 'sync-ok'}


@app.get('/async-bad')
async def async_bad() -> dict[str, str]:
    time.sleep(1)  # WRONG: blocks the event loop for everybody
    return {'endpoint': 'async-bad'}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
