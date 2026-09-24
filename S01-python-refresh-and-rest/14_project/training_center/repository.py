"""A generic in-memory repository: the shape of the real database layer later."""

from collections.abc import Callable, Iterator
from typing import Protocol

from training_center.exceptions import DuplicateError, NotFoundError


class HasId(Protocol):
    """Anything with an integer `id` attribute can be stored."""

    id: int


class InMemoryRepository[T: HasId]:
    def __init__(self, entity_name: str) -> None:
        self.entity_name = entity_name
        self._items: dict[int, T] = {}

    def next_id(self) -> int:
        return max(self._items, default=0) + 1

    def add(self, item: T) -> T:
        if item.id in self._items:
            raise DuplicateError(f'{self.entity_name} {item.id} already exists')
        self._items[item.id] = item
        return item

    def get(self, item_id: int) -> T:
        try:
            return self._items[item_id]
        except KeyError:
            raise NotFoundError(self.entity_name, item_id) from None

    def find(self, predicate: Callable[[T], bool]) -> list[T]:
        """Higher-order method: the caller passes the filtering rule as a function."""
        return [item for item in self._items.values() if predicate(item)]

    def remove(self, item_id: int) -> None:
        self.get(item_id)
        del self._items[item_id]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._items.values()))
