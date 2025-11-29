# Prior Authorization Workflow

Testing PA request, approval, and denial scenarios.

---

## Understanding Prior Authorization

**User:** Explain prior authorization and how to test it

**Assistant:** Prior Authorization (PA) requires pre-approval before a drug is covered. Here's the workflow:

```
1. Pharmacy submits claim
   ↓
2. PBM returns reject code 75 (PA Required)
   ↓
3. Prescriber submits PA request
   ↓
4. PBM reviews against clinical criteria
   ↓
5. Decision: Approved / Denied / Pend for info
   ↓
6. If approved: PA number issued
   ↓
7. Pharmacy resubmits claim with PA number
   ↓
8. Claim processes normally
```

Let me set up PA testing:

```python
from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.formulary.formulary import FormularyGenerator
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.authorization.prior_auth import PAWorkflow
from decimal import Decimal

# Setup
generator = RxMemberGenerator(seed=42)
member = generator.generate(bin="610014", pcn="TEST", group_number="GRP001")
formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)
pa_workflow = PAWorkflow()
```

---

## Testing PA Required Rejection

**User:** Show me a claim that requires PA

**Assistant:** I'll submit a claim for Ozempic (requires PA):

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date

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
    prescription_number="RX789012",
    fill_number=1,
    ndc="00169413512",  # Ozempic 0.5mg
    quantity_dispensed=Decimal("1"),
    days_supply=28,
    daw_code="0",
    prescriber_npi="1234567890",
    ingredient_cost_submitted=Decimal("850.00"),
    dispensing_fee_submitted=Decimal("2.00"),
    patient_paid_submitted=Decimal("0.00"),
    usual_customary_charge=Decimal("950.00"),
    gross_amount_due=Decimal("852.00"),
)

response = engine.adjudicate(claim, member)
```

**Adjudication Result:**

| Field | Value |
|-------|-------|
| Status | R (Rejected) |
| Reject Code | 75 |
| Message | Prior Authorization Required |
| Additional Info | GLP-1 agonist requires PA |

The claim was rejected because Ozempic requires prior authorization.

---

## Submitting a PA Request

**User:** Submit a PA request for this drug

**Assistant:** I'll create a PA request:

```python
request = pa_workflow.create_request(
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    ndc="00169413512",
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Sarah Johnson",
    diagnosis_codes=["E11.9", "E11.65"],  # Type 2 DM, Type 2 DM with hyperglycemia
    clinical_notes="Patient has A1c of 8.2%. Failed metformin 2000mg/day for 6 months.",
    urgency="standard",
)
```

**PA Request Created:**

| Field | Value |
|-------|-------|
| PA Request ID | PA-2024-001234 |
| Status | PENDING |
| Member ID | MEM-7f8a9b12 |
| Drug | Ozempic 0.5mg |
| NDC | 00169413512 |
| Prescriber | Dr. Sarah Johnson |
| Urgency | Standard (72 hour review) |

**Request Summary:**
```
PA Request: PA-2024-001234
Drug: Ozempic 0.5mg (00169413512)
Diagnosis: E11.9 (Type 2 Diabetes)
Clinical: A1c 8.2%, failed metformin
Status: PENDING - Under clinical review
Expected Decision: Within 72 hours
```

---

## PA Clinical Criteria

**User:** What criteria does Ozempic require?

**Assistant:** Here are the clinical criteria for GLP-1 agonists like Ozempic:

**Ozempic PA Criteria:**

```yaml
criteria:
  diagnosis:
    required:
      - Type 2 Diabetes (E11.*)

  clinical_requirements:
    - A1c >= 7.0% documented within 90 days
    - Failed or contraindicated: metformin (minimum 3 months trial)
    - BMI documented in medical record

  exclusions:
    - Type 1 Diabetes (E10.*)
    - Personal/family history of MTC
    - MEN2 syndrome
    - History of pancreatitis

  approval_terms:
    initial_duration: 6 months
    renewal_duration: 12 months
    quantity_per_fill: 1 pen
    max_days_supply: 28 days
```

**Our Request Assessment:**

| Criteria | Required | Submitted | Met? |
|----------|----------|-----------|------|
| Diagnosis | E11.* | E11.9 | Yes |
| A1c >= 7% | Yes | 8.2% | Yes |
| Failed metformin | Yes | 6 months | Yes |
| No exclusions | Yes | Not documented | Assumed |

Based on the submitted information, this PA should be approved.

---

## PA Approval Scenario

**User:** Show me an approved PA

**Assistant:** Let me simulate approval:

```python
# Simulated approval response
approval = {
    "pa_request_id": "PA-2024-001234",
    "decision": "APPROVED",
    "pa_number": "AUTH-2024-56789",
    "effective_date": "2024-01-15",
    "expiration_date": "2024-07-15",
    "approved_quantity": 1,
    "approved_days_supply": 28,
    "approved_refills": 5,
    "notes": "Approved for 6 months. Renewal requires updated A1c."
}
```

**PA Approval:**

| Field | Value |
|-------|-------|
| Decision | APPROVED |
| PA Number | AUTH-2024-56789 |
| Effective | 2024-01-15 |
| Expires | 2024-07-15 |
| Approved Qty | 1 pen per 28 days |
| Refills | 5 |

Now the pharmacy can resubmit the claim:

```python
# Resubmit claim with PA number
claim_with_pa = PharmacyClaim(
    # ... same fields as before ...
    prior_auth_number="AUTH-2024-56789",  # Add PA number
)

response = engine.adjudicate(claim_with_pa, member)
```

**Result with PA:**

| Field | Value |
|-------|-------|
| Status | P (Paid) |
| Authorization | AUTH-2024-56789 |
| Plan Pays | $637.50 |
| Patient Pays | $212.50 (25% coinsurance) |

---

## PA Denial Scenario

**User:** What does a denial look like?

**Assistant:** Here's a denial scenario where step therapy wasn't completed:

```python
# Request for Ozempic without trying metformin first
request_denied = pa_workflow.create_request(
    member_id="MEM002",
    cardholder_id="CH002",
    ndc="00169413512",
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    diagnosis_codes=["E11.9"],
    clinical_notes="New diagnosis of Type 2 diabetes. A1c 7.5%.",
    # No mention of metformin trial
)
```

**PA Denial:**

| Field | Value |
|-------|-------|
| Decision | DENIED |
| Denial Reason | Step therapy not completed |
| Denial Code | ST01 |
| Alternative | Metformin 1000mg twice daily |
| Appeal Deadline | 2024-02-15 |

**Denial Details:**
```
PA Request: PA-2024-001235
Decision: DENIED
Reason: Step therapy not completed

Clinical Note: GLP-1 agonists require trial of metformin
(minimum 3 months) before approval unless contraindicated.

Suggested Alternative: Metformin 1000mg BID
If metformin contraindicated, submit documentation.

Appeal Information:
- Deadline: 30 days from denial date
- Submit to: PBM Appeals Department
- Include: Documentation of metformin trial or contraindication
```

---

## Emergency PA / Auto-Approval

**User:** Can anything be auto-approved?

**Assistant:** Emergency requests may receive automatic approval:

```python
# Emergency PA request
request_emergency = pa_workflow.create_request(
    member_id=member.member_id,
    cardholder_id=member.cardholder_id,
    ndc="00169413512",
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    urgency="emergency",  # Emergency flag
)

response = pa_workflow.check_auto_approval(request_emergency)
```

**Auto-Approval Result:**

| Field | Value |
|-------|-------|
| Auto-Approved | Yes |
| PA Number | TEMP-2024-001236 |
| Quantity | 72-hour supply |
| Expiration | 72 hours |
| Follow-up | Full PA required within 72 hours |

**Emergency Auto-Approval Criteria:**

| Scenario | Auto-Approve | Supply |
|----------|--------------|--------|
| Emergency urgency | Yes | 72 hours |
| Hospital discharge | Yes | 72 hours |
| Continuation therapy | Maybe | 30 days |
| Standard request | No | N/A |

---

## Pend for Information

**User:** What if more information is needed?

**Assistant:** Here's a "pend" scenario where additional documentation is required:

```python
# Simulated pend response
pend = {
    "pa_request_id": "PA-2024-001237",
    "decision": "PENDED_INFO",
    "pend_reason": "Missing documentation",
    "information_needed": [
        "A1c lab result within last 90 days",
        "Documentation of metformin trial duration",
        "Current BMI measurement",
    ],
    "response_deadline": "2024-01-25",
}
```

**Pend Response:**

| Field | Value |
|-------|-------|
| Decision | PENDED_INFO |
| Reason | Missing documentation |
| Response Deadline | 2024-01-25 |

**Information Needed:**
1. A1c lab result within last 90 days
2. Documentation of metformin trial duration
3. Current BMI measurement

**Next Steps:**
- Prescriber submits additional documentation
- If not received by deadline, PA auto-denies
- Once received, clinical review continues

---

## Appeals Process

**User:** How do appeals work?

**Assistant:** If a PA is denied, the prescriber can appeal:

**Level 1: Internal Appeal**

```python
# Submit internal appeal
appeal = {
    "original_pa_id": "PA-2024-001235",
    "appeal_type": "internal",
    "appeal_reason": "Patient has documented contraindication to metformin",
    "supporting_docs": [
        "GI_consultation_notes.pdf",
        "contraindication_documentation.pdf",
    ],
}
```

| Field | Value |
|-------|-------|
| Appeal Type | Internal |
| Submission Window | 30 days from denial |
| Review By | Different clinical reviewer |
| Decision Timeline | 30 days (standard), 72 hours (expedited) |

**Level 2: External Review (IRO)**

```python
# Submit external review if internal denied
external_appeal = {
    "original_pa_id": "PA-2024-001235",
    "appeal_type": "external",
    "iro_requested": True,
}
```

| Field | Value |
|-------|-------|
| Appeal Type | External (IRO) |
| Submission Window | 60 days from Level 1 denial |
| Review By | Independent Review Organization |
| Decision Timeline | 45 days (standard), 72 hours (expedited) |
| Binding | Yes, if overturned |

---

## Common PA-Required Drugs

**User:** What other drugs commonly require PA?

**Assistant:** Here are categories and examples of PA-required drugs:

| Category | Examples | Common Criteria |
|----------|----------|-----------------|
| GLP-1 Agonists | Ozempic, Wegovy, Trulicity | A1c > 7%, failed metformin |
| Biologics | Humira, Enbrel, Remicade | Failed conventional therapy |
| MS Drugs | Tecfidera, Ocrevus | Confirmed MS diagnosis |
| Hepatitis C | Harvoni, Epclusa | Confirmed HCV, fibrosis staging |
| Growth Hormone | Genotropin, Norditropin | Documented deficiency |
| ADHD (Adult) | Vyvanse, Adderall | Confirmed ADHD diagnosis |
| Weight Loss | Wegovy, Saxenda | BMI >= 30 or BMI >= 27 + comorbidity |

---

## Batch PA Testing

**User:** How can I test multiple PA scenarios?

**Assistant:** Here's how to batch test PA workflows:

```python
test_scenarios = [
    {"drug": "Ozempic", "ndc": "00169413512", "has_metformin_trial": True},
    {"drug": "Ozempic", "ndc": "00169413512", "has_metformin_trial": False},
    {"drug": "Humira", "ndc": "00074433902", "has_failed_conventional": True},
    {"drug": "Humira", "ndc": "00074433902", "has_failed_conventional": False},
]

for scenario in test_scenarios:
    clinical_notes = f"Documentation: {scenario}"
    request = pa_workflow.create_request(
        member_id=member.member_id,
        cardholder_id=member.cardholder_id,
        ndc=scenario["ndc"],
        drug_name=scenario["drug"],
        quantity=Decimal("1"),
        days_supply=28,
        prescriber_npi="1234567890",
        prescriber_name="Dr. Test",
        clinical_notes=clinical_notes,
    )
    print(f"{scenario['drug']}: {request.status}")
```

---

## Next Steps

Continue testing with:
- **[Specialty Pharmacy](05-specialty-pharmacy.md)** - Hub services, REMS
- **[Formulary Testing](02-formulary-testing.md)** - Coverage scenarios
- **[API Reference](../../docs/reference/api.md)** - Complete API