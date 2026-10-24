from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Numeric, Text, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    __table_args__ = (
        CheckConstraint("account_mode IN ('household', 'business', 'both')", name="ck_financial_profiles_account_mode"),
        CheckConstraint("current_balance >= 0", name="ck_financial_profiles_current_balance_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    account_mode = Column(String(20), nullable=False, default="household")  # household, business, both
    current_balance = Column(Numeric(14, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="INR")
    preferred_language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="financial_profile")


class FinancialEntry(Base):
    __tablename__ = "financial_entries"
    __table_args__ = (
        Index("ix_financial_entries_user_date", "user_id", "occurred_on"),
        Index("ix_financial_entries_user_context", "user_id", "context_type"),
        CheckConstraint("context_type IN ('household', 'business')", name="ck_financial_entries_context_type"),
        CheckConstraint("entry_type IN ('income', 'expense')", name="ck_financial_entries_entry_type"),
        CheckConstraint("amount > 0", name="ck_financial_entries_amount_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    context_type = Column(String(20), nullable=False, default="household")  # household, business
    entry_type = Column(String(10), nullable=False)  # income, expense
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String(60), nullable=False)
    description = Column(String(240), nullable=True)
    occurred_on = Column(Date, nullable=False)
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_frequency = Column(String(20), nullable=True)  # weekly, monthly, yearly
    source = Column(String(20), nullable=False, default="manual")  # manual, imported, document
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="financial_entries")


class FinancialObligation(Base):
    __tablename__ = "financial_obligations"
    __table_args__ = (
        Index("ix_financial_obligations_user_due", "user_id", "due_date"),
        CheckConstraint("amount > 0", name="ck_financial_obligations_amount_positive"),
        CheckConstraint("status IN ('pending', 'paid', 'cancelled')", name="ck_financial_obligations_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    obligation_type = Column(String(30), nullable=False, default="bill")  # bill, emi, rent, school_fee, other
    title = Column(String(120), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, paid, cancelled
    recurrence_frequency = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="financial_obligations")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    __table_args__ = (CheckConstraint("opening_balance >= 0", name="ck_business_profiles_opening_balance_nonnegative"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_name = Column(String(160), nullable=False)
    business_type = Column(String(80), nullable=True)
    opening_balance = Column(Numeric(14, 2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="business_profiles")
    invoices = relationship("BusinessInvoice", back_populates="business", cascade="all, delete-orphan")


class BusinessInvoice(Base):
    __tablename__ = "business_invoices"
    __table_args__ = (
        Index("ix_business_invoices_user_due", "user_id", "due_date"),
        Index("ix_business_invoices_business_direction", "business_id", "direction"),
        CheckConstraint("direction IN ('receivable', 'payable')", name="ck_business_invoices_direction"),
        CheckConstraint("total_amount > 0", name="ck_business_invoices_total_positive"),
        CheckConstraint("amount_paid >= 0 AND amount_paid <= total_amount", name="ck_business_invoices_amount_paid_range"),
        CheckConstraint("status IN ('open', 'partial', 'paid', 'cancelled')", name="ck_business_invoices_status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    direction = Column(String(12), nullable=False)  # receivable, payable
    counterparty = Column(String(160), nullable=False)
    invoice_number = Column(String(80), nullable=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(14, 2), nullable=False)
    amount_paid = Column(Numeric(14, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="open")  # open, partial, paid, cancelled
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    business = relationship("BusinessProfile", back_populates="invoices")
    user = relationship("User")
