# Formulary Testing Scenarios

Testing drug coverage, tier assignments, and utilization management.

---

## Setting Up Formulary Testing

**User:** I need to test our formulary system. How do I set up test data?

**Assistant:** Let me set up a comprehensive formulary testing environment:

```python
from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.formulary.formulary import FormularyGenerator
from rxmembersim.claims.adjudication import AdjudicationEngine

# Generate test member
generator = RxMemberGenerator(seed=42)
member = generator.generate(bin="610014", pcn="TEST", group_number="GRP001")

# Generate standard commercial formulary
formulary = FormularyGenerator().generate_standard_commercial()

# Create adjudication engine
engine = AdjudicationEngine(formulary=formulary)
```

Now I can test various coverage scenarios. What would you like to test first?

---

## Testing Tier Structure

**User:** Show me drugs from each tier

**Assistant:** Here are representative drugs from each formulary tier:

**Tier 1 - Preferred Generic ($10 copay)**

```python
status = formulary.check_coverage("00071015523")  # Atorvastatin 10mg
```

| Drug | NDC | Covered | Tier | Cost |
|------|-----|---------|------|------|
| Atorvastatin 10mg | 00071015523 | Yes | 1 | $10 copay |
| Metformin 500mg | 00093017101 | Yes | 1 | $10 copay |
| Lisinopril 10mg | 00378080101 | Yes | 1 | $10 copay |
| Omeprazole 20mg | 00093051801 | Yes | 1 | $10 copay |

**Tier 2 - Non-Preferred Generic ($25 copay)**

| Drug | NDC | Covered | Tier | Cost |
|------|-----|---------|------|------|
| Gabapentin 300mg | 00228266311 | Yes | 2 | $25 copay |
| Tramadol 50mg | 00093003701 | Yes | 2 | $25 copay |

**Tier 3 - Preferred Brand ($40 copay)**

| Drug | NDC | Covered | Tier | Cost |
|------|-----|---------|------|------|
| Eliquis 5mg | 00003089421 | Yes | 3 | $40 copay |
| Jardiance 10mg | 00597014810 | Yes | 3 | $40 copay |

**Tier 4 - Non-Preferred Brand ($80 copay)**

| Drug | NDC | Covered | Tier | Cost |
|------|-----|---------|------|------|
| Lipitor 10mg | 00069015430 | Yes | 4 | $80 copay |
| Nexium 40mg | 00186502131 | Yes | 4 | $80 copay |

**Tier 5 - Specialty (25% coinsurance)**

| Drug | NDC | Covered | Tier | Cost |
|------|-----|---------|------|------|
| Humira 40mg | 00074433902 | Yes | 5 | 25% coins |
| Ozempic 0.5mg | 00169413512 | Yes | 5 | 25% coins |
| Enbrel 50mg | 58406044504 | Yes | 5 | 25% coins |

---

## Testing Prior Authorization

**User:** Which drugs require prior authorization?

**Assistant:** Here are drugs with PA requirements:

```python
# Check PA-required drugs
pa_drugs = [
    ("00169413512", "Ozempic 0.5mg", "GLP-1 agonist"),
    ("00074433902", "Humira 40mg", "Specialty biologic"),
    ("61958060101", "Wegovy 0.25mg", "Weight loss"),
    ("00002141080", "Trulicity 1.5mg", "GLP-1 agonist"),
]

for ndc, name, category in pa_drugs:
    status = formulary.check_coverage(ndc)
    print(f"{name}: PA Required = {status.requires_pa}")
```

**PA-Required Drugs:**

| Drug | Category | PA Required | Step Therapy |
|------|----------|-------------|--------------|
| Ozempic | GLP-1 Agonist | Yes | Yes |
| Humira | Biologic | Yes | No |
| Wegovy | Weight Loss | Yes | Yes |
| Trulicity | GLP-1 Agonist | Yes | Yes |
| Enbrel | Biologic | Yes | No |

**Common PA Criteria:**

- **GLP-1 Agonists**: A1c >= 7%, failed metformin
- **Biologics**: Failed conventional therapy, specialist confirmation
- **Weight Loss**: BMI >= 30 or BMI >= 27 with comorbidity

---

## Testing Step Therapy

**User:** How does step therapy work? Give me an example.

**Assistant:** Step therapy requires trying lower-cost alternatives first. Here's a statin example:

**Statin Step Protocol:**

```
Step 1: Simvastatin 20mg (generic) - Tier 1
   ↓ If fails or contraindicated
Step 2: Atorvastatin 10mg (generic) - Tier 1
   ↓ If fails or contraindicated
Step 3: Rosuvastatin 10mg (brand Crestor equivalent) - Tier 3
   ↓ If fails or contraindicated
Step 4: Lipitor 10mg (brand) - Tier 4
```

**Testing Step Therapy:**

```python
# Direct request for brand Lipitor
status = formulary.check_coverage("00069015430")  # Lipitor

print(f"Step Therapy Required: {status.step_therapy}")
# Output: Step Therapy Required: True

# Submit claim without completing steps
claim = create_claim(ndc="00069015430", member=member)
response = engine.adjudicate(claim, member)

# Result: Rejected
# Reject Code: 76 (Plan Limitations Exceeded)
# Message: "Step therapy required - try generic atorvastatin first"
```

**Overcoming Step Therapy:**

1. Document failure on Step 1 drug
2. Submit PA with clinical documentation
3. Receive step therapy override approval

---

## Testing Quantity Limits

**User:** What quantity limits exist?

**Assistant:** Quantity limits restrict dispensing amounts. Here are common examples:

```python
# Check quantity limit
status = formulary.check_coverage("00093317431")  # Controlled substance
print(f"Quantity Limit: {status.quantity_limit}")
```

**Standard Quantity Limits:**

| Drug Type | Max Quantity | Max Days |
|-----------|--------------|----------|
| Maintenance drugs | 90 tablets | 90 days |
| Controlled substances | 30 tablets | 30 days |
| Acute medications | 14 tablets | 14 days |
| Specialty drugs | 30 units | 30 days |
| Migraine (triptans) | 9 tablets | 30 days |

**Testing Quantity Limit Rejection:**

```python
from decimal import Decimal

# Request 180 tablets of controlled substance (limit is 30)
claim = PharmacyClaim(
    ndc="00093317431",
    quantity_dispensed=Decimal("180"),
    days_supply=180,
    # ... other fields
)

response = engine.adjudicate(claim, member)

# Result: Rejected
# Reject Code: 76 (Plan Limitations Exceeded)
# Message: "Quantity exceeds plan maximum of 30 per 30 days"
```

---

## Testing Not Covered Drugs

**User:** How do I test drugs that aren't on the formulary?

**Assistant:** Here's how to test non-covered scenarios:

```python
# Unknown/not covered drug
status = formulary.check_coverage("99999999999")

print(f"Covered: {status.covered}")
print(f"Message: {status.message}")
```

**Output:**
```
Covered: False
Message: Drug not on formulary
```

**Claim Rejection:**

```python
claim = PharmacyClaim(
    ndc="99999999999",  # Not on formulary
    # ... other fields
)

response = engine.adjudicate(claim, member)

# Result: Rejected
# Reject Code: 70 (Product/Service Not Covered)
```

**Common Non-Covered Scenarios:**

| Scenario | Reject Code | Message |
|----------|-------------|---------|
| Not on formulary | 70 | Product not covered |
| Cosmetic drug | 70 | Excluded benefit |
| Experimental | 70 | Not FDA approved for indication |
| Discontinued | 77 | Drug discontinued |

---

## Brand vs Generic Testing

**User:** How do I test brand/generic scenarios with DAW codes?

**Assistant:** DAW (Dispense as Written) codes control brand vs generic dispensing:

**DAW Codes:**

| Code | Meaning | Who Requests |
|------|---------|--------------|
| 0 | No selection | Default |
| 1 | Brand required | Prescriber |
| 2 | Brand requested | Patient |
| 3 | Pharmacist selected | Pharmacist |
| 4 | Generic not in stock | Pharmacist |

**Testing DAW Scenarios:**

```python
# DAW 0 - Generic dispensed (default)
claim_generic = PharmacyClaim(
    ndc="00071015523",  # Atorvastatin (generic)
    daw_code="0",
    # ...
)
response = engine.adjudicate(claim_generic, member)
# Copay: $10 (Tier 1)

# DAW 1 - Brand required by prescriber
claim_brand = PharmacyClaim(
    ndc="00069015430",  # Lipitor (brand)
    daw_code="1",
    # ...
)
response = engine.adjudicate(claim_brand, member)
# Copay: $80 (Tier 4) + brand penalty may apply

# DAW 2 - Patient requests brand
claim_patient_brand = PharmacyClaim(
    ndc="00069015430",
    daw_code="2",
    # ...
)
response = engine.adjudicate(claim_patient_brand, member)
# Copay: $80 + cost difference between brand and generic
```

**Brand Penalty:**
When patient requests brand (DAW 2), they pay:
- Brand copay ($80) PLUS
- Difference between brand and generic cost

---

## Batch Formulary Testing

**User:** How do I test multiple drugs at once?

**Assistant:** Here's how to batch test formulary coverage:

```python
# Define test drugs
test_drugs = [
    ("00071015523", "Atorvastatin 10mg"),
    ("00093017101", "Metformin 500mg"),
    ("00169413512", "Ozempic 0.5mg"),
    ("00074433902", "Humira 40mg"),
    ("99999999999", "Unknown Drug"),
]

# Test each drug
results = []
for ndc, name in test_drugs:
    status = formulary.check_coverage(ndc)
    results.append({
        "NDC": ndc,
        "Drug": name,
        "Covered": status.covered,
        "Tier": status.tier if status.covered else "N/A",
        "PA": status.requires_pa,
        "ST": status.step_therapy,
    })

# Display results
for r in results:
    print(f"{r['Drug']}: Tier {r['Tier']}, PA={r['PA']}, ST={r['ST']}")
```

**Output:**
```
Atorvastatin 10mg: Tier 1, PA=False, ST=False
Metformin 500mg: Tier 1, PA=False, ST=False
Ozempic 0.5mg: Tier 5, PA=True, ST=True
Humira 40mg: Tier 5, PA=True, ST=False
Unknown Drug: Tier N/A, PA=False, ST=False
```

---

## Next Steps

Continue testing with:
- **[DUR Scenarios](03-dur-scenarios.md)** - Drug interaction testing
- **[Prior Auth Workflow](04-prior-auth-workflow.md)** - PA request processing
- **[Specialty Pharmacy](05-specialty-pharmacy.md)** - Specialty drug handling