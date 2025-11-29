# Specialty Pharmacy

## Overview

Specialty pharmacy handles high-cost, complex medications requiring special handling, administration, or monitoring. These drugs typically treat chronic, complex, or rare conditions.

## Specialty Drug Characteristics

### Defining Features

| Characteristic | Description |
|----------------|-------------|
| Cost | >$600/month or >$10,000/year |
| Handling | Cold chain, hazardous, limited stability |
| Administration | Injectable, infusible, complex oral |
| Distribution | Limited distribution network |
| Monitoring | Requires clinical oversight |

### Common Categories

- Biologics (monoclonal antibodies)
- Oncology medications
- Autoimmune treatments
- Hepatitis C antivirals
- HIV antiretrovirals
- Multiple sclerosis drugs
- Growth hormones
- Hemophilia factors

## Specialty Pharmacy Services

### Hub Services

```yaml
enrollment:
  - Benefits verification
  - Prior authorization support
  - Financial assistance coordination
  - Patient consent/enrollment

clinical:
  - Medication therapy management
  - Adherence monitoring
  - Side effect management
  - Lab monitoring coordination

logistics:
  - Cold chain shipping
  - Delivery scheduling
  - Refill reminders
  - Supply management
```

### Patient Support Programs

| Service | Description |
|---------|-------------|
| Nurse Educators | Injection training, disease education |
| Care Coordinators | Navigate insurance, schedule shipments |
| Financial Counselors | Copay assistance, PAP enrollment |
| Clinical Pharmacists | Drug interactions, side effects |

## Limited Distribution Drugs (LDD)

### Distribution Networks

```
Exclusive Distribution:
  Drug → Single specialty pharmacy
  Example: Some oncology drugs
  
Limited Network:
  Drug → 2-5 specialty pharmacies
  Example: Hepatitis C treatments
  
Preferred Network:
  Drug → Multiple but restricted pharmacies
  Example: Many biologics
```

### REMS Programs

Risk Evaluation and Mitigation Strategies:
```yaml
rems_drug:
  name: "Thalomid (thalidomide)"
  program: "THALOMID REMS"
  requirements:
    prescriber: Certified, registered
    pharmacy: Certified, registered
    patient: 
      - Enrolled in program
      - Pregnancy tests (if applicable)
      - Informed consent signed
    dispensing:
      - Confirm authorization number
      - Maximum 28-day supply
      - No telephone prescriptions
```

## Specialty Billing

### Site of Care

| Site | Billing | Typical Drugs |
|------|---------|---------------|
| Pharmacy | Pharmacy benefit | Self-administered |
| Physician Office | Medical benefit | Office-administered |
| Infusion Center | Medical benefit | IV infusions |
| Home Infusion | Medical/Pharmacy | Home IV therapy |
| Hospital Outpatient | Medical benefit | Complex infusions |

### White Bagging vs Brown Bagging

```
White Bagging:
  Specialty pharmacy → Ships to physician office
  Physician administers
  Billed under pharmacy benefit
  
Brown Bagging:
  Specialty pharmacy → Ships to patient
  Patient brings to appointment
  Physician administers
  Billed under pharmacy benefit

Clear Bagging:
  Specialty pharmacy → Ships to physician office
  Pharmacy bills; physician administers
  Split billing arrangement
```

## Adherence & Outcomes

### Adherence Metrics

```yaml
metrics:
  pdc: # Proportion of Days Covered
    calculation: "Days with medication / Days in period"
    target: ">= 80%"
    
  mpr: # Medication Possession Ratio
    calculation: "Days supply dispensed / Days in period"
    target: ">= 80%"
    
  gap_days:
    calculation: "Days between fills - days supply"
    alert: "> 7 days"
```

### Outcomes Tracking

| Condition | Outcome Measure |
|-----------|-----------------|
| Rheumatoid Arthritis | DAS28 score, joint counts |
| Hepatitis C | SVR12 (viral cure) |
| Multiple Sclerosis | Relapse rate, MRI lesions |
| Oncology | Response rate, progression |
| Diabetes (GLP-1) | A1C reduction, weight |

## Cold Chain Management

### Temperature Requirements

| Category | Range | Examples |
|----------|-------|----------|
| Refrigerated | 2-8°C (36-46°F) | Biologics, insulins |
| Frozen | -25 to -10°C | Some vaccines |
| Controlled Room | 20-25°C (68-77°F) | Oral specialty |

### Shipping Requirements

```yaml
cold_chain_shipment:
  packaging:
    - Insulated container
    - Gel packs (frozen/refrigerated)
    - Temperature monitor
    
  shipping:
    - Overnight or 2-day maximum
    - Signature required
    - Weather monitoring
    
  alerts:
    - Temperature excursion notification
    - Delivery exception notification
    - Patient availability confirmation
```

## Specialty Drug Example

```yaml
drug:
  name: "Humira"
  generic: "adalimumab"
  ndc: "00074433902"
  
classification:
  specialty: true
  biologic: true
  self_administered: true
  
requirements:
  prior_auth: true
  specialty_pharmacy: true
  cold_chain: true
  
handling:
  storage: "Refrigerated 2-8°C"
  stability: "14 days at room temp"
  shipping: "Cold pack overnight"
  
support:
  hub: "AbbVie Patient Support"
  nurse_support: true
  copay_card: true
  
pricing:
  awp: 7500.00
  typical_copay: "20-30% with max"
  copay_assist_max: 6000.00
```
