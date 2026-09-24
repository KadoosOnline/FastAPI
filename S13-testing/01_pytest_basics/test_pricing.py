"""pytest basics: plain functions and `assert`.

    pytest                 find and run every test_*.py file
    pytest -v              one line per test
    pytest -k discount     only tests whose name contains "discount"
    pytest -x              stop at the first failure

A test has three parts: ARRANGE (prepare), ACT (call), ASSERT (check).
Test the unhappy paths too: bad input must fail in the way we promised.
"""

import pytest

from pricing import PricingError, apply_discount, installments


def test_discount_reduces_the_price() -> None:
    assert apply_discount(1_000_000, 10) == 900_000


def test_no_discount_keeps_the_price() -> None:
    assert apply_discount(1_000_000, 0) == 1_000_000


@pytest.mark.parametrize(
    ('price', 'percent', 'expected'),
    [
        (100, 50, 50),
        (99, 50, 49),  # rounded down
        (4_800_000, 100, 0),
    ],
)
def test_discount_table(price: int, percent: int, expected: int) -> None:
    assert apply_discount(price, percent) == expected


@pytest.mark.parametrize('percent', [-1, 101, 1000])
def test_invalid_discount_is_rejected(percent: int) -> None:
    with pytest.raises(PricingError, match='between 0 and 100'):
        apply_discount(1000, percent)


def test_installments_add_up_to_the_total() -> None:
    parts = installments(1_000_000, 3)

    assert sum(parts) == 1_000_000
    assert parts == [333_334, 333_333, 333_333]


@pytest.fixture
def big_price() -> int:
    """A fixture: reusable test data, created fresh for every test that asks for it."""
    return 12_345_678


def test_installments_with_fixture(big_price: int) -> None:
    assert len(installments(big_price, 12)) == 12


def test_zero_installments_fail() -> None:
    with pytest.raises(PricingError):
        installments(100, 0)
