# Pivot Sidebar User Guide

## Overview

The Pivot Sidebar allows you to create pivot tables by selecting:
1. **Index columns** (rows) - Groups your data by these columns
2. **Pivot columns** (columns) - Spreads values across columns
3. **Value columns** - The data to aggregate with functions like Sum, Mean, etc.

## UI Layout

```
┌─ Pivot Table Configuration ─────────────────────────┐
│                                                      │
│ Index (rows) - Select multiple with Space:          │
│ ┌────────────────────────────────────────┐          │
│ │ □ category                             │          │
│ │ □ region                               │          │
│ │ □ product                              │          │
│ │ □ sales                                │          │
│ │ □ quantity                             │          │
│ │ □ year                                 │          │
│ └────────────────────────────────────────┘          │
│                                                      │
│ Columns (spread) - Select multiple with Space:      │
│ ┌────────────────────────────────────────┐          │
│ │ □ category                             │          │
│ │ □ region                               │          │
│ │ □ product                              │          │
│ │ (same columns as above)                │          │
│ └────────────────────────────────────────┘          │
│                                                      │
│ Values & Aggregations:                              │
│ ┌─ Value #1 ─────────────────────────────┐          │
│ │ Column (click to select):              │          │
│ │ [Select value column ▼]                │          │
│ │                                        │          │
│ │ Aggregations (Space to toggle):        │          │
│ │ □ Count                                │          │
│ │ □ Sum                                  │          │
│ │ □ Mean                                 │          │
│ │ □ Min                                  │          │
│ │ □ Max                                  │          │
│ │ □ First                                │          │
│ │ □ Last                                 │          │
│ │ □ Len                                  │          │
│ │                                        │          │
│ │ [Remove Value]                         │          │
│ └────────────────────────────────────────┘          │
│                                                      │
│ [+ Add Value]                                        │
│                                                      │
│ [Apply] [Cancel]                                     │
└──────────────────────────────────────────────────────┘
```

## How to Use

### Navigation
- **Tab / Shift+Tab**: Move between fields
- **Up/Down arrows**: Navigate within lists
- **Space**: Toggle selection in SelectionLists
- **Enter**: Open dropdown / Confirm selection
- **Esc**: Cancel and close sidebar

### Step-by-Step Guide

#### 1. Select Index Columns (Rows)
- Navigate to the "Index (rows)" SelectionList
- Use **Up/Down** to highlight a column
- Press **Space** to toggle selection (✓ appears when selected)
- You can select multiple columns

**Example**: Select `category` to group rows by category

#### 2. Select Pivot Columns
- Navigate to the "Columns (spread)" SelectionList
- Use **Up/Down** and **Space** to select columns
- These columns will spread across your pivot table

**Example**: Select `region` to create columns for East, West, etc.

#### 3. Configure Values

##### Select a Column
- Navigate to "Column (click to select):" dropdown
- Press **Enter** to open the dropdown
- Use **Up/Down** to highlight a column
- Press **Enter** to select

**Example**: Select `sales`

##### Select Aggregations
- Navigate to the "Aggregations" SelectionList below
- Use **Up/Down** to highlight an aggregation function
- Press **Space** to toggle selection
- You can select multiple aggregations

**Example**: Select `Sum` and `Mean`

##### Add More Values (Optional)
- Click **[+ Add Value]** button to add another value column
- Each value can have different aggregations

**Example**: Add `quantity` with `Count` aggregation

#### 4. Apply
- Navigate to **[Apply]** button
- Press **Enter** to execute the pivot

## Example Workflow

### Simple Sales by Category and Region

**Scenario**: You have sales data and want to see total sales by category and region

**Configuration**:
- Index: `category`
- Columns: `region`
- Value #1: 
  - Column: `sales`
  - Aggregations: `Sum`

**Result**: 
```
category  | East | West
----------|------|------
A         | 220  | 200
B         | 150  | 430
```

### Advanced: Multiple Aggregations

**Configuration**:
- Index: `category`
- Columns: `region`
- Value #1:
  - Column: `sales`
  - Aggregations: `Sum`, `Mean`
- Value #2:
  - Column: `quantity`
  - Aggregations: `Count`

**Result**: Pivot table with columns like:
- `sales_sum_East`, `sales_sum_West`
- `sales_mean_East`, `sales_mean_West`
- `quantity_count_East`, `quantity_count_West`

### Multi-Index Example

**Configuration**:
- Index: `category`, `year` (multiple!)
- Columns: `region`
- Value #1:
  - Column: `sales`
  - Aggregations: `Sum`

**Result**: Rows grouped by both category AND year

## Troubleshooting

### "SelectionLists appear empty"
- Make sure the sidebar was opened with columns set
- Try closing and reopening the sidebar
- The lists should auto-populate when shown

### "Column dropdown is empty"
- Check that your dataset has loaded successfully
- Verify columns are available in the main table view

### "Nothing happens when I click Apply"
- Ensure you selected at least one Index column
- Ensure you selected at least one Pivot column
- Ensure you selected a Value column AND at least one aggregation

### "I see 'Column:<empty> Aggregation:<empty>'"
- The "Column:" is a **dropdown** - click it or press Enter to see options
- The "Aggregations:" is a **SelectionList** - should show 8 aggregation options
- If lists are empty, the sidebar may not have been initialized with columns

## Technical Notes

- SelectionLists allow multiple selections (checkbox-style UI)
- Select dropdowns allow single selection (classic dropdown)
- Pivot tables use Narwhals library under the hood
- Generated code is shown in the operations sidebar
