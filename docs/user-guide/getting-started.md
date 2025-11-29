# Getting Started with RxMemberSim

This guide walks you through installing RxMemberSim and generating your first pharmacy data.

## Installation

### From PyPI

```bash
pip install rxmembersim
```

### From Source

```bash
git clone https://github.com/mark64oswald/rxmembersim.git
cd rxmembersim
pip install -e ".[dev]"
```

### Verify Installation

```python
from rxmembersim.core.member import RxMemberGenerator
print("RxMemberSim installed successfully!")
```

## Key Concepts

### Pharmacy Member

A pharmacy member represents a person with pharmacy benefits:

```python
from rxmembersim.core.member import RxMemberGenerator

generator = RxMemberGenerator()
member = generator.generate(
    bin="610014",           # Bank Identification Number
    pcn="RXTEST",           # Processor Control Number
    group_number="GRP001"   # Group/employer identifier
)

print(f"Member ID: {member.member_id}")
print(f"Cardholder ID: {member.cardholder_id}")
print(f"BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")
```

**Key Fields:**
- `bin` - 6-digit Bank Identification Number (routes claims to PBM)
- `pcn` - Processor Control Number (identifies specific processor)
- `group_number` - Employer or group identifier
- `cardholder_id` - Unique member identifier on card
- `person_code` - Dependent code (01=cardholder, 02=spouse, 03+=children)

### Accumulators

Track deductible and out-of-pocket spending:

```python
print(f"Deductible Met: ${member.accumulators.deductible_met}")
print(f"Deductible Remaining: ${member.accumulators.deductible_remaining}")
print(f"OOP Met: ${member.accumulators.oop_met}")
print(f"OOP Remaining: ${member.accumulators.oop_remaining}")
```

### Pharmacy Claim

A claim represents a prescription fill request:

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date
from decimal import Decimal

claim = PharmacyClaim(
    claim_id="CLM001",
    transaction_code=TransactionCode.BILLING,  # B1
    service_date=date.today(),
    pharmacy_npi="9876543210",
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    bin=member.bin,
    pcn=member.pcn,
    group_number=member.group_number,
    ndc="00071015523",              # Atorvastatin 10mg
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    daw_code="0",                   # No product selection
    prescriber_npi="1234567890",
    ingredient_cost_submitted=Decimal("15.00"),
    dispensing_fee_submitted=Decimal("2.00"),
)
```

### Formulary

A formulary defines drug coverage and pricing:

```python
from rxmembersim.formulary.formulary import FormularyGenerator

formulary = FormularyGenerator().generate_standard_commercial()

# Check if a drug is covered
status = formulary.check_coverage("00071015523")
print(f"Covered: {status.covered}")
print(f"Tier: {status.tier} ({status.tier_name})")
print(f"Copay: ${status.copay}")
```

**Standard Tiers:**
| Tier | Name | Typical Cost |
|------|------|--------------|
| 1 | Preferred Generic | $10-15 |
| 2 | Non-Preferred Generic | $20-30 |
| 3 | Preferred Brand | $35-50 |
| 4 | Non-Preferred Brand | $75-100 |
| 5 | Specialty | 20-30% coinsurance |

## Basic Workflow

### 1. Generate a Member

```python
from rxmembersim.core.member import RxMemberGenerator

generator = RxMemberGenerator()
member = generator.generate(bin="610014", pcn="RXTEST", group_number="GRP001")
```

### 2. Create a Claim

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date
from decimal import Decimal

claim = PharmacyClaim(
    claim_id="CLM001",
    transaction_code=TransactionCode.BILLING,
    service_date=date.today(),
    pharmacy_npi="9876543210",
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    person_code=member.person_code,
    bin=member.bin,
    pcn=member.pcn,
    group_number=member.group_number,
    prescription_number="RX123456",
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
```

### 3. Adjudicate the Claim

```python
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator

formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)
response = engine.adjudicate(claim, member)

print(f"Status: {response.response_status}")
print(f"Plan Pay: ${response.total_amount_paid}")
print(f"Patient Pay: ${response.patient_pay_amount}")
```

## Seeding for Reproducibility

Use seeds for deterministic generation:

```python
from rxmembersim.core.member import RxMemberGenerator

# Same seed = same member every time
gen1 = RxMemberGenerator(seed=42)
member1 = gen1.generate(bin="610014", pcn="TEST", group_number="GRP001")

gen2 = RxMemberGenerator(seed=42)
member2 = gen2.generate(bin="610014", pcn="TEST", group_number="GRP001")

assert member1.member_id == member2.member_id  # True
```

## Next Steps

- **[Pharmacy Claims](pharmacy-claims.md)** - Deep dive into claim processing
- **[Formulary Management](formulary.md)** - Configure drug coverage
- **[DUR Screening](dur-screening.md)** - Drug interaction checks
- **[First Claim Tutorial](../tutorials/first-claim.md)** - Step-by-step walkthrough