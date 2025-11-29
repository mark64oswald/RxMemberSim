# NCPDP Telecommunications Standard

## Overview

NCPDP (National Council for Prescription Drug Programs) defines the standard format for pharmacy claim transactions. RxMemberSim implements NCPDP D.0 format.

## Transaction Types

| Code | Type | Description |
|------|------|-------------|
| B1 | Billing | New prescription claim |
| B2 | Reversal | Cancel previous claim |
| B3 | Rebill | Resubmit with changes |
| E1 | Eligibility | Check member eligibility |
| P1 | Prior Auth Request | Submit PA request |
| P2 | Prior Auth Inquiry | Check PA status |
| P4 | Prior Auth Cancel | Cancel PA request |

## Segment Structure

### Header Segment (Required)
- BIN Number (101-A1)
- Version/Release Number (102-A2)
- Transaction Code (103-A3)
- Processor Control Number (104-A4)
- Service Provider ID (201-B1)
- Date of Service (401-D1)

### Patient Segment
- Cardholder ID (302-C2)
- Date of Birth (304-C4)
- Patient Gender Code (305-C5)
- Patient Location (307-C7)
- Person Code (303-C3)

### Insurance Segment
- Group ID (301-C1)
- Cardholder First Name (312-CC)
- Cardholder Last Name (313-CD)

### Claim Segment
- Prescription/Service Reference Number (402-D2)
- Product/Service ID (407-D7) - NDC
- Quantity Dispensed (442-E7)
- Days Supply (405-D5)
- Compound Code (406-D6)
- DAW Code (408-D8)
- Date Written (414-DE)
- Number of Refills Authorized (415-DF)
- Fill Number (403-D3)

### Prescriber Segment
- Prescriber ID (411-DB) - NPI
- Prescriber Last Name (427-DR)
- Prescriber Phone Number (498-PM)

### Pricing Segment
- Ingredient Cost Submitted (409-D9)
- Dispensing Fee Submitted (412-DC)
- Patient Paid Amount Submitted (433-DX)
- Usual and Customary Charge (426-DQ)
- Gross Amount Due (430-DU)
- Basis of Cost Determination (423-DN)

## Response Codes

### Status Codes
- **A** - Accepted/Approved
- **R** - Rejected
- **P** - Paid (with changes)
- **D** - Duplicate

### Common Reject Codes

```
70 - Product/Service Not Covered
75 - Prior Authorization Required
76 - Plan Limitations Exceeded
79 - Refill Too Soon
88 - DUR Reject
MR - M/I Prescriber ID
NN - M/I Cardholder ID
```

## DUR Response Codes

### Reason for Service Codes
- **TD** - Therapeutic Duplication
- **DD** - Drug-Drug Interaction
- **DA** - Drug-Age Precaution
- **DG** - Drug-Gender Precaution
- **ER** - Early Refill
- **HD** - High Dose
- **LD** - Low Dose

### Professional Service Codes
- **M0** - Prescriber Consulted
- **P0** - Patient Consulted
- **R0** - Pharmacist Consulted Other Source
- **DE** - Deferred Action

### Result of Service Codes
- **1A** - Filled as Is
- **1B** - Filled with Different Dose
- **1C** - Filled with Different Directions
- **1D** - Filled with Different Drug
- **1E** - Filled with Different Quantity
- **2A** - Not Filled, Rx Not Ready
- **2B** - Not Filled, Patient Request

## Example B1 Request

```
BIN: 610014
PCN: RXTEST
Transaction: B1 (Billing)
Group: TESTGRP
Member: MEM001
Person Code: 01
NDC: 00071015523
Quantity: 30
Days Supply: 30
Prescriber NPI: 1234567890
Ingredient Cost: $100.00
Dispensing Fee: $2.00
```
