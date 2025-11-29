# Pharmacy Benefits Testing with RxMemberSim

This guide demonstrates how to use RxMemberSim for comprehensive PBM (Pharmacy Benefit Manager) system integration testing.

## Overview

RxMemberSim generates realistic synthetic pharmacy data in industry-standard formats, making it ideal for:

- **Claims Processing** - NCPDP B1/B2 transaction workflows
- **Formulary Testing** - Drug coverage and tier assignment validation
- **DUR Screening** - Drug interaction and utilization review
- **Prior Authorization** - PA request/response workflows
- **Specialty Pharmacy** - Hub services and REMS programs

## Quick Start

### 1. Installation

```bash
cd /path/to/rxmembersim
pip install -e ".[dev]"
```

### 2. Generate Your First Pharmacy Member

```python
from rxmembersim.core.member import RxMemberGenerator

generator = RxMemberGenerator()
member = generator.generate(bin="610014", pcn="DEMO", group_number="GRP001")

print(f"Member: {member.member_id}")
print(f"BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")
print(f"Deductible Remaining: ${member.accumulators.deductible_remaining}")
```

### 3. Run the Interactive Demo

```bash
python demos/interactive_demo.py
```

## Testing Scenarios

### Scenario 1: NCPDP B1/B2 Claims Processing

Test pharmacy claim submission and adjudication workflows.

**What you'll test:**
- New claim submission (B1)
- Claim reversal (B2)
- Claim adjudication logic
- Copay/coinsurance calculation
- Reject code handling

**Code Example:**

```python
from datetime import date
from decimal import Decimal

from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator

# Generate member and formulary
member = RxMemberGenerator().generate(
    bin="610014", pcn="RXTEST", group_number="GRP001"
)
formulary = FormularyGenerator().generate_standard_commercial()

# Create B1 (billing) claim
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
    ndc="00071015523",  # Atorvastatin 10mg
    quantity_dispensed=Decimal("30"),
    days_supply=30,
    daw_code="0",  # No product selection indicated
    prescriber_npi="1234567890",
    ingredient_cost_submitted=Decimal("15.00"),
    dispensing_fee_submitted=Decimal("2.00"),
    patient_paid_submitted=Decimal("0.00"),
    usual_customary_charge=Decimal("25.00"),
    gross_amount_due=Decimal("17.00"),
)

# Adjudicate
engine = AdjudicationEngine(formulary=formulary)
response = engine.adjudicate(claim, member)

print(f"Status: {response.response_status}")  # A = Approved
print(f"Plan Pay: ${response.total_amount_paid}")
print(f"Patient Pay: ${response.patient_pay_amount}")
print(f"Copay: ${response.copay_amount}")
```

**Transaction Codes:**

| Code | Type | Description |
|------|------|-------------|
| B1 | Billing | New prescription claim |
| B2 | Reversal | Cancel previous claim |
| B3 | Rebill | Resubmit with changes |
| E1 | Eligibility | Check member eligibility |

---

### Scenario 2: Formulary Testing

Test drug coverage lookups and tier assignments.

**What you'll test:**
- Drug coverage status
- Tier placement
- Copay/coinsurance amounts
- Prior authorization requirements
- Step therapy protocols
- Quantity limits

**Code Example:**

```python
from rxmembersim.formulary.formulary import FormularyGenerator

# Generate standard commercial formulary
formulary = FormularyGenerator().generate_standard_commercial()

# Test different drug types
drugs = [
    ("00071015523", "Atorvastatin 10mg", "Generic statin"),
    ("00169413512", "Ozempic 0.5mg", "Brand GLP-1"),
    ("00074430014", "Humira 40mg", "Specialty biologic"),
    ("99999999999", "Unknown Drug", "Not on formulary"),
]

for ndc, name, description in drugs:
    status = formulary.check_coverage(ndc)
    print(f"\n{name} ({description}):")
    print(f"  NDC: {ndc}")
    print(f"  Covered: {status.covered}")

    if status.covered:
        print(f"  Tier: {status.tier} ({status.tier_name})")
        print(f"  Requires PA: {status.requires_pa}")
        print(f"  Step Therapy: {status.step_therapy}")
        if status.copay:
            print(f"  Copay: ${status.copay}")
        if status.coinsurance:
            print(f"  Coinsurance: {status.coinsurance}%")
        if status.quantity_limit:
            print(f"  Qty Limit: {status.quantity_limit}")
    else:
        print(f"  Message: {status.message}")
```

**Standard Tier Structure:**

| Tier | Name | Typical Cost | Examples |
|------|------|--------------|----------|
| 1 | Preferred Generic | $10-15 copay | Atorvastatin, Metformin |
| 2 | Non-Preferred Generic | $20-30 copay | Omeprazole, Gabapentin |
| 3 | Preferred Brand | $35-50 copay | Eliquis, Jardiance |
| 4 | Non-Preferred Brand | $75-100 copay | Lipitor, Nexium |
| 5 | Specialty | 20-30% coinsurance | Humira, Enbrel |

---

### Scenario 3: DUR (Drug Utilization Review)

Test drug interaction screening and clinical alerts.

**What you'll test:**
- Drug-drug interactions (DD)
- Therapeutic duplication (TD)
- Early refill prevention (ER)
- High dose alerts (HD)
- Drug-age precautions (DA)
- Drug-gender precautions (DG)

**Code Example:**

```python
from datetime import date
from rxmembersim.dur.validator import DURValidator

validator = DURValidator()

# Scenario A: Clean prescription - no alerts
result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",  # Atorvastatin
    drug_name="Atorvastatin 10mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
)

print("Clean Prescription:")
print(f"  DUR Passed: {result.passed}")
print(f"  Alerts: {result.total_alerts}")

# Scenario B: Drug-drug interaction (Warfarin + NSAID)
result = validator.validate_simple(
    ndc="00056017270",
    gpi="83300010000330",  # Warfarin
    drug_name="Warfarin 5mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[
        {
            "ndc": "00904515260",
            "gpi": "66100010000310",  # Ibuprofen
            "name": "Ibuprofen 200mg",
        }
    ],
    patient_age=65,
    patient_gender="F",
)

print("\nWarfarin + NSAID Interaction:")
print(f"  DUR Passed: {result.passed}")
print(f"  Alerts: {result.total_alerts}")
for alert in result.alerts:
    print(f"    [{alert.alert_type.value}] {alert.message}")
    print(f"    Severity: Level {alert.clinical_significance.value}")
```

**DUR Alert Types:**

| Code | Type | Description |
|------|------|-------------|
| DD | Drug-Drug | Interaction between medications |
| TD | Therapeutic Duplication | Multiple drugs in same class |
| ER | Early Refill | Refill requested too soon |
| HD | High Dose | Exceeds maximum daily dose |
| LD | Low Dose | Below therapeutic threshold |
| DA | Drug-Age | Age-inappropriate medication |
| DG | Drug-Gender | Gender-specific contraindication |

**Severity Levels:**

| Level | Description | Action |
|-------|-------------|--------|
| 1 | Severe | Hard reject - cannot override |
| 2 | Serious | Soft reject - requires intervention |
| 3 | Moderate | Warning - pharmacist review |
| 4 | Minor | Information only |

---

### Scenario 4: Prior Authorization (ePA)

Test prior authorization request and approval workflows.

**What you'll test:**
- PA request submission
- Auto-approval rules
- Clinical criteria evaluation
- Appeal workflows
- ePA transaction formats

**Code Example:**

```python
from decimal import Decimal
from rxmembersim.authorization.prior_auth import PAWorkflow

# Create PA workflow
pa_workflow = PAWorkflow()

# Submit standard PA request
request = pa_workflow.create_request(
    member_id="MEM001",
    cardholder_id="CH001",
    ndc="00169413512",  # Ozempic
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    diagnosis_codes=["E11.9"],  # Type 2 diabetes
)

print(f"PA Request ID: {request.pa_request_id}")
print(f"Status: {request.status}")
print(f"Drug: {request.drug_name}")

# Check for auto-approval (emergency situations)
request_urgent = pa_workflow.create_request(
    member_id="MEM001",
    cardholder_id="CH001",
    ndc="00169413512",
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    urgency="emergency",
)

response = pa_workflow.check_auto_approval(request_urgent)
print(f"\nEmergency Request:")
print(f"Auto-Approved: {response.auto_approved if response else False}")
```

**PA Status Values:**

| Status | Description |
|--------|-------------|
| PENDING | Request submitted, awaiting review |
| APPROVED | PA approved, claim can process |
| DENIED | PA denied, claim will reject |
| PENDED_INFO | Additional information needed |
| CANCELLED | Request cancelled |

**Common PA Required Drugs:**

| Drug Class | Examples | Typical Criteria |
|------------|----------|------------------|
| GLP-1 Agonists | Ozempic, Wegovy | A1c > 7%, BMI > 27 |
| Biologics | Humira, Enbrel | Failed conventional therapy |
| Specialty | Harvoni, Sovaldi | Confirmed diagnosis |
| Brand-only | Eliquis, Xarelto | No generic equivalent |

---

### Scenario 5: Specialty Pharmacy

Test specialty pharmacy hub services and REMS programs.

**What you'll test:**
- Hub enrollment
- REMS compliance
- Cold chain requirements
- Patient assistance programs
- Copay card processing

**Common Specialty Scenarios:**

| Scenario | Drug Example | Special Handling |
|----------|--------------|------------------|
| Biologic | Humira | Cold chain, hub enrollment |
| Oncology | Revlimid | REMS certification required |
| HIV | Biktarvy | Copay assistance program |
| Hepatitis C | Harvoni | Cure-based pricing |

---

## NCPDP Format Details

### Claim Segment Fields

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| BIN | 101-A1 | Bank ID Number | 610014 |
| PCN | 104-A4 | Processor Control Number | RXTEST |
| Group ID | 301-C1 | Group Number | GRP001 |
| Cardholder ID | 302-C2 | Member ID | MEM001 |
| Person Code | 303-C3 | Dependent Code | 01 |
| NDC | 407-D7 | National Drug Code | 00071015523 |
| Quantity | 442-E7 | Quantity Dispensed | 30 |
| Days Supply | 405-D5 | Days Supply | 30 |
| DAW | 408-D8 | Dispense as Written | 0 |

### Response Codes

**Status Codes:**

| Code | Status | Description |
|------|--------|-------------|
| A | Accepted | Claim approved and paid |
| R | Rejected | Claim denied |
| P | Paid | Paid with changes |
| D | Duplicate | Duplicate claim detected |

**Common Reject Codes:**

| Code | Description | Resolution |
|------|-------------|------------|
| 70 | Product/Service Not Covered | Check formulary |
| 75 | Prior Authorization Required | Submit PA |
| 76 | Plan Limitations Exceeded | Check quantity limits |
| 79 | Refill Too Soon | Wait or submit override |
| 88 | DUR Reject | Review DUR conflict |
| MR | Missing/Invalid Prescriber ID | Verify NPI |
| NN | Missing/Invalid Cardholder ID | Verify member ID |

### DAW (Dispense as Written) Codes

| Code | Description |
|------|-------------|
| 0 | No product selection indicated |
| 1 | Substitution not allowed by prescriber |
| 2 | Patient requested brand |
| 3 | Pharmacist selected product |
| 4 | Generic not in stock |
| 5 | Brand dispensed as generic |

---

## MCP Integration (Claude Code)

RxMemberSim provides an MCP server for AI agent integration.

### Setup

Add to `.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "rxmembersim": {
      "command": "python",
      "args": ["-m", "rxmembersim.mcp.server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `generate_rx_member` | Create pharmacy member with BIN/PCN/Group |
| `check_formulary` | Look up drug coverage and tier |
| `check_dur` | Execute DUR screening |
| `submit_prior_auth` | Submit PA request |
| `run_rx_scenario` | Execute test scenario |
| `list_scenarios` | List available scenarios |

### Usage Examples

**Generate test members:**
```
Generate a pharmacy member with diabetes medications
```

**Check drug coverage:**
```
Check if Humira is on the formulary and what tier
```

**Process a claim:**
```
Process a claim for 30 tablets of metformin
```

**Run a scenario:**
```
Run the step therapy rejection scenario
```

---

## Testing Workflows

### 1. Claims Adjudication Testing

**Goal:** Validate claim processing logic

**Steps:**
1. Generate pharmacy member with known accumulators
2. Submit claim for covered drug
3. Verify adjudication response
4. Check copay/coinsurance calculation
5. Verify accumulator updates

### 2. Formulary Validation

**Goal:** Test coverage lookups

**Steps:**
1. Generate standard formulary
2. Query drugs across all tiers
3. Verify tier assignments
4. Check PA/step therapy flags
5. Validate quantity limits

### 3. DUR Integration

**Goal:** Validate clinical screening

**Steps:**
1. Submit clean prescription
2. Submit with known interaction
3. Verify alert generation
4. Test override processing
5. Validate severity levels

### 4. PA Workflow

**Goal:** Test authorization processing

**Steps:**
1. Submit PA-required claim (expect 75 reject)
2. Create PA request
3. Process approval/denial
4. Resubmit claim with PA number
5. Verify claim processes

---

## Troubleshooting

### Common Issues

**Issue:** Import errors when running demos
```
ModuleNotFoundError: No module named 'rxmembersim'
```
**Solution:** Install in development mode: `pip install -e ".[dev]"`

---

**Issue:** Claim rejected with code 70
```
Status: R (Rejected)
Reject Code: 70 - Product/Service Not Covered
```
**Solution:** Verify NDC is on formulary or use a known covered drug

---

**Issue:** DUR check returns no alerts for known interaction
```
DUR Passed: True
Alerts: 0
```
**Solution:** Verify GPI codes are correct for the drugs being checked

---

**Issue:** PA request not auto-approving
```
Auto-Approved: False
```
**Solution:** Set `urgency="emergency"` for auto-approval testing

---

## Performance Benchmarks

Generation performance on MacBook Pro (M1):

| Operation | Count | Time | Rate |
|-----------|-------|------|------|
| Generate Members | 1,000 | 1.8s | 556/sec |
| Formulary Lookups | 10,000 | 0.5s | 20,000/sec |
| DUR Checks | 1,000 | 2.1s | 476/sec |
| Claim Adjudication | 1,000 | 3.2s | 312/sec |

---

## Next Steps

- **Run the demo:** `python demos/interactive_demo.py`
- **Explore examples:** See [examples/](../../examples/)
- **Read the API:** See [docs/api.md](../../docs/api.md) (coming soon)
- **Check skills:** See [skills/](../../skills/) for domain documentation

## Support

- **Issues:** [GitHub Issues](https://github.com/mark64oswald/rxmembersim/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mark64oswald/rxmembersim/discussions)

## License

Apache License 2.0 - See [LICENSE](../../LICENSE) for details.