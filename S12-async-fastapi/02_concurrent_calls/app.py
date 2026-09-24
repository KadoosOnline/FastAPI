"""Several I/O operations inside ONE request, at the same time.

A course page needs: the course, the weather in the city of the class, and
the exchange rate for the price in dollars -- three independent waits.

    sequential:  a = await f(); b = await g(); c = await h()     -> sum of the waits
    concurrent:  a, b, c = await asyncio.gather(f(), g(), h())   -> the LONGEST wait

This is where async really pays off in a backend: calling other services.
`/slow` and `/fast` return the same data; compare the `took_ms` value.
"""

import asyncio
import time

import uvicorn
from fastapi import FastAPI

app = FastAPI()


async def load_course(course_id: int) -> dict:
    await asyncio.sleep(0.3)  # a database query
    return {'id': course_id, 'title': 'FastAPI', 'price_toman': 4_800_000}


async def load_weather(city: str) -> str:
    await asyncio.sleep(0.5)  # an external weather API
    return f'sunny in {city}'


async def load_rate() -> int:
    await asyncio.sleep(0.4)  # an exchange-rate API
    return 95_000  # toman per dollar


@app.get('/courses/{course_id}/slow')
async def page_slow(course_id: int) -> dict:
    started = time.perf_counter()
    course = await load_course(course_id)
    weather = await load_weather('Rasht')
    rate = await load_rate()
    return build(course, weather, rate, started)


@app.get('/courses/{course_id}/fast')
async def page_fast(course_id: int) -> dict:
    started = time.perf_counter()
    course, weather, rate = await asyncio.gather(
        load_course(course_id), load_weather('Rasht'), load_rate()
    )
    return build(course, weather, rate, started)


def build(course: dict, weather: str, rate: int, started: float) -> dict:
    return {
        **course,
        'price_usd': round(course['price_toman'] / rate),
        'weather': weather,
        'took_ms': round((time.perf_counter() - started) * 1000),
    }


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
