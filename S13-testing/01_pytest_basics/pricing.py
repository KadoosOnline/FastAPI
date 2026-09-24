"""Small pricing rules of the training center -- the code under test."""


class PricingError(ValueError):
    pass


def apply_discount(price: int, percent: int) -> int:
    """Price in Toman after a percentage discount, rounded down."""
    if not 0 <= percent <= 100:
        raise PricingError(f'discount must be between 0 and 100, got {percent}')
    return price * (100 - percent) // 100


def installments(total: int, parts: int) -> list[int]:
    """Split a price into `parts` payments; the first ones absorb the remainder."""
    if parts < 1:
        raise PricingError('parts must be at least 1')
    base, remainder = divmod(total, parts)
    return [base + 1 if i < remainder else base for i in range(parts)]
