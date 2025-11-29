# Your First Pharmacy Claim

This tutorial walks you through generating and adjudicating your first pharmacy claim with RxMemberSim.

## Prerequisites

Install RxMemberSim:

```bash
pip install rxmembersim
# or from source
git clone https://github.com/mark64oswald/rxmembersim.git
cd rxmembersim
pip install -e ".[dev]"
```

## Step 1: Generate a Pharmacy Member

First, create a member with pharmacy benefits:

```python
from rxmembersim.core.member import RxMemberGenerator

# Create generator with seed for reproducibility
generator = RxMemberGenerator(seed=42)

# Generate member
member = generator.generate(
    bin="610014",           # Bank ID Number
    pcn="RXTEST",           # Processor Control Number
    group_number="GRP001"   # Group/employer ID
)

print("=== Member Generated ===")
print(f"Member ID: {member.member_id}")
print(f"Cardholder ID: {member.cardholder_id}")
print(f"Name: {member.demographics.first_name} {member.demographics.last_name}")
print(f"DOB: {member.demographics.date_of_birth}")
print(f"BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")
print(f"Deductible Remaining: ${member.accumulators.deductible_remaining}")
print(f"OOP Remaining: ${member.accumulators.oop_remaining}")
```

**Output:**
```
=== Member Generated ===
Member ID: MEM-7f8a9b12
Cardholder ID: CH-7f8a9b12
Name: John Smith
DOB: 1970-03-15
BIN/PCN/Group: 610014/RXTEST/GRP001
Deductible Remaining: $500.00
OOP Remaining: $3000.00
```

## Step 2: Check the Formulary

Before submitting a claim, check if the drug is covered:

```python
from rxmembersim.formulary.formulary import FormularyGenerator

# Generate standard commercial formulary
formulary = FormularyGenerator().generate_standard_commercial()

# Check coverage for Atorvastatin (generic statin)
ndc = "00071015523"  # Atorvastatin 10mg
status = formulary.check_coverage(ndc)

print("\n=== Formulary Check ===")
print(f"NDC: {ndc}")
print(f"Covered: {status.covered}")
print(f"Tier: {status.tier} ({status.tier_name})")
print(f"Copay: ${status.copay}")
print(f"Requires PA: {status.requires_pa}")
print(f"Step Therapy: {status.step_therapy}")
```

**Output:**
```
=== Formulary Check ===
NDC: 00071015523
Covered: True
Tier: 1 (Preferred Generic)
Copay: $10.00
Requires PA: False
Step Therapy: False
```

## Step 3: Create a Pharmacy Claim

Now create the claim for a 30-day supply:

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date
from decimal import Decimal

claim = PharmacyClaim(
    # Claim identification
    claim_id="CLM001",
    transaction_code=TransactionCode.BILLING,  # B1 = new claim
    service_date=date.today(),

    # Pharmacy
    pharmacy_npi="9876543210",

    # Member info (from generated member)
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    person_code=member.person_code,
    bin=member.bin,
    pcn=member.pcn,
    group_number=member.group_number,

    # Prescription details
    prescription_number="RX123456",
    fill_number=1,                      # Original fill
    ndc="00071015523",                  # Atorvastatin 10mg
    quantity_dispensed=Decimal("30"),   # 30 tablets
    days_supply=30,                     # 30 days
    daw_code="0",                       # No product selection

    # Prescriber
    prescriber_npi="1234567890",

    # Pricing
    ingredient_cost_submitted=Decimal("15.00"),
    dispensing_fee_submitted=Decimal("2.00"),
    patient_paid_submitted=Decimal("0.00"),
    usual_customary_charge=Decimal("25.00"),
    gross_amount_due=Decimal("17.00"),
)

print("\n=== Claim Created ===")
print(f"Claim ID: {claim.claim_id}")
print(f"Transaction: {claim.transaction_code.value}")
print(f"Drug NDC: {claim.ndc}")
print(f"Quantity: {claim.quantity_dispensed}")
print(f"Days Supply: {claim.days_supply}")
print(f"Gross Amount Due: ${claim.gross_amount_due}")
```

**Output:**
```
=== Claim Created ===
Claim ID: CLM001
Transaction: B1
Drug NDC: 00071015523
Quantity: 30
Days Supply: 30
Gross Amount Due: $17.00
```

## Step 4: Adjudicate the Claim

Submit the claim for adjudication:

```python
from rxmembersim.claims.adjudication import AdjudicationEngine

# Create adjudication engine with formulary
engine = AdjudicationEngine(formulary=formulary)

# Adjudicate the claim
response = engine.adjudicate(claim, member)

print("\n=== Adjudication Result ===")
print(f"Status: {response.response_status}")

if response.response_status in ["A", "P"]:
    print(f"Authorization: {response.authorization_number}")
    print(f"Plan Pays: ${response.total_amount_paid}")
    print(f"Patient Pays: ${response.patient_pay_amount}")
    print(f"  Copay: ${response.copay_amount}")
    print(f"  Coinsurance: ${response.coinsurance_amount}")
    print(f"  Deductible: ${response.deductible_amount}")
else:
    print("Claim Rejected!")
    for reject in response.reject_codes:
        print(f"  Reject: {reject.code} - {reject.description}")
```

**Output:**
```
=== Adjudication Result ===
Status: P
Authorization: AUTH-7f8a9b12-001
Plan Pays: $7.00
Patient Pays: $10.00
  Copay: $10.00
  Coinsurance: $0.00
  Deductible: $0.00
```

## Complete Example

Here's the full script:

```python
"""First pharmacy claim tutorial."""
from datetime import date
from decimal import Decimal

from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator


def main():
    # Step 1: Generate member
    generator = RxMemberGenerator(seed=42)
    member = generator.generate(
        bin="610014", pcn="RXTEST", group_number="GRP001"
    )
    print(f"Member: {member.member_id}")

    # Step 2: Check formulary
    formulary = FormularyGenerator().generate_standard_commercial()
    status = formulary.check_coverage("00071015523")
    print(f"Coverage: Tier {status.tier}, Copay ${status.copay}")

    # Step 3: Create claim
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

    # Step 4: Adjudicate
    engine = AdjudicationEngine(formulary=formulary)
    response = engine.adjudicate(claim, member)

    print(f"Status: {response.response_status}")
    print(f"Plan Pays: ${response.total_amount_paid}")
    print(f"Patient Pays: ${response.patient_pay_amount}")


if __name__ == "__main__":
    main()
```

## What's Next?

Now that you've processed your first claim, try these scenarios:

1. **PA-Required Drug**: Try `ndc="00169413512"` (Ozempic) - expect reject code 75
2. **Early Refill**: Submit same claim again immediately - expect reject code 79
3. **Drug Interaction**: Add Warfarin with existing NSAID - see DUR alerts

Continue learning:
- **[Pharmacy Claims](../user-guide/pharmacy-claims.md)** - More claim scenarios
- **[Formulary Management](../user-guide/formulary.md)** - Configure coverage
- **[DUR Screening](../user-guide/dur-screening.md)** - Drug interaction checks
- **[Prior Authorization](../user-guide/prior-auth.md)** - PA workflows