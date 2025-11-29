# Electronic Prior Authorization (ePA)

## Overview

Electronic Prior Authorization (ePA) is the electronic submission and processing of prior authorization requests, replacing fax-based workflows with real-time digital transactions.

## ePA Standards

### NCPDP SCRIPT Standard

```
Version: SCRIPT 2017071 (current)
Transaction Types:
  - PAInitiationRequest
  - PAInitiationResponse
  - PARequest
  - PAResponse
  - PAAppealRequest
  - PAAppealResponse
  - PACancelRequest
  - PACancelResponse
```

### CMS ePA Requirements

- Part D plans required to support ePA (2021)
- Real-time benefit check integration
- Question/answer workflow support
- Appeals process support

## ePA Workflow

### Initiation Flow

```
1. Prescriber sends Rx (NewRx)
   ↓
2. Pharmacy submits claim
   ↓
3. Claim rejects: "PA Required" (75)
   ↓
4. Pharmacy sends PAInitiationRequest
   ↓
5. PBM returns PAInitiationResponse
   - Questions for prescriber
   - Clinical criteria
   ↓
6. Prescriber completes questions in EHR
   ↓
7. PARequest submitted with answers
   ↓
8. PBM processes, returns PAResponse
   ↓
9. If approved: PA number issued
   ↓
10. Claim resubmitted, processes
```

### Real-Time Determination

```yaml
real_time_pa:
  eligibility: 
    - Auto-approve based on claims history
    - Member has diagnosis on file
    - Step therapy already completed
    
  auto_approval:
    response_time: "<30 seconds"
    no_questions: true
    pa_number: "Returned immediately"
    
  standard:
    response_time: "24-72 hours"
    questions: "Clinical criteria questions"
    review: "Clinical pharmacist review"
```

## Question Sets

### Question Structure

```yaml
question:
  id: "Q001"
  text: "Has the patient tried and failed metformin?"
  type: "boolean"
  required: true
  
question:
  id: "Q002"  
  text: "What is the patient's current A1C?"
  type: "numeric"
  required: true
  validation:
    min: 4.0
    max: 20.0
    
question:
  id: "Q003"
  text: "Select all diagnoses that apply:"
  type: "multi_select"
  required: true
  options:
    - code: "E11.9"
      text: "Type 2 diabetes without complications"
    - code: "E11.65"
      text: "Type 2 diabetes with hyperglycemia"
```

### Conditional Questions

```yaml
question:
  id: "Q004"
  text: "Why was metformin discontinued?"
  type: "single_select"
  required: true
  condition:
    question: "Q001"
    answer: true
  options:
    - "GI intolerance"
    - "Renal insufficiency"
    - "Lactic acidosis risk"
    - "Inadequate response"
```

## ePA Message Types

### PAInitiationRequest

```xml
<PAInitiationRequest>
  <Patient>
    <MemberID>MEM001</MemberID>
    <DateOfBirth>1965-03-15</DateOfBirth>
  </Patient>
  <Drug>
    <NDC>00169413512</NDC>
    <DrugName>Ozempic</DrugName>
    <Quantity>1</Quantity>
    <DaysSupply>28</DaysSupply>
  </Drug>
  <Prescriber>
    <NPI>1234567890</NPI>
    <Name>Dr. Smith</Name>
  </Prescriber>
</PAInitiationRequest>
```

### PAInitiationResponse

```xml
<PAInitiationResponse>
  <Status>PA_REQUIRED</Status>
  <PARequestID>EPA-2024-001234</PARequestID>
  <QuestionSet>
    <Question id="Q001">
      <Text>Has patient tried metformin?</Text>
      <Type>Boolean</Type>
    </Question>
    <Question id="Q002">
      <Text>Current A1C value?</Text>
      <Type>Numeric</Type>
    </Question>
  </QuestionSet>
  <Deadline>2024-01-20T23:59:59</Deadline>
</PAInitiationResponse>
```

### PARequest (with answers)

```xml
<PARequest>
  <PARequestID>EPA-2024-001234</PARequestID>
  <Answers>
    <Answer questionId="Q001">true</Answer>
    <Answer questionId="Q002">8.5</Answer>
  </Answers>
  <SupportingInfo>
    <Diagnosis>E11.65</Diagnosis>
    <ClinicalNotes>Patient failed metformin...</ClinicalNotes>
  </SupportingInfo>
</PARequest>
```

### PAResponse

```xml
<PAResponse>
  <PARequestID>EPA-2024-001234</PARequestID>
  <Decision>APPROVED</Decision>
  <PANumber>PA-2024-567890</PANumber>
  <EffectiveDate>2024-01-15</EffectiveDate>
  <ExpirationDate>2024-07-15</ExpirationDate>
  <ApprovedQuantity>1</ApprovedQuantity>
  <ApprovedDaysSupply>28</ApprovedDaysSupply>
</PAResponse>
```

## Integration Points

### EHR Integration

```
Prescriber Workflow:
1. E-prescribe from EHR
2. Real-time PA check
3. If PA needed: Questions appear in EHR
4. Prescriber answers questions
5. Submitted automatically
6. Response received in EHR
7. PA status visible in chart
```

### Pharmacy Integration

```
Pharmacy Workflow:
1. Receive Rx
2. Submit claim → PA reject
3. Initiate ePA from pharmacy system
4. Forward questions to prescriber
5. Track PA status
6. Receive approval notification
7. Resubmit claim with PA number
```

## ePA Status Tracking

| Status | Description |
|--------|-------------|
| INITIATED | Request started, awaiting questions |
| PENDING_PRESCRIBER | Questions sent, awaiting answers |
| SUBMITTED | Answers received, under review |
| APPROVED | PA granted |
| DENIED | PA not granted |
| CANCELLED | Request withdrawn |
| APPEALED | Under appeal |

## Performance Metrics

```yaml
epa_metrics:
  auto_approval_rate: "35-45%"
  avg_turnaround_time:
    auto: "<30 seconds"
    standard: "24-48 hours"
    complex: "48-72 hours"
  prescriber_response_rate: "85%"
  approval_rate: "75-85%"
  
comparison_to_fax:
  fax_turnaround: "3-5 days"
  epa_turnaround: "24-48 hours"
  improvement: "60-80% faster"
```
