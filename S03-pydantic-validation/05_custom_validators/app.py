"""Custom validators: rules that `Field` can not express.

    @field_validator('title')       one field: clean it or reject it
    @model_validator(mode='after')  several fields together

Inside a validator: return the (maybe changed) value, or `raise ValueError`
-- Pydantic turns it into a normal validation error.

`EmailStr` checks e-mail addresses (needs `pip install pydantic[email]`).
"""

from typing import Self

from pydantic import BaseModel, EmailStr, ValidationError, field_validator, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = ' '.join(value.split())  # '  sara   ahmadi ' -> 'sara ahmadi'
        if len(value) < 2:
            raise ValueError('name is too short')
        return value.title()

    @field_validator('password')
    @classmethod
    def strong_password(cls, value: str) -> str:
        if len(value) < 8 or value.isalpha() or value.isdigit():
            raise ValueError('at least 8 characters, with letters AND digits')
        return value


class PriceRange(BaseModel):
    min_price: int = 0
    max_price: int = 1_000_000_000

    @model_validator(mode='after')
    def check_order(self) -> Self:
        if self.min_price > self.max_price:
            raise ValueError('min_price cannot be greater than max_price')
        return self


def main() -> None:
    print(UserCreate(email='Sara@Example.com', full_name='  sara   ahmadi ', password='secret123'))

    for data in [
        {'email': 'not-an-email', 'full_name': 'S', 'password': 'short'},
        {'email': 'a@b.com', 'full_name': 'Ali', 'password': 'onlyletters'},
    ]:
        try:
            UserCreate(**data)
        except ValidationError as error:
            print([f'{e["loc"][0]}: {e["msg"]}' for e in error.errors()])

    try:
        PriceRange(min_price=500, max_price=100)
    except ValidationError as error:
        print(error.errors()[0]['msg'])


if __name__ == '__main__':
    main()
