# Specialty Pharmacy Scenarios

Testing hub services, REMS programs, and specialty drug workflows.

---

## Understanding Specialty Pharmacy

**User:** What makes a drug "specialty" and how does RxMemberSim handle it?

**Assistant:** Specialty drugs have unique characteristics that require special handling:

**Defining Characteristics:**

| Characteristic | Threshold |
|----------------|-----------|
| Cost | >$600/month or >$10,000/year |
| Handling | Cold chain, hazardous, limited stability |
| Administration | Injectable, infusible, complex oral |
| Distribution | Limited distribution network |
| Monitoring | Requires clinical oversight |

**Common Specialty Categories:**

| Category | Examples | Special Requirements |
|----------|----------|---------------------|
| Biologics | Humira, Enbrel, Remicade | Cold chain, PA |
| Oncology | Revlimid, Ibrance | REMS, PA |
| Autoimmune | Otezla, Xeljanz | PA, monitoring |
| Hepatitis C | Harvoni, Epclusa | PA, cure-based |
| HIV | Biktarvy, Descovy | PAP programs |
| MS | Tecfidera, Ocrevus | PA, monitoring |

---

## Specialty Drug Claim

**User:** Process a claim for Humira

**Assistant:** I'll process a specialty claim for Humira (adalimumab):

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator
from datetime import date
from decimal import Decimal

# Setup
formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)

# Check coverage first
status = formulary.check_coverage("00074433902")  # Humira 40mg
```

**Humira Coverage:**

| Field | Value |
|-------|-------|
| Covered | Yes |
| Tier | 5 (Specialty) |
| Coinsurance | 25% |
| Requires PA | Yes |
| Specialty Pharmacy Required | Yes |
| Cold Chain | Yes |

**Without PA:**

```python
claim = PharmacyClaim(
    claim_id="CLM-SPEC-001",
    transaction_code=TransactionCode.BILLING,
    service_date=date.today(),
    pharmacy_npi="9876543210",
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    bin=member.bin,
    pcn=member.pcn,
    group_number=member.group_number,
    prescription_number="RX-SPEC-001",
    fill_number=1,
    ndc="00074433902",  # Humira 40mg
    quantity_dispensed=Decimal("2"),  # 2 syringes
    days_supply=28,
    daw_code="0",
    prescriber_npi="1234567890",
    ingredient_cost_submitted=Decimal("6500.00"),
    dispensing_fee_submitted=Decimal("50.00"),
    usual_customary_charge=Decimal("7500.00"),
    gross_amount_due=Decimal("6550.00"),
)

response = engine.adjudicate(claim, member)
```

**Result (No PA):**

| Field | Value |
|-------|-------|
| Status | R (Rejected) |
| Reject Code | 75 |
| Message | Prior Authorization Required |

**With PA:**

```python
claim_with_pa = PharmacyClaim(
    # ... same fields ...
    prior_auth_number="AUTH-HUMIRA-001",
)

response = engine.adjudicate(claim_with_pa, member)
```

**Result (With PA):**

| Field | Value |
|-------|-------|
| Status | P (Paid) |
| Plan Pays | $4,912.50 |
| Patient Pays | $1,637.50 (25% coinsurance) |

That's a lot for the patient! Let's discuss patient assistance.

---

## Copay Assistance Programs

**User:** That's expensive. Are there copay assistance options?

**Assistant:** Yes! Most specialty drugs have manufacturer copay assistance programs:

**Humira Complete (AbbVie):**

| Benefit | Details |
|---------|---------|
| Program | Humira Complete Savings Card |
| Max Benefit | Up to $16,000/year |
| Copay Reduction | Pay as little as $5/month |
| Eligibility | Commercial insurance only |
| Exclusions | Medicare, Medicaid, government programs |

**With Copay Card Applied:**

```python
# Original patient responsibility
patient_pay = Decimal("1637.50")

# Copay card covers most
copay_card_payment = Decimal("1632.50")
patient_final = patient_pay - copay_card_payment

print(f"Original Patient Pay: ${patient_pay}")
print(f"Copay Card Covers: ${copay_card_payment}")
print(f"Patient Final: ${patient_final}")
```

**Output:**
```
Original Patient Pay: $1,637.50
Copay Card Covers: $1,632.50
Patient Final: $5.00
```

**Common Manufacturer Programs:**

| Drug | Program | Max Annual Benefit |
|------|---------|-------------------|
| Humira | Humira Complete | $16,000 |
| Enbrel | Enbrel Support | $12,000 |
| Stelara | Janssen CarePath | $20,000 |
| Keytruda | Merck Access | Varies |
| Biktarvy | Gilead Copay | No limit |

---

## Hub Services

**User:** What are hub services and how do they work?

**Assistant:** Specialty hubs coordinate care between manufacturer, pharmacy, and patient:

**Hub Service Components:**

```yaml
enrollment:
  - Benefits verification
  - Prior authorization support
  - Financial assistance coordination
  - Patient consent/enrollment

clinical:
  - Medication therapy management
  - Adherence monitoring
  - Side effect management
  - Lab monitoring coordination

logistics:
  - Cold chain shipping
  - Delivery scheduling
  - Refill reminders
  - Supply management
```

**Hub Enrollment Workflow:**

```
1. Prescriber writes Rx for specialty drug
   ↓
2. Rx sent to specialty pharmacy
   ↓
3. Hub contacts patient for enrollment
   ↓
4. Benefits investigation completed
   ↓
5. PA submitted if required
   ↓
6. Financial assistance arranged
   ↓
7. First shipment scheduled
   ↓
8. Ongoing monitoring begins
```

**Support Services:**

| Service | Description |
|---------|-------------|
| Nurse Educators | Injection training, disease education |
| Care Coordinators | Navigate insurance, schedule shipments |
| Financial Counselors | Copay assistance, PAP enrollment |
| Clinical Pharmacists | Drug interactions, side effects |

---

## REMS Programs

**User:** What are REMS programs?

**Assistant:** REMS (Risk Evaluation and Mitigation Strategies) are FDA-required programs for drugs with serious safety concerns:

**Example: Revlimid REMS**

```yaml
drug:
  name: "Revlimid (lenalidomide)"
  program: "REMS"
  reason: "Teratogenic - causes severe birth defects"

requirements:
  prescriber:
    - Must be certified in REMS program
    - Complete training and enrollment
    - Verify patient meets requirements before each Rx

  pharmacy:
    - Must be certified in REMS program
    - Can only dispense with authorization number
    - Maximum 28-day supply

  patient:
    - Enrolled in REMS program
    - Signed patient agreement
    - Pregnancy tests (if applicable)
    - Use two forms of contraception (FCBP)

  dispensing_rules:
    - Verify authorization number
    - Maximum 28-day supply
    - No automatic refills
    - Fill within 7 days of survey
```

**REMS Authorization Check:**

```python
# Simulated REMS verification
rems_check = {
    "drug": "Revlimid",
    "ndc": "59572040028",
    "prescriber_certified": True,
    "pharmacy_certified": True,
    "patient_enrolled": True,
    "authorization_number": "REMS-2024-56789",
    "survey_completed": True,
    "days_since_survey": 3,
}

if all([
    rems_check["prescriber_certified"],
    rems_check["pharmacy_certified"],
    rems_check["patient_enrolled"],
    rems_check["survey_completed"],
    rems_check["days_since_survey"] <= 7,
]):
    print("REMS requirements met - can dispense")
else:
    print("REMS requirements NOT met - cannot dispense")
```

**Common REMS Programs:**

| Drug | Reason | Key Requirement |
|------|--------|-----------------|
| Revlimid | Teratogenic | Pregnancy prevention |
| Thalomid | Teratogenic | Pregnancy prevention |
| Clozaril | Agranulocytosis | WBC monitoring |
| Accutane | Teratogenic | iPLEDGE program |
| Suboxone | Opioid | Provider certification |

---

## Cold Chain Requirements

**User:** How does cold chain shipping work?

**Assistant:** Many biologics require temperature-controlled shipping:

**Temperature Categories:**

| Category | Range | Examples |
|----------|-------|----------|
| Refrigerated | 2-8°C (36-46°F) | Humira, Enbrel, insulin |
| Frozen | -25 to -10°C | Some vaccines |
| Controlled Room | 20-25°C (68-77°F) | Oral specialty drugs |

**Cold Chain Shipping Requirements:**

```yaml
cold_chain_shipment:
  packaging:
    - Insulated container
    - Gel packs (frozen or refrigerated)
    - Temperature monitor/data logger

  shipping:
    - Overnight or 2-day maximum
    - Signature required
    - Weather monitoring (hold if extreme temps)

  alerts:
    - Temperature excursion notification
    - Delivery exception notification
    - Patient availability confirmation

  patient_instructions:
    - Refrigerate immediately upon receipt
    - Check temperature monitor
    - Do not freeze (unless specified)
    - Report any concerns to pharmacy
```

**Temperature Excursion Handling:**

| Scenario | Action |
|----------|--------|
| Package delayed | Contact patient, assess stability |
| Temp excursion detected | Do not use, replace shipment |
| Patient not home | Reschedule delivery |
| Extreme weather | Hold shipment until safe |

---

## Site of Care

**User:** Where can specialty drugs be administered?

**Assistant:** Specialty drugs can be administered at different sites:

**Site of Care Options:**

| Site | Billing | Drug Types |
|------|---------|------------|
| Home (Self-Admin) | Pharmacy benefit | SC injectables (Humira) |
| Physician Office | Medical benefit | Office-administered |
| Infusion Center | Medical benefit | IV infusions |
| Home Infusion | Medical/Pharmacy | Home IV therapy |
| Hospital Outpatient | Medical benefit | Complex infusions |

**Billing Implications:**

```yaml
pharmacy_benefit:
  # Self-administered drugs
  examples: ["Humira", "Enbrel", "Ozempic"]
  billing: "Pharmacy claim (B1)"
  cost_share: "Pharmacy copay/coinsurance"

medical_benefit:
  # Provider-administered drugs
  examples: ["Remicade", "Keytruda", "Rituxan"]
  billing: "Medical claim"
  cost_share: "Medical deductible + coinsurance"
```

**White Bagging vs Brown Bagging:**

| Method | Flow | Benefit |
|--------|------|---------|
| White Bagging | Specialty pharmacy → Physician office | Cost savings |
| Brown Bagging | Specialty pharmacy → Patient → Office | Patient convenience |
| Buy & Bill | Physician buys drug → Administers → Bills | Traditional |

---

## Patient Assistance Programs (PAP)

**User:** What about patients without insurance or Medicare?

**Assistant:** Patient Assistance Programs help uninsured or underinsured patients:

**AbbVie Patient Assistance (Humira):**

| Criteria | Requirement |
|----------|-------------|
| Insurance | Uninsured or underinsured |
| Income | ≤ 400% Federal Poverty Level |
| Medicare | Medicare Part D coverage gap |
| Documentation | Proof of income required |

**Program Benefits:**

```yaml
pap_enrollment:
  application:
    - Patient demographics
    - Insurance information
    - Income verification
    - Prescriber signature

  if_approved:
    - Drug provided free of charge
    - Shipped directly to patient or physician
    - Renewal required annually

  typical_duration:
    initial: 12 months
    renewal: Annual with income verification
```

**PAP vs Copay Card:**

| Feature | PAP | Copay Card |
|---------|-----|------------|
| Eligibility | Uninsured/underinsured | Commercial insurance |
| Cost to Patient | Free | Reduced copay |
| Medicare | Some qualify | Not eligible |
| Medicaid | Some qualify | Not eligible |
| Income Limit | Yes (FPL-based) | No |

---

## Specialty Adherence Monitoring

**User:** How is adherence tracked for specialty drugs?

**Assistant:** Specialty pharmacies actively monitor adherence:

**Adherence Metrics:**

```yaml
metrics:
  pdc:  # Proportion of Days Covered
    calculation: "Days with medication / Days in period"
    target: ">= 80%"

  mpr:  # Medication Possession Ratio
    calculation: "Days supply dispensed / Days in period"
    target: ">= 80%"

  gap_days:
    calculation: "Days between fills - days supply"
    alert_threshold: "> 7 days"
```

**Adherence Interventions:**

| Gap Days | Intervention |
|----------|--------------|
| 3-7 days | Automated refill reminder |
| 7-14 days | Phone call from pharmacist |
| 14-21 days | Care coordinator outreach |
| >21 days | Prescriber notification |

**Outcomes Tracking:**

| Condition | Outcome Measure |
|-----------|-----------------|
| Rheumatoid Arthritis | DAS28 score |
| Hepatitis C | SVR12 (viral cure) |
| Multiple Sclerosis | Relapse rate |
| Oncology | Response rate |
| Diabetes (GLP-1) | A1c reduction |

---

## Next Steps

Continue testing with:
- **[Prior Auth Workflow](04-prior-auth-workflow.md)** - PA processing
- **[Formulary Testing](02-formulary-testing.md)** - Coverage scenarios
- **[API Reference](../../docs/reference/api.md)** - Complete API