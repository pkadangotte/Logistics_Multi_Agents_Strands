"""
Approver Data Module
Contains approval thresholds and workflow data definitions.
"""

import pandas as pd

# Approval thresholds data
approval_thresholds = {
    "low_value": {"max_cost": 1000, "auto_approve": True},
    "medium_value": {"max_cost": 5000, "requires_manager": True},
    "high_value": {"max_cost": 999999, "requires_director": True}
}


def get_approval_dataframe():
    """Initialize and return approval thresholds DataFrame."""
    approval_df = pd.DataFrame.from_dict(approval_thresholds, orient='index')
    print(f"✅ Approval Thresholds DataFrame loaded with shape: {approval_df.shape}")
    return approval_df


def demo_approval_access(approval_df):
    """Demonstrate approval data access examples."""
    print("🔍 APPROVAL DATA ACCESS EXAMPLES:")
    print("=" * 38)

    # Show all approval levels
    print("1. Approval levels and thresholds:")
    for level in approval_df.index:
        max_cost = approval_df.loc[level, 'max_cost']
        print(f"   - {level}: Up to ${max_cost:,}")
        
        # Show approval requirements
        if 'auto_approve' in approval_df.columns and approval_df.loc[level, 'auto_approve']:
            print(f"     → Auto-approved")
        elif 'requires_manager' in approval_df.columns and approval_df.loc[level, 'requires_manager']:
            print(f"     → Requires manager approval")
        elif 'requires_director' in approval_df.columns and approval_df.loc[level, 'requires_director']:
            print(f"     → Requires director approval")

    # Test approval scenarios
    print("\n2. Sample approval scenarios:")
    test_costs = [500, 3000, 15000]
    
    for cost in test_costs:
        approval_level = determine_approval_level(cost, approval_df)
        print(f"   - Cost ${cost:,}: {approval_level} level")

    print("\n✅ Approval DataFrame is ready for use!")


def determine_approval_level(cost, approval_df):
    """Determine the approval level required for a given cost."""
    for level in approval_df.index:
        max_cost = approval_df.loc[level, 'max_cost']
        if cost <= max_cost:
            return level
    return "exceeds_limits"


if __name__ == "__main__":
    # Test approval data when run directly
    approval_df = get_approval_dataframe()
    demo_approval_access(approval_df)