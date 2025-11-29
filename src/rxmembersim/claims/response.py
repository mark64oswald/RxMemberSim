"""Pharmacy claim response model."""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class RejectCode(BaseModel):
    """NCPDP reject code."""

    code: str
    description: str


class DURAlert(BaseModel):
    """Drug Utilization Review alert."""

    reason_for_service: str
    clinical_significance: str
    other_pharmacy_indicator: Optional[str] = None
    previous_fill_date: Optional[str] = None
    quantity_of_previous_fill: Optional[Decimal] = None
    database_indicator: Optional[str] = None
    other_prescriber_indicator: Optional[str] = None
    message: Optional[str] = None


class ClaimResponse(BaseModel):
    """Response to pharmacy claim."""

    claim_id: str
    transaction_response_status: str  # A=Accepted, R=Rejected, C=Captured, D=Duplicate
    response_status: str  # P=Paid, R=Rejected, D=Duplicate

    # Authorization
    authorization_number: Optional[str] = None

    # Reject codes (if rejected)
    reject_codes: list[RejectCode] = Field(default_factory=list)

    # Pricing (if approved)
    ingredient_cost_paid: Optional[Decimal] = None
    dispensing_fee_paid: Optional[Decimal] = None
    flat_sales_tax_paid: Optional[Decimal] = None
    percentage_sales_tax_paid: Optional[Decimal] = None
    incentive_amount_paid: Optional[Decimal] = None
    total_amount_paid: Optional[Decimal] = None

    # Patient responsibility
    patient_pay_amount: Optional[Decimal] = None
    copay_amount: Optional[Decimal] = None
    coinsurance_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None

    # Accumulators
    amount_applied_to_deductible: Optional[Decimal] = None
    remaining_deductible: Optional[Decimal] = None
    remaining_oop: Optional[Decimal] = None

    # DUR alerts
    dur_alerts: list[DURAlert] = Field(default_factory=list)

    # Messaging
    message: Optional[str] = None
    additional_message: Optional[str] = None
