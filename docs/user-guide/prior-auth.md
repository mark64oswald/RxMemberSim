# Prior Authorization

Generate and process prior authorization requests with RxMemberSim.

## Overview

Prior Authorization (PA) requires pre-approval before coverage of certain medications. RxMemberSim simulates the complete PA workflow.

## PA Workflow

```
1. Pharmacy submits claim
   ↓
2. Claim rejected: Code 75 (PA Required)
   ↓
3. Prescriber submits PA request
   ↓
4. Clinical review against criteria
   ↓
5. Decision: Approve / Deny / Pend
   ↓
6. If approved: PA number issued
   ↓
7. Claim resubmitted with PA
   ↓
8. Claim processed
```

## PAWorkflow

### Create PA Request

```python
from decimal import Decimal
from rxmembersim.authorization.prior_auth import PAWorkflow

pa_workflow = PAWorkflow()

request = pa_workflow.create_request(
    member_id="MEM001",
    cardholder_id="CH001",
    ndc="00169413512",        # Ozempic
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    diagnosis_codes=["E11.9"],  # Type 2 diabetes
)

print(f"PA Request ID: {request.pa_request_id}")
print(f"Status: {request.status}")
```

### Request Fields

| Field | Required | Description |
|-------|----------|-------------|
| `member_id` | Yes | Member identifier |
| `cardholder_id` | Yes | Cardholder ID |
| `ndc` | Yes | Drug NDC |
| `drug_name` | Yes | Drug name and strength |
| `quantity` | Yes | Requested quantity |
| `days_supply` | Yes | Days supply |
| `prescriber_npi` | Yes | Prescriber NPI |
| `prescriber_name` | Yes | Prescriber name |
| `diagnosis_codes` | No | ICD-10 codes |
| `clinical_notes` | No | Supporting information |
| `urgency` | No | standard/urgent/emergency |

## PA Status

| Status | Description |
|--------|-------------|
| `PENDING` | Request submitted, under review |
| `APPROVED` | Authorization granted |
| `DENIED` | Request denied |
| `PENDED_INFO` | Additional info needed |
| `CANCELLED` | Request withdrawn |
| `EXPIRED` | Authorization expired |
| `APPEALED` | Under appeal review |

## Auto-Approval

### Check for Auto-Approval

```python
# Emergency requests may auto-approve
request = pa_workflow.create_request(
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

response = pa_workflow.check_auto_approval(request)
if response and response.auto_approved:
    print(f"Auto-approved: {response.pa_number}")
```

### Auto-Approval Criteria

| Scenario | Result |
|----------|--------|
| Emergency urgency | 72-hour supply approved |
| Continuation of therapy | May auto-approve |
| Hospital discharge | May auto-approve |
| Standard request | Manual review required |

## Urgency Levels

| Level | Response Time | Use Case |
|-------|---------------|----------|
| Standard | 72 hours | Routine requests |
| Urgent | 24 hours | Clinical urgency |
| Emergency | 4 hours | Life-threatening |

```python
# Standard request
request = pa_workflow.create_request(
    # ... fields ...
    urgency="standard",
)

# Urgent request
request = pa_workflow.create_request(
    # ... fields ...
    urgency="urgent",
)

# Emergency request
request = pa_workflow.create_request(
    # ... fields ...
    urgency="emergency",
)
```

## PA Decisions

### Approval

```python
# Simulated approval response
approval = {
    "decision": "APPROVED",
    "pa_number": "PA-2024-001234",
    "effective_date": "2024-01-15",
    "expiration_date": "2024-07-15",
    "approved_quantity": 1,
    "approved_days_supply": 28,
    "approved_refills": 5,
}
```

### Denial

```python
# Simulated denial response
denial = {
    "decision": "DENIED",
    "denial_reason": "Step therapy not completed",
    "denial_code": "ST01",
    "alternative_suggested": "Metformin 1000mg",
    "appeal_deadline": "2024-02-15",
}
```

### Pend (Additional Info Needed)

```python
# Simulated pend response
pend = {
    "decision": "PENDED_INFO",
    "pend_reason": "Missing lab results",
    "information_needed": [
        "A1C within last 90 days",
        "Current weight/BMI",
    ],
    "response_deadline": "2024-01-25",
}
```

## Clinical Criteria Examples

### GLP-1 Agonist (Ozempic)

```yaml
criteria:
  diagnosis:
    - Type 2 Diabetes (E11.*)

  requirements:
    - A1C >= 7.0% within 90 days
    - Failed or contraindicated: metformin
    - BMI documented

  exclusions:
    - Type 1 Diabetes
    - History of pancreatitis
    - MEN2 syndrome

  approval:
    initial: 6 months
    renewal: 12 months
    quantity: 1 pen per 28 days
```

### Specialty Biologic (Humira)

```yaml
criteria:
  diagnosis:
    - Rheumatoid Arthritis (M05.*, M06.*)
    - Psoriatic Arthritis (L40.5*)
    - Crohn's Disease (K50.*)

  requirements:
    - Confirmed diagnosis by specialist
    - Failed conventional therapy
    - TB screening negative

  approval:
    initial: 6 months
    renewal: 12 months
```

## Common PA-Required Drugs

| Category | Examples | Typical Criteria |
|----------|----------|------------------|
| GLP-1 Agonists | Ozempic, Wegovy | A1c > 7%, failed metformin |
| Biologics | Humira, Enbrel | Failed conventional therapy |
| Specialty | Harvoni, Sovaldi | Confirmed diagnosis |
| Growth Hormone | Genotropin | Documented deficiency |
| MS Drugs | Tecfidera, Ocrevus | Confirmed MS diagnosis |

## Appeals Process

### Level 1: Internal Appeal

```python
# Submit within 30 days of denial
appeal = {
    "original_pa_id": "PA-2024-001234",
    "appeal_type": "internal",
    "appeal_reason": "Clinical documentation attached",
    "supporting_docs": ["lab_results.pdf", "chart_notes.pdf"],
}
```

### Level 2: External Review

```python
# If Level 1 denied, submit within 60 days
external_appeal = {
    "original_pa_id": "PA-2024-001234",
    "appeal_type": "external",
    "iro_requested": True,  # Independent Review Organization
}
```

## Testing Scenarios

### PA Required Drug

```python
from rxmembersim.claims.claim import PharmacyClaim
from rxmembersim.claims.adjudication import AdjudicationEngine

# Submit claim without PA
claim = PharmacyClaim(
    ndc="00169413512",  # Ozempic
    # ... other fields
)

response = engine.adjudicate(claim, member)

# Expect reject code 75
assert response.response_status == "R"
assert any(r.code == "75" for r in response.reject_codes)
```

### With PA Number

```python
# Resubmit with PA number
claim = PharmacyClaim(
    ndc="00169413512",
    prior_auth_number="PA-2024-001234",
    # ... other fields
)

response = engine.adjudicate(claim, member)

# Should process
assert response.response_status in ["A", "P"]
```

## Next Steps

- **[NCPDP Formats](../reference/ncpdp-formats.md)** - PA transaction formats
- **[Pharmacy Claims](pharmacy-claims.md)** - Claims processing
- **[Specialty Pharmacy](../reference/api.md)** - Hub services