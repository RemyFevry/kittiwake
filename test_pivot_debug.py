#!/usr/bin/env python3
"""Debug test - print what should be in the sidebar."""

from kittiwake.widgets.sidebars.pivot_sidebar import PivotSidebar, ValueAggregationSection

# Test data
test_columns = ["category", "region", "product", "sales", "quantity", "year"]

print("="*60)
print("PIVOT SIDEBAR DEBUG INFO")
print("="*60)

# Create sidebar
sidebar = PivotSidebar(columns=test_columns)
print(f"\n1. Sidebar created with {len(sidebar.columns)} columns:")
for col in sidebar.columns:
    print(f"   - {col}")

print(f"\n2. ValueAggregationSection available aggregations:")
for func_id, func_label in ValueAggregationSection.AGG_FUNCTIONS:
    print(f"   - {func_label} ({func_id})")

print("\n3. Expected UI structure:")
print("""
   Pivot Table Configuration
   ─────────────────────────────
   
   Index (rows) - Select multiple:
   ┌─ SelectionList (height: 8) ─┐
   │ □ category                  │
   │ □ region                    │
   │ □ product                   │
   │ □ sales                     │
   │ □ quantity                  │
   │ □ year                      │
   └─────────────────────────────┘
   
   Columns (spread) - Select multiple:
   ┌─ SelectionList (height: 8) ─┐
   │ □ category                  │
   │ □ region                    │
   │ □ product                   │
   │ □ sales                     │
   │ □ quantity                  │
   │ □ year                      │
   └─────────────────────────────┘
   
   Values & Aggregations:
   ┌─ Value #1 ──────────────────┐
   │ Column: [Select dropdown ▼] │
   │                             │
   │ Aggregations:               │
   │ □ Count                     │
   │ □ Sum                       │
   │ □ Mean                      │
   │ □ Min                       │
   │ □ Max                       │
   │ □ First                     │
   │ □ Last                      │
   │ □ Len                       │
   │                             │
   │ [Remove Value]              │
   └─────────────────────────────┘
   
   [+ Add Value]
   
   [Apply] [Cancel]
""")

print("\n4. How to use:")
print("   • Use Tab/Shift+Tab to navigate between fields")
print("   • In SelectionLists: Use Space to toggle selection, Up/Down to move")
print("   • In Select dropdown: Use Enter to open, Up/Down to select, Enter to confirm")
print("   • Click '+ Add Value' to add more value columns")
print("   • Click 'Apply' when done")

print("\n5. Example configuration:")
print("   Index: Select 'category' (creates rows grouped by category)")
print("   Columns: Select 'region' (spreads data across East/West columns)")
print("   Value #1:")
print("     Column: 'sales'")
print("     Aggregations: Select 'Sum' and 'Mean'")
print("   Result: Shows sum and mean of sales by category and region")

print("\n" + "="*60)
