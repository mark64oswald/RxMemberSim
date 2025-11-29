# Formulary Management

## Overview

A formulary is a list of prescription drugs covered by a health plan. Formulary management involves drug selection, tier placement, and utilization management.

## Formulary Structure

### Tier System

| Tier | Description | Typical Copay |
|------|-------------|---------------|
| 1 | Preferred Generic | $10-15 |
| 2 | Non-Preferred Generic | $20-30 |
| 3 | Preferred Brand | $35-50 |
| 4 | Non-Preferred Brand | $75-100 |
| 5 | Specialty | 20-30% coinsurance |

### Coverage Status

- **Covered**: Drug is on formulary, standard processing
- **Not Covered**: Drug excluded from formulary
- **Prior Auth Required**: Coverage requires pre-approval
- **Step Therapy**: Must try alternative first
- **Quantity Limit**: Coverage limited to specific quantity

## Drug Classification

### Therapeutic Categories (GPI)

```
39 - Antihyperlipidemic Agents (Statins)
  3940 - HMG-CoA Reductase Inhibitors
    394000 - Atorvastatin
    394010 - Simvastatin
    394020 - Rosuvastatin

27 - Antidiabetic Agents
  2710 - Insulins
  2728 - GLP-1 Receptor Agonists
    272850 - Semaglutide (Ozempic)
    272840 - Liraglutide (Victoza)
```

### Brand vs Generic

- **Brand**: Original manufacturer drug
- **Generic**: Equivalent drug after patent expiration
- **Authorized Generic**: Brand drug sold as generic
- **Biosimilar**: Generic equivalent of biologic drug

## Utilization Management

### Prior Authorization (PA)

Required for:
- High-cost medications
- Specialty drugs
- Drugs with safety concerns
- Off-label use

PA Process:
1. Pharmacy submits claim → PA required reject
2. Prescriber submits PA request
3. Clinical review against criteria
4. Approval/Denial decision
5. If approved, claim can process

### Step Therapy

Common step protocols:
- Try generic before brand
- Try older drug before newer
- Try lower-cost therapeutic alternative

Example: Lipitor Step Therapy
```
Step 1: Simvastatin (generic)
Step 2: Atorvastatin (generic)
Step 3: Lipitor (brand) - if steps 1-2 fail
```

### Quantity Limits

| Drug Type | Typical Limit |
|-----------|---------------|
| Acute medications | 10-14 days |
| Maintenance drugs | 30-90 days |
| Controlled substances | 30 days |
| Specialty drugs | 30 days |

## Formulary Updates

### P&T Committee Review

Quarterly review considers:
- Clinical efficacy data
- Safety profile
- Cost-effectiveness
- Rebate agreements
- Market alternatives

### Changes

- **Addition**: New drug added to formulary
- **Deletion**: Drug removed from formulary
- **Tier Change**: Drug moved to different tier
- **UM Change**: New utilization management applied

## Example Formulary Entry

```yaml
drug:
  ndc: "00069015430"
  name: "Lipitor 10mg"
  gpi: "39400010100310"
  
coverage:
  status: "covered"
  tier: 3
  
utilization_management:
  prior_auth: false
  step_therapy: true
  quantity_limit:
    max_quantity: 30
    max_days_supply: 30
    
alternatives:
  - ndc: "00781506492"
    name: "Atorvastatin 10mg"
    tier: 1
```
