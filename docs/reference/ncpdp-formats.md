# NCPDP Formats Reference

NCPDP transaction formats and codes used in RxMemberSim.

## Transaction Types

| Code | Type | Description |
|------|------|-------------|
| B1 | Billing | New prescription claim |
| B2 | Reversal | Cancel previous claim |
| B3 | Rebill | Resubmit with changes |
| E1 | Eligibility | Check member eligibility |
| P1 | PA Request | Submit prior auth |
| P2 | PA Inquiry | Check PA status |
| P4 | PA Cancel | Cancel PA request |

## Claim Segments

### Header Segment (Required)

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| BIN Number | 101-A1 | Bank ID Number | 610014 |
| Version/Release | 102-A2 | NCPDP version | D.0 |
| Transaction Code | 103-A3 | Transaction type | B1 |
| PCN | 104-A4 | Processor Control Number | RXTEST |
| Service Provider ID | 201-B1 | Pharmacy NPI | 9876543210 |
| Date of Service | 401-D1 | Service date | 20240115 |

### Patient Segment

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| Cardholder ID | 302-C2 | Member ID | MEM001 |
| Person Code | 303-C3 | Dependent code | 01 |
| Date of Birth | 304-C4 | DOB | 19700315 |
| Patient Gender | 305-C5 | Gender | M |
| Patient Location | 307-C7 | Location code | 01 |

### Insurance Segment

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| Group ID | 301-C1 | Group number | GRP001 |
| Cardholder First Name | 312-CC | First name | John |
| Cardholder Last Name | 313-CD | Last name | Smith |

### Claim Segment

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| Rx Number | 402-D2 | Prescription number | RX123456 |
| Fill Number | 403-D3 | Refill number | 1 |
| Days Supply | 405-D5 | Days supply | 30 |
| Compound Code | 406-D6 | Compound indicator | 1 |
| NDC | 407-D7 | National Drug Code | 00071015523 |
| DAW Code | 408-D8 | Dispense as written | 0 |
| Date Written | 414-DE | Rx date | 20240110 |
| Refills Authorized | 415-DF | Number of refills | 5 |
| Quantity Dispensed | 442-E7 | Quantity | 30 |

### Prescriber Segment

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| Prescriber ID | 411-DB | NPI | 1234567890 |
| Prescriber Last Name | 427-DR | Last name | Smith |
| Prescriber Phone | 498-PM | Phone | 5551234567 |

### Pricing Segment

| Field | Code | Description | Example |
|-------|------|-------------|---------|
| Ingredient Cost | 409-D9 | Drug cost | 15.00 |
| Dispensing Fee | 412-DC | Dispense fee | 2.00 |
| Patient Paid | 433-DX | Patient payment | 0.00 |
| U&C Charge | 426-DQ | Usual charge | 25.00 |
| Gross Amount Due | 430-DU | Total due | 17.00 |
| Basis of Cost | 423-DN | Cost basis | 01 |

## Response Codes

### Status Codes

| Code | Status | Description |
|------|--------|-------------|
| A | Accepted | Claim approved |
| R | Rejected | Claim denied |
| P | Paid | Paid with changes |
| D | Duplicate | Duplicate claim |

### Common Reject Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 70 | Product/Service Not Covered | Check formulary |
| 71 | Prescriber Not Covered | Verify prescriber |
| 72 | Pharmacy Not Covered | Check network |
| 75 | Prior Authorization Required | Submit PA |
| 76 | Plan Limitations Exceeded | Check quantity limits |
| 77 | Discontinued Drug | Use alternative |
| 78 | Cost Exceeds Maximum | Check pricing |
| 79 | Refill Too Soon | Wait for refill date |
| 88 | DUR Reject | Review DUR conflict |
| MR | M/I Prescriber ID | Verify NPI |
| NN | M/I Cardholder ID | Verify member ID |

## DAW Codes

| Code | Description |
|------|-------------|
| 0 | No product selection indicated |
| 1 | Substitution not allowed by prescriber |
| 2 | Patient requested brand |
| 3 | Pharmacist selected product |
| 4 | Generic not in stock |
| 5 | Brand dispensed as generic |
| 6 | Override |
| 7 | Brand mandated by law |
| 8 | Generic not available |
| 9 | Other |

## DUR Codes

### Reason for Service Codes

| Code | Description |
|------|-------------|
| DD | Drug-Drug Interaction |
| TD | Therapeutic Duplication |
| DA | Drug-Age Precaution |
| DG | Drug-Gender Precaution |
| ER | Early Refill |
| HD | High Dose |
| LD | Low Dose |
| DC | Drug-Disease |
| AL | Drug-Allergy |
| PG | Drug-Pregnancy |

### Professional Service Codes

| Code | Description |
|------|-------------|
| M0 | Prescriber consulted |
| P0 | Patient consulted |
| R0 | Pharmacist consulted other source |
| PH | Patient history obtained |
| DE | Deferred - will follow up |

### Result of Service Codes

| Code | Description |
|------|-------------|
| 1A | Filled as is (false positive) |
| 1B | Filled with different dose |
| 1C | Filled with different directions |
| 1D | Filled with different drug |
| 1E | Filled with different quantity |
| 2A | Not filled - Rx not ready |
| 2B | Not filled - patient request |
| 3A | Recommendation accepted |
| 3B | Recommendation not accepted |

## Example Transactions

### B1 Request (Billing)

```
BIN: 610014
PCN: RXTEST
Transaction: B1
Group: GRP001
Cardholder: MEM001
Person Code: 01
NDC: 00071015523
Quantity: 30
Days Supply: 30
DAW: 0
Prescriber NPI: 1234567890
Ingredient Cost: $15.00
Dispensing Fee: $2.00
```

### B1 Response (Approved)

```
Status: P (Paid)
Authorization: AUTH123456
Ingredient Cost Paid: $15.00
Dispensing Fee Paid: $2.00
Patient Pay: $10.00
Copay: $10.00
Deductible: $0.00
Total Paid: $7.00
```

### B1 Response (Rejected)

```
Status: R (Rejected)
Reject Code: 75
Reject Message: Prior Authorization Required
Additional Info: Submit PA for GLP-1 agonist
```

### B2 Request (Reversal)

```
BIN: 610014
PCN: RXTEST
Transaction: B2
Authorization Number: AUTH123456
Original Rx Number: RX123456
```

## NDC Format

11-digit National Drug Code: `AAAAA-BBBB-CC`

| Segment | Description | Example |
|---------|-------------|---------|
| AAAAA | Labeler code | 00071 (Pfizer) |
| BBBB | Product code | 0155 (Atorvastatin 10mg) |
| CC | Package code | 23 (90 count) |

## GPI Format

14-character Generic Product Identifier:

```
39400010000310
│││││││││││││└─ Form (10 = Tablet)
││││││││││└────── Strength (0003 = 10mg)
│││││└──────────── Drug (0010 = Atorvastatin)
│└───────────────── Subclass (40 = HMG-CoA)
└─────────────────── Class (39 = Antihyperlipidemic)
```