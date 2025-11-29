# Prior Authorization (PA)

## Overview

Prior Authorization is a utilization management process requiring pre-approval before a prescription drug is covered by a health plan.

## PA Triggers

### Common Reasons

| Trigger | Description |
|---------|-------------|
| High Cost | Specialty/expensive medications |
| Safety | Drugs with serious side effects |
| Off-Label | Non-FDA approved use |
| Step Therapy | Alternative not tried first |
| Quantity | Exceeds plan limits |
| Age | Outside approved age range |
| Diagnosis | Specific conditions required |

### Drug Categories Requiring PA

- Specialty medications (biologics, oncology)
- GLP-1 agonists (Ozempic, Wegovy)
- Growth hormones
- Hepatitis C treatments
- MS medications
- Controlled substances (some plans)

## PA Process Flow

```
1. Claim Submitted
   ↓
2. PA Required (Reject 75)
   ↓
3. Prescriber Submits PA Request
   ↓
4. Clinical Review
   ↓
5. Decision (Approve/Deny/Pend)
   ↓
6. If Approved → PA Number Issued
   ↓
7. Claim Resubmitted with PA
   ↓
8. Claim Processed
```

## PA Request Requirements

### Required Information

```yaml
patient:
  member_id: required
  cardholder_id: required
  date_of_birth: required
  
drug:
  ndc: required
  drug_name: required
  strength: required
  quantity: required
  days_supply: required
  
prescriber:
  npi: required
  name: required
  phone: required
  fax: required
  
clinical:
  diagnosis_codes: required
  clinical_notes: optional
  lab_results: optional
  prior_therapies: conditional
```

### Supporting Documentation

- Chart notes/medical records
- Lab results (A1C, lipid panel, etc.)
- Prior medication history
- Specialist consultation notes
- Step therapy failure documentation

## Clinical Criteria

### Example: GLP-1 Agonist (Ozempic)

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
    - Medullary thyroid cancer
    
  approval:
    initial: 6 months
    renewal: 12 months
    quantity: 1 pen per 28 days
```

### Example: Specialty Drug (Humira)

```yaml
criteria:
  diagnosis:
    - Rheumatoid Arthritis (M05.*, M06.*)
    - Psoriatic Arthritis (L40.5*)
    - Crohn's Disease (K50.*)
    
  requirements:
    - Confirmed diagnosis by specialist
    - Failed conventional therapy:
        - RA: methotrexate 3+ months
        - Crohn's: corticosteroids, immunomodulators
    - TB screening negative
    
  approval:
    initial: 6 months
    renewal: 12 months
```

## PA Decisions

### Approval

```yaml
decision: approved
pa_number: "PA-2024-001234"
effective_date: "2024-01-15"
expiration_date: "2024-07-15"
approved_quantity: 30
approved_days_supply: 30
approved_refills: 5
```

### Denial

```yaml
decision: denied
denial_reason: "Step therapy not completed"
denial_code: "ST01"
alternative_suggested: "Metformin 1000mg"
appeal_deadline: "2024-02-15"
appeal_instructions: "Submit to PBM appeals department..."
```

### Pend (Additional Info Needed)

```yaml
decision: pend
pend_reason: "Missing lab results"
information_needed:
  - "A1C within last 90 days"
  - "Current weight/BMI"
response_deadline: "2024-01-25"
```

## Urgency Levels

| Level | Response Time | Use Case |
|-------|---------------|----------|
| Standard | 72 hours | Non-urgent requests |
| Urgent | 24 hours | Clinical urgency |
| Emergency | 4 hours | Life-threatening |

### Emergency Override

```yaml
emergency_criteria:
  - Immediate risk to patient health
  - Hospital discharge medication
  - Continuation of therapy (out of refills)
  
emergency_fill:
  quantity: 72-hour supply
  override_code: "EMERGENCY"
  follow_up: "Full PA within 72 hours"
```

## Appeals Process

### Level 1: Internal Appeal

```
Timeline: 30 days from denial
Submit to: PBM appeals department
Review by: Different clinical reviewer
Decision: 30 days (standard), 72 hours (expedited)
```

### Level 2: External Review

```
Timeline: 60 days from Level 1 denial
Submit to: Independent Review Organization (IRO)
Decision: 45 days (standard), 72 hours (expedited)
Binding: Yes, if overturned
```

## PA Status Codes

| Status | Description |
|--------|-------------|
| PENDING | Request submitted, under review |
| APPROVED | Authorization granted |
| DENIED | Request denied |
| CANCELLED | Request withdrawn |
| EXPIRED | Authorization period ended |
| APPEALED | Under appeal review |
