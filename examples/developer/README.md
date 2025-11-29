# Developer Examples

Runnable Python examples demonstrating RxMemberSim's pharmacy benefit simulation API.

## Quickstart Examples

Get started with these fundamental examples:

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| [basic_claim.py](quickstart/basic_claim.py) | Generate member and process claim | `RxMemberGenerator`, `PharmacyClaim`, adjudication |

### Running Quickstart Examples

```bash
cd /path/to/rxmembersim
pip install -e ".[dev]"

# Run basic claim example
python examples/developer/quickstart/basic_claim.py
```

## Example Categories

### Quickstart (`quickstart/`)

Essential examples for getting started:

- **basic_claim.py** - Member generation, claim creation, adjudication

### Claims (Coming Soon)

Claims processing examples:

- `claim_reversal.py` - B2 reversal transactions
- `batch_claims.py` - Process multiple claims
- `reject_scenarios.py` - Common reject codes

### Formulary (Coming Soon)

Formulary testing examples:

- `coverage_check.py` - Check drug coverage
- `tier_testing.py` - Test all tier levels
- `pa_required.py` - PA-required drugs

### DUR (Coming Soon)

Drug utilization review examples:

- `drug_interactions.py` - DD interaction detection
- `therapeutic_dup.py` - TD duplication alerts
- `early_refill.py` - ER prevention

### Prior Auth (Coming Soon)

Prior authorization examples:

- `pa_request.py` - Submit PA requests
- `auto_approval.py` - Emergency auto-approval
- `pa_workflow.py` - Complete PA workflow

### Specialty (Coming Soon)

Specialty pharmacy examples:

- `specialty_claim.py` - Process specialty claims
- `hub_services.py` - Hub service simulation
- `cold_chain.py` - Temperature requirements

## Code Patterns

### Reproducible Generation

All examples support deterministic generation with seeds:

```python
from rxmembersim.core.member import RxMemberGenerator

# Same seed = same output every time
gen1 = RxMemberGenerator(seed=42)
member1 = gen1.generate(bin="610014", pcn="TEST", group_number="GRP001")

gen2 = RxMemberGenerator(seed=42)
member2 = gen2.generate(bin="610014", pcn="TEST", group_number="GRP001")

assert member1.member_id == member2.member_id
```

### Complete Claim Workflow

Standard pattern for claim processing:

```python
from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.formulary.formulary import FormularyGenerator
from datetime import date
from decimal import Decimal

# 1. Generate member
generator = RxMemberGenerator(seed=42)
member = generator.generate(bin="610014", pcn="TEST", group_number="GRP001")

# 2. Create formulary and engine
formulary = FormularyGenerator().generate_standard_commercial()
engine = AdjudicationEngine(formulary=formulary)

# 3. Create claim
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

# 4. Adjudicate
response = engine.adjudicate(claim, member)
print(f"Status: {response.response_status}")
print(f"Patient Pay: ${response.patient_pay_amount}")
```

### DUR Validation Pattern

Pattern for DUR screening:

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
    current_medications=[],
    patient_age=55,
    patient_gender="M",
)

if not result.passed:
    for alert in result.alerts:
        print(f"[{alert.alert_type.value}] {alert.message}")
```

## Prerequisites

```bash
# Clone repository
git clone https://github.com/mark64oswald/rxmembersim.git
cd rxmembersim

# Install with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "from rxmembersim.core.member import RxMemberGenerator; print('OK')"
```

## Output Directory

Examples save output to `examples/developer/output/`:

```
examples/developer/
├── output/
│   ├── claims.json
│   └── members.csv
├── quickstart/
│   └── basic_claim.py
└── README.md
```

## Contributing

To add new examples:

1. Create a new `.py` file in the appropriate category directory
2. Include comprehensive docstrings and comments
3. Follow existing code patterns (seeding, error handling)
4. Add entry to this README
5. Submit a pull request

## Related Resources

- **[Conversation Examples](../conversations/)** - Natural language interaction patterns
- **[API Reference](../../docs/reference/api.md)** - Complete Python API
- **[User Guide](../../docs/user-guide/)** - Step-by-step tutorials
- **[Demos](../../demos/)** - Interactive demonstrations