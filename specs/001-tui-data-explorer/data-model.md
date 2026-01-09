# Data Model: TUI Data Explorer

**Branch**: `001-tui-data-explorer` | **Date**: 2026-01-09  
**Phase**: Phase 1 (Design & Contracts)

This document defines the core entities, their attributes, relationships, and validation rules.

---

## Entity: Dataset

**Purpose**: Represents a loaded dataset with its schema, source, backend engine, and operation history.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `str` | Yes | Unique identifier (UUID) |
| `name` | `str` | Yes | Display name (derived from filename or user-provided) |
| `source` | `str` | Yes | File path or URL where data was loaded from |
| `schema` | `dict[str, str]` | Yes | Column names → data types (e.g., `{"age": "Int64", "name": "Utf8"}`) |
| `row_count` | `int` | Yes | Total number of rows in dataset |
| `backend` | `str` | Yes | narwhals backend engine (e.g., "polars", "pandas") |
| `df` | `nw.DataFrame \| nw.LazyFrame` | Yes | The actual narwhals dataframe object |
| `operations` | `list[Operation]` | Yes | Ordered list of operations applied to this dataset |
| `is_active` | `bool` | Yes | Whether this dataset is currently displayed in main view |
| `created_at` | `datetime` | Yes | Timestamp when dataset was loaded |

### Validation Rules

- `name`: Must be unique within DatasetSession
- `source`: Must be valid file path or HTTP(S) URL
- `schema`: Must have at least 1 column
- `row_count`: Must be >= 0
- `backend`: Must be one of narwhals-supported backends
- `operations`: Maximum 1000 operations per dataset (practical limit)

### State Transitions

```
[Created] → load_data() → [Loaded]
[Loaded] → apply_operation() → [Modified]
[Modified] → clear_operations() → [Loaded]
[Loaded|Modified] → close() → [Closed]
```

### Relationships

- **DatasetSession** contains 0-10 Datasets (1:N)
- **Dataset** has 0-N Operations (1:N)
- **SavedAnalysis** references 1 Dataset via `dataset_path` (N:1)

---

## Entity: DatasetSession

**Purpose**: Manages the collection of all loaded datasets in the current TUI session.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `datasets` | `list[Dataset]` | Yes | List of loaded datasets (max 10) |
| `active_dataset_id` | `str \| None` | No | ID of currently active dataset |
| `split_pane_left_id` | `str \| None` | No | ID of dataset in left split pane |
| `split_pane_right_id` | `str \| None` | No | ID of dataset in right split pane |
| `split_mode_active` | `bool` | Yes | Whether split pane mode is enabled |

### Validation Rules

- `datasets`: Maximum 10 datasets (FR-063)
- `active_dataset_id`: Must reference existing dataset ID if not None
- `split_pane_left_id` and `split_pane_right_id`: Must reference existing dataset IDs if not None
- Split pane IDs must be different from each other

### Methods

```python
def add_dataset(dataset: Dataset) -> None:
    """Add dataset to session. Raises ValueError if limit reached."""
    if len(self.datasets) >= 10:
        raise ValueError("Maximum 10 datasets allowed")
    self.datasets.append(dataset)
    if self.active_dataset_id is None:
        self.active_dataset_id = dataset.id

def get_active_dataset() -> Dataset | None:
    """Get currently active dataset."""
    return next((d for d in self.datasets if d.id == self.active_dataset_id), None)

def switch_dataset(dataset_id: str) -> None:
    """Switch active dataset. Raises ValueError if ID not found."""
    if not any(d.id == dataset_id for d in self.datasets):
        raise ValueError(f"Dataset {dataset_id} not found")
    self.active_dataset_id = dataset_id

def remove_dataset(dataset_id: str) -> None:
    """Remove dataset from session."""
    self.datasets = [d for d in self.datasets if d.id != dataset_id]
    if self.active_dataset_id == dataset_id:
        self.active_dataset_id = self.datasets[0].id if self.datasets else None
```

---

## Entity: Operation

**Purpose**: Represents a single data transformation operation with executable function, display string, and editable parameters.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `str` | Yes | Unique identifier (UUID) |
| `code` | `str` | Yes | Display-only narwhals expression string (e.g., `'df.filter(nw.col("age") > 25)'`) |
| `display` | `str` | Yes | Human-readable description (e.g., `"Filter: age > 25"`) |
| `operation_type` | `str` | Yes | Operation category (see Valid Operation Types below) |
| `params` | `dict[str, Any]` | Yes | Parameters for rebuilding operation (e.g., `{"column": "age", "operator": ">", "value": 25}`) |
| `created_at` | `datetime` | Yes | Timestamp when operation was created |

### Valid Operation Types

| Type | Description | Example Params |
|------|-------------|----------------|
| `filter` | Row filtering with conditions | `{"column": "age", "operator": ">", "value": 25}` |
| `search` | Full-text search across columns | `{"query": "male"}` |
| `aggregate` | Group-by aggregation | `{"group_by_cols": ["category"], "agg_col": "sales", "agg_func": "sum"}` |
| `pivot` | Pivot table transformation | `{"row_dims": ["region"], "col_dims": ["quarter"], "values": ["sales"], "agg_func": "sum"}` |
| `join` | Merge with another dataset | `{"right_dataset_id": "uuid", "left_on": ["id"], "right_on": ["user_id"], "how": "inner"}` |
| `select` | Select specific columns | `{"columns": ["name", "age", "city"]}` |
| `drop` | Drop specific columns | `{"columns": ["temp_col", "debug_col"]}` |
| `rename` | Rename columns | `{"old_name": "usr_nm", "new_name": "username"}` |
| `with_columns` | Add/modify columns | `{"new_col": "age_group", "expression": "pl.when(pl.col('age') < 18).then('minor').otherwise('adult')"}` |
| `sort` | Sort by columns | `{"columns": ["age", "name"], "descending": [True, False]}` |
| `unique` | Remove duplicate rows | `{"subset": ["email"], "keep": "first"}` |
| `fill_null` | Fill null values | `{"column": "age", "value": 0}` |
| `drop_nulls` | Remove rows with nulls | `{"subset": ["email", "phone"]}` |
| `head` | Take first N rows | `{"n": 100}` |
| `tail` | Take last N rows | `{"n": 100}` |
| `sample` | Random sample | `{"n": 1000, "seed": 42}` |

### Validation Rules

- `operation_type`: Must be one of the 16 valid types listed above
- `params`: Must contain required keys for the operation type
- `code`: Generated by `OperationBuilder.to_code_string()`, not user-editable
- `display`: Maximum 200 characters

### Lifecycle

```
[Created by sidebar form] → validate_params() → [Valid]
[Valid] → build_function() → [Executable]
[Executable] → apply_to_dataframe() → [Applied]
[Applied] → added to Dataset.operations → [Stored]
[Stored] → edit (via right sidebar) → [Recreated from params]
[Stored] → remove (via right sidebar) → [Deleted]
[Stored] → reorder (via right sidebar) → [Resequenced & Reapplied]
```

---

## Entity: SavedAnalysis

**Purpose**: Persisted analysis with dataset reference and operation sequence, stored in DuckDB.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `int` | Yes | Auto-increment primary key (DuckDB) |
| `name` | `str` | Yes | User-provided analysis name (must be unique) |
| `description` | `str` | No | Optional description of analysis purpose |
| `created_at` | `datetime` | Yes | Timestamp when first saved |
| `modified_at` | `datetime` | Yes | Timestamp of last modification |
| `operation_count` | `int` | Yes | Number of operations in sequence |
| `dataset_path` | `str` | Yes | Original dataset file path or URL |
| `operations` | `list[dict]` | Yes | JSON-serialized list of operation params (NOT full Operation objects) |

### Storage Schema (DuckDB)

See `/specs/001-tui-data-explorer/contracts/saved-analysis-schema.sql` for full SQL schema.

### Validation Rules

- `name`: Must be unique, 1-100 characters, no path separators
- `description`: Maximum 500 characters
- `operation_count`: Must equal `len(operations)`, range [1, 1000]
- `dataset_path`: Must be valid path or URL (not validated for existence on save)
- `operations`: Each operation dict must have `operation_type` and `params` keys

### Serialization Format

```json
{
  "id": 42,
  "name": "Q4 Sales Analysis",
  "description": "Filter and aggregate Q4 sales by region",
  "created_at": "2026-01-09T10:30:00Z",
  "modified_at": "2026-01-09T11:45:00Z",
  "operation_count": 3,
  "dataset_path": "/data/sales_2025.csv",
  "operations": [
    {
      "operation_type": "filter",
      "params": {"column": "quarter", "operator": "==", "value": "Q4"},
      "display": "Filter: quarter == Q4"
    },
    {
      "operation_type": "aggregate",
      "params": {
        "group_by_cols": ["region"],
        "agg_col": "sales",
        "agg_func": "sum"
      },
      "display": "Aggregate: sum(sales) by region"
    },
    {
      "operation_type": "sort",
      "params": {"columns": ["sales"], "descending": [true]},
      "display": "Sort: sales descending"
    }
  ]
}
```

### Methods

```python
def to_dict() -> dict:
    """Serialize for DuckDB storage."""
    return {
        "name": self.name,
        "description": self.description,
        "created_at": self.created_at,
        "modified_at": self.modified_at,
        "operation_count": len(self.operations),
        "dataset_path": self.dataset_path,
        "operations": json.dumps([op.to_dict() for op in self.operations])
    }

@classmethod
def from_dict(cls, data: dict) -> SavedAnalysis:
    """Deserialize from DuckDB result."""
    return cls(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        created_at=data["created_at"],
        modified_at=data["modified_at"],
        operation_count=data["operation_count"],
        dataset_path=data["dataset_path"],
        operations=json.loads(data["operations"])
    )
```

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│  DatasetSession     │
│  ─────────────────  │
│  datasets: [0..10]  │ 1
│  active_dataset_id  ├───────┐
│  split_pane_*_id    │       │
└─────────────────────┘       │ N
                              │
                              ▼
                     ┌─────────────────┐
                     │    Dataset      │
                     │  ─────────────  │
                     │  id, name       │ 1
                     │  source, schema ├───────┐
                     │  df, operations │       │
                     │  is_active      │       │ N
                     └─────────────────┘       │
                                               ▼
                                      ┌─────────────────┐
                                      │   Operation     │
                                      │  ─────────────  │
                                      │  id, code       │
                                      │  display, type  │
                                      │  params         │
                                      └─────────────────┘

┌──────────────────────┐
│   SavedAnalysis      │ N            1 ┌──────────────┐
│  ──────────────────  ├───────────────▶│   Dataset    │
│  id, name            │  references    │  (via path)  │
│  dataset_path        │                └──────────────┘
│  operations: JSON    │
│  (stored in DuckDB)  │
└──────────────────────┘
```

---

## Data Flow

### Loading a Dataset

```
User: kw load data.csv
  ↓
CLI: Parse arguments
  ↓
DataLoader: Load CSV via narwhals
  ↓
Dataset: Create entity with schema, df, source
  ↓
DatasetSession: Add to datasets list (max 10)
  ↓
DatasetTable widget: Display first page
```

### Applying an Operation (via Left Sidebar)

```
User: Ctrl+F → Fill filter form → Apply
  ↓
FilterSidebar: Collect form values (column, operator, value)
  ↓
OperationBuilder: Validate params → Build executable function
  ↓
Dataset: Execute function on df → Update df
  ↓
Operation: Create entity with params, code, display
  ↓
Dataset: Append to operations list
  ↓
RightSidebar: Show new operation in history (auto-appear)
  ↓
DatasetTable: Refresh to show filtered data
```

### Editing an Operation (via Right Sidebar)

```
User: Select operation in right sidebar → Press Enter
  ↓
RightSidebar: Get operation params
  ↓
LeftSidebar: Open with pre-filled form values
  ↓
User: Modify values → Apply
  ↓
Dataset: Remove old operation, apply new operation
  ↓
Dataset: Reapply all subsequent operations in order
  ↓
DatasetTable: Refresh with updated data
```

### Reordering Operations (via Right Sidebar)

```
User: Select operation → Ctrl+Up/Down
  ↓
RightSidebar: Update operations list order
  ↓
Dataset: Clear df → Reload original data
  ↓
Dataset: Reapply all operations in new sequence
  ↓
DatasetTable: Refresh with reordered result
```

### Saving an Analysis

```
User: Ctrl+S → Enter name/description → Save
  ↓
SavedAnalysis: Create entity from Dataset.operations
  ↓
AnalysisPersistence: Serialize to JSON
  ↓
DuckDB: INSERT into saved_analyses table
  ↓
TUI: Show "Analysis saved" notification
```

### Loading a Saved Analysis

```
User: Ctrl+L → Select analysis from list → Load
  ↓
DuckDB: SELECT saved_analyses WHERE id = ?
  ↓
AnalysisPersistence: Deserialize JSON → SavedAnalysis
  ↓
DataLoader: Load dataset from dataset_path
  ↓
Dataset: Create entity
  ↓
OperationBuilder: Rebuild operations from params
  ↓
Dataset: Apply operations in sequence
  ↓
DatasetSession: Add dataset
  ↓
DatasetTable: Display final result
```

---

## Scale Assumptions

- **Datasets per session**: Maximum 10 (FR-063)
- **Operations per dataset**: Recommended max 1000 (performance degrades beyond)
- **Saved analyses in DuckDB**: Optimized for up to 10,000 (SC-013: <200ms queries for 1000)
- **Dataset size**: 10M+ rows supported via lazy evaluation (SC-004)
- **Column count**: Up to 1000 columns (beyond may impact UI performance)
- **Operation parameters**: Maximum 100KB serialized size per operation

---

**Data model version**: 1.0  
**Last updated**: 2026-01-09  
**Next**: Contracts (SQL schema, export templates)
