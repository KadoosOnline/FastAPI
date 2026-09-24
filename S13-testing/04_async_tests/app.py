"""An async app: endpoints that await other coroutines."""

import asyncio

from fastapi import FastAPI

app = FastAPI()


async def fetch_seats(course_id: int) -> int:
    await asyncio.sleep(0.01)
    return 10 + course_id


@app.get('/courses/{course_id}/seats')
async def seats(course_id: int) -> dict[str, int]:
    return {'course_id': course_id, 'seats': await fetch_seats(course_id)}
