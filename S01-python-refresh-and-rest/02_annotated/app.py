"""`Annotated`: a type PLUS extra information about it.

    from typing import Annotated
    Age = Annotated[int, 'must be between 18 and 99']

For Python itself, `Age` is simply `int`. The second part (the "metadata")
is ignored by Python, but *other tools can read it*.

That is exactly how modern FastAPI is written. You will see this in every
session from now on:

    def list_courses(page: Annotated[int, Query(ge=1)] = 1): ...
    def get_me(user: Annotated[User, Depends(get_current_user)]): ...

"`page` is an int; ALSO, FastAPI, read it from the query string and make sure
it is >= 1". The type stays honest (`int`), and the extra rules travel with it.

In this example we build a tiny version of that idea ourselves: we attach
rules to types with `Annotated`, then write a function that reads the rules
back with `typing.get_type_hints(..., include_extras=True)` and validates the
arguments. That is (in 40 lines) what FastAPI and Pydantic do for us.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, get_args, get_origin, get_type_hints


@dataclass(frozen=True)
class Between:
    """A rule object that we will attach to a type."""

    low: int
    high: int


@dataclass(frozen=True)
class MinLength:
    size: int


# Reusable annotated types: define the rule ONCE, use it everywhere.
Capacity = Annotated[int, Between(1, 500)]
Title = Annotated[str, MinLength(3)]


def validate_call(func: Callable[..., object], **arguments: object) -> list[str]:
    """Check `arguments` against the rules found in the hints of `func`."""
    errors: list[str] = []
    hints = get_type_hints(func, include_extras=True)
    for name, value in arguments.items():
        hint = hints.get(name)
        if get_origin(hint) is not Annotated:
            continue
        base_type, *rules = get_args(hint)
        if not isinstance(value, base_type):
            errors.append(f'{name}: expected {base_type.__name__}, got {type(value).__name__}')
            continue
        for rule in rules:
            if isinstance(rule, Between) and not rule.low <= value <= rule.high:
                errors.append(f'{name}: must be between {rule.low} and {rule.high}')
            if isinstance(rule, MinLength) and len(value) < rule.size:
                errors.append(f'{name}: must have at least {rule.size} characters')
    return errors


def create_course(title: Title, capacity: Capacity) -> str:
    return f'created {title!r} with {capacity} seats'


def main() -> None:
    for arguments in [
        {'title': 'FastAPI', 'capacity': 20},
        {'title': 'Py', 'capacity': 0},
        {'title': 'SQL', 'capacity': '20'},
    ]:
        errors = validate_call(create_course, **arguments)
        if errors:
            print('REJECTED', arguments, '->', errors)
        else:
            print('OK      ', create_course(**arguments))

    # For Python, the annotated type is just the base type:
    print(get_type_hints(create_course))


if __name__ == '__main__':
    main()
