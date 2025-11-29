# RxMemberSim API Reference

Complete Python API for RxMemberSim.

## Core Models

### RxMember

```python
from rxmembersim.core.member import RxMemberGenerator

generator = RxMemberGenerator(seed=42)
member = generator.generate(
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001",
)

# Member attributes
member.member_id           # Unique identifier
member.cardholder_id       # Card ID
member.person_code         # "01" = subscriber
member.bin                 # Bank ID Number
member.pcn                 # Processor Control Number
member.group_number        # Group identifier

# Demographics
member.demographics.first_name
member.demographics.last_name
member.demographics.date_of_birth
member.demographics.gender
member.demographics.address

# Accumulators
member.accumulators.deductible_met
member.accumulators.deductible_remaining
member.accumulators.oop_met
member.accumulators.oop_remaining
```

### RxMemberGenerator

```python
from rxmembersim.core.member import RxMemberGenerator

# Basic generation
generator = RxMemberGenerator(seed=42)
member = generator.generate(
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001",
)

# Generate multiple
members = [generator.generate(
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001",
) for _ in range(100)]
```

## Claims

### PharmacyClaim

```python
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from datetime import date
from decimal import Decimal

claim = PharmacyClaim(
    claim_id="CLM001",
    transaction_code=TransactionCode.BILLING,
    service_date=date.today(),
    pharmacy_npi="9876543210",
    member_id="MEM001",
    cardholder_id="CH001",
    person_code="01",
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001",
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
```

### TransactionCode

```python
from rxmembersim.claims.claim import TransactionCode

TransactionCode.BILLING      # B1 - New claim
TransactionCode.REVERSAL     # B2 - Cancel claim
TransactionCode.REBILL       # B3 - Resubmit
TransactionCode.ELIGIBILITY  # E1 - Check eligibility
```

### AdjudicationEngine

```python
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator

formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)

response = engine.adjudicate(claim, member)

# Response attributes
response.response_status       # A, R, P, D
response.authorization_number  # If approved
response.total_amount_paid     # Plan payment
response.patient_pay_amount    # Member responsibility
response.copay_amount          # Copay
response.coinsurance_amount    # Coinsurance
response.deductible_amount     # Deductible applied
response.reject_codes          # List of RejectCode
```

## Formulary

### FormularyGenerator

```python
from rxmembersim.formulary.formulary import FormularyGenerator

generator = FormularyGenerator()

# Commercial formulary
formulary = generator.generate_standard_commercial()

# Medicare Part D
formulary = generator.generate_medicare_partd()

# Medicaid
formulary = generator.generate_medicaid()
```

### Coverage Check

```python
status = formulary.check_coverage("00071015523")

# CoverageStatus attributes
status.covered          # bool
status.tier             # int (1-5)
status.tier_name        # str
status.copay            # Decimal
status.coinsurance      # Decimal (percentage)
status.requires_pa      # bool
status.step_therapy     # bool
status.quantity_limit   # int
status.message          # str
```

## DUR

### DURValidator

```python
from rxmembersim.dur.validator import DURValidator
from datetime import date

validator = DURValidator()

result = validator.validate_simple(
    ndc="00071015523",
    gpi="39400010000310",
    drug_name="Atorvastatin 10mg",
    member_id="MEM001",
    service_date=date.today(),
    current_medications=[
        {"ndc": "...", "gpi": "...", "name": "..."}
    ],
    patient_age=55,
    patient_gender="M",
)

# DURResult attributes
result.passed           # bool
result.total_alerts     # int
result.alerts           # List[DURAlert]
result.override_allowed # bool
```

### DURAlert

```python
for alert in result.alerts:
    alert.alert_type              # AlertType enum
    alert.clinical_significance   # Severity (1-4)
    alert.message                 # Description
    alert.conflicting_drug        # If interaction
```

### AlertType

```python
from rxmembersim.dur.validator import AlertType

AlertType.DD  # Drug-Drug Interaction
AlertType.TD  # Therapeutic Duplication
AlertType.ER  # Early Refill
AlertType.HD  # High Dose
AlertType.LD  # Low Dose
AlertType.DA  # Drug-Age
AlertType.DG  # Drug-Gender
AlertType.DC  # Drug-Disease
AlertType.AL  # Drug-Allergy
AlertType.PG  # Drug-Pregnancy
```

## Prior Authorization

### PAWorkflow

```python
from rxmembersim.authorization.prior_auth import PAWorkflow
from decimal import Decimal

pa_workflow = PAWorkflow()

# Create request
request = pa_workflow.create_request(
    member_id="MEM001",
    cardholder_id="CH001",
    ndc="00169413512",
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
    diagnosis_codes=["E11.9"],
    urgency="standard",  # standard, urgent, emergency
)

# Check auto-approval
response = pa_workflow.check_auto_approval(request)
if response and response.auto_approved:
    print(f"PA Number: {response.pa_number}")
```

### PARequest Attributes

```python
request.pa_request_id    # Request identifier
request.status           # PENDING, APPROVED, DENIED, etc.
request.member_id        # Member ID
request.ndc              # Drug NDC
request.drug_name        # Drug name
request.quantity         # Requested quantity
request.days_supply      # Days supply
request.prescriber_npi   # Prescriber NPI
request.diagnosis_codes  # ICD-10 codes
request.urgency          # Urgency level
```

## Scenarios

### RxScenarioEngine

```python
from rxmembersim.scenarios.engine import RxScenarioEngine

engine = RxScenarioEngine()

# List available scenarios
scenarios = engine.list_scenarios()
for scenario in scenarios:
    print(f"{scenario.scenario_id}: {scenario.scenario_name}")

# Run a scenario
scenario = engine.new_therapy_approved()
timeline = engine.execute_scenario(scenario, "MEM001")

# Timeline events
for event in timeline.events:
    print(f"{event.event_date}: {event.event_type.value}")
    print(f"  Data: {event.data}")
```

### Available Scenarios

| Method | Description |
|--------|-------------|
| `new_therapy_approved()` | New drug approved |
| `step_therapy_rejected()` | Step therapy required |
| `pa_required()` | Prior auth workflow |
| `refill_too_soon()` | Early refill rejection |
| `drug_interaction()` | DUR interaction alert |

## MCP Server

### Available Tools

| Tool | Description |
|------|-------------|
| `generate_rx_member` | Create pharmacy member |
| `check_formulary` | Look up drug coverage |
| `check_dur` | Execute DUR screening |
| `submit_prior_auth` | Submit PA request |
| `run_rx_scenario` | Execute scenario |
| `list_scenarios` | List available scenarios |

### Starting Server

```bash
python -m rxmembersim.mcp.server
```

### Claude Configuration

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