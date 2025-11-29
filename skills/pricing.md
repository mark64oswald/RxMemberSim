# Pharmacy Pricing Models

## Overview

Pharmacy pricing involves multiple components and benchmarks used to determine drug costs, reimbursement rates, and patient cost-sharing.

## Pricing Benchmarks

### AWP (Average Wholesale Price)

- Published benchmark price (often inflated)
- "Sticker price" - rarely reflects actual cost
- Used for reimbursement calculations
- AWP discounts common: AWP - 15% to AWP - 20%

### WAC (Wholesale Acquisition Cost)

- Manufacturer's list price to wholesalers
- More accurate than AWP
- Does not include rebates or discounts
- Typically 16-20% below AWP

### MAC (Maximum Allowable Cost)

- PBM-set ceiling price for generics
- Updated frequently (weekly/monthly)
- Based on market prices for multi-source drugs
- Pharmacies reimbursed at MAC regardless of acquisition cost

### NADAC (National Average Drug Acquisition Cost)

- CMS survey-based actual acquisition cost
- Used for Medicaid reimbursement
- Updated weekly
- Most accurate cost benchmark

## Reimbursement Formulas

### Brand Drugs

```
Reimbursement = AWP - Discount% + Dispensing Fee

Example:
AWP: $500.00
Discount: 15%
Dispensing Fee: $2.00

Reimbursement = $500 - $75 + $2 = $427.00
```

### Generic Drugs

```
Reimbursement = Lower of:
  - MAC + Dispensing Fee
  - AWP - Discount% + Dispensing Fee
  - U&C Price

Example:
MAC: $15.00
AWP: $100.00 (15% discount = $85.00)
U&C: $25.00
Dispensing Fee: $2.00

Reimbursement = $15 + $2 = $17.00 (MAC wins)
```

## Spread Pricing

### Traditional Model

```
Plan Pays PBM:     AWP - 15% + $2.00 = $87.00
PBM Pays Pharmacy: AWP - 17% + $1.50 = $84.50
PBM Spread:        $2.50 per claim
```

### Pass-Through Model

```
Plan Pays PBM:     Actual pharmacy payment + admin fee
PBM Pays Pharmacy: AWP - 17% + $1.50 = $84.50
PBM Fee:          $3.00 per claim
Plan Cost:        $87.50 (transparent)
```

## Rebates

### Manufacturer Rebates

Types:
- **Base Rebate**: Guaranteed % of WAC
- **Market Share Rebate**: Bonus for formulary position
- **Price Protection**: Protection against price increases
- **Admin Fees**: PBM administrative fees

Example:
```
Drug WAC: $1,000
Base Rebate: 25% = $250
Market Share Bonus: 5% = $50
Total Rebate: $300 per Rx
```

### Rebate Flow

```
1. Manufacturer → PBM (quarterly)
2. PBM retains admin fee (3-5%)
3. PBM → Plan Sponsor (pass-through or retained)
4. Rebates may reduce net plan cost
```

## Patient Cost-Sharing

### Copay Structure

| Tier | Copay | Description |
|------|-------|-------------|
| 1 | $10 | Preferred generic |
| 2 | $25 | Non-preferred generic |
| 3 | $50 | Preferred brand |
| 4 | $75 | Non-preferred brand |
| 5 | 25% | Specialty (with max) |

### Coinsurance

```
Drug Cost: $500
Coinsurance: 20%
Patient Pays: $100
Plan Pays: $400
```

### Deductible

```
Annual Deductible: $500
Claims YTD: $300
New Claim: $150

Patient Pays: $150 (toward deductible)
Remaining Deductible: $50
```

### Out-of-Pocket Maximum

```
OOPM: $3,000
YTD Patient Spend: $2,900
New Claim Copay: $200

Patient Pays: $100 (reaches OOPM)
Plan Pays: $100 (patient at max)
```

## Copay Assistance

### Manufacturer Copay Cards

```
Brand Drug Cost: $500
Plan Copay: $75
Copay Card Covers: $65
Patient Pays: $10

Note: $65 may not count toward deductible/OOPM
```

### Copay Accumulator Programs

Plan design to prevent copay card from counting:
```
Drug Cost: $500
Copay Card Pays: $75 → Does NOT apply to deductible
Patient True Spend: $0
Deductible Credit: $0
```

## Example Pricing Calculation

```yaml
claim:
  ndc: "00071015523"
  quantity: 30
  days_supply: 30
  
pricing_input:
  awp_unit: 15.50
  awp_total: 465.00
  mac_unit: 2.50
  mac_total: 75.00
  u_and_c: 125.00
  
calculation:
  ingredient_cost: 75.00  # MAC wins
  dispensing_fee: 2.00
  gross_amount: 77.00
  
member:
  tier: 1
  copay: 10.00
  deductible_remaining: 0.00
  
result:
  patient_pay: 10.00
  plan_pay: 67.00
  total_paid: 77.00
```
