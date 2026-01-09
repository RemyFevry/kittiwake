# Data Model: Column Type Display and Quick Filter

**Feature**: 002-column-type-display  
**Date**: 2026-01-09  
**Status**: Complete

This document defines the data entities and relationships for column type visualization and quick filtering functionality.

## Overview

This feature adds visual type indicators to column headers and enables quick filtering by clicking headers. It does NOT introduce new persistent data models - instead, it extends existing models with type detection and styling logic.

## Core Entities

### 1. ColumnTypeMapping (Configuration Entity)

**Purpose**: Maps narwhals data types to visual representation (color, icon) and available filter operators.

**Attributes**:
- `type_category`: str - Visual category identifier
  - Valid values: `"numeric"`, `"text"`, `"date"`, `"boolean"`, `"unknown"`
  - Determined by type detection logic based on narwhals dtype
- `narwhals_dtypes`: list[str] - Narwhals dtype names that map to this category
  - Examples: `["Int64", "Float64"]` for numeric, `["String", "Categorical"]` for text
- `color_variable`: str - Textual CSS variable name for this type
  - Format: `"$semantic-name"` (e.g., `"$primary"`, `"$success"`)
- `icon_ascii`: str - ASCII character representing this type
  - Single character, printable ASCII range (32-126)
  - Examples: `"#"` for numeric, `"\""` for text
- `icon_unicode`: str - Unicode character fallback for enhanced terminals
  - Single character, Unicode emoji or symbol
  - Examples: `"🔢"` for numeric, `"📝"` for text
- `filter_operators`: list[str] - Available filter operators for this type
  - Examples: `[">", "<", ">=", "<=", "=", "!="]` for numeric

**Relationships**:
- One ColumnTypeMapping per `type_category` (5 total)
- Each Dataset column schema entry maps to exactly one ColumnTypeMapping
- Referenced by ColumnHeader when rendering

**Storage**: Defined as Python constants in `src/kittiwake/utils/type_colors.py`, validated against JSON schema in `contracts/type-mappings.json`

**Lifecycle**: Static configuration, loaded once at application start

---

### 2. ColumnHeader (Logical Entity - Extension of DataTable Column)

**Purpose**: Represents a table column header with type-aware styling and click handling.

**Attributes**:
- `column_name`: str - Column name from `Dataset.schema.keys()`
- `dtype`: str - Narwhals dtype string from `Dataset.schema.values()`
- `type_category`: str - Visual category (from ColumnTypeMapping)
  - Computed via `detect_column_type_category(dtype)`
- `display_text`: Rich Text - Styled header text with icon and color
  - Format: `"{icon} {column_name}\n({dtype})"`
  - Example: `"# Age\n(Int64)"` with blue color styling
- `is_clickable`: bool - Whether header triggers quick filter
  - Always `True` in this feature
- `column_key`: str - Unique identifier for DataTable column
  - Same as `column_name`

**Relationships**:
- Belongs to one `DatasetTable` widget
- References one `Dataset` (via parent DatasetTable)
- References one `ColumnTypeMapping` (via `type_category`)
- Triggers one `ColumnHeaderQuickFilter` on click event

**Storage**: Ephemeral - created during `DatasetTable.load_dataset()`, destroyed when table reloads

**Lifecycle**: 
1. Created when dataset loaded into DatasetTable
2. Rendered as Rich Text header in DataTable widget
3. Click event triggers `ColumnHeaderQuickFilter` modal
4. Destroyed when dataset changes or table reloaded

---

### 3. ColumnHeaderQuickFilter (UI Widget Entity)

**Purpose**: Modal interface for creating filters directly from column header clicks.

**Attributes**:
- `selected_column`: str - Pre-selected column name (from clicked header)
  - Read-only in UI (cannot be changed by user)
- `dtype`: str - Column's narwhals dtype
- `type_category`: str - Visual category (determines available operators)
- `available_operators`: list[str] - Operators for this type
  - Filtered from ColumnTypeMapping based on `type_category`
  - Example: `[">", "<", ">=", "<=", "=", "!="]` for numeric types
- `selected_operator`: str - User-selected operator
  - Default: First operator in `available_operators`
- `filter_value`: str - User-entered value to filter by
  - Validation rules based on `type_category` (numeric, date format, etc.)
- `callback`: callable - Function to receive created Operation
  - Signature: `(operation: Operation) -> None`
- `dataset`: Dataset - Reference to active dataset (for context)

**Relationships**:
- Created by `DatasetTable` on `ColumnSelected` event
- References parent `Dataset` (read-only)
- Produces one `Operation` object on submit
- Returns Operation to `MainScreen` via callback

**Storage**: Ephemeral - created on header click, destroyed on submit or cancel

**Lifecycle**:
1. Created when user clicks column header
2. Pre-populated with column name and type-specific operators
3. User selects operator and enters value
4. On submit: Creates Operation object, invokes callback, closes modal
5. On cancel: Closes modal without creating Operation

---

### 4. Operation (Existing Entity - Reused)

**Purpose**: Represents a data transformation operation (filter, search, etc.). This feature reuses the existing Operation model without modifications.

**Attributes** (relevant to this feature):
- `code`: str - Narwhals filter expression
  - Example: `"df = df.filter(nw.col('Age') > 30)"`
- `display`: str - Human-readable description
  - Example: `"Filter: Age > 30"`
- `operation_type`: str - Always `"filter"` for quick filters
- `params`: dict - Filter parameters
  - Keys: `"column"`, `"operator"`, `"value"`
  - Example: `{"column": "Age", "operator": ">", "value": "30"}`
- `state`: str - Execution state
  - Values: `"queued"`, `"executed"`, `"failed"`
  - Determined by Dataset.execution_mode

**Relationships**:
- Created by `ColumnHeaderQuickFilter` widget
- Added to `Dataset.queued_operations` or `Dataset.executed_operations`
- Displayed in `OperationsSidebar` with state indicators
- Undoable/redoable via `Dataset.undo()` / `Dataset.redo()`

**Storage**: In-memory in Dataset object, persisted in DuckDB for SavedAnalysis

**Lifecycle**: Same as existing Operation lifecycle (no changes)

---

## Entity Relationships Diagram

```text
┌─────────────────────────┐
│  Dataset                │
│  ├── schema: dict       │  1:N
│  ├── queued_operations  ├──────┐
│  └── executed_operations│      │
└────────┬────────────────┘      │
         │ 1:N                   │
         │                       │
         ▼                       ▼
┌─────────────────────────┐   ┌──────────────────────┐
│  ColumnHeader           │   │  Operation           │
│  ├── column_name        │   │  ├── code            │
│  ├── dtype              │   │  ├── display         │
│  ├── type_category ────┼───┤  ├── operation_type  │
│  └── display_text       │   │  ├── params          │
└────────┬────────────────┘   │  └── state           │
         │                    └──────────────────────┘
         │ click                        ▲
         ▼                              │ creates
┌─────────────────────────┐             │
│  ColumnHeaderQuickFilter│─────────────┘
│  ├── selected_column    │
│  ├── type_category      │
│  ├── available_operators│
│  └── filter_value       │
└────────┬────────────────┘
         │ references
         ▼
┌─────────────────────────┐
│  ColumnTypeMapping      │  (Static Config)
│  ├── type_category      │
│  ├── narwhals_dtypes    │
│  ├── color_variable     │
│  ├── icon_ascii         │
│  ├── icon_unicode       │
│  └── filter_operators   │
└─────────────────────────┘
```

## Data Flows

### Flow 1: Dataset Load with Type Display

1. User loads dataset → `Dataset` object created with `schema` dict
2. `DatasetTable.load_dataset()` called
3. For each column in schema:
   a. Extract dtype string
   b. Call `detect_column_type_category(dtype)` → get type_category
   c. Lookup ColumnTypeMapping for type_category
   d. Create Rich Text header with color and icon
   e. Add column to DataTable with styled header
4. User sees colored column headers with type icons

**Data accessed**: `Dataset.schema`, `ColumnTypeMapping` constants

**Performance**: O(N) where N = number of columns, <1ms for 100 columns

---

### Flow 2: Quick Filter Creation

1. User clicks column header (or focuses + Enter)
2. DataTable fires `ColumnSelected` event with `column_key`
3. `DatasetTable.on_column_selected()` handler:
   a. Extract column_name from event
   b. Lookup dtype from `Dataset.schema[column_name]`
   c. Compute type_category via `detect_column_type_category(dtype)`
   d. Create `ColumnHeaderQuickFilter` modal with pre-populated data
4. Modal displays:
   a. Column name (read-only)
   b. Operator dropdown (filtered by type_category)
   c. Value input field (focused)
5. User selects operator, enters value, submits
6. Modal creates `Operation` object:
   ```python
   Operation(
       code=f"df = df.filter(nw.col('{column}') {operator} {value})",
       display=f"Filter: {column} {operator} {value}",
       operation_type="filter",
       params={"column": column, "operator": operator, "value": value}
   )
   ```
7. Operation passed to `MainScreen` via callback
8. `MainScreen` calls `Dataset.apply_operation(operation)`
9. Operation queued or executed based on execution mode
10. `OperationsSidebar` refreshed with new operation
11. DataTable refreshed if operation executed

**Data created**: One `Operation` object

**Performance**: <50ms from click to modal display, <100ms from submit to operation created

---

### Flow 3: Type Detection

**Function**: `detect_column_type_category(dtype: str) -> str`

**Input**: Narwhals dtype string (e.g., `"Int64"`, `"String"`, `"Datetime"`)

**Process**:
1. Convert dtype to lowercase
2. Check for numeric patterns: `int`, `float`, `decimal`, `uint`
3. If match → return `"numeric"`
4. Check for text patterns: `string`, `str`, `categorical`, `enum`, `object`
5. If match → return `"text"`
6. Check for date patterns: `date`, `time`, `duration`
7. If match → return `"date"`
8. Check for boolean pattern: `bool`
9. If match → return `"boolean"`
10. No match → return `"unknown"`

**Output**: Type category string (one of 5 values)

**Edge Cases**:
- Mixed types (`Object`) → `"unknown"`
- Null columns (`Null`) → `"unknown"`
- Nested types (`Struct`, `List`, `Array`) → `"unknown"`
- Unknown backend types → `"unknown"`

**Performance**: O(1), <1μs per call

---

## Validation Rules

### Column Type Categories

**Constraint**: Must be one of 5 predefined values
- Valid: `"numeric"`, `"text"`, `"date"`, `"boolean"`, `"unknown"`
- Invalid: Any other string value

**Enforcement**: Type hints + validation in type detection function

---

### Color Variables

**Constraint**: Must be valid Textual CSS variable
- Format: `"$variable-name"`
- Must exist in Textual's default theme
- Must meet WCAG 2.1 AA contrast ratio (4.5:1)

**Enforcement**: CSS validation at application start, runtime error if variable undefined

---

### Icons

**Constraint**: Single character (width 1)
- ASCII: Printable range 32-126
- Unicode: Single codepoint, display width 1 or 2

**Enforcement**: Length check in configuration validation

---

### Filter Operators

**Constraint**: Must be valid narwhals filter operators
- Numeric: `>`, `<`, `>=`, `<=`, `=`, `!=`
- Text: `==`, `!=`, `contains` (mapped to narwhals `.str.contains()`)
- Date: `>`, `<`, `>=`, `<=`, `=`, `!=` (date comparison)
- Boolean: `==`, `!=` (true/false comparison)

**Enforcement**: Operator whitelist validation in ColumnHeaderQuickFilter

---

## State Transitions

### Operation State (Reused from 001-tui-data-explorer)

```text
[created] ──apply_operation()──> [queued] (lazy mode)
                               └> [executed] (eager mode)

[queued] ──execute_next()──> [executed] (success)
                         └──> [failed] (error)

[executed] ──undo()──> [in redo_stack]

[in redo_stack] ──redo()──> [executed]
                       └─new_operation()─> [cleared from redo_stack]
```

**No new states added by this feature.**

---

## Configuration

### Type Mappings Configuration File

**Location**: `src/kittiwake/utils/type_colors.py`

**Format**: Python constants

```python
TYPE_MAPPINGS: dict[str, ColumnTypeMapping] = {
    "numeric": {
        "type_category": "numeric",
        "narwhals_dtypes": ["Int8", "Int16", "Int32", "Int64", "UInt8", "UInt16", "UInt32", "UInt64", "Float32", "Float64", "Decimal"],
        "color_variable": "$primary",
        "icon_ascii": "#",
        "icon_unicode": "🔢",
        "filter_operators": [">", "<", ">=", "<=", "=", "!="]
    },
    # ... 4 more mappings
}
```

**Validation**: JSON schema in `contracts/type-mappings.json`

---

## Integration with Existing Models

### Dataset Model

**No modifications required** - reuses existing `schema` attribute

**Usage**:
- `Dataset.schema: dict[str, str]` → source of column types
- `Dataset.apply_operation(operation)` → receives Operations from quick filter

### Operation Model

**No modifications required** - reuses existing model exactly

**Usage**:
- Quick filter creates standard Operation objects
- Indistinguishable from Ctrl+F filter operations
- Same execution, undo/redo, persistence behavior

### DatasetTable Widget

**Modifications**:
- Add `_create_column_header()` method to generate Rich Text headers
- Add `on_column_selected()` message handler for click events
- Modify `load_dataset()` to use styled headers

**No breaking changes** - existing functionality preserved

---

## Testing Considerations

### Unit Tests

**test_type_detector.py**:
- Test all narwhals dtype → category mappings
- Test edge cases (mixed types, null columns, nested types)
- Test case-insensitive matching

**test_column_header_styling.py**:
- Test Rich Text generation for each type category
- Test color variable resolution
- Test icon rendering (ASCII and Unicode)

**test_quick_filter_widget.py**:
- Test operator filtering by type
- Test operation creation
- Test validation (numeric values, date formats)

### Integration Tests

**test_column_type_workflow.py**:
- Load dataset → verify colored headers
- Click header → verify quick filter opens
- Submit filter → verify operation created
- Execute operation → verify data filtered
- Undo operation → verify filter removed

### Accessibility Tests

- Manual: Test with colorblind simulation
- Manual: Test in terminals with 16 colors (limited palette)
- Manual: Test in light and dark themes
- Automated: Verify icons present in all configurations

---

## Performance Considerations

### Type Detection Caching

**Optimization**: Type category computed once per column on dataset load, stored in ColumnHeader entity

**Benefit**: No repeated type detection on re-renders

**Trade-off**: Slight memory overhead (~50 bytes per column)

### Header Rendering

**Optimization**: Rich Text headers created once, reused by Textual rendering engine

**Benefit**: No per-frame styling overhead

**Trade-off**: None - native Textual rendering

### Quick Filter Modal

**Optimization**: Modal created on-demand, destroyed after use

**Benefit**: No memory overhead when not in use

**Trade-off**: ~50ms modal creation time (acceptable)

---

## Summary

This data model extends existing Kittiwake entities with type-aware visualization and quick filtering without introducing new persistent data structures. All new entities are ephemeral (UI state) or static configuration. Integration with existing Operation and Dataset models is seamless and non-breaking.
