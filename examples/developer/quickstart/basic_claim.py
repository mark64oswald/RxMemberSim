"""Basic pharmacy claim example."""
from datetime import date
from decimal import Decimal

from rxmembersim.claims.adjudication import AdjudicationEngine
from rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.formulary.formulary import FormularyGenerator


def main():
    print("=== RxMemberSim Basic Example ===\n")

    # Generate a member
    member_gen = RxMemberGenerator()
    member = member_gen.generate(bin="610014", pcn="RXTEST", group_number="GRP001")
    print(f"Generated member: {member.member_id}")
    print(f"  BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")
    print(f"  Name: {member.demographics.first_name} {member.demographics.last_name}")
    print(f"  Deductible remaining: ${member.accumulators.deductible_remaining}")

    # Create a claim
    claim = PharmacyClaim(
        claim_id="CLM001",
        transaction_code=TransactionCode.BILLING,
        service_date=date.today(),
        pharmacy_npi="9876543210",
        member_id=member.member_id,
        cardholder_id=member.cardholder_id,
        person_code=member.person_code,
        bin=member.bin,
        pcn=member.pcn,
        group_number=member.group_number,
        prescription_number="RX123456",
        fill_number=1,
        ndc="00071015523",  # Atorvastatin
        quantity_dispensed=Decimal("30"),
        days_supply=30,
        daw_code="0",
        prescriber_npi="1234567890",
        ingredient_cost_submitted=Decimal("15.00"),
        dispensing_fee_submitted=Decimal("2.00"),
        patient_paid_submitted=Decimal("0.00"),
        usual_customary_charge=Decimal("25.00"),
        gross_amount_due=Decimal("17.00"),
    )
    print(f"\nClaim created: {claim.claim_id}")
    print(f"  Drug NDC: {claim.ndc}")
    print(f"  Quantity: {claim.quantity_dispensed}")
    print(f"  Days supply: {claim.days_supply}")

    # Adjudicate
    formulary = FormularyGenerator().generate_standard_commercial()
    engine = AdjudicationEngine(formulary=formulary)
    response = engine.adjudicate(claim, member)

    print(f"\nAdjudication result:")
    print(f"  Status: {response.response_status}")
    if response.response_status == "P":
        print(f"  Authorization: {response.authorization_number}")
        print(f"  Plan pays: ${response.total_amount_paid}")
        print(f"  Patient pays: ${response.patient_pay_amount}")
        print(f"  Copay: ${response.copay_amount}")
        print(f"  Deductible applied: ${response.deductible_amount}")
    else:
        for reject in response.reject_codes:
            print(f"  Reject: {reject.code} - {reject.description}")


if __name__ == "__main__":
    main()
