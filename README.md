# RxMemberSim

[![CI](https://github.com/mark64oswald/rxmembersim/actions/workflows/ci.yml/badge.svg)](https://github.com/mark64oswald/rxmembersim/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Synthetic pharmacy benefit data generation for PBM system testing**

## What is RxMemberSim?

RxMemberSim generates realistic synthetic pharmacy benefit data—prescriptions, pharmacy claims, formulary adjudication, DUR alerts, prior authorizations, and specialty pharmacy workflows—for testing PBM (Pharmacy Benefit Manager) systems without PHI exposure.

Built on [healthsim-core](https://github.com/mark64oswald/healthsim-core), it provides:
- Complete NCPDP Telecommunication (B1/B2) claim generation
- E-prescribing via NCPDP SCRIPT standard
- Electronic Prior Authorization (ePA) workflows
- Formulary management with tier structures
- Drug Utilization Review (DUR) alerts
- Specialty pharmacy hub simulations
- Pharmacy pricing, rebates, and copay assistance

## What Can You Do?

### Through Conversation (Claude Desktop/Code)
- "Generate a pharmacy member with diabetes medications"
- "Check if Humira is on the formulary and what tier"
- "Process a claim for 30 tablets of metformin"
- "Run the step therapy scenario"

### Through Code

| Capability | Description |
|------------|-------------|
| **Generate Members** | Create pharmacy members with BIN/PCN/Group and accumulators |
| **Generate Claims** | Create realistic B1/B2 pharmacy claims with proper adjudication |
| **Check Formulary** | Simulate formulary lookups with tier assignments and restrictions |
| **DUR Screening** | Generate drug interaction, duplicate therapy, and clinical alerts |
| **Prior Auth** | Create PA requests, reviews, and approval/denial workflows |
| **ePA Transactions** | NCPDP ePA format initiation and response handling |
| **Specialty Pharmacy** | Hub enrollment, REMS programs, patient assistance |
| **Pricing Models** | AWP, WAC, MAC pricing with spread and rebate calculations |
| **Test Scenarios** | Pre-built scenarios for common pharmacy workflows |

## Quick Start

### Installation

```bash
pip install rxmembersim
```

Or install from source:

```bash
git clone https://github.com/mark64oswald/rxmembersim.git
cd rxmembersim
pip install -e ".[dev]"
```

### Basic Usage

```python
from datetime import date
from decimal import Decimal

from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator

# Generate a pharmacy member
member = RxMemberGenerator().generate(
    bin="610014",
    pcn="RXTEST",
    group_number="GRP001"
)
print(f"Member: {member.member_id}")
print(f"BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")

# Create a claim
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
    ndc="00071015523",  # Atorvastatin
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

# Adjudicate the claim
formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)
response = engine.adjudicate(claim, member)

print(f"Status: {response.response_status}")
print(f"Plan Pay: ${response.total_amount_paid}")
print(f"Patient Pay: ${response.patient_pay_amount}")
```

### Formulary Check

```python
from rxmembersim.formulary.formulary import FormularyGenerator

# Generate a formulary
formulary = FormularyGenerator().generate_standard_commercial()

# Check drug coverage
status = formulary.check_coverage("00071015523")  # Atorvastatin

print(f"Covered: {status.covered}")
print(f"Tier: {status.tier} ({status.tier_name})")
print(f"Copay: ${status.copay}")
print(f"Requires PA: {status.requires_pa}")
```

### DUR Check

```python
from datetime import date
from rxmembersim.dur.validator import DURValidator

# Create DUR validator
validator = DURValidator()

# Check for drug interactions
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

print(f"DUR Passed: {result.passed}")
print(f"Alerts: {result.total_alerts}")
for alert in result.alerts:
    print(f"  [{alert.alert_type.value}] {alert.message}")
```

### Prior Authorization

```python
from decimal import Decimal
from rxmembersim.authorization.prior_auth import PAWorkflow

# Create PA workflow
pa_workflow = PAWorkflow()

# Submit PA request
request = pa_workflow.create_request(
    member_id="MEM001",
    cardholder_id="CH001",
    ndc="00169413512",  # Ozempic
    drug_name="Ozempic 0.5mg",
    quantity=Decimal("1"),
    days_supply=28,
    prescriber_npi="1234567890",
    prescriber_name="Dr. Smith",
)

print(f"PA Request ID: {request.pa_request_id}")
print(f"Status: {request.status}")

# Check for auto-approval (emergency)
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
print(f"Auto-Approved: {response.auto_approved if response else False}")
```

### Run Scenarios

```python
from rxmembersim.scenarios.engine import RxScenarioEngine

engine = RxScenarioEngine()

# List available scenarios
for scenario in engine.list_scenarios():
    print(f"  {scenario.scenario_id}: {scenario.scenario_name}")

# Run a scenario
scenario = engine.new_therapy_approved()
timeline = engine.execute_scenario(scenario, "MEM001")

print(f"\nTimeline ({len(timeline.events)} events):")
for event in timeline.events:
    print(f"  {event.event_type.value}")
```

## What RxMemberSim Generates

| Category | Data Generated |
|----------|----------------|
| **Members** | Demographics, BIN/PCN/Group, accumulators, coverage dates |
| **Claims** | B1/B2 transactions, reversals, pricing, reject codes |
| **Formulary** | Tier structures, step therapy, quantity limits, PA requirements |
| **DUR** | Drug interactions, therapeutic duplication, early refill, dose alerts |
| **Prior Auth** | PA requests, ePA transactions, approvals/denials, appeals |
| **Specialty** | Hub enrollment, REMS, copay assistance, cold chain |
| **Pricing** | Rebates, spread pricing, copay cards, deductibles |

## Output Formats

- **NCPDP Telecommunication** (B1/B2 claims)
- **NCPDP SCRIPT** (NewRx, RxChange)
- **NCPDP ePA** (Prior authorization)
- **JSON / CSV** exports

## Project Structure

```
rxmembersim/
├── src/rxmembersim/
│   ├── core/           # Member, Drug models
│   ├── claims/         # Claim, Response, Adjudication
│   ├── formulary/      # Formulary, Tiers, Step Therapy
│   ├── dur/            # DUR rules and validation
│   ├── authorization/  # Prior auth and ePA
│   ├── specialty/      # Hub services
│   ├── pricing/        # Rebates, spread, copay assist
│   ├── scenarios/      # Event engine
│   ├── formats/        # NCPDP formatters
│   ├── mcp/            # MCP server
│   └── validation/     # Validation framework
├── tests/              # Test suite
├── examples/           # Usage examples
├── demos/              # Interactive demos
└── skills/             # Domain documentation
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rxmembersim --cov-report=html

# Run specific test file
pytest tests/test_claims.py -v
```

## Code Quality

```bash
# Lint
ruff check src tests

# Format
ruff format src tests
```

## MCP Integration

RxMemberSim provides an MCP server for AI agent integration:

```bash
# Start MCP server
python -m rxmembersim.mcp.server
```

Available tools:
- `generate_rx_member` - Create a pharmacy member
- `check_formulary` - Look up drug coverage
- `check_dur` - Execute DUR screening
- `submit_prior_auth` - Submit prior authorization
- `run_rx_scenario` - Execute test scenario
- `list_scenarios` - List available scenarios

## Related Projects

- [healthsim-core](https://github.com/mark64oswald/healthsim-core) - Shared foundation library
- [PatientSim](https://github.com/mark64oswald/patientsim) - Clinical patient data generation
- [MemberSim](https://github.com/mark64oswald/membersim) - Health plan member generation
- [healthsim-hello](https://github.com/mark64oswald/healthsim-hello) - Getting started tutorial

## License

MIT License - see [LICENSE](LICENSE) for details.