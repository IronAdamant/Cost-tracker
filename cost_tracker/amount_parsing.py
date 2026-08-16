"""Parse and format currency-like amounts without assuming a locale symbol."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENTS = Decimal("0.01")
ZERO = Decimal("0.00")


def parse_amount(text: str) -> Decimal:
    cleaned = text.strip().replace("$", "").replace(",", "")
    if cleaned == "":
        return ZERO
    try:
        value = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {text!r}") from exc
    if value < 0:
        raise ValueError("Amounts cannot be negative")
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def format_amount(value: Decimal, blank_if_zero: bool = False) -> str:
    quantized = value.quantize(CENTS, rounding=ROUND_HALF_UP)
    if blank_if_zero and quantized == ZERO:
        return ""
    return f"{quantized:,.2f}"


def format_amount_plain(value: Decimal, blank_if_zero: bool = False) -> str:
    quantized = value.quantize(CENTS, rounding=ROUND_HALF_UP)
    if blank_if_zero and quantized == ZERO:
        return ""
    return f"{quantized:.2f}"
