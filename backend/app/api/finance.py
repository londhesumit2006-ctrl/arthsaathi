from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.finance import (
    FinancialProfile, FinancialEntry, FinancialObligation,
    BusinessProfile, BusinessInvoice,
)
from app.schemas.finance import (
    FinancialProfileUpdate, FinancialProfileResponse,
    FinancialEntryCreate, FinancialEntryResponse,
    ObligationCreate, ObligationResponse, ObligationStatusUpdate,
    BusinessProfileCreate, BusinessProfileResponse,
    InvoiceCreate, InvoiceResponse, InvoicePaymentUpdate, OverviewResponse,
)
from app.utils.dependencies import get_current_user
from app.services.finance_service import calculate_business_projection, calculate_household_projection, india_today

router = APIRouter(prefix="/finance", tags=["ArthSaathi finance"])


def _get_or_create_profile(db: Session, user_id: int) -> FinancialProfile:
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
    if profile is None:
        profile = FinancialProfile(user_id=user_id, account_mode="household", current_balance=Decimal("0"))
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/profile", response_model=FinancialProfileResponse)
def get_financial_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_or_create_profile(db, user.id)


@router.put("/profile", response_model=FinancialProfileResponse)
def update_financial_profile(payload: FinancialProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_or_create_profile(db, user.id)
    profile.account_mode = payload.account_mode
    profile.current_balance = payload.current_balance
    profile.preferred_language = payload.preferred_language
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/entries", response_model=FinancialEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(payload: FinancialEntryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = FinancialEntry(user_id=user.id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/entries", response_model=list[FinancialEntryResponse])
def list_entries(
    context_type: str | None = Query(default=None, pattern="^(household|business)$"),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    query = db.query(FinancialEntry).filter(FinancialEntry.user_id == user.id)
    if context_type:
        query = query.filter(FinancialEntry.context_type == context_type)
    return query.order_by(FinancialEntry.occurred_on.desc(), FinancialEntry.id.desc()).limit(limit).all()


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(FinancialEntry).filter(FinancialEntry.id == entry_id, FinancialEntry.user_id == user.id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Financial entry not found")
    db.delete(entry)
    db.commit()


@router.post("/obligations", response_model=ObligationResponse, status_code=status.HTTP_201_CREATED)
def create_obligation(payload: ObligationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obligation = FinancialObligation(user_id=user.id, **payload.model_dump())
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


@router.get("/obligations", response_model=list[ObligationResponse])
def list_obligations(
    status_filter: str | None = Query(default=None, alias="status", pattern="^(pending|paid|cancelled)$"),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    query = db.query(FinancialObligation).filter(FinancialObligation.user_id == user.id)
    if status_filter:
        query = query.filter(FinancialObligation.status == status_filter)
    return query.order_by(FinancialObligation.due_date.asc()).limit(limit).all()


@router.patch("/obligations/{obligation_id}/status", response_model=ObligationResponse)
def update_obligation_status(obligation_id: int, payload: ObligationStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    obligation = db.query(FinancialObligation).filter(
        FinancialObligation.id == obligation_id, FinancialObligation.user_id == user.id
    ).first()
    if obligation is None:
        raise HTTPException(status_code=404, detail="Obligation not found")
    obligation.status = payload.status
    db.commit()
    db.refresh(obligation)
    return obligation


@router.post("/businesses", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
def create_business(payload: BusinessProfileCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    business = BusinessProfile(user_id=user.id, **payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get("/businesses", response_model=list[BusinessProfileResponse])
def list_businesses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(BusinessProfile).filter(BusinessProfile.user_id == user.id).order_by(BusinessProfile.id.asc()).all()


@router.post("/businesses/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    business = db.query(BusinessProfile).filter(
        BusinessProfile.id == payload.business_id, BusinessProfile.user_id == user.id
    ).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    values = payload.model_dump()
    amount_paid = values["amount_paid"]
    total_amount = values["total_amount"]
    values["status"] = "paid" if amount_paid == total_amount else ("partial" if amount_paid > 0 else "open")
    invoice = BusinessInvoice(user_id=user.id, **values)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/businesses/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    business_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(get_current_user),
):
    query = db.query(BusinessInvoice).filter(BusinessInvoice.user_id == user.id)
    if business_id is not None:
        query = query.filter(BusinessInvoice.business_id == business_id)
    return query.order_by(BusinessInvoice.due_date.asc()).limit(200).all()


@router.patch("/businesses/invoices/{invoice_id}/payment", response_model=InvoiceResponse)
def update_invoice_payment(invoice_id: int, payload: InvoicePaymentUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = db.query(BusinessInvoice).filter(
        BusinessInvoice.id == invoice_id, BusinessInvoice.user_id == user.id
    ).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if payload.amount_paid > invoice.total_amount:
        raise HTTPException(status_code=422, detail="amount_paid cannot exceed total_amount")
    invoice.amount_paid = payload.amount_paid
    invoice.status = "paid" if payload.amount_paid == invoice.total_amount else ("partial" if payload.amount_paid > 0 else "open")
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    context_type: str = Query(default="household", pattern="^(household|business)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return a 30-day estimate for one financial context at a time.

    Household cash and business cash are intentionally kept separate. A user
    with both account modes must not see business receivables treated as money
    available to pay household rent, or household savings treated as business
    working capital.
    """
    today = india_today()
    horizon = today + timedelta(days=30)
    profile = _get_or_create_profile(db, user.id)

    if context_type == "household":
        entries = db.query(FinancialEntry).filter(
            FinancialEntry.user_id == user.id,
            FinancialEntry.context_type == "household",
            FinancialEntry.entry_type == "income",
            FinancialEntry.occurred_on > today,
            FinancialEntry.occurred_on <= horizon,
        ).all()
        obligations = db.query(FinancialObligation).filter(
            FinancialObligation.user_id == user.id,
            FinancialObligation.status == "pending",
            FinancialObligation.due_date <= horizon,
        ).order_by(FinancialObligation.due_date.asc()).all()
        result = calculate_household_projection(
            current_balance=profile.current_balance,
            expected_income_entries=entries,
            obligations=obligations,
            today=today,
        )
        upcoming_obligations = obligations[:8]
    else:
        businesses = db.query(BusinessProfile).filter(BusinessProfile.user_id == user.id).all()
        entries = db.query(FinancialEntry).filter(
            FinancialEntry.user_id == user.id,
            FinancialEntry.context_type == "business",
            FinancialEntry.entry_type == "income",
            FinancialEntry.occurred_on > today,
            FinancialEntry.occurred_on <= horizon,
        ).all()
        invoices = db.query(BusinessInvoice).filter(
            BusinessInvoice.user_id == user.id,
            BusinessInvoice.status.in_(["open", "partial"]),
            BusinessInvoice.due_date <= horizon,
        ).all()
        result = calculate_business_projection(
            opening_balances=[business.opening_balance for business in businesses],
            expected_income_entries=entries,
            invoices=invoices,
            today=today,
        )
        upcoming_obligations = []

    return OverviewResponse(
        context_type=context_type,
        **result,
        upcoming_obligations=upcoming_obligations,
    )
