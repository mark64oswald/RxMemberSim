# Pharmacy Claims

Generate and process NCPDP pharmacy claims with RxMemberSim.

## Claim Model

### PharmacyClaim

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date
from decimal import Decimal

claim = PharmacyClaim(
    # Identification
    claim_id="CLM001",
    transaction_code=TransactionCode.BILLING,
    service_date=date.today(),

    # Pharmacy
    pharmacy_npi="9876543210",

    # Member
    member_id="MEM001",
    cardholder_id="CH001",
    person_code="01",
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001",

    # Prescription
    prescription_number="RX123456",
    fill_number=1,
    ndc="00071015523",
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    daw_code="0",

    # Prescriber
    prescriber_npi="1234567890",

    # Pricing
    ingredient_cost_submitted=Decimal("15.00"),
    dispensing_fee_submitted=Decimal("2.00"),
    patient_paid_submitted=Decimal("0.00"),
    usual_customary_charge=Decimal("25.00"),
    gross_amount_due=Decimal("17.00"),
)
```

### Transaction Codes

| Code | Name | Description |
|------|------|-------------|
| B1 | Billing | New prescription claim |
| B2 | Reversal | Cancel previous claim |
| B3 | Rebill | Resubmit with changes |
| E1 | Eligibility | Check member eligibility |

```python
from rxmembersim.claims.claim import TransactionCode

# New claim
claim.transaction_code = TransactionCode.BILLING

# Reversal
reversal = PharmacyClaim(
    transaction_code=TransactionCode.REVERSAL,
    # ... reference original claim
)
```

### DAW (Dispense as Written) Codes

| Code | Description |
|------|-------------|
| 0 | No product selection indicated |
| 1 | Substitution not allowed by prescriber |
| 2 | Patient requested brand |
| 3 | Pharmacist selected product |
| 4 | Generic not in stock |
| 5 | Brand dispensed as generic |
| 7 | Brand mandated by law |
| 8 | Generic not available |
| 9 | Other |

## Adjudication

### AdjudicationEngine

```python
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator

# Create engine with formulary
formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)

# Adjudicate claim
response = engine.adjudicate(claim, member)
```

### ClaimResponse

```python
# Response fields
response.response_status      # A=Approved, R=Rejected, P=Paid
response.authorization_number # If approved
response.total_amount_paid    # Plan payment
response.patient_pay_amount   # Patient responsibility
response.copay_amount         # Copay portion
response.coinsurance_amount   # Coinsurance portion
response.deductible_amount    # Deductible applied
response.reject_codes         # List of reject codes if R
```

### Response Status Codes

| Code | Status | Description |
|------|--------|-------------|
| A | Accepted | Claim approved |
| R | Rejected | Claim denied |
| P | Paid | Paid with changes |
| D | Duplicate | Duplicate claim |

## Reject Codes

### Common Reject Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 70 | Product/Service Not Covered | Check formulary |
| 75 | Prior Authorization Required | Submit PA |
| 76 | Plan Limitations Exceeded | Check quantity limits |
| 79 | Refill Too Soon | Wait or submit override |
| 88 | DUR Reject | Review DUR conflict |
| MR | Missing/Invalid Prescriber ID | Verify NPI |
| NN | Missing/Invalid Cardholder ID | Verify member ID |

### Handling Rejects

```python
response = engine.adjudicate(claim, member)

if response.response_status == "R":
    for reject in response.reject_codes:
        print(f"Reject: {reject.code} - {reject.description}")

        if reject.code == "75":
            # Prior auth required
            print("Submit prior authorization request")
        elif reject.code == "79":
            # Refill too soon
            print(f"Earliest refill date: {reject.additional_info}")
```

## Claim Scenarios

### Clean Claim (Approved)

```python
# Generic drug, tier 1, no restrictions
claim = PharmacyClaim(
    ndc="00071015523",  # Atorvastatin (generic)
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    # ...
)

response = engine.adjudicate(claim, member)
# response.response_status == "P"
# response.copay_amount == Decimal("10.00")  # Tier 1 copay
```

### PA Required

```python
# Specialty drug requiring PA
claim = PharmacyClaim(
    ndc="00169413512",  # Ozempic
    quantity_dispensed=Decimal("1"),
    days_supply=28,
    # ...
)

response = engine.adjudicate(claim, member)
# response.response_status == "R"
# response.reject_codes[0].code == "75"  # PA Required
```

### Quantity Limit Exceeded

```python
# Exceeds quantity limit
claim = PharmacyClaim(
    ndc="00071015523",
    quantity_dispensed=Decimal("180"),  # 6 months supply
    days_supply=180,
    # ...
)

response = engine.adjudicate(claim, member)
# response.response_status == "R"
# response.reject_codes[0].code == "76"  # Plan Limitations
```

### Early Refill

```python
# Refill too soon (within 75% of previous fill)
# Previous fill: 30 days on Jan 1
# Current date: Jan 15 (only 50% through)

claim = PharmacyClaim(
    ndc="00071015523",
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    service_date=date(2024, 1, 15),
    # ...
)

response = engine.adjudicate(claim, member)
# response.response_status == "R"
# response.reject_codes[0].code == "79"  # Refill Too Soon
```

## Batch Processing

### Generate Multiple Claims

```python
from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date, timedelta
from decimal import Decimal

generator = RxMemberGenerator(seed=42)
members = [generator.generate(bin="610014", pcn="TEST", group_number="GRP001")
           for _ in range(10)]

claims = []
for i, member in enumerate(members):
    claim = PharmacyClaim(
        claim_id=f"CLM{i:04d}",
        transaction_code=TransactionCode.BILLING,
        service_date=date.today() - timedelta(days=i),
        pharmacy_npi="9876543210",
        member_id=member.member_id,
        cardholder_id=member.cardholder_id,
        person_code=member.person_code,
        bin=member.bin,
        pcn=member.pcn,
        group_number=member.group_number,
        prescription_number=f"RX{i:06d}",
        fill_number=1,
        ndc="00071015523",
        quantity_dispensed=Decimal("30"),
        days_supply=30,
        daw_code="0",
        prescriber_npi="1234567890",
        ingredient_cost_submitted=Decimal("15.00"),
        dispensing_fee_submitted=Decimal("2.00"),
        patient_paid_submitted=Decimal("0.00"),
        usual_customary_charge=Decimal("25.00"),
        gross_amount_due=Decimal("17.00"),
    )
    claims.append(claim)

# Adjudicate all
for claim in claims:
    response = engine.adjudicate(claim, member)
    print(f"{claim.claim_id}: {response.response_status}")
```

## Next Steps

- **[Formulary Management](formulary.md)** - Configure drug coverage
- **[DUR Screening](dur-screening.md)** - Drug interaction checks
- **[Prior Authorization](prior-auth.md)** - PA workflows