# DUR Screening

Drug Utilization Review (DUR) ensures patient safety through real-time clinical screening.

## Overview

DUR checks are performed at point of sale to identify potential drug therapy problems:

- Drug-drug interactions
- Therapeutic duplication
- Early refill attempts
- Dose checking
- Age/gender appropriateness

## DURValidator

### Basic Usage

```python
from datetime import date
from rxmembersim.dur.validator import DURValidator

validator = DURValidator()

result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
)

print(f"DUR Passed: {result.passed}")
print(f"Total Alerts: {result.total_alerts}")
```

### DURResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `passed` | bool | No blocking alerts |
| `total_alerts` | int | Number of alerts |
| `alerts` | list | Alert details |
| `override_allowed` | bool | Can be overridden |

## Alert Types

### Drug-Drug Interaction (DD)

Identifies interactions between medications:

```python
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

# Alert: Warfarin + NSAID = increased bleeding risk
for alert in result.alerts:
    if alert.alert_type.value == "DD":
        print(f"Drug-Drug Interaction: {alert.message}")
```

**Common Interactions:**

| Drug A | Drug B | Risk |
|--------|--------|------|
| Warfarin | NSAIDs | Bleeding |
| Warfarin | Aspirin | Bleeding |
| Simvastatin | Amiodarone | Myopathy |
| Metformin | Contrast dye | Lactic acidosis |
| Lisinopril | Potassium | Hyperkalemia |
| Fluoxetine | Tramadol | Seizure |

### Therapeutic Duplication (TD)

Multiple drugs in the same therapeutic class:

```python
result = validator.validate_simple(
    ndc="00078057715",
    gpi="39400020000310",  # Rosuvastatin
    drug_name="Rosuvastatin 10mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[
        {
            "ndc": "00071015523",
            "gpi": "39400010000310",  # Atorvastatin
            "name": "Atorvastatin 10mg",
        }
    ],
    patient_age=55,
    patient_gender="M",
)

# Alert: Two statins - therapeutic duplication
```

**Classes Checked:**
- Statins (only one allowed)
- ACE inhibitors
- ARBs
- PPIs
- SSRIs

### Early Refill (ER)

Refill requested before supply should be depleted:

```python
# Standard rule: 75% of days supply must elapse
# 30-day supply → earliest refill day 23

result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id="MEM001",
    service_date=date(2024, 1, 15),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
    last_fill_date=date(2024, 1, 1),
    last_days_supply=30,
)

# If day 15 < day 23: Early Refill alert
```

**Early Refill Thresholds:**

| Days Supply | Earliest Refill |
|-------------|-----------------|
| 30 days | Day 23 (75%) |
| 60 days | Day 48 (80%) |
| 90 days | Day 75 (83%) |

### High Dose (HD)

Exceeds maximum recommended daily dose:

```python
result = validator.validate_simple(
    ndc="00071015580",
    gpi="39400010000380",  # Atorvastatin 80mg
    drug_name="Atorvastatin 80mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
    quantity=60,  # 2 tablets/day = 160mg/day
    days_supply=30,
)

# Alert: Exceeds max daily dose of 80mg
```

### Drug-Age (DA)

Age-inappropriate medications:

```python
result = validator.validate_simple(
    ndc="00378808001",
    gpi="66100010200310",  # Ibuprofen
    drug_name="Ibuprofen 800mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=82,  # Elderly patient
    patient_gender="F",
)

# Alert: NSAIDs in elderly - increased GI/renal risk
```

### Drug-Gender (DG)

Gender-specific contraindications:

```python
result = validator.validate_simple(
    ndc="00006011731",
    gpi="24100070100310",  # Finasteride
    drug_name="Finasteride 5mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=35,
    patient_gender="F",  # Female
)

# Alert: Finasteride contraindicated in women
```

## Severity Levels

| Level | Code | Action |
|-------|------|--------|
| 1 | Severe | Hard reject - cannot override |
| 2 | Serious | Soft reject - requires intervention |
| 3 | Moderate | Warning - pharmacist review |
| 4 | Minor | Information only |

```python
for alert in result.alerts:
    print(f"Type: {alert.alert_type.value}")
    print(f"Severity: Level {alert.clinical_significance.value}")
    print(f"Message: {alert.message}")

    if alert.clinical_significance.value == 1:
        print("HARD REJECT - Cannot override")
    elif alert.clinical_significance.value == 2:
        print("Requires pharmacist intervention")
```

## Override Processing

### Professional Service Codes

| Code | Description |
|------|-------------|
| M0 | Prescriber consulted |
| P0 | Patient consulted |
| R0 | Pharmacist consulted other source |
| PH | Patient history obtained |
| DE | Deferred - will follow up |

### Result of Service Codes

| Code | Description |
|------|-------------|
| 1A | Filled as is (false positive) |
| 1B | Filled with different dose |
| 1C | Filled with different directions |
| 1D | Filled with different drug |
| 1E | Filled with different quantity |
| 2A | Not filled - Rx not ready |
| 2B | Not filled - patient request |

## Testing Scenarios

### Clean Prescription

```python
result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
)

assert result.passed == True
assert result.total_alerts == 0
```

### Drug Interaction

```python
result = validator.validate_simple(
    ndc="00056017270",
    gpi="83300010000330",  # Warfarin
    drug_name="Warfarin 5mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[
        {"ndc": "00904515260", "gpi": "66100010000310", "name": "Ibuprofen"}
    ],
    patient_age=65,
    patient_gender="F",
)

assert result.passed == False
assert any(a.alert_type.value == "DD" for a in result.alerts)
```

## Next Steps

- **[Prior Authorization](prior-auth.md)** - PA workflows
- **[Pharmacy Claims](pharmacy-claims.md)** - Process claims
- **[NCPDP Formats](../reference/ncpdp-formats.md)** - DUR response codes