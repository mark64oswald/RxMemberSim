# RxMemberSim Demos

Interactive demonstrations of RxMemberSim pharmacy benefit capabilities for PBM system testing.

## Quick Start

Run the interactive demo to see RxMemberSim in action:

```bash
cd demos
python interactive_demo.py
```

This showcases:
- Member generation with pharmacy accumulators
- Formulary checking and tier assignments
- DUR (Drug Utilization Review) alerts
- Scenario execution

## Available Demos

### [Interactive Demo](interactive_demo.py)

Quick demonstration of core RxMemberSim capabilities.

**Run it:**
```bash
python demos/interactive_demo.py
```

**What it shows:**
- Generate a pharmacy member with BIN/PCN/Group
- Check drug formulary coverage and tiers
- Run DUR screening for drug interactions
- Execute predefined scenarios

---

### [Pharmacy Benefits Demo](pharmacy-benefits/README.md)

Comprehensive guide to PBM system testing.

**What you'll learn:**
- NCPDP B1/B2 claim processing
- Formulary management and tier testing
- Drug Utilization Review (DUR) screening
- Prior authorization workflows
- Specialty pharmacy scenarios

**Key scenarios covered:**
- Claims adjudication and pricing
- Formulary lookups with PA/step therapy
- Drug-drug interaction detection
- Prior auth request/approval
- Hub services and REMS

---

### Pricing Demo (Coming Soon)

Pharmacy pricing and rebate calculations.

**Planned content:**
- AWP, WAC, MAC pricing models
- Spread pricing calculations
- Rebate simulations
- Copay card processing
- 340B pricing scenarios

---

### ePA Demo (Coming Soon)

Electronic Prior Authorization workflows.

**Planned content:**
- NCPDP ePA transaction format
- Question/response workflows
- Auto-approval criteria
- Appeal processing
- Status tracking

---

## Demo Categories

| Category | Description | Status |
|----------|-------------|--------|
| **Interactive** | Quick capability showcase | Available |
| **Pharmacy Benefits** | Comprehensive PBM testing guide | Available |
| **Pricing** | AWP/MAC/rebates/spread | Coming Soon |
| **ePA** | Electronic prior auth workflows | Coming Soon |
| **Specialty** | Hub services and REMS | Coming Soon |

## Running Demos

Each demo is self-contained with setup instructions:

```bash
# Navigate to rxmembersim
cd /path/to/rxmembersim

# Install dependencies
pip install -e ".[dev]"

# Run interactive demo
python demos/interactive_demo.py

# Or explore the comprehensive guide
cat demos/pharmacy-benefits/README.md
```

## Prerequisites

```bash
# Clone repository
git clone https://github.com/mark64oswald/rxmembersim.git
cd rxmembersim

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "from rxmembersim.core.member import RxMemberGenerator; print('OK')"
```

## Quick Links

- **[Main README](../README.md)** - Project overview and quick start
- **[Examples](../examples/)** - Code examples and scripts
- **[Skills](../skills/)** - Pharmacy domain documentation

## What RxMemberSim Generates

| Category | Data Generated |
|----------|----------------|
| **Members** | Demographics, BIN/PCN/Group, accumulators |
| **Claims** | B1/B2 transactions, reversals, pricing |
| **Formulary** | Tier structures, PA, step therapy, QL |
| **DUR** | Drug interactions, duplications, alerts |
| **Prior Auth** | PA requests, approvals, denials, ePA |
| **Specialty** | Hub enrollment, REMS, copay assist |

## Output Formats

- **NCPDP Telecommunication** (B1/B2 claims)
- **NCPDP SCRIPT** (NewRx, RxChange)
- **NCPDP ePA** (Prior authorization)
- **JSON / CSV** exports

## Contributing

Want to add a demo? We welcome contributions:

1. Create a new directory under `demos/`
2. Add a comprehensive `README.md`
3. Include working code examples
4. Submit a pull request

## Support

- **Issues:** [GitHub Issues](https://github.com/mark64oswald/rxmembersim/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mark64oswald/rxmembersim/discussions)
- **Documentation:** [skills/](../skills/)