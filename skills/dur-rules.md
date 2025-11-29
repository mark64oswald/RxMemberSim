# Drug Utilization Review (DUR) Rules

## Overview

Drug Utilization Review (DUR) is a system of ongoing, criteria-based drug therapy evaluation to ensure patient safety and appropriate medication use.

## DUR Categories

### Prospective DUR (Pro-DUR)

Real-time checks at point of sale:

| Check Type | Code | Description |
|------------|------|-------------|
| Drug-Drug Interaction | DD | Interaction between medications |
| Therapeutic Duplication | TD | Multiple drugs in same class |
| Drug-Age | DA | Age-inappropriate medication |
| Drug-Gender | DG | Gender-specific contraindication |
| Drug-Disease | DC | Contraindicated for condition |
| Drug-Allergy | AL | Patient allergy alert |
| Early Refill | ER | Refill too soon |
| High Dose | HD | Exceeds maximum dose |
| Low Dose | LD | Below therapeutic dose |
| Drug-Pregnancy | PG | Pregnancy category concern |

### Severity Levels

| Level | Code | Action |
|-------|------|--------|
| 1 | Severe | Hard reject - cannot override |
| 2 | Serious | Soft reject - requires intervention |
| 3 | Moderate | Warning - pharmacist review |
| 4 | Minor | Information only |

## Drug-Drug Interactions

### Severity Classifications

```
Level 1 - Contraindicated
  Example: MAOIs + SSRIs (serotonin syndrome)
  
Level 2 - Major
  Example: Warfarin + NSAIDs (bleeding risk)
  
Level 3 - Moderate  
  Example: Statins + Grapefruit (increased levels)
  
Level 4 - Minor
  Example: Multivitamins + Tetracyclines (reduced absorption)
```

### Common Interactions

| Drug A | Drug B | Effect |
|--------|--------|--------|
| Warfarin | Aspirin | Increased bleeding |
| Metformin | Contrast dye | Lactic acidosis |
| Simvastatin | Amiodarone | Myopathy |
| Lisinopril | Potassium | Hyperkalemia |
| Fluoxetine | Tramadol | Seizure risk |

## Therapeutic Duplication

### Same Drug Class Rules

```
Class: HMG-CoA Reductase Inhibitors (Statins)
  - Only ONE statin allowed concurrently
  - Reject if: atorvastatin + rosuvastatin
  
Class: ACE Inhibitors
  - Only ONE ACE inhibitor allowed
  - Reject if: lisinopril + benazepril
  
Class: Proton Pump Inhibitors
  - Only ONE PPI allowed
  - Reject if: omeprazole + pantoprazole
```

## Early Refill Prevention

### Standard Rules

| Days Supply | Minimum Days Before Refill |
|-------------|---------------------------|
| 30 days | Day 23 (75% through) |
| 60 days | Day 48 (80% through) |
| 90 days | Day 75 (83% through) |

### Override Reasons

- **Vacation Supply**: Travel requiring early fill
- **Lost/Stolen**: Police report may be required
- **Therapy Change**: Dose or drug change
- **Disaster**: Emergency situation

### Controlled Substance Rules

Schedule II substances:
- No early refill allowed
- Maximum 30-day supply
- No refills - new Rx required
- Must verify with PMP

## Dose Checking

### High Dose Alerts

```yaml
drug: metformin
max_daily_dose: 2550mg
alert_threshold: 2000mg  # 78% of max

drug: lisinopril
max_daily_dose: 80mg
alert_threshold: 60mg

drug: atorvastatin  
max_daily_dose: 80mg
alert_threshold: 80mg
high_dose_warning: true  # FDA warning for 80mg
```

### Pediatric Dose Limits

Weight-based calculations:
```
amoxicillin: 25-45 mg/kg/day
ibuprofen: 10 mg/kg every 6-8 hours
acetaminophen: 15 mg/kg every 4-6 hours
```

## DUR Response Handling

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
| 1A | Filled as is, false positive |
| 1B | Filled, different dose |
| 1C | Filled, different directions |
| 1D | Filled, different drug |
| 1E | Filled, different quantity |
| 2A | Not filled, Rx not ready |
| 2B | Not filled, patient request |
| 3A | Recommendation accepted |
| 3B | Recommendation not accepted |

## Example DUR Check

```python
# Input
patient_medications = ["lisinopril 10mg", "metformin 1000mg"]
new_drug = "spironolactone 25mg"
patient_age = 68

# DUR Checks Performed
1. Drug-Drug: lisinopril + spironolactone
   Result: ALERT - Hyperkalemia risk (Level 2)
   
2. Therapeutic Duplication: None found
   Result: PASS
   
3. Drug-Age: spironolactone for age 68
   Result: PASS (monitor potassium in elderly)
   
4. High Dose Check: 25mg within limits
   Result: PASS

# Final Result
Status: SOFT_REJECT
Reason: DD - Drug-Drug Interaction
Message: "Hyperkalemia risk with ACE inhibitor + potassium-sparing diuretic"
Override: Allowed with intervention code
```
