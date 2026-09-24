"""Consuming a third-party REST API: an integration you do not control.

Rules for foreign APIs:
* read their documentation, model ONLY the fields you need (extra='ignore')
* timeouts everywhere; their outage must not become yours
* validate their data: a missing field should be a clear error, not a KeyError deep inside
* keep the integration in one module, behind your own functions

Here: a report "which user finished the most todos", from
https://jsonplaceholder.typicode.com, with users and todos fetched concurrently.
"""

import asyncio
from collections import Counter

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError


class ExternalModel(BaseModel):
    model_config = ConfigDict(extra='ignore')


class User(ExternalModel):
    id: int
    name: str
    email: str


class Todo(ExternalModel):
    userId: int  # noqa: N815  (their field name, not ours)
    completed: bool


class ExternalApiError(Exception):
    pass


async def fetch_list[T: ExternalModel](
    client: httpx.AsyncClient, path: str, model: type[T]
) -> list[T]:
    try:
        response = await client.get(path)
        response.raise_for_status()
        return [model.model_validate(item) for item in response.json()]
    except httpx.HTTPError as error:
        raise ExternalApiError(f'{path}: {error!r}') from error
    except ValidationError as error:
        raise ExternalApiError(
            f'{path}: unexpected data ({error.error_count()} problems)'
        ) from error


async def main() -> None:
    async with httpx.AsyncClient(
        base_url='https://jsonplaceholder.typicode.com', timeout=10
    ) as client:
        try:
            users, todos = await asyncio.gather(
                fetch_list(client, '/users', User), fetch_list(client, '/todos', Todo)
            )
        except ExternalApiError as error:
            print('The external API failed; our program continues without it:', error)
            return

    finished = Counter(todo.userId for todo in todos if todo.completed)
    names = {user.id: user.name for user in users}
    for user_id, count in finished.most_common(3):
        print(f'{names[user_id]:<25} {count} todos finished')


if __name__ == '__main__':
    asyncio.run(main())
