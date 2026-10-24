"""Deterministic cash-flow calculations used by ArthSaathi.

These calculations are planning estimates based on user-entered records. They are
not credit scores, lending decisions, or guarantees of future cash availability.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Iterable, Mapping, Any

ZERO = Decimal("0.00")
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def india_today() -> date:
    """Return the current calendar date in the product's primary timezone."""
    return datetime.now(INDIA_TIMEZONE).date()


def _amount(value: Any) -> Decimal:
    """Convert database numeric values safely to Decimal."""
    return value if isinstance(value, Decimal) else Decimal(str(value or "0"))


def _status(projected_balance: Decimal, current_balance: Decimal) -> tuple[str, str]:
    if projected_balance < ZERO:
        return (
            "shortfall",
            "Based on the information entered, planned payments may exceed available money in the next 30 days. Review due dates and confirm expected income.",
        )
    watch_threshold = max(current_balance * Decimal("0.25"), Decimal("1000"))
    if projected_balance <= watch_threshold:
        return (
            "watch",
            "Your projected balance is relatively low compared with the money available today. Keep essential payments in view.",
        )
    return (
        "comfortable",
        "No shortfall is indicated by the information currently entered. Keep your income, expenses and due dates up to date.",
    )


def calculate_household_projection(
    *,
    current_balance: Decimal,
    expected_income_entries: Iterable[Any],
    obligations: Iterable[Any],
    today: date | None = None,
    horizon_days: int = 30,
) -> dict[str, Decimal | str]:
    """Calculate household cash position without mixing in business records.

    Future income entries are included only when dated after today and within
    the horizon. Pending overdue obligations are included because they remain
    unpaid. The current balance is the starting point, so historical entries
    are intentionally not added again.
    """
    today = today or india_today()
    horizon = today + timedelta(days=horizon_days)
    expected_income = sum(
        (
            _amount(entry.amount)
            for entry in expected_income_entries
            if entry.occurred_on is not None and today < entry.occurred_on <= horizon
        ),
        ZERO,
    )
    pending = sum(
        (
            _amount(item.amount)
            for item in obligations
            if item.status == "pending" and item.due_date <= horizon
        ),
        ZERO,
    )
    current = _amount(current_balance)
    projected = current + expected_income - pending
    cash_status, explanation = _status(projected, current)
    return {
        "current_balance": current,
        "projected_balance_30_days": projected,
        "expected_income_30_days": expected_income,
        "pending_obligations_30_days": pending,
        "receivables_30_days": ZERO,
        "payables_30_days": ZERO,
        "cash_status": cash_status,
        "explanation": explanation,
    }


def calculate_business_projection(
    *,
    opening_balances: Iterable[Decimal],
    expected_income_entries: Iterable[Any],
    invoices: Iterable[Any],
    today: date | None = None,
    horizon_days: int = 30,
) -> dict[str, Decimal | str]:
    """Calculate business cash position separately from household money."""
    today = today or india_today()
    horizon = today + timedelta(days=horizon_days)
    current = sum((_amount(value) for value in opening_balances), ZERO)
    expected_income = sum(
        (
            _amount(entry.amount)
            for entry in expected_income_entries
            if entry.occurred_on is not None and today < entry.occurred_on <= horizon
        ),
        ZERO,
    )
    receivables = ZERO
    payables = ZERO
    for invoice in invoices:
        if invoice.status not in {"open", "partial"} or invoice.due_date > horizon:
            continue
        outstanding = max(ZERO, _amount(invoice.total_amount) - _amount(invoice.amount_paid))
        if invoice.direction == "receivable":
            receivables += outstanding
        elif invoice.direction == "payable":
            payables += outstanding
    projected = current + expected_income + receivables - payables
    cash_status, explanation = _status(projected, current)
    return {
        "current_balance": current,
        "projected_balance_30_days": projected,
        "expected_income_30_days": expected_income,
        "pending_obligations_30_days": ZERO,
        "receivables_30_days": receivables,
        "payables_30_days": payables,
        "cash_status": cash_status,
        "explanation": explanation,
    }
