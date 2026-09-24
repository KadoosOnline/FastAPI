"""Training Center API — version 11 (session 12 project): async from top to bottom.

What changed since session 11 (the behaviour of the API did NOT change):
* DATABASE_URL uses an async driver: sqlite+aiosqlite://  (or postgresql+asyncpg://)
* app/database.py: create_async_engine, async_sessionmaker(expire_on_commit=False),
  `async def get_db()` yields an AsyncSession
* services: `async def` + `await` on every database call; no lazy loading
* routers: `async def` endpoints that `await` the services
* storage: `await upload.read()`, disk writes through anyio (no blocked event loop)
* app/main.py: a lifespan that disposes the engine at shutdown
* alembic/env.py and seed.py: async too

Run the Bruno collection of session 11 against it: same answers.

    alembic upgrade head
    python seed.py
    python main.py
"""

import uvicorn

if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
