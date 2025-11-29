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

| Capability | Description |
|------------|-------------|
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
from rxmembersim.core import Member, Drug, Pharmacy, Prescriber
from rxmembersim.claims import Claim, ClaimProcessor

# Create a pharmacy member
member = Member(
    member_id="RX123456789",
    cardholder_id="CH987654321",
    group_number="GRP001",
    bin="610014",
    pcn="RXTEST",
    first_name="John",
    last_name="Doe"
)

# Create a drug by NDC
drug = Drug.from_ndc("00071015523")  # Lipitor 20mg

# Submit a claim
claim = Claim(
    member=member,
    drug=drug,
    pharmacy_npi="1234567890",
    prescriber_npi="0987654321",
    quantity=30,
    days_supply=30
)

# Process the claim
processor = ClaimProcessor()
response = processor.adjudicate(claim)

print(f"Status: {response.status}")
print(f"Patient Pay: ${response.patient_pay}")
print(f"Plan Pay: ${response.plan_pay}")
```

### Formulary Check

```python
from rxmembersim.formulary import Formulary, FormularyCheck

# Load a formulary
formulary = Formulary.load("commercial_standard")

# Check drug coverage
result = formulary.check(
    ndc="00071015523",
    member_id="RX123456789"
)

print(f"Covered: {result.is_covered}")
print(f"Tier: {result.tier}")
print(f"Copay: ${result.copay}")
print(f"Restrictions: {result.restrictions}")
```

### DUR Check

```python
from rxmembersim.dur import DURValidator

# Create DUR validator
dur = DURValidator()

# Check for alerts
alerts = dur.validate(
    drug_ndc="00071015523",
    member_id="RX123456789",
    prescriber_npi="0987654321"
)

for alert in alerts:
    print(f"[{alert.severity}] {alert.code}: {alert.message}")
```

### Prior Authorization

```python
from rxmembersim.authorization import PriorAuthRequest, PriorAuthProcessor

# Create PA request
pa_request = PriorAuthRequest(
    member_id="RX123456789",
    drug_ndc="00093720101",  # Specialty drug
    prescriber_npi="0987654321",
    diagnosis_codes=["M05.79"],
    clinical_info={
        "prior_therapies": ["methotrexate", "sulfasalazine"],
        "lab_results": {"RF": "positive", "CRP": 12.5}
    }
)

# Process the request
processor = PriorAuthProcessor()
response = processor.evaluate(pa_request)

print(f"Decision: {response.decision}")
print(f"Auth Number: {response.auth_number}")
print(f"Valid Through: {response.expiration_date}")
```

## What RxMemberSim Generates

### Core Entities
- **Members**: Pharmacy benefit enrollees with BIN/PCN/Group
- **Drugs**: NDC-based products with therapeutic classification (GPI)
- **Pharmacies**: Retail, mail-order, and specialty pharmacy NPIs
- **Prescribers**: Physician NPIs with DEA numbers and specialties
- **Prescriptions**: Rx details with sig codes, quantities, refills

### Claims & Adjudication
- **B1 Claims**: Billing requests with all NCPDP segments
- **B2 Responses**: Paid, rejected, or needs-PA responses
- **Pricing**: Ingredient cost, dispensing fee, patient pay breakdown
- **Reject Codes**: NCPDP standard rejection reasons

### Clinical Data
- **DUR Alerts**: Drug interactions, duplicate therapy, age/gender contraindications
- **Prior Authorizations**: Clinical criteria, approval workflows
- **Step Therapy**: Required drug progressions
- **Quantity Limits**: Daily/monthly supply restrictions

### Specialty Pharmacy
- **Hub Enrollments**: Patient intake and onboarding
- **REMS Programs**: Risk evaluation and mitigation
- **Copay Assistance**: Manufacturer programs
- **Adherence Tracking**: Refill patterns and interventions

## Output Formats

### NCPDP Telecommunication

```python
from rxmembersim.formats.ncpdp import TelecomFormatter

formatter = TelecomFormatter()
b1_message = formatter.format_claim(claim)
```

### NCPDP SCRIPT

```python
from rxmembersim.formats.ncpdp import ScriptFormatter

formatter = ScriptFormatter()
new_rx = formatter.format_new_rx(prescription)
```

### NCPDP ePA

```python
from rxmembersim.formats.ncpdp import EPAFormatter

formatter = EPAFormatter()
pa_initiation = formatter.format_pa_initiation(pa_request)
```

### X12 835 (Payment)

```python
from rxmembersim.formats.x12 import EDI835Formatter

formatter = EDI835Formatter()
remittance = formatter.format_payment(paid_claims)
```

## Use Cases

### PBM System Testing
Test claim adjudication engines, formulary lookups, and DUR processing with realistic synthetic data.

### Integration Testing
Validate NCPDP message parsing and generation across system boundaries.

### Training Environments
Provide realistic pharmacy data for analyst and pharmacist training without privacy concerns.

### Analytics Development
Build and test pharmacy analytics dashboards with representative claim distributions.

### Compliance Testing
Verify system behavior for prior authorization requirements and formulary restrictions.

## For Developers

### Project Structure

```
rxmembersim/
├── src/rxmembersim/
│   ├── core/           # Member, Drug, Pharmacy, Prescriber models
│   ├── claims/         # Claim submission and adjudication
│   ├── formulary/      # Formulary management, tiers, restrictions
│   ├── dur/            # Drug Utilization Review rules and alerts
│   ├── authorization/  # Prior auth and ePA workflows
│   ├── specialty/      # Specialty pharmacy hub simulations
│   ├── pricing/        # Rebates, spread, copay assistance
│   ├── scenarios/      # Pre-built test scenarios
│   ├── formats/        # NCPDP, X12 formatters
│   ├── mcp/            # MCP server integration
│   └── validation/     # Data validation framework
├── tests/              # Test suite
├── examples/           # Usage examples
├── demos/              # Interactive demonstrations
└── skills/             # Domain knowledge documentation
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rxmembersim --cov-report=html

# Run specific test file
pytest tests/test_claims.py
```

### Code Quality

```bash
# Lint
ruff check src tests

# Type check
mypy src --ignore-missing-imports

# Format
ruff format src tests
```

## Scenarios

RxMemberSim includes pre-built scenarios for common pharmacy workflows:

### New Therapy Start
```python
from rxmembersim.scenarios.templates import NewTherapyScenario

scenario = NewTherapyScenario(
    drug_class="statin",
    member_type="commercial"
)
events = scenario.execute()
```

### Step Therapy Progression
```python
from rxmembersim.scenarios.templates import StepTherapyScenario

scenario = StepTherapyScenario(
    target_drug="adalimumab",
    required_steps=["methotrexate", "sulfasalazine"]
)
events = scenario.execute()
```

### Specialty Onboarding
```python
from rxmembersim.scenarios.templates import SpecialtyOnboardScenario

scenario = SpecialtyOnboardScenario(
    drug_ndc="00093720101",
    hub="manufacturer_hub"
)
events = scenario.execute()
```

### Adherence Journey
```python
from rxmembersim.scenarios.templates import AdherenceScenario

scenario = AdherenceScenario(
    therapy="diabetes",
    duration_months=12,
    adherence_pattern="declining"
)
events = scenario.execute()
```

## MCP Integration

RxMemberSim provides an MCP server for AI agent integration:

```bash
# Start MCP server
python -m rxmembersim.mcp.server
```

Available tools:
- `generate_claim` - Create a pharmacy claim
- `check_formulary` - Look up drug coverage
- `run_dur` - Execute DUR screening
- `submit_pa` - Submit prior authorization
- `get_member` - Retrieve member information
- `search_drugs` - Search drug database by name/NDC

## Related Projects

- [healthsim-core](https://github.com/mark64oswald/healthsim-core) - Shared foundation library
- [PatientSim](https://github.com/mark64oswald/patientsim) - Clinical patient data generation
- [MemberSim](https://github.com/mark64oswald/membersim) - Health plan member generation

## License

MIT License - see [LICENSE](LICENSE) for details.