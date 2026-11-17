from datetime import datetime, timezone
from decimal import Decimal

from app.routers.invoices import financial_year, money


def test_financial_year_april_boundary() -> None:
    assert financial_year(datetime(2026, 3, 31, tzinfo=timezone.utc)) == "25-26"
    assert financial_year(datetime(2026, 4, 1, tzinfo=timezone.utc)) == "26-27"


def test_money_rounds_to_paise() -> None:
    assert money(Decimal("12.345")) == Decimal("12.35")
    assert money(Decimal("12.344")) == Decimal("12.34")
