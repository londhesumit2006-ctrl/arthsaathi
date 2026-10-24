from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.services.finance_service import (
    calculate_business_projection,
    calculate_household_projection,
)


def test_household_projection_includes_expected_income_and_overdue_pending_bills():
    today = date(2026, 10, 24)
    entries = [
        SimpleNamespace(amount=Decimal("12000.00"), occurred_on=today + timedelta(days=10)),
        SimpleNamespace(amount=Decimal("5000.00"), occurred_on=today + timedelta(days=45)),
    ]
    obligations = [
        SimpleNamespace(amount=Decimal("4000.00"), due_date=today - timedelta(days=2), status="pending"),
        SimpleNamespace(amount=Decimal("2000.00"), due_date=today + timedelta(days=5), status="pending"),
        SimpleNamespace(amount=Decimal("900.00"), due_date=today + timedelta(days=4), status="paid"),
        SimpleNamespace(amount=Decimal("800.00"), due_date=today + timedelta(days=40), status="pending"),
    ]

    result = calculate_household_projection(
        current_balance=Decimal("5000.00"),
        expected_income_entries=entries,
        obligations=obligations,
        today=today,
    )

    assert result["current_balance"] == Decimal("5000.00")
    assert result["expected_income_30_days"] == Decimal("12000.00")
    assert result["pending_obligations_30_days"] == Decimal("6000.00")
    assert result["projected_balance_30_days"] == Decimal("11000.00")
    assert result["cash_status"] == "comfortable"


def test_business_projection_uses_unpaid_invoice_remainders_and_ignores_paid_or_late_horizon():
    today = date(2026, 10, 24)
    invoices = [
        SimpleNamespace(direction="receivable", total_amount=Decimal("10000"), amount_paid=Decimal("3000"), status="partial", due_date=today + timedelta(days=5)),
        SimpleNamespace(direction="payable", total_amount=Decimal("6000"), amount_paid=Decimal("1000"), status="open", due_date=today - timedelta(days=3)),
        SimpleNamespace(direction="receivable", total_amount=Decimal("2000"), amount_paid=Decimal("2000"), status="paid", due_date=today + timedelta(days=2)),
        SimpleNamespace(direction="receivable", total_amount=Decimal("4000"), amount_paid=Decimal("0"), status="open", due_date=today + timedelta(days=50)),
    ]
    result = calculate_business_projection(
        opening_balances=[Decimal("8000"), Decimal("2000")],
        expected_income_entries=[],
        invoices=invoices,
        today=today,
    )

    assert result["current_balance"] == Decimal("10000")
    assert result["receivables_30_days"] == Decimal("7000")
    assert result["payables_30_days"] == Decimal("5000")
    assert result["projected_balance_30_days"] == Decimal("12000")


def test_household_and_business_cash_are_calculated_independently():
    today = date(2026, 10, 24)
    household = calculate_household_projection(
        current_balance=Decimal("3000"),
        expected_income_entries=[],
        obligations=[SimpleNamespace(amount=Decimal("5000"), due_date=today + timedelta(days=2), status="pending")],
        today=today,
    )
    business = calculate_business_projection(
        opening_balances=[Decimal("50000")],
        expected_income_entries=[],
        invoices=[],
        today=today,
    )

    assert household["projected_balance_30_days"] == Decimal("-2000")
    assert household["cash_status"] == "shortfall"
    assert business["projected_balance_30_days"] == Decimal("50000")
    assert business["cash_status"] == "comfortable"
