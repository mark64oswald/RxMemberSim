"""Interactive RxMemberSim demo."""
from datetime import date

from rxmembersim.core.member import RxMemberGenerator
from rxmembersim.dur.validator import DURValidator
from rxmembersim.formulary.formulary import FormularyGenerator
from rxmembersim.scenarios.engine import RxScenarioEngine


def print_header(title: str):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def demo_member_generation():
    print_header("MEMBER GENERATION")
    generator = RxMemberGenerator()
    member = generator.generate(bin="610014", pcn="DEMO", group_number="DEMO001")
    print(f"Member ID: {member.member_id}")
    print(f"BIN/PCN/Group: {member.bin}/{member.pcn}/{member.group_number}")
    print(f"Name: {member.demographics.first_name} {member.demographics.last_name}")
    print(f"DOB: {member.demographics.date_of_birth}")
    print(f"Deductible remaining: ${member.accumulators.deductible_remaining}")
    print(f"OOP remaining: ${member.accumulators.oop_remaining}")
    return member


def demo_formulary_check():
    print_header("FORMULARY CHECK")
    formulary = FormularyGenerator().generate_standard_commercial()

    drugs_to_check = [
        ("00071015523", "Atorvastatin 10mg (generic statin)"),
        ("00169413512", "Ozempic 0.5mg (brand GLP-1)"),
        ("99999999999", "Unknown drug"),
    ]

    for ndc, desc in drugs_to_check:
        status = formulary.check_coverage(ndc)
        print(f"\n{desc}:")
        print(f"  NDC: {ndc}")
        print(f"  Covered: {status.covered}")
        if status.covered:
            print(f"  Tier: {status.tier} ({status.tier_name})")
            print(f"  Requires PA: {status.requires_pa}")
            if status.copay:
                print(f"  Copay: ${status.copay}")
            if status.coinsurance:
                print(f"  Coinsurance: {status.coinsurance}%")
        else:
            print(f"  Message: {status.message}")


def demo_dur_check():
    print_header("DUR CHECK")
    validator = DURValidator()

    print("\nScenario 1: New prescription with no interactions")
    result = validator.validate_simple(
        ndc="00071015523",
        gpi="39400010000310",
        drug_name="Atorvastatin 10mg",
        member_id="DEMO001",
        service_date=date.today(),
        current_medications=[],
        patient_age=55,
        patient_gender="M",
    )
    print(f"  DUR Passed: {result.passed}")
    print(f"  Alerts: {result.total_alerts}")

    print("\nScenario 2: Warfarin with existing NSAID (interaction)")
    result = validator.validate_simple(
        ndc="00056017270",
        gpi="83300010000330",  # Warfarin
        drug_name="Warfarin 5mg",
        member_id="DEMO001",
        service_date=date.today(),
        current_medications=[
            {
                "ndc": "00904515260",
                "gpi": "66100010000310",  # Ibuprofen (NSAID)
                "name": "Ibuprofen 200mg",
            }
        ],
        patient_age=65,
        patient_gender="F",
    )
    print(f"  DUR Passed: {result.passed}")
    print(f"  Alerts: {result.total_alerts}")
    for alert in result.alerts:
        print(f"    - {alert.alert_type.value}: {alert.message}")
        print(f"      Severity: Level {alert.clinical_significance.value}")


def demo_scenario():
    print_header("SCENARIO EXECUTION")
    engine = RxScenarioEngine()

    print("Available scenarios:")
    scenarios = engine.list_scenarios()
    for scenario in scenarios[:5]:  # Show first 5
        print(f"  - {scenario.scenario_id}: {scenario.scenario_name}")

    # Run new therapy approved scenario
    print("\nRunning 'New Therapy Approved' scenario...")
    scenario = engine.new_therapy_approved()
    timeline = engine.execute_scenario(scenario, "DEMO-MEM-001")

    print(f"\nTimeline ({len(timeline.events)} events):")
    for event in timeline.events:
        day_offset = (event.event_date - date.today()).days
        print(f"  Day {day_offset:+3d}: {event.event_type.value}")
        if event.data:
            for key, value in list(event.data.items())[:2]:
                print(f"          {key}: {value}")


def main():
    print("\n" + "=" * 50)
    print("       RxMemberSim Interactive Demo")
    print("=" * 50)

    demo_member_generation()
    demo_formulary_check()
    demo_dur_check()
    demo_scenario()

    print("\n" + "=" * 50)
    print("  Demo complete!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
