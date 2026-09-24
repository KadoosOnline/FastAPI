"""A context manager that rolls repositories back if the block fails."""

import copy
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from training_center.repository import InMemoryRepository


@contextmanager
def transaction(*repositories: InMemoryRepository[Any]) -> Iterator[None]:
    """All-or-nothing changes, like a database transaction.

    with transaction(users, courses):
        ...   # an exception here restores both repositories
    """
    snapshots = [copy.deepcopy(repo._items) for repo in repositories]
    try:
        yield
    except BaseException:
        for repo, snapshot in zip(repositories, snapshots, strict=True):
            repo._items = snapshot
        raise
