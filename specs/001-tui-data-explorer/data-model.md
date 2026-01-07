# Data Model: TUI Data Explorer

**Date**: 2026-01-08  
**Feature**: 001-tui-data-explorer  
**Purpose**: Concrete entity designs from spec + research decisions

---

## Core Entities

### Dataset

**Purpose**: Represents a loaded dataset in the active session with its source, schema, operation history, and display state.

**Fields**:
- `id` (UUID): Unique session identifier generated on load
- `name` (str): Display name derived from file path (e.g., "sales.csv")
- `source` (str): Original file path or URL
- `backend` (str): Detected narwhals backend ("pandas", "polars", or "pyarrow")
- `frame` (nw.LazyFrame | nw.DataFrame): Narwhals frame object (lazy for large files, eager for small)
- `schema` (dict[str, str]): Column name → dtype mapping (e.g., {"age": "Int64", "name": "String"})
- `row_count` (int): Total row count (may be approximate for lazy frames)
- `is_active` (bool): Whether currently displayed in main view
- `is_lazy` (bool): Whether using lazy evaluation
- `operation_history` (list[Operation]): Ordered list of applied operations (narwhals expressions)
- `current_frame` (nw.DataFrame): Materialized result after applying operations (for display)
- `checkpoints` (dict[int, nw.DataFrame]): Cached states at operation indices for undo/redo optimization
- `checkpoint_interval` (int): Number of operations between checkpoints (default: 10)

**Relationships**:
- Contained in DatasetSession (N:1)
- References Operation objects (1:N)
- May be referenced by SavedAnalysis via dataset_path field

**Validation Rules** (from spec requirements):
- FR-001/FR-002: `source` must be valid file path (exists, readable) or HTTP(S) URL
- FR-004: `frame` must be narwhals type (no direct pandas/polars DataFrame)
- FR-063: Session can contain max 10 Dataset instances
- `name` must be unique within DatasetSession
- `backend` must be one of ["pandas", "polars", "pyarrow","duckdb"]
- `operation_history` contains serializable Operation objects (code + metadata)

**State Transitions**:
```text
LOADING → READY → ACTIVE ←→ INACTIVE → CLOSED
            ↓
          ERROR
```
- LOADING: Initial state during data load (async)
- READY: Data loaded, not yet displayed
- ACTIVE: Currently displayed in main view (only 1 dataset active per session)
- INACTIVE: Loaded but not displayed (user switched to another dataset)
- CLOSED: User closed dataset, freed from memory
- ERROR: Load failed (invalid file, network timeout, etc.)

**Methods**:

```python
def apply_operation(self, operation: Operation) -> None:
    """
    Applies operation to current frame, adds to history, creates checkpoint if needed.
    
    Args:
        operation: Operation to apply (Filter, Aggregation, etc.)
    
    Raises:
        OperationError: If operation fails (invalid column, type mismatch, etc.)
    """

def undo(self) -> bool:
    """
    Removes last operation and restores previous state using checkpoints.
    
    Returns:
        True if undo succeeded, False if history empty
    """

def redo(self) -> bool:
    """
    Reapplies previously undone operation.
    
    Returns:
        True if redo succeeded, False if redo stack empty
    """

def get_page(self, page_num: int, page_size: int = 500) -> nw.DataFrame:
    """
    Returns materialized page of data for display in DataTable.
    
    Args:
        page_num: 0-based page index
        page_size: Number of rows per page (default: 500)
    
    Returns:
        DataFrame with page_size rows starting at offset page_num * page_size
    """

def to_dict(self) -> dict:
    """
    Serializes dataset metadata and operations for SavedAnalysis persistence.
    
    Returns:
        {
            "name": str,
            "source": str,
            "backend": str,
            "operations": [op.to_dict() for op in operation_history]
        }
    """
```

---

### DatasetSession

**Purpose**: Manages the collection of all loaded datasets in the current TUI session with navigation state and configuration.

**Fields**:
- `datasets` (list[Dataset]): List of loaded datasets (max 10 per FR-063)
- `active_dataset_id` (UUID | None): ID of currently displayed dataset
- `max_datasets` (int): Maximum simultaneous datasets (default: 10, configurable)
- `split_pane_enabled` (bool): Whether split pane mode is active
- `split_pane_datasets` (tuple[UUID, UUID] | None): IDs of datasets in split pane view

**Relationships**:
- Contains Dataset instances (1:N)
- Referenced by MainScreen for display state

**Validation Rules**:
- FR-063: len(datasets) ≤ max_datasets
- FR-054: Exactly one dataset has is_active=True when len(datasets) > 0
- FR-056: split_pane_datasets references must exist in datasets list
- active_dataset_id must reference an existing dataset ID

**State Transitions**:
```text
EMPTY → LOADING_FIRST → SINGLE_DATASET ←→ MULTIPLE_DATASETS
                                ↓               ↓
                           SPLIT_PANE ←────────┘
```

**Methods**:

```python
def add_dataset(self, dataset: Dataset) -> bool:
    """
    Adds dataset to session if under limit.
    
    Args:
        dataset: Dataset to add
    
    Returns:
        True if added, False if at max_datasets limit
    
    Raises:
        ValueError: If dataset name conflicts with existing dataset
    """

def remove_dataset(self, dataset_id: UUID) -> None:
    """
    Removes dataset from session and frees memory.
    
    Args:
        dataset_id: UUID of dataset to remove
    
    Side effects:
        - If removed dataset was active, makes first remaining dataset active
        - Disables split pane if removed dataset was in split view
    """

def set_active_dataset(self, dataset_id: UUID) -> None:
    """
    Switches active dataset (updates is_active flags).
    
    Args:
        dataset_id: UUID of dataset to make active
    
    Raises:
        KeyError: If dataset_id not found in session
    """

def get_active_dataset(self) -> Dataset | None:
    """
    Returns currently active dataset.
    
    Returns:
        Active Dataset or None if session empty
    """

def enable_split_pane(self, dataset_id_1: UUID, dataset_id_2: UUID) -> None:
    """
    Enables split pane mode with two datasets.
    
    Args:
        dataset_id_1: First dataset to display
        dataset_id_2: Second dataset to display
    
    Raises:
        ValueError: If either ID not found or both IDs are the same
    """
```

---

### Operation

**Purpose**: Represents a single data transformation operation stored as executable narwhals code with metadata for display and editing.

**Fields**:
- `code` (str): Narwhals expression code string (e.g., `"df.filter(nw.col('age') > 25)"`)
- `display` (str): Human-readable description (e.g., `"Filter: age > 25"`)
- `operation_type` (str): Operation category for modal routing
- `params` (dict): Operation parameters for modal editing
- `id` (UUID): Unique identifier for operation management

**Operation Types** (13 with dedicated TUI modals):
- **Core**: `filter`, `aggregate`, `pivot`, `join`
- **Selection**: `select`, `drop`, `rename`
- **Transform**: `with_columns`, `sort`
- **Data cleaning**: `unique`, `fill_null`, `drop_nulls`
- **Sampling**: `head`, `tail`, `sample`

**Relationships**:
- Contained in Dataset.operation_history (N:1)
- Can be serialized to SavedAnalysis.operations JSON
- Can be reused in Workflow sequences

**Validation Rules**:
- `code` must be valid Python expression using narwhals API
- `operation_type` must be one of the 13 supported types
- `params` structure depends on operation_type (see Modal Specifications)
- Code validated immediately on creation (modal submit) and at runtime (apply)

**State Transitions**: None (immutable once created)

**Methods**:

```python
def to_dict(self) -> dict:
    """
    Serializes operation for SavedAnalysis persistence.
    
    Returns:
        {
            "code": str,
            "display": str,
            "operation_type": str,
            "params": dict
        }
    """

@classmethod
def from_dict(cls, data: dict) -> "Operation":
    """
    Deserializes operation from SavedAnalysis operations JSON.
    
    Args:
        data: Serialized operation dict
    
    Returns:
        Operation instance
    """

def apply(self, df: nw.LazyFrame) -> nw.LazyFrame:
    """
    Applies operation by executing code string in narwhals context.
    
    Args:
        df: Input frame
    
    Returns:
        Transformed frame after executing self.code
    
    Raises:
        OperationError: If code execution fails (invalid column, type mismatch, etc.)
    
    Example:
        # Operation(code="df.filter(nw.col('age') > 25)", ...)
        # Executes: eval(code, {"df": df, "nw": narwhals})
    """

def validate(self, df: nw.LazyFrame) -> tuple[bool, str | None]:
    """
    Validates operation code against dataset schema.
    
    Args:
        df: Target dataset frame
    
    Returns:
        (is_valid, error_message)
    """
```

**Example Operations**:

```python
# Filter operation
Operation(
    code="df.filter(nw.col('age') > 25)",
    display="Filter: age > 25",
    operation_type="filter",
    params={"column": "age", "operator": ">", "value": 25}
)

# Aggregation operation
Operation(
    code="df.group_by('region').agg([nw.col('sales').sum().alias('sales_sum'), nw.col('sales').mean().alias('sales_mean')])",
    display="Aggregate: SUM, MEAN of sales grouped by region",
    operation_type="aggregate",
    params={"column": "sales", "functions": ["sum", "mean"], "group_by": ["region"]}
)

# Sort operation
Operation(
    code="df.sort('date', descending=True)",
    display="Sort: date descending",
    operation_type="sort",
    params={"columns": ["date"], "descending": [True]}
)
```

---

### Workflow

**Purpose**: Represents a saved sequence of operations that can be reapplied to datasets with compatible schemas.

**Fields**:
- `id` (UUID): Unique identifier
- `name` (str): User-provided workflow name
- `description` (str): Optional description of workflow purpose
- `operations` (list[Operation]): Ordered sequence of Filter, Aggregation, PivotTable operations
- `required_columns` (set[str]): Union of all column names referenced in operations (for schema validation)
- `created_at` (datetime): Creation timestamp
- `modified_at` (datetime): Last modification timestamp

**Relationships**:
- Contains Operation objects (1:N)
- Can be applied to any Dataset with compatible schema
- Persisted to disk as JSON file (human-readable per FR-034)

**Validation Rules** (from FR-033, FR-034, FR-035):
- FR-034: `name` must be unique within user's workflows
- FR-035: Target dataset must have all columns in `required_columns` with compatible types
- `operations` must not be empty
- All operations must be serializable (to_dict() implemented)

**State Transitions**: None (immutable once saved, new version created on edit)

**Methods**:

```python
def to_dict(self) -> dict:
    """
    Serializes workflow for disk persistence.
    
    Returns:
        {
            "id": str,
            "name": str,
            "description": str,
            "operations": [op.to_dict() for op in operations],
            "required_columns": [str, ...],
            "created_at": ISO timestamp,
            "modified_at": ISO timestamp
        }
    """

@classmethod
def from_dict(cls, data: dict) -> "Workflow":
    """
    Deserializes workflow from JSON file.
    """

def apply_to_dataset(self, dataset: Dataset) -> None:
    """
    Applies all operations in sequence to target dataset.
    
    Args:
        dataset: Target dataset with compatible schema
    
    Raises:
        SchemaError: If dataset missing required columns or incompatible types
        OperationError: If any operation fails during application
    """

def validate_schema(self, schema: dict[str, str]) -> tuple[bool, list[str]]:
    """
    Checks if schema is compatible with workflow.
    
    Args:
        schema: Column name → dtype mapping
    
    Returns:
        (is_valid, list of missing/incompatible columns)
    """

def to_display_string(self) -> str:
    """
    Generates human-readable workflow description for UI.
    
    Returns:
        String like "Data Cleaning (3 ops): filter nulls → filter age > 18 → aggregate by region"
    """
```

---

### SavedAnalysis

**Purpose**: Represents a complete analysis stored in DuckDB with dataset reference, operations, and metadata for loading, exporting, and sharing.

**Fields**:
- `id` (int): Auto-incrementing primary key
- `name` (str): User-provided analysis name (unique per FR-041)
- `description` (str | None): Optional description of analysis purpose
- `created_at` (datetime): Creation timestamp
- `modified_at` (datetime): Last modification timestamp
- `operation_count` (int): Number of operations in sequence
- `dataset_path` (str): Original dataset file path or URL (for reloading per FR-061)
- `operations` (list[dict]): Serialized operations as JSON array (stored as DuckDB JSON type)

**Relationships**:
- References Dataset via dataset_path (weak reference, dataset may no longer exist)
- Operations can be deserialized to Filter, Aggregation, PivotTable instances

**Validation Rules** (from FR-040-050, FR-061-062):
- FR-040: `name` must be unique (enforced by DuckDB UNIQUE constraint)
- FR-040: `operation_count` must match len(operations)
- FR-045: Must be saved before export is allowed
- FR-050: Export file path conflicts require user confirmation
- FR-062: `dataset_path` accessibility verified before loading
- `operations` must be valid JSON array conforming to operations-schema.json

**State Transitions**:
```text
UNSAVED → SAVING → SAVED → LOADING → LOADED
            ↓         ↓        ↓
          ERROR    EXPORTED  ERROR
```

**Methods**:

```python
def to_dict(self) -> dict:
    """
    Serializes analysis for DuckDB insertion.
    
    Returns:
        {
            "name": str,
            "description": str | None,
            "operation_count": int,
            "dataset_path": str,
            "operations": str  # JSON string for DuckDB
        }
    """

@classmethod
def from_dict(cls, data: dict) -> "SavedAnalysis":
    """
    Deserializes analysis from DuckDB query result.
    
    Args:
        data: Row dict from DuckDB query
    
    Returns:
        SavedAnalysis instance with operations parsed from JSON
    """

async def load_dataset(self) -> Dataset:
    """
    Reloads original dataset from dataset_path (per FR-061).
    
    Returns:
        Loaded Dataset instance
    
    Raises:
        FileNotFoundError: If dataset_path no longer accessible (FR-062)
        LoadError: If dataset format changed or corrupted
    """

def apply_operations(self, dataset: Dataset) -> None:
    """
    Applies all saved operations to loaded dataset.
    
    Args:
        dataset: Dataset loaded from dataset_path
    
    Raises:
        OperationError: If operations fail (schema changed, invalid values, etc.)
    """

def export_marimo(self, output_path: Path) -> None:
    """
    Exports analysis as marimo notebook (FR-046).
    
    Args:
        output_path: Destination .py file path
    
    Raises:
        FileExistsError: If path exists and overwrite not confirmed (FR-050)
    """

def export_python(self, output_path: Path) -> None:
    """
    Exports analysis as Python script (FR-047).
    """

def export_jupyter(self, output_path: Path) -> None:
    """
    Exports analysis as Jupyter notebook (FR-048).
    """
```

---

## Persistence Schema (DuckDB)

### SavedAnalysis Table

```sql
-- SavedAnalysis Schema Version 1.0
-- Compatible with: kittiwake >=0.1.0
-- Database location: ~/.kittiwake/analyses.db

CREATE TABLE IF NOT EXISTS saved_analyses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- FR-040: Unique analysis names
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operation_count INTEGER NOT NULL CHECK (operation_count >= 0),
    dataset_path TEXT NOT NULL,  -- FR-061: Source dataset for reloading
    operations JSON NOT NULL  -- Serialized operation list (see operations-schema.json)
);

-- Performance indices (SC-013: <200ms for 1000 analyses)
CREATE INDEX IF NOT EXISTS idx_saved_analyses_name 
    ON saved_analyses(name);

CREATE INDEX IF NOT EXISTS idx_saved_analyses_created_at 
    ON saved_analyses(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_saved_analyses_modified_at 
    ON saved_analyses(modified_at DESC);

-- Enable WAL mode for concurrent readers (research.md decision #5)
PRAGMA journal_mode = WAL;
```

### Migration Strategy

Future schema changes use versioned migration files:

```sql
-- migrations/001_add_tags.sql (example)
ALTER TABLE saved_analyses ADD COLUMN tags TEXT[];  -- Future enhancement
```

---

## Operation Serialization

### JSON Schema

Stored in `contracts/operations-schema.json` and validated at runtime:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://kittiwake.dev/schemas/operations-v1.json",
  "title": "Kittiwake Operations Schema",
  "description": "Serialization format for Filter, Aggregation, and PivotTable operations",
  "type": "array",
  "items": {
    "oneOf": [
      {
        "type": "object",
        "title": "Filter Operation",
        "properties": {
          "type": {"const": "filter"},
          "column": {"type": "string", "minLength": 1},
          "operator": {
            "enum": ["=", "!=", ">", "<", ">=", "<=", "contains", "is_null", "not_null"]
          },
          "value": {
            "oneOf": [
              {"type": "string"},
              {"type": "number"},
              {"type": "boolean"},
              {"type": "null"}
            ]
          },
          "logic": {"enum": ["AND", "OR"], "default": "AND"}
        },
        "required": ["type", "column", "operator", "value"],
        "additionalProperties": false
      },
      {
        "type": "object",
        "title": "Aggregation Operation",
        "properties": {
          "type": {"const": "aggregate"},
          "column": {"type": "string", "minLength": 1},
          "functions": {
            "type": "array",
            "items": {
              "enum": ["count", "sum", "mean", "median", "min", "max", "std"]
            },
            "minItems": 1,
            "uniqueItems": true
          },
          "group_by": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "default": []
          }
        },
        "required": ["type", "column", "functions"],
        "additionalProperties": false
      },
      {
        "type": "object",
        "title": "Pivot Table Operation",
        "properties": {
          "type": {"const": "pivot"},
          "row_dimensions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
          },
          "column_dimensions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
          },
          "values": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "column": {"type": "string", "minLength": 1},
                "function": {
                  "enum": ["count", "sum", "mean", "median", "min", "max", "std"]
                }
              },
              "required": ["column", "function"],
              "additionalProperties": false
            },
            "minItems": 1
          }
        },
        "required": ["type", "values"],
        "additionalProperties": false,
        "anyOf": [
          {"required": ["row_dimensions"]},
          {"required": ["column_dimensions"]}
        ]
      }
    ]
  }
}
```

### Python Types

Example implementation using Python 3.13+ dataclasses and narwhals:

```python
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4
import narwhals as nw


@dataclass
class Operation:
    """
    Represents a data transformation operation stored as executable narwhals code.
    Generated by TUI modals, never written by users directly.
    """
    code: str  # Narwhals expression (e.g., "df.filter(nw.col('age') > 25)")
    display: str  # Human-readable (e.g., "Filter: age > 25")
    operation_type: str  # One of 13 supported types
    params: dict[str, Any]  # Parameters for modal editing
    id: UUID = field(default_factory=uuid4)
    
    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        return {
            "code": self.code,
            "display": self.display,
            "operation_type": self.operation_type,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Operation":
        """Deserialize from dict."""
        return cls(
            code=data["code"],
            display=data["display"],
            operation_type=data["operation_type"],
            params=data["params"],
            id=uuid4()  # Generate new ID on load
        )
    
    def apply(self, df: nw.LazyFrame) -> nw.LazyFrame:
        """
        Apply operation by executing code string in narwhals context.
        
        Raises:
            OperationError: If code execution fails
        """
        try:
            # Execute code in safe namespace with only df and nw
            namespace = {"df": df, "nw": nw}
            result = eval(self.code, {"__builtins__": {}}, namespace)
            return result
        except Exception as e:
            raise OperationError(f"Failed to apply operation '{self.display}': {e}")
    
    def validate(self, df: nw.LazyFrame) -> tuple[bool, str | None]:
        """
        Validate operation code against dataset schema.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Try to execute on sample data
            sample = df.head(10).collect()
            self.apply(sample.lazy())
            return (True, None)
        except Exception as e:
            return (False, str(e))


class OperationError(Exception):
    """Raised when operation execution fails."""
    pass


# Operation type constants
OPERATION_TYPES = [
    "filter", "aggregate", "pivot", "join",
    "select", "drop", "rename",
    "with_columns", "sort",
    "unique", "fill_null", "drop_nulls",
    "head", "tail", "sample"
]
```

**Example Operation Instances**:

```python
# Filter: age > 25
Operation(
    code="df.filter(nw.col('age') > 25)",
    display="Filter: age > 25",
    operation_type="filter",
    params={"column": "age", "operator": ">", "value": 25}
)

# Aggregate: sum and mean of sales by region
Operation(
    code="df.group_by('region').agg([nw.col('sales').sum().alias('sales_sum'), nw.col('sales').mean().alias('sales_mean')])",
    display="Aggregate: SUM, MEAN of sales grouped by region",
    operation_type="aggregate",
    params={
        "column": "sales",
        "functions": ["sum", "mean"],
        "group_by": ["region"]
    }
)

# Sort by date descending
Operation(
    code="df.sort('date', descending=True)",
    display="Sort: date (descending)",
    operation_type="sort",
    params={"columns": ["date"], "descending": [True]}
)

# Select specific columns
Operation(
    code="df.select(['name', 'email', 'age'])",
    display="Select: name, email, age",
    operation_type="select",
    params={"columns": ["name", "email", "age"]}
)

# Drop null values
Operation(
    code="df.drop_nulls()",
    display="Drop rows with null values",
    operation_type="drop_nulls",
    params={}
)

# Calculated column
Operation(
    code="df.with_columns(nw.col('price') * nw.col('quantity').alias('total'))",
    display="Add column: total = price * quantity",
    operation_type="with_columns",
    params={
        "new_column": "total",
        "expression": "price * quantity"
    }
)
```

---

## Entity Relationships Diagram

```text
┌─────────────────┐
│ DatasetSession  │
│ ─────────────── │       contains (1:N)
│ - datasets[]    │◄─────────────────────┐
│ - active_id     │                      │
│ - split_pane    │                      │
└─────────────────┘                      │
                                         │
                                         │
┌────────────────────────────────────────┼────────────────────┐
│ Dataset                                │                    │
│ ──────────────────────────────         │                    │
│ - id (UUID)                            │                    │
│ - name, source, backend                │                    │
│ - frame (nw.LazyFrame)                 │                    │
│ - schema, row_count                    │                    │
│ - is_active, is_lazy                   │                    │
│ - operation_history[]  ────────────────┼────┐               │
│ - current_frame                        │    │               │
│ - checkpoints{}                        │    │               │
└────────────────────────────────────────┘    │               │
         │                                    │               │
         │ references (weak)                  │               │
         │                                    │               │
         ▼                                    ▼               │
┌─────────────────┐              ┌─────────────────────┐     │
│ SavedAnalysis   │              │ Operation           │     │
│ ─────────────── │              │ (abstract)          │     │
│ - id            │              │ ─────────────────── │     │
│ - name          │              │ - id (UUID)         │     │
│ - description   │              │ + to_dict()         │     │
│ - created_at    │              │ + from_dict()       │     │
│ - modified_at   │              │ + apply(df)         │     │
│ - dataset_path ─┼──────────────┤ + to_display_str()  │     │
│ - operations    │              └──────────▲──────────┘     │
│   (JSON)        │                         │                │
└─────────────────┘                         │                │
    │ stored in                             │                │
    │ DuckDB                          ┌─────┴─────┬──────────┴────┐
    ▼                                 │           │               │
~/.kittiwake/                 ┌───────┴──────┐ ┌─┴──────────┐ ┌─┴──────────┐
analyses.db                   │ Filter       │ │Aggregation │ │PivotTable  │
(WAL mode)                    │ ────────────│ │────────────│ │────────────│
                              │- column     │ │- target_col│ │- row_dims  │
┌─────────────────┐           │- operator   │ │- functions │ │- col_dims  │
│ Workflow        │           │- value      │ │- group_by  │ │- values    │
│ ─────────────── │           │- logic      │ │- result_df │ │- result_df │
│ - id            │           └─────────────┘ └────────────┘ └────────────┘
│ - name          │                 │                │               │
│ - description   │                 └────────────────┴───────────────┘
│ - operations[] ─┼─────────────────────────────────────────────────────┘
│ - required_cols │                     applies to (N:1)
│ - created_at    │
│ - modified_at   │
└─────────────────┘
    │ persisted as
    ▼
~/.kittiwake/
workflows/*.json
```

**Key Relationships**:

1. **DatasetSession → Dataset** (1:N, max 10): Session contains up to 10 datasets
2. **Dataset → Operation** (1:N): Each dataset has operation history
3. **SavedAnalysis → Dataset** (weak reference): SavedAnalysis stores dataset_path string
4. **Workflow → Operation** (1:N): Workflow contains reusable operation sequence
5. **Operation** (inheritance): Filter, Aggregation, PivotTable extend Operation base

---

## Validation Rules Summary

| Entity | Rule | FR Reference | Constraint Type |
|--------|------|--------------|----------------|
| **Dataset** | source must be valid path/URL | FR-001, FR-002 | Runtime validation |
| Dataset | frame must be narwhals type | FR-004 | Type enforcement |
| Dataset | name unique within session | FR-053 | Business logic |
| **DatasetSession** | max 10 datasets | FR-063 | Hard limit |
| DatasetSession | exactly 1 active dataset when non-empty | FR-054 | Invariant |
| DatasetSession | split_pane_datasets IDs exist in session | FR-056 | Foreign key |
| **Filter** | column exists in schema | FR-017 | Runtime validation |
| Filter | operator compatible with dtype | FR-017 | Type checking |
| Filter | value type matches column | FR-017 | Type checking |
| **Aggregation** | target_column numeric for SUM/MEAN/etc | FR-021 | Type checking |
| Aggregation | group_by columns exist | FR-022 | Runtime validation |
| Aggregation | functions list not empty | FR-023 | Business logic |
| **PivotTable** | dimensions exist in schema | FR-025 | Runtime validation |
| PivotTable | at least 1 dimension specified | FR-025 | Business logic |
| PivotTable | values list not empty | FR-026 | Business logic |
| **Workflow** | name unique | FR-034 | File system |
| Workflow | target schema has required_columns | FR-035 | Pre-apply check |
| Workflow | operations not empty | - | Business logic |
| **SavedAnalysis** | name unique | FR-040 | DuckDB UNIQUE |
| SavedAnalysis | operation_count matches len(operations) | FR-040 | Consistency check |
| SavedAnalysis | dataset_path accessible before load | FR-062 | Pre-load check |
| SavedAnalysis | operations valid JSON | - | JSON schema |

---

## Notes

### Design Decisions

1. **UUID vs Auto-increment IDs**: UUIDs used for session entities (Dataset, Operation instances) to avoid collisions when merging datasets or applying workflows. Auto-increment used for SavedAnalysis (single-user DB).

2. **Lazy vs Eager Evaluation**: Dataset.is_lazy flag controls whether operations use LazyFrame (chained, optimized) or DataFrame (materialized). Large files (>100MB) default to lazy per research.md decision #1.

3. **Checkpoint Strategy**: Operation replay optimization uses checkpoints every N operations (configurable, default 10). Trade-off: ~200MB memory per checkpoint on 1GB dataset vs full replay cost (research.md decision #7).

4. **Operation Serialization**: Command pattern with to_dict()/from_dict() enables workflow persistence, undo/redo, and export (research.md decision #7). All operations implement Operation base class.

5. **DuckDB vs JSON Files**: SavedAnalysis uses DuckDB for ACID properties, concurrent access (WAL mode), and query performance (SC-013: <200ms). Workflows use JSON files for human readability (FR-034).

### Future Extensions

- **Tags for SavedAnalysis**: Add `tags TEXT[]` column for organization
- **Workflow Parameters**: Parameterize filter values for reusable templates
- **Merge Operation**: Add JoinOperation(left_col, right_col, join_type) to operation types
- **Column Transformations**: Add TransformOperation for calculated columns
- **Export Format Plugins**: Extensible export system for custom formats

---

**Status**: ✅ Complete  
**Next Phase**: Generate contracts/ directory with CLI spec and export templates  
**Validation**: All entities map to spec requirements (FR-001 through FR-062)
