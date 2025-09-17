# Test script for matching rules persistence
from models.matching_rules import MatchingRule, MatchingRulesManager

def test_matching_rules():
    manager = MatchingRulesManager()
    
    # Create a test rule
    rule = MatchingRule(
        name="Test Rule",
        description="A test rule for persistence",
        priority=75,
        conditions=["Amount Match", "Date Proximity"],
        actions=["Auto-Match", "Highlight"]
    )
    
    # Save the rule
    print("Saving rule...")
    if manager.save_rule(rule):
        print(f"Rule saved successfully with ID: {rule.id}")
    else:
        print("Failed to save rule")
        return
    
    # Load all rules
    print("Loading rules...")
    rules = manager.get_all_rules()
    print(f"Loaded {len(rules)} rules:")
    for r in rules:
        print(f"  - {r.name} (ID: {r.id}, Priority: {r.priority})")
        print(f"    Conditions: {r.conditions}")
        print(f"    Actions: {r.actions}")

if __name__ == "__main__":
    test_matching_rules()