"""
Quick test to verify the XML builder correctly handles multiple actions
"""

from dinapy.ena.mappers.xml_builder.submission import build_submission_xml_from_model

# Test 1: Single action (string)
print("Test 1: Single action string")
print("-" * 50)
xml1 = build_submission_xml_from_model(
    submission_alias="test_single",
    action="ADD"
)
print(xml1)
print()

# Test 2: Multiple actions (list of strings with shared hold_until_date)
print("Test 2: Multiple actions with shared hold date")
print("-" * 50)
xml2 = build_submission_xml_from_model(
    submission_alias="test_multi_shared",
    action=["ADD", "HOLD"],
    hold_until_date="2025-12-31"
)
print(xml2)
print()

# Test 3: Multiple actions (list of dicts with specific attributes)
print("Test 3: Multiple actions with specific attributes")
print("-" * 50)
xml3 = build_submission_xml_from_model(
    submission_alias="test_multi_dict",
    action=[
        {"type": "ADD"},
        {"type": "HOLD", "HoldUntilDate": "2025-12-31"}
    ]
)
print(xml3)
print()

# Test 4: RELEASE action with target
print("Test 4: RELEASE action with target accession")
print("-" * 50)
xml4 = build_submission_xml_from_model(
    submission_alias="test_release",
    action=[{"type": "RELEASE", "target": "PRJEB12345"}]
)
print(xml4)
print()

print("✓ All tests generated XML successfully!")
