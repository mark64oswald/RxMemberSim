"""Pharmacy benefit member model."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class MemberDemographics(BaseModel):
    """Member demographic information."""

    first_name: str
    last_name: str
    date_of_birth: date
    gender: str  # M, F, U
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None


class BenefitAccumulators(BaseModel):
    """Member benefit accumulators."""

    deductible_met: Decimal = Decimal("0")
    deductible_remaining: Decimal
    oop_met: Decimal = Decimal("0")
    oop_remaining: Decimal


class RxMember(BaseModel):
    """Pharmacy benefit member."""

    member_id: str
    cardholder_id: str
    person_code: str = "01"  # 01=cardholder, 02=spouse, 03+=dependent

    # Pharmacy benefit identifiers
    bin: str  # Bank Identification Number
    pcn: str  # Processor Control Number
    group_number: str

    # Demographics
    demographics: MemberDemographics

    # Coverage dates
    effective_date: date
    termination_date: Optional[date] = None

    # Accumulators
    accumulators: BenefitAccumulators

    # Plan info
    plan_code: Optional[str] = None
    formulary_id: Optional[str] = None


class RxMemberGenerator:
    """Generate synthetic pharmacy members."""

    def generate(
        self,
        bin: str = "610014",
        pcn: str = "RXTEST",
        group_number: str = "GRP001",
    ) -> RxMember:
        """Generate a random pharmacy member."""
        from faker import Faker

        fake = Faker()

        member_id = f"RXM-{fake.random_number(digits=8, fix_len=True)}"

        return RxMember(
            member_id=member_id,
            cardholder_id=str(fake.random_number(digits=9, fix_len=True)),
            person_code="01",
            bin=bin,
            pcn=pcn,
            group_number=group_number,
            demographics=MemberDemographics(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=85),
                gender=fake.random_element(["M", "F"]),
                address_line1=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.zipcode(),
            ),
            effective_date=date(2025, 1, 1),
            accumulators=BenefitAccumulators(
                deductible_remaining=Decimal("250"),
                oop_remaining=Decimal("3000"),
            ),
        )
