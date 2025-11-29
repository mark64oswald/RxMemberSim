# Getting Started with RxMemberSim

A first-time user conversation exploring pharmacy benefit simulation capabilities.

---

## Exploring Capabilities

**User:** What can RxMemberSim do?

**Assistant:** RxMemberSim generates synthetic pharmacy benefit data for PBM system testing. Here's what it can do:

**Generate Pharmacy Members**
- Members with BIN/PCN/Group identifiers
- Accumulators (deductible, out-of-pocket)
- Demographics and coverage dates

**Process Pharmacy Claims**
- NCPDP B1/B2 transactions
- Full claim adjudication
- Reject code handling

**Formulary Management**
- Drug coverage lookups
- Tier assignments (1-5)
- PA and step therapy flags

**DUR Screening**
- Drug-drug interactions
- Therapeutic duplication
- Early refill prevention
- Dose checking

**Prior Authorization**
- PA request creation
- Auto-approval rules
- Approval/denial simulation

Would you like to start with generating a pharmacy member?

---

## Generating Your First Member

**User:** Yes, generate a pharmacy member for me

**Assistant:** I'll generate a pharmacy member with standard commercial coverage:

```python
from rxmembersim.core.member import RxMemberGenerator

generator = RxMemberGenerator(seed=42)
member = generator.generate(
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001"
)
```

**Generated Member:**

| Field | Value |
|-------|-------|
| Member ID | MEM-7f8a9b12 |
| Cardholder ID | CH-7f8a9b12 |
| Name | John Smith |
| DOB | 1970-03-15 |
| BIN | 610014 |
| PCN | RXTEST |
| Group | GRP001 |
| Person Code | 01 (Subscriber) |

**Accumulators:**

| Accumulator | Met | Remaining |
|-------------|-----|-----------|
| Deductible | $0.00 | $500.00 |
| Out-of-Pocket | $0.00 | $3,000.00 |

The member has a $500 pharmacy deductible and $3,000 out-of-pocket maximum.

---

## Checking Formulary Coverage

**User:** Is metformin covered? What tier?

**Assistant:** Let me check formulary coverage for metformin:

```python
from rxmembersim.formulary.formulary import FormularyGenerator

formulary = FormularyGenerator().generate_standard_commercial()
status = formulary.check_coverage("00093017101")  # Metformin 500mg
```

**Coverage Status:**

| Field | Value |
|-------|-------|
| Covered | Yes |
| Tier | 1 (Preferred Generic) |
| Copay | $10.00 |
| Requires PA | No |
| Step Therapy | No |
| Quantity Limit | 180/30 days |

Metformin is on Tier 1 with a $10 copay. No prior authorization required.

**User:** What about Ozempic?

**Assistant:** Let me check Ozempic:

```python
status = formulary.check_coverage("00169413512")  # Ozempic 0.5mg
```

**Coverage Status:**

| Field | Value |
|-------|-------|
| Covered | Yes |
| Tier | 5 (Specialty) |
| Coinsurance | 25% |
| Requires PA | Yes |
| Step Therapy | Yes |

Ozempic is on Tier 5 (Specialty) with 25% coinsurance. It requires:
- **Prior Authorization** - Submit PA before claim processes
- **Step Therapy** - Must try metformin first

---

## Submitting a Pharmacy Claim

**User:** Submit a claim for 30 tablets of metformin

**Assistant:** I'll create and adjudicate a claim for metformin:

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
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
    ndc="00093017101",  # Metformin 500mg
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    daw_code="0",
    prescriber_npi="1234567890",
    ingredient_cost_submitted=Decimal("8.00"),
    dispensing_fee_submitted=Decimal("2.00"),
    patient_paid_submitted=Decimal("0.00"),
    usual_customary_charge=Decimal("15.00"),
    gross_amount_due=Decimal("10.00"),
)

engine = AdjudicationEngine(formulary=formulary)
response = engine.adjudicate(claim, member)
```

**Adjudication Result:**

| Field | Value |
|-------|-------|
| Status | P (Paid) |
| Authorization | AUTH-001234 |
| Plan Pays | $0.00 |
| Patient Pays | $10.00 |
| Copay | $10.00 |
| Deductible Applied | $0.00 |

The claim was approved. Since the drug cost ($10) is at the copay level, the member pays the $10 copay and the plan pays $0. The deductible wasn't applied because copay-based plans often don't apply deductibles to generic drugs.

---

## Understanding Accumulators

**User:** How do accumulators work?

**Assistant:** Accumulators track member spending toward deductibles and out-of-pocket maximums.

**Current Member Accumulators:**

| Accumulator | Met | Remaining | Limit |
|-------------|-----|-----------|-------|
| Deductible | $0.00 | $500.00 | $500.00 |
| Out-of-Pocket | $10.00 | $2,990.00 | $3,000.00 |

**How They Work:**

1. **Deductible** - Amount member pays before plan begins paying
   - Often waived for generic drugs (Tier 1)
   - Usually applies to brand and specialty drugs

2. **Out-of-Pocket Maximum** - Cap on member spending
   - After reaching $3,000, plan pays 100%
   - Includes copays, coinsurance, and deductible

After the metformin claim, the member has $10 toward their OOP max but deductible unchanged (generic exemption).

---

## DUR Screening Preview

**User:** What kind of drug interactions can RxMemberSim detect?

**Assistant:** RxMemberSim performs comprehensive DUR (Drug Utilization Review) screening:

**Interaction Types:**

| Code | Type | Example |
|------|------|---------|
| DD | Drug-Drug Interaction | Warfarin + NSAIDs (bleeding) |
| TD | Therapeutic Duplication | Two statins together |
| ER | Early Refill | Refill before supply depleted |
| HD | High Dose | Exceeds max daily dose |
| DA | Drug-Age | NSAIDs in elderly |
| DG | Drug-Gender | Finasteride in women |

**Example: Warfarin + Ibuprofen**

```python
from rxmembersim.dur.validator import DURValidator

validator = DURValidator()
result = validator.validate_simple(
    ndc="00056017270",        # Warfarin
    gpi="83300010000330",
    drug_name="Warfarin 5mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[
        {"ndc": "00904515260", "gpi": "66100010000310", "name": "Ibuprofen"}
    ],
    patient_age=65,
    patient_gender="F",
)
```

**Result:**
- DUR Passed: No
- Alert: Drug-Drug Interaction
- Message: "Warfarin + NSAID increases bleeding risk"
- Severity: Level 2 (Serious)

Want me to run a specific DUR scenario?

---

## Next Steps

**User:** What should I explore next?

**Assistant:** Here are some suggested next steps:

**1. Formulary Testing**
Test different drug tiers and coverage scenarios:
- Tier 1-5 drugs
- PA-required medications
- Step therapy protocols
- Quantity limits

**2. DUR Scenarios**
Explore drug interaction detection:
- Drug-drug interactions
- Therapeutic duplication
- Early refill rejection
- Dose checking

**3. Prior Authorization**
Test PA workflows:
- Submit PA requests
- Auto-approval rules
- Approval/denial handling

**4. Batch Processing**
Generate larger datasets:
- Multiple members
- Claim batches
- Population testing

**Resources:**
- **[Formulary Testing](02-formulary-testing.md)** - Coverage scenarios
- **[DUR Scenarios](03-dur-scenarios.md)** - Interaction testing
- **[Prior Auth Workflow](04-prior-auth-workflow.md)** - PA processing
- **[API Reference](../../docs/reference/api.md)** - Complete API

Would you like to explore any of these areas?