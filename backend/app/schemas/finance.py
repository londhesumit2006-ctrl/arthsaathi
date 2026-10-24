from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.services.finance_service import india_today


class FinancialProfileUpdate(BaseModel):
    account_mode: Literal["household", "business", "both"] = "household"
    current_balance: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999"))
    preferred_language: Literal["en", "hi"] = "en"


class FinancialProfileResponse(FinancialProfileUpdate):
    id: int
    currency: str
    model_config = ConfigDict(from_attributes=True)


class FinancialEntryCreate(BaseModel):
    context_type: Literal["household", "business"] = "household"
    entry_type: Literal["income", "expense"]
    amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    category: str = Field(min_length=1, max_length=60)
    description: Optional[str] = Field(default=None, max_length=240)
    occurred_on: date
    is_recurring: bool = False
    recurrence_frequency: Optional[Literal["weekly", "monthly", "yearly"]] = None

    @model_validator(mode="after")
    def validate_recurrence(self):
        if self.is_recurring and not self.recurrence_frequency:
            raise ValueError("recurrence_frequency is required for recurring entries")
        if self.occurred_on > india_today() and self.entry_type != "income":
            raise ValueError("Future expenses should be recorded as upcoming payments, not actual expenses")
        return self


class FinancialEntryResponse(FinancialEntryCreate):
    id: int
    source: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ObligationCreate(BaseModel):
    obligation_type: Literal["bill", "emi", "rent", "school_fee", "other"] = "bill"
    title: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    due_date: date
    recurrence_frequency: Optional[Literal["weekly", "monthly", "yearly"]] = None
    notes: Optional[str] = Field(default=None, max_length=2000)


class ObligationResponse(ObligationCreate):
    id: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ObligationStatusUpdate(BaseModel):
    status: Literal["pending", "paid", "cancelled"]


class BusinessProfileCreate(BaseModel):
    business_name: str = Field(min_length=1, max_length=160)
    business_type: Optional[str] = Field(default=None, max_length=80)
    opening_balance: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999"))


class BusinessProfileResponse(BusinessProfileCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InvoiceCreate(BaseModel):
    business_id: int
    direction: Literal["receivable", "payable"]
    counterparty: str = Field(min_length=1, max_length=160)
    invoice_number: Optional[str] = Field(default=None, max_length=80)
    issue_date: date
    due_date: date
    total_amount: Decimal = Field(gt=0, le=Decimal("999999999999"))
    amount_paid: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999"))

    @model_validator(mode="after")
    def validate_amount_paid(self):
        if self.amount_paid > self.total_amount:
            raise ValueError("amount_paid cannot exceed total_amount")
        if self.due_date < self.issue_date:
            raise ValueError("due_date cannot be before issue_date")
        return self


class InvoicePaymentUpdate(BaseModel):
    amount_paid: Decimal = Field(ge=0, le=Decimal("999999999999"))


class InvoiceResponse(InvoiceCreate):
    id: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OverviewResponse(BaseModel):
    context_type: Literal["household", "business"] = "household"
    current_balance: Decimal
    projected_balance_30_days: Decimal
    expected_income_30_days: Decimal
    pending_obligations_30_days: Decimal
    receivables_30_days: Decimal
    payables_30_days: Decimal
    upcoming_obligations: list[ObligationResponse]
    cash_status: Literal["comfortable", "watch", "shortfall"]
    explanation: str
