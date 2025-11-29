# Formulary Management

Configure and test drug coverage with RxMemberSim's formulary system.

## Formulary Overview

A formulary defines which drugs are covered and at what cost to the member. RxMemberSim provides tools to generate and customize formularies for testing.

## FormularyGenerator

### Generate Standard Formulary

```python
from rxmembersim.formulary.formulary import FormularyGenerator

generator = FormularyGenerator()
formulary = generator.generate_standard_commercial()
```

### Formulary Types

| Type | Method | Description |
|------|--------|-------------|
| Commercial | `generate_standard_commercial()` | Standard employer coverage |
| Medicare Part D | `generate_medicare_partd()` | Medicare drug coverage |
| Medicaid | `generate_medicaid()` | State Medicaid formulary |

## Coverage Check

### Check Drug Coverage

```python
# Check single drug
status = formulary.check_coverage("00071015523")  # Atorvastatin

print(f"Covered: {status.covered}")
print(f"Tier: {status.tier}")
print(f"Tier Name: {status.tier_name}")
print(f"Copay: ${status.copay}")
print(f"Coinsurance: {status.coinsurance}%")
print(f"Requires PA: {status.requires_pa}")
print(f"Step Therapy: {status.step_therapy}")
print(f"Quantity Limit: {status.quantity_limit}")
```

### CoverageStatus Fields

| Field | Type | Description |
|-------|------|-------------|
| `covered` | bool | Drug is on formulary |
| `tier` | int | Tier number (1-5) |
| `tier_name` | str | Tier description |
| `copay` | Decimal | Flat copay amount |
| `coinsurance` | Decimal | Coinsurance percentage |
| `requires_pa` | bool | Prior auth required |
| `step_therapy` | bool | Step therapy applies |
| `quantity_limit` | int | Max quantity per fill |
| `message` | str | Additional info/reason |

## Tier Structure

### Standard Commercial Tiers

| Tier | Name | Copay | Examples |
|------|------|-------|----------|
| 1 | Preferred Generic | $10 | Atorvastatin, Metformin, Lisinopril |
| 2 | Non-Preferred Generic | $25 | Gabapentin, Omeprazole |
| 3 | Preferred Brand | $40 | Eliquis, Jardiance |
| 4 | Non-Preferred Brand | $80 | Lipitor, Nexium |
| 5 | Specialty | 25% coinsurance | Humira, Enbrel, Ozempic |

### Medicare Part D Tiers

| Tier | Name | Cost Share |
|------|------|------------|
| 1 | Preferred Generic | $0-5 |
| 2 | Generic | $5-15 |
| 3 | Preferred Brand | $35-50 |
| 4 | Non-Preferred Drug | $80-100 |
| 5 | Specialty | 25-33% |

## Utilization Management

### Prior Authorization

Drugs requiring pre-approval:

```python
# Check PA requirement
status = formulary.check_coverage("00169413512")  # Ozempic

if status.requires_pa:
    print("Prior authorization required")
    print("Submit PA request before claim")
```

**Common PA-Required Categories:**
- GLP-1 agonists (Ozempic, Wegovy)
- Specialty biologics (Humira, Enbrel)
- Growth hormones
- Hepatitis C medications
- Some controlled substances

### Step Therapy

Must try alternative drugs first:

```python
status = formulary.check_coverage("00069015430")  # Lipitor

if status.step_therapy:
    print("Step therapy required")
    print("Try generic atorvastatin first")
```

**Common Step Therapy Protocols:**
```
Statins:
  Step 1: Simvastatin (generic)
  Step 2: Atorvastatin (generic)
  Step 3: Lipitor (brand)

PPIs:
  Step 1: Omeprazole (generic)
  Step 2: Pantoprazole (generic)
  Step 3: Nexium (brand)
```

### Quantity Limits

Maximum quantities per fill:

```python
status = formulary.check_coverage("00093317431")  # Controlled substance

if status.quantity_limit:
    print(f"Maximum quantity: {status.quantity_limit}")
```

**Typical Limits:**

| Drug Type | Limit |
|-----------|-------|
| Acute medications | 10-14 days |
| Maintenance drugs | 30-90 days |
| Controlled substances | 30 days |
| Specialty drugs | 30 days |

## Drug Classification

### NDC (National Drug Code)

11-digit identifier: `AAAAA-BBBB-CC`
- A: Labeler code (manufacturer)
- B: Product code
- C: Package code

```python
ndc = "00071015523"  # Atorvastatin 10mg
# 00071 = Pfizer
# 0155 = Atorvastatin 10mg
# 23 = 90 count bottle
```

### GPI (Generic Product Identifier)

14-character therapeutic classification:

```python
gpi = "39400010000310"
# 39 = Antihyperlipidemic
# 40 = HMG-CoA Reductase Inhibitors
# 0010 = Atorvastatin
# 000310 = 10mg tablet
```

## Testing Scenarios

### Tier 1 - Generic

```python
# Atorvastatin - Tier 1 generic
status = formulary.check_coverage("00071015523")
assert status.covered == True
assert status.tier == 1
assert status.copay == Decimal("10.00")
```

### Tier 5 - Specialty

```python
# Humira - Tier 5 specialty
status = formulary.check_coverage("00074433902")
assert status.covered == True
assert status.tier == 5
assert status.coinsurance == Decimal("25")
assert status.requires_pa == True
```

### Not Covered

```python
# Drug not on formulary
status = formulary.check_coverage("99999999999")
assert status.covered == False
assert status.message == "Drug not on formulary"
```

### PA Required

```python
# Ozempic - requires PA
status = formulary.check_coverage("00169413512")
assert status.covered == True
assert status.requires_pa == True
```

## Next Steps

- **[DUR Screening](dur-screening.md)** - Drug interaction checks
- **[Prior Authorization](prior-auth.md)** - PA request workflows
- **[Pharmacy Claims](pharmacy-claims.md)** - Process claims