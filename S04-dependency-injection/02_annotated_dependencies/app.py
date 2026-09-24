"""The modern way: `Annotated[Type, Depends(func)]`, written once, used everywhere.

    Paging = Annotated[PageParams, Depends(get_paging)]

    def list_courses(paging: Paging): ...

Three more things to see here:
1. A dependency can depend on another dependency (`get_paging` uses
   `get_max_size`). FastAPI solves the whole tree.
2. Inside one request, each dependency is called only ONCE, even if several
   parts ask for it (look at the counter in the output).
3. The type (`PageParams`) is honest, so the editor auto-completes `paging.offset`.
"""

from dataclasses import dataclass
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

app = FastAPI()
calls = {'get_max_size': 0}


@dataclass
class PageParams:
    page: int
    size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


def get_max_size() -> int:
    calls['get_max_size'] += 1
    return 50


def get_paging(
    max_size: Annotated[int, Depends(get_max_size)], page: int = 1, size: int = 10
) -> PageParams:
    return PageParams(page=max(page, 1), size=min(size, max_size))


Paging = Annotated[PageParams, Depends(get_paging)]
MaxSize = Annotated[int, Depends(get_max_size)]


@app.get('/courses')
def list_courses(paging: Paging, max_size: MaxSize) -> dict:
    return {
        'offset': paging.offset,
        'size': paging.size,
        'max_size': max_size,
        'get_max_size was called': calls['get_max_size'],  # grows by 1 per request
    }


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
