# DUR Testing Scenarios

Testing drug utilization review, interactions, and clinical alerts.

---

## Setting Up DUR Testing

**User:** I need to test our DUR system. How do I get started?

**Assistant:** Let me set up a DUR testing environment:

```python
from datetime import date
from rxmembersim.dur.validator import DURValidator
from rxmembersim.core.member import RxMemberGenerator

# Create DUR validator
validator = DURValidator()

# Generate test member
generator = RxMemberGenerator(seed=42)
member = generator.generate(bin="610014", pcn="TEST", group_number="GRP001")
```

Now I can test various DUR scenarios. What type of interaction would you like to test?

---

## Drug-Drug Interaction (DD)

**User:** Test a drug-drug interaction scenario

**Assistant:** I'll test the classic Warfarin + NSAID interaction:

```python
result = validator.validate_simple(
    ndc="00056017270",
    gpi="83300010000330",  # Warfarin
    drug_name="Warfarin 5mg",
    member_id=member.member_id,
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
```

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Total Alerts | 1 |
| Alert Type | DD (Drug-Drug Interaction) |
| Severity | Level 2 (Serious) |
| Message | Warfarin + NSAID: Increased bleeding risk |

**Alert Details:**
```
Type: DD
Conflicting Drug: Ibuprofen 200mg
Clinical Significance: 2 (Serious)
Message: Concurrent use of warfarin and NSAIDs increases
         risk of GI bleeding. Consider alternative for pain.
Override Allowed: Yes (with intervention code)
```

**User:** What other drug interactions can you test?

**Assistant:** Here are common drug-drug interactions to test:

| Drug A | Drug B | Risk | Severity |
|--------|--------|------|----------|
| Warfarin | Aspirin | Bleeding | 2 |
| Warfarin | NSAIDs | Bleeding | 2 |
| Simvastatin | Amiodarone | Myopathy | 2 |
| Metformin | Contrast dye | Lactic acidosis | 1 |
| Lisinopril | Potassium | Hyperkalemia | 2 |
| Fluoxetine | Tramadol | Seizure risk | 2 |
| MAOIs | SSRIs | Serotonin syndrome | 1 |

**Severity Level 1 (Contraindicated):**

```python
# MAOI + SSRI interaction
result = validator.validate_simple(
    ndc="00049502050",  # Fluoxetine
    gpi="58160010100310",
    drug_name="Fluoxetine 20mg",
    member_id=member.member_id,
    service_date=date.today(),
    current_medications=[
        {"ndc": "00781186001", "gpi": "58200020000310", "name": "Phenelzine 15mg"}
    ],
    patient_age=45,
    patient_gender="M",
)

# Result: Hard reject - cannot override
# Severity: Level 1 (Contraindicated)
# Message: SSRI + MAOI: Risk of serotonin syndrome
```

---

## Therapeutic Duplication (TD)

**User:** Test therapeutic duplication detection

**Assistant:** I'll test duplicate statin therapy:

```python
result = validator.validate_simple(
    ndc="00078057715",
    gpi="39400020000310",  # Rosuvastatin
    drug_name="Rosuvastatin 10mg",
    member_id=member.member_id,
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
```

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Alert Type | TD (Therapeutic Duplication) |
| Severity | Level 2 (Serious) |
| Message | Two HMG-CoA reductase inhibitors (statins) |

**Therapeutic Classes Checked:**

| Class | Rule | Example |
|-------|------|---------|
| Statins | Only 1 allowed | Atorvastatin + Rosuvastatin |
| ACE Inhibitors | Only 1 allowed | Lisinopril + Benazepril |
| ARBs | Only 1 allowed | Losartan + Valsartan |
| PPIs | Only 1 allowed | Omeprazole + Pantoprazole |
| SSRIs | Only 1 allowed | Fluoxetine + Sertraline |

---

## Early Refill (ER)

**User:** How does early refill detection work?

**Assistant:** Early refill checks prevent filling before the previous supply should be depleted:

**Standard Rule:** 75% of days supply must elapse

```python
result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id=member.member_id,
    service_date=date(2024, 1, 15),  # Day 15
    current_medications=[],
    patient_age=55,
    patient_gender="M",
    last_fill_date=date(2024, 1, 1),  # Filled Jan 1
    last_days_supply=30,              # 30 days supply
)
```

**Calculation:**
- Last fill: Jan 1, 30 days supply
- 75% threshold: Day 23 (0.75 × 30 = 22.5)
- Current date: Jan 15 (Day 15)
- Result: Too early (Day 15 < Day 23)

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Alert Type | ER (Early Refill) |
| Message | Refill too soon. Earliest fill: Jan 23 |

**Early Refill Thresholds:**

| Days Supply | % Threshold | Earliest Day |
|-------------|-------------|--------------|
| 30 days | 75% | Day 23 |
| 60 days | 80% | Day 48 |
| 90 days | 83% | Day 75 |

**Override Reasons:**

```python
# Valid early refill override
override_reasons = [
    "VACATION",    # Travel requiring early fill
    "LOST_STOLEN", # Lost or stolen (may require police report)
    "THERAPY_CHANGE", # Dose or drug changed
    "DISASTER",    # Emergency/disaster situation
]
```

---

## High Dose Alert (HD)

**User:** Test high dose detection

**Assistant:** I'll test a high dose scenario:

```python
result = validator.validate_simple(
    ndc="00093017101",
    gpi="27250010000310",  # Metformin
    drug_name="Metformin 1000mg",
    member_id=member.member_id,
    service_date=date.today(),
    current_medications=[],
    patient_age=55,
    patient_gender="M",
    quantity=90,      # 90 tablets
    days_supply=30,   # 30 days
    # 3 tablets/day × 1000mg = 3000mg/day
)
```

**Dose Calculation:**
- Quantity: 90 tablets
- Days supply: 30
- Tablets/day: 3
- Strength: 1000mg
- Daily dose: 3000mg
- Max daily dose: 2550mg

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Alert Type | HD (High Dose) |
| Severity | Level 3 (Moderate) |
| Message | Daily dose 3000mg exceeds max of 2550mg |

**Common Max Daily Doses:**

| Drug | Max Daily Dose | Alert Threshold |
|------|----------------|-----------------|
| Metformin | 2550mg | 2000mg |
| Lisinopril | 80mg | 60mg |
| Atorvastatin | 80mg | 80mg |
| Omeprazole | 40mg | 40mg |
| Gabapentin | 3600mg | 2400mg |

---

## Drug-Age Precaution (DA)

**User:** Test age-related drug precautions

**Assistant:** I'll test NSAID use in elderly patients:

```python
result = validator.validate_simple(
    ndc="00904515260",
    gpi="66100010000310",  # Ibuprofen
    drug_name="Ibuprofen 800mg",
    member_id=member.member_id,
    service_date=date.today(),
    current_medications=[],
    patient_age=82,  # Elderly patient
    patient_gender="F",
)
```

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Alert Type | DA (Drug-Age) |
| Severity | Level 3 (Moderate) |
| Message | NSAIDs in elderly: increased GI/renal risk |

**Age-Related Alerts:**

| Drug Category | Age Group | Risk |
|---------------|-----------|------|
| NSAIDs | Age > 65 | GI bleeding, renal |
| Benzodiazepines | Age > 65 | Falls, cognitive |
| Anticholinergics | Age > 65 | Confusion, falls |
| Fluoroquinolones | Age < 18 | Tendon damage |
| Tetracyclines | Age < 8 | Tooth discoloration |

---

## Drug-Gender Precaution (DG)

**User:** Test gender-specific contraindications

**Assistant:** I'll test finasteride (contraindicated in women):

```python
result = validator.validate_simple(
    ndc="00006011731",
    gpi="24100070100310",  # Finasteride
    drug_name="Finasteride 5mg",
    member_id=member.member_id,
    service_date=date.today(),
    current_medications=[],
    patient_age=35,
    patient_gender="F",  # Female patient
)
```

**DUR Result:**

| Field | Value |
|-------|-------|
| DUR Passed | No |
| Alert Type | DG (Drug-Gender) |
| Severity | Level 1 (Severe) |
| Message | Finasteride contraindicated in women |

**Gender-Specific Alerts:**

| Drug | Gender | Alert |
|------|--------|-------|
| Finasteride | Female | Contraindicated (teratogenic) |
| Dutasteride | Female | Contraindicated (teratogenic) |
| Testosterone | Female | Verify indication |
| Estrogen | Male | Verify indication |

---

## Clean Prescription (No Alerts)

**User:** Show me a clean prescription with no alerts

**Assistant:** Here's a straightforward prescription with no DUR issues:

```python
result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id=member.member_id,
    service_date=date.today(),
    current_medications=[],  # No other meds
    patient_age=55,         # Adult
    patient_gender="M",     # Male
    quantity=30,            # Standard quantity
    days_supply=30,         # Standard supply
)

print(f"DUR Passed: {result.passed}")
print(f"Total Alerts: {result.total_alerts}")
```

**Output:**
```
DUR Passed: True
Total Alerts: 0
```

This is a "clean" prescription:
- No current medications (no interactions)
- Appropriate age
- Appropriate gender
- Standard dose
- Not an early refill

---

## Batch DUR Testing

**User:** How can I test multiple DUR scenarios at once?

**Assistant:** Here's how to batch test DUR scenarios:

```python
test_scenarios = [
    {
        "name": "Clean prescription",
        "ndc": "00071015523",
        "current_meds": [],
        "age": 55,
        "gender": "M",
    },
    {
        "name": "Warfarin + NSAID",
        "ndc": "00056017270",  # Warfarin
        "current_meds": [{"ndc": "00904515260", "name": "Ibuprofen"}],
        "age": 65,
        "gender": "F",
    },
    {
        "name": "Duplicate statin",
        "ndc": "00078057715",  # Rosuvastatin
        "current_meds": [{"ndc": "00071015523", "name": "Atorvastatin"}],
        "age": 55,
        "gender": "M",
    },
    {
        "name": "NSAID in elderly",
        "ndc": "00904515260",  # Ibuprofen
        "current_meds": [],
        "age": 82,
        "gender": "F",
    },
]

results = []
for scenario in test_scenarios:
    result = validator.validate_simple(
        ndc=scenario["ndc"],
        current_medications=scenario["current_meds"],
        patient_age=scenario["age"],
        patient_gender=scenario["gender"],
        # ... other fields
    )
    results.append({
        "Scenario": scenario["name"],
        "Passed": result.passed,
        "Alerts": result.total_alerts,
    })

for r in results:
    status = "PASS" if r["Passed"] else "FAIL"
    print(f"{r['Scenario']}: {status} ({r['Alerts']} alerts)")
```

**Output:**
```
Clean prescription: PASS (0 alerts)
Warfarin + NSAID: FAIL (1 alerts)
Duplicate statin: FAIL (1 alerts)
NSAID in elderly: FAIL (1 alerts)
```

---

## Next Steps

Continue testing with:
- **[Prior Auth Workflow](04-prior-auth-workflow.md)** - PA processing
- **[Specialty Pharmacy](05-specialty-pharmacy.md)** - Specialty scenarios
- **[NCPDP Formats](../../docs/reference/ncpdp-formats.md)** - DUR response codes