# Pharmacy Benefits Domain Knowledge

## Overview

Pharmacy Benefits Management (PBM) is a specialized segment of healthcare that manages prescription drug programs. This skill provides essential domain knowledge for working with RxMemberSim.

## Key Entities

### Members
- **Member ID**: Unique identifier for the patient/subscriber
- **Cardholder ID**: ID printed on the pharmacy card
- **Person Code**: Distinguishes subscriber (01) from dependents (02, 03, etc.)
- **Group Number**: Employer or plan group identifier

### Pharmacy Identifiers
- **BIN (Bank Identification Number)**: 6-digit routing number for claim submission
- **PCN (Processor Control Number)**: Secondary routing identifier
- **NPI (National Provider Identifier)**: 10-digit pharmacy/prescriber identifier

### Drug Identifiers
- **NDC (National Drug Code)**: 11-digit drug identifier (5-4-2 format: labeler-product-package)
- **GPI (Generic Product Identifier)**: 14-digit therapeutic classification
- **GCN (Generic Code Number)**: Links equivalent drug products

## Claims Processing Flow

```
1. Pharmacy submits claim → PBM receives
2. Eligibility check → Member active?
3. Formulary check → Drug covered?
4. DUR check → Drug safe for patient?
5. Pricing calculation → Apply copay/coinsurance
6. Adjudication → Approve/reject claim
7. Response to pharmacy
```

## Common Reject Codes

| Code | Meaning |
|------|---------|
| 70 | Product/Service Not Covered |
| 75 | Prior Authorization Required |
| 76 | Plan Limitations Exceeded |
| 79 | Refill Too Soon |
| 88 | DUR Reject |

## Pricing Terminology

- **AWP (Average Wholesale Price)**: Benchmark drug price
- **WAC (Wholesale Acquisition Cost)**: Manufacturer list price
- **MAC (Maximum Allowable Cost)**: Generic pricing limit
- **U&C (Usual and Customary)**: Pharmacy's retail price
- **Ingredient Cost**: Drug acquisition cost
- **Dispensing Fee**: Pharmacy service fee
- **Copay**: Fixed member payment
- **Coinsurance**: Percentage member payment
- **Deductible**: Annual amount before coverage begins

## Plan Design Elements

### Tiers
- **Tier 1**: Generic drugs (lowest copay)
- **Tier 2**: Preferred brand (moderate copay)
- **Tier 3**: Non-preferred brand (higher copay)
- **Tier 4**: Specialty drugs (highest copay/coinsurance)

### Quantity Limits
- **Days Supply**: Maximum days per fill (30, 90)
- **Quantity per Fill**: Maximum units dispensed
- **Fills per Period**: Annual fill limits

### Coverage Rules
- **Step Therapy**: Try generic before brand
- **Prior Authorization**: Pre-approval required
- **Age Limits**: Coverage restricted by age
- **Gender Limits**: Coverage based on gender
