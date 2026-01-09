# Research Report R8: Multi-Dataset Navigation with Independent States

**Date**: 2026-01-09  
**Feature**: 001-tui-data-explorer  
**Status**: Complete

## Executive Summary

This research investigated state management patterns for managing up to 10 datasets simultaneously in the kittiwake TUI, where each dataset maintains independent operation histories (queued + executed operations). The investigation focused on:

1. **DatasetSession State Management**: How to structure the session to manage multiple datasets
2. **State Preservation**: Ensuring independent operation states when switching between datasets
3. **UI Widget Selection**: Choosing between Tabs vs ListView for dataset selection
4. **Memory Management**: Warning/enforcement patterns when approaching the 10-dataset limit

**Key Finding**: The existing `DatasetSession` and `Dataset` classes provide a solid foundation for multi-dataset state management. The current implementation uses a **reactive tab-based UI** with UUID-based dataset references that automatically preserves independent states when switching.

---

## 1. DatasetSession State Management Pattern

### 1.1 Current Implementation (dataset_session.py:10-105)

```python
@dataclass
class DatasetSession:
    """Manages collection of loaded datasets."""
    
    datasets: list[Dataset] = field(default_factory=list)
    active_dataset_id: UUID | None = None
    max_datasets: int = 10
    split_pane_enabled: bool = False
    split_pane_datasets: tuple[UUID, UUID] | None = None
```

### 1.2 Core Methods

#### Adding Datasets (dataset_session.py:19-39)
```python
def add_dataset(self, dataset: Dataset) -> bool:
    """Add dataset to session."""
    if len(self.datasets) >= self.max_datasets:
        return False  # Enforce 10-dataset limit
    
    # Handle name conflicts with auto-renaming (dataset_1, dataset_2, etc.)
    names = [d.name for d in self.datasets]
    if dataset.name in names:
        counter = 1
        while f"{dataset.name}_{counter}" in names:
            counter += 1
        dataset.name = f"{dataset.name}_{counter}"
    
    self.datasets.append(dataset)
    
    # Auto-activate first dataset
    if self.active_dataset_id is None:
        self.set_active_dataset(dataset.id)
    
    return True
```

**Key Design Decision**: Returns `bool` to indicate success/failure rather than raising exception. This enables graceful UI feedback when limit is reached.

#### Switching Active Dataset (dataset_session.py:57-70)
```python
def set_active_dataset(self, dataset_id: UUID) -> None:
    """Set active dataset."""
    # Clear all active flags (multi-pass approach)
    for dataset in self.datasets:
        dataset.is_active = False
    
    # Set new active dataset
    for dataset in self.datasets:
        if dataset.id == dataset_id:
            dataset.is_active = True
            self.active_dataset_id = dataset_id
            return
    
    raise KeyError(f"Dataset {dataset_id} not found in session")
```

**Key Design Decision**: Uses UUID-based reference instead of index-based. This prevents stale references when datasets are removed or reordered.

#### Retrieving Active Dataset (dataset_session.py:72-77)
```python
def get_active_dataset(self) -> Dataset | None:
    """Get currently active dataset."""
    for dataset in self.datasets:
        if dataset.is_active:
            return dataset
    return None
```

### 1.3 State Management Strengths

✅ **UUID-based references**: Prevents stale pointers when datasets are reordered  
✅ **Explicit active tracking**: Both `active_dataset_id` (session-level) and `is_active` (dataset-level) flags  
✅ **Limit enforcement**: Hard limit of 10 datasets enforced in `add_dataset()`  
✅ **Split pane support**: First-class support for side-by-side dataset comparison  
✅ **Name conflict resolution**: Auto-rename with suffixes prevents duplicate names  

### 1.4 Recommended API Extensions

```python
# Add method to check if limit is approaching (for proactive warnings)
def is_near_limit(self, threshold: int = 8) -> bool:
    """Check if dataset count is approaching limit."""
    return len(self.datasets) >= threshold

# Add method to get dataset count for status displays
def dataset_count(self) -> int:
    """Get current dataset count."""
    return len(self.datasets)

# Add method to validate dataset ID before operations
def has_dataset(self, dataset_id: UUID) -> bool:
    """Check if dataset exists in session."""
    return any(d.id == dataset_id for d in self.datasets)
```

---

## 2. Dataset Model with Independent Operation State

### 2.1 Current Implementation (dataset.py:12-29)

```python
@dataclass
class Dataset:
    """Represents a loaded dataset."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    source: str = ""
    backend: str = ""
    frame: nw.LazyFrame | None = None
    original_frame: nw.LazyFrame | None = None  # For reset/undo
    schema: dict[str, str] = field(default_factory=dict)
    row_count: int = 0
    is_active: bool = False
    is_lazy: bool = True
    operation_history: list[Operation] = field(default_factory=list)
    current_frame: nw.LazyFrame | None = None
    checkpoints: dict[int, nw.LazyFrame] = field(default_factory=dict)
    checkpoint_interval: int = 10
```

### 2.2 Independent State Components

Each `Dataset` instance maintains:

1. **Operation History** (`operation_history: list[Operation]`):
   - All applied operations in sequence
   - Persists when dataset is inactive
   - Used for undo/redo and operation editing
   - Survives dataset switching

2. **Frame State** (`current_frame`, `original_frame`):
   - `original_frame`: Immutable reference to loaded data
   - `current_frame`: Result after applying operations
   - Checkpoints every 10 operations for efficient undo

3. **Execution State** (`is_lazy: bool`):
   - Per-dataset execution mode (lazy vs eager)
   - **Note**: Spec requires lazy/eager as session-wide toggle (FR-080 to FR-086)
   - **Recommendation**: Remove `is_lazy` from Dataset, manage at UI level

### 2.3 State Preservation During Switching

When switching from Dataset A to Dataset B:

```python
# In MainScreen.on_dataset_tabs_tab_changed (main_screen.py:112-119)
def on_dataset_tabs_tab_changed(self, message: DatasetTabs.TabChanged) -> None:
    """Handle tab change - update table view."""
    active_dataset = self.session.get_active_dataset()
    
    # Load new dataset (preserves old dataset's state automatically)
    if active_dataset and self.dataset_table_left:
        self.dataset_table_left.load_dataset(active_dataset)
```

**Key Insight**: State preservation is **implicit** - no explicit save/restore needed because:
- Each `Dataset` instance holds its own state
- `DatasetTable.load_dataset()` only updates display widgets
- Switching datasets doesn't modify the inactive dataset's state

### 2.4 Operation State for Lazy/Eager Mode

**Current Limitation**: The spec requires separate queued/executed operation lists (FR-080 to FR-085), but the current model only has `operation_history`.

**Recommended Extension**:

```python
@dataclass
class Dataset:
    # ... existing fields ...
    
    # Replace single operation_history with split queues
    queued_operations: list[Operation] = field(default_factory=list)
    executed_operations: list[Operation] = field(default_factory=list)
    
    # Remove is_lazy (managed at session/UI level instead)
    
    def queue_operation(self, operation: Operation) -> None:
        """Add operation to queue (lazy mode)."""
        self.queued_operations.append(operation)
    
    def execute_next_queued(self) -> bool:
        """Execute next queued operation (Ctrl+E)."""
        if not self.queued_operations:
            return False
        
        op = self.queued_operations.pop(0)
        self.apply_operation(op)
        self.executed_operations.append(op)
        return True
    
    def execute_all_queued(self) -> int:
        """Execute all queued operations (Ctrl+Shift+E)."""
        count = 0
        while self.queued_operations:
            if self.execute_next_queued():
                count += 1
            else:
                break
        return count
    
    def clear_queued(self) -> int:
        """Clear all queued operations without executing."""
        count = len(self.queued_operations)
        self.queued_operations.clear()
        return count
```

**Migration Path**:
1. Rename `operation_history` → `executed_operations`
2. Add `queued_operations` list
3. Update `apply_operation()` to work with both modes
4. Add state transition methods for executing queued operations

---

## 3. UI Widget Selection: Tabs vs ListView

### 3.1 Current Implementation: Tabs (DatasetTabs widget)

**Implementation**: dataset_tabs.py:12-230

#### Features:
- Horizontal tab bar at top of screen
- Displays up to 10 dataset tabs
- Highlights active dataset with `variant="primary"`
- Click or keyboard navigation (Tab/Shift+Tab)
- Close button for each tab (Ctrl+W)
- Truncates long dataset names (20 chars max)

#### Example Layout:
```
┌─────────────────────────────────────────────────────────┐
│ Datasets: [sales.csv*] [users.json] [metrics.parquet] ▼│
└─────────────────────────────────────────────────────────┘
```

### 3.2 Alternative: ListView (Not Implemented)

A ListView-based approach would look like:
```
┌────────────────────┐
│ Datasets           │
│ ┌────────────────┐ │
│ │ * sales.csv    │ │  ← Active (highlighted)
│ │   users.json   │ │
│ │   metrics.pqt  │ │
│ └────────────────┘ │
└────────────────────┘
```

### 3.3 Comparison Analysis

| Criteria | Tabs (Current) | ListView |
|----------|----------------|----------|
| **Screen real estate** | Minimal (1-2 lines) | Requires dedicated sidebar (15-20% width) |
| **Visibility** | All datasets visible at once | Scrollable list, 5-7 visible |
| **Navigation** | Tab/Shift+Tab (2 keys) | Up/Down + Enter (3 keys) |
| **Visual scan** | Horizontal scan (fast) | Vertical scan (slower) |
| **Context display** | Limited (name only) | Could show metadata (row count, ops) |
| **10-dataset limit** | Fits comfortably | Better for >10 (but not needed) |
| **Keyboard efficiency** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Screen complexity** | ⭐⭐⭐⭐ (simple) | ⭐⭐ (adds sidebar) |

### 3.4 Recommendation: Keep Tabs

**Rationale**:
1. **Space-efficient**: Leaves maximum space for data table (primary focus)
2. **Fast navigation**: Tab/Shift+Tab cycle is intuitive and minimal-keystroke
3. **Visual clarity**: All datasets visible without scrolling
4. **Spec alignment**: "visual indicators (tabs or list)" (FR-063) - tabs chosen
5. **10-dataset limit**: Tabs comfortably fit 10 items in typical terminal width

**Enhancement Suggestions** for tabs:
```python
# Add dataset metadata to tab tooltip (on hover or via keybinding)
def _create_tab_label(self, dataset: Dataset) -> str:
    """Create tab label with metadata."""
    name = dataset.name[:20] + "..." if len(dataset.name) > 20 else dataset.name
    op_count = len(dataset.operation_history)
    return f"{name} ({op_count} ops)" if op_count > 0 else name
```

---

## 4. Memory Management and 10-Dataset Limit

### 4.1 Current Limit Enforcement

#### Hard Limit (dataset_session.py:19-22)
```python
def add_dataset(self, dataset: Dataset) -> bool:
    """Add dataset to session."""
    if len(self.datasets) >= self.max_datasets:
        return False  # Hard rejection
```

#### UI Feedback (main_screen.py:138)
```python
if len(self.session.datasets) < 2 and not self.split_pane_active:
    self.notify("Need at least 2 datasets for split pane mode", severity="warning")
```

### 4.2 Memory Warning Patterns

**Recommendation**: Add proactive warnings as user approaches limit

#### Implementation Strategy:

```python
# In KittiwakeApp.load_dataset_async() after successful load
def _check_dataset_limit_warnings(self) -> None:
    """Show warnings as user approaches dataset limit."""
    count = self.session.dataset_count()
    remaining = self.session.max_datasets - count
    
    if remaining == 2:
        self.notify(
            f"Approaching dataset limit ({count}/{self.session.max_datasets} loaded). "
            f"Close unused datasets before loading more.",
            severity="warning",
            timeout=5
        )
    elif remaining == 1:
        self.notify(
            f"Dataset limit almost reached ({count}/{self.session.max_datasets} loaded). "
            f"One slot remaining.",
            severity="warning",
            timeout=8
        )
    elif remaining == 0:
        self.notify(
            f"Dataset limit reached ({count}/{self.session.max_datasets} loaded). "
            f"Close a dataset before loading another.",
            severity="error",
            timeout=10
        )
```

### 4.3 Graceful Load Rejection

When user attempts to load 11th dataset:

```python
# In KittiwakeApp._on_dataset_loaded()
def _on_dataset_loaded(self, dataset: Dataset) -> None:
    """Handle dataset loaded (runs in main thread)."""
    try:
        success = self.session.add_dataset(dataset)
        
        if not success:
            # Show actionable error with dataset management options
            self.notify_error(
                f"Cannot load {dataset.name}: Dataset limit reached "
                f"({self.session.max_datasets} maximum).\n\n"
                f"Actions:\n"
                f"• Press Ctrl+W to close current dataset\n"
                f"• Press Tab to switch to other datasets\n"
                f"• Press ? for help",
                title="Dataset Limit Reached"
            )
            return
        
        # Success - update UI
        self.main_screen.load_dataset(dataset)
        
        # Check for warnings
        self._check_dataset_limit_warnings()
        
    except Exception as e:
        self.notify_error(f"Error displaying dataset: {e}", title="Display Error")
```

### 4.4 CLI Behavior for Bulk Loading

When user runs `kw load file1.csv file2.csv ... file11.csv` (>10 files):

```python
# In cli.py or app.py
def _load_initial_datasets(self) -> None:
    """Load datasets from CLI arguments."""
    total = len(self.initial_load_paths)
    
    if total > self.session.max_datasets:
        # Warn about excess files
        excess = total - self.session.max_datasets
        self.notify(
            f"Warning: {total} files specified, but limit is {self.session.max_datasets}. "
            f"Loading first {self.session.max_datasets} files. "
            f"{excess} file(s) skipped: {', '.join(self.initial_load_paths[self.session.max_datasets:])[:100]}...",
            severity="warning",
            timeout=15
        )
        # Truncate to limit
        self.initial_load_paths = self.initial_load_paths[:self.session.max_datasets]
    
    # Load allowed files
    for path in self.initial_load_paths:
        self.run_worker(self.load_dataset_async(path), exclusive=False)
```

### 4.5 Memory Estimation Display

**Future Enhancement**: Show estimated memory usage in footer or status bar

```python
# Add to DatasetSession
def estimate_memory_mb(self) -> float:
    """Estimate total memory usage of all datasets."""
    total_mb = 0.0
    for dataset in self.datasets:
        if dataset.frame:
            # Rough estimate: row_count * column_count * 8 bytes
            cols = len(dataset.schema)
            total_mb += (dataset.row_count * cols * 8) / (1024 * 1024)
    return total_mb

# Display in footer
f"Datasets: {count}/10 | Memory: ~{session.estimate_memory_mb():.1f} MB"
```

---

## 5. State Switching Implementation Pattern

### 5.1 Current Tab Switching Flow

```
User: Press Tab key
  ↓
MainScreen.action_next_dataset()
  ↓
DatasetTabs.next_tab()
  ↓
DatasetTabs.switch_to(next_index)
  ↓
DatasetSession.set_active_dataset(dataset.id)
  ↓
DatasetTabs.TabChanged message posted
  ↓
MainScreen.on_dataset_tabs_tab_changed(message)
  ↓
DatasetTable.load_dataset(active_dataset)
  ↓
Operations sidebar refreshes with active_dataset.operation_history
```

**Key Insight**: State switching is **declarative** - the UI reacts to the new active dataset without manually saving/restoring state.

### 5.2 Widget State Management

#### DatasetTable Widget (dataset_table.py)
```python
class DatasetTable(Container):
    dataset: Dataset | None = None  # Reactive variable
    
    def load_dataset(self, dataset: Dataset) -> None:
        """Load dataset and display first page."""
        self.dataset = dataset
        self._refresh_table()
    
    def watch_dataset(self, old: Dataset | None, new: Dataset | None) -> None:
        """React to dataset changes."""
        if new:
            self._load_page(0)
```

**State Preservation**: When switching from Dataset A to B:
- Dataset A: `dataset_table.dataset = None` (widget reference cleared)
- Dataset A's internal state (`operation_history`, `current_frame`) **unchanged**
- Dataset B: `dataset_table.dataset = dataset_b` (widget points to B)
- Dataset B's state is displayed

#### Operations Sidebar (operations_sidebar.py)
```python
class OperationsSidebar(Container):
    def refresh_operations(self, operations: list[Operation]) -> None:
        """Refresh operations list display."""
        self._clear_list()
        for op in operations:
            self._add_operation_item(op)
```

**State Preservation**: The sidebar displays a **read-only view** of the active dataset's operations. No state is stored in the sidebar itself.

### 5.3 State Consistency Guarantees

✅ **Independent operation histories**: Each dataset has its own `operation_history` list  
✅ **Automatic preservation**: Switching datasets doesn't trigger any save/restore logic  
✅ **No shared state**: Datasets don't reference each other or share dataframes  
✅ **UUID-based identity**: Dataset identity persists even if order changes  

---

## 6. Recommendations Summary

### 6.1 DatasetSession API

**Status**: ✅ Solid foundation, minor extensions recommended

**Recommended Additions**:
```python
class DatasetSession:
    def is_near_limit(self, threshold: int = 8) -> bool: ...
    def dataset_count(self) -> int: ...
    def has_dataset(self, dataset_id: UUID) -> bool: ...
```

### 6.2 Dataset Model for Lazy/Eager Operations

**Status**: ⚠️ Requires modification to support queued/executed split

**Required Changes**:
```python
@dataclass
class Dataset:
    # Split operation_history into:
    queued_operations: list[Operation] = field(default_factory=list)
    executed_operations: list[Operation] = field(default_factory=list)
    
    # Add state transition methods:
    def queue_operation(self, operation: Operation) -> None: ...
    def execute_next_queued(self) -> bool: ...
    def execute_all_queued(self) -> int: ...
    def clear_queued(self) -> int: ...
```

### 6.3 UI Widget Selection

**Status**: ✅ Tabs implementation is optimal

**Recommendation**: Keep `DatasetTabs` widget, add metadata tooltips

### 6.4 Memory Management

**Status**: ⚠️ Hard limit enforced, but warnings needed

**Recommended Additions**:
1. Proactive warnings at 8, 9, 10 datasets
2. Graceful rejection with actionable guidance
3. CLI bulk load truncation with warning
4. Optional memory estimation display

---

## 7. Final API Reference

### DatasetSession State Management

```python
from uuid import UUID
from dataclasses import dataclass, field
from .dataset import Dataset

@dataclass
class DatasetSession:
    """Manages collection of up to 10 loaded datasets."""
    
    datasets: list[Dataset] = field(default_factory=list)
    active_dataset_id: UUID | None = None
    max_datasets: int = 10
    split_pane_enabled: bool = False
    split_pane_datasets: tuple[UUID, UUID] | None = None
    
    # Core Operations
    def add_dataset(self, dataset: Dataset) -> bool:
        """Add dataset. Returns False if limit reached."""
    
    def remove_dataset(self, dataset_id: UUID) -> None:
        """Remove dataset and handle active/split pane cleanup."""
    
    def set_active_dataset(self, dataset_id: UUID) -> None:
        """Switch active dataset. Raises KeyError if not found."""
    
    def get_active_dataset(self) -> Dataset | None:
        """Get currently active dataset."""
    
    def get_dataset_by_id(self, dataset_id: UUID) -> Dataset | None:
        """Get dataset by UUID."""
    
    # Split Pane
    def enable_split_pane(self, dataset_id_1: UUID, dataset_id_2: UUID) -> None:
        """Enable split pane with two datasets."""
    
    def disable_split_pane(self) -> None:
        """Disable split pane mode."""
    
    # Utility (Recommended Extensions)
    def dataset_count(self) -> int:
        """Get current dataset count."""
        return len(self.datasets)
    
    def is_near_limit(self, threshold: int = 8) -> bool:
        """Check if approaching dataset limit."""
        return len(self.datasets) >= threshold
    
    def has_dataset(self, dataset_id: UUID) -> bool:
        """Check if dataset exists."""
        return any(d.id == dataset_id for d in self.datasets)
```

### Dataset Model with Independent State

```python
from uuid import UUID, uuid4
from dataclasses import dataclass, field
import narwhals as nw
from .operations import Operation

@dataclass
class Dataset:
    """Represents a loaded dataset with independent operation state."""
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    source: str = ""
    backend: str = ""
    
    # Data frames
    frame: nw.LazyFrame | None = None
    original_frame: nw.LazyFrame | None = None
    current_frame: nw.LazyFrame | None = None
    
    # Metadata
    schema: dict[str, str] = field(default_factory=dict)
    row_count: int = 0
    
    # State
    is_active: bool = False
    is_lazy: bool = True
    
    # Operations (RECOMMENDED: Split into queued/executed)
    operation_history: list[Operation] = field(default_factory=list)
    # OR (for lazy/eager mode support):
    # queued_operations: list[Operation] = field(default_factory=list)
    # executed_operations: list[Operation] = field(default_factory=list)
    
    # Undo/Redo
    checkpoints: dict[int, nw.LazyFrame] = field(default_factory=dict)
    checkpoint_interval: int = 10
    
    # Core Operations
    def apply_operation(self, operation: Operation) -> None:
        """Apply operation and update history."""
    
    def undo(self) -> bool:
        """Undo last operation."""
    
    def get_page(self, page_num: int, page_size: int = 500) -> nw.DataFrame | None:
        """Get paginated data for display."""
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
```

### State Switching Pattern

```python
# 1. User triggers dataset switch (Tab key)
active_index = (current_index + 1) % len(session.datasets)
dataset = session.datasets[active_index]

# 2. Update session state
session.set_active_dataset(dataset.id)

# 3. Update UI (reactive)
dataset_table.load_dataset(dataset)
operations_sidebar.refresh_operations(dataset.operation_history)

# 4. State preservation is automatic - no save/restore needed
```

### Memory Warning Pattern

```python
def check_dataset_limit_warnings(session: DatasetSession) -> str | None:
    """Return warning message if approaching limit."""
    count = session.dataset_count()
    remaining = session.max_datasets - count
    
    if remaining <= 0:
        return (
            f"Dataset limit reached ({count}/{session.max_datasets}). "
            f"Close a dataset (Ctrl+W) before loading more."
        )
    elif remaining == 1:
        return f"Almost at limit ({count}/{session.max_datasets}). One slot remaining."
    elif remaining == 2:
        return f"Approaching limit ({count}/{session.max_datasets}). 2 slots remaining."
    
    return None
```

---

## 8. Implementation Checklist

### Phase 1: Dataset Model Update (for Lazy/Eager Mode)
- [ ] Split `operation_history` into `queued_operations` and `executed_operations`
- [ ] Add `queue_operation()` method
- [ ] Add `execute_next_queued()` method
- [ ] Add `execute_all_queued()` method
- [ ] Add `clear_queued()` method
- [ ] Update `apply_operation()` to respect execution mode
- [ ] Update operations sidebar to display queued vs executed with icons

### Phase 2: DatasetSession Utility Methods
- [ ] Add `dataset_count()` method
- [ ] Add `is_near_limit()` method
- [ ] Add `has_dataset()` method

### Phase 3: Memory Warning System
- [ ] Add `_check_dataset_limit_warnings()` to KittiwakeApp
- [ ] Show warnings at 8, 9, 10 datasets
- [ ] Update `_on_dataset_loaded()` to show limit rejection message
- [ ] Add CLI bulk load truncation with warning
- [ ] (Optional) Add memory estimation to footer

### Phase 4: Tab Widget Enhancements
- [ ] Add operation count to tab labels (e.g., "sales.csv (5 ops)")
- [ ] Add tooltip/help text showing dataset metadata
- [ ] Improve visual distinction for active tab

---

## 9. References

### Codebase Files
- `src/kittiwake/models/dataset_session.py` - Session management
- `src/kittiwake/models/dataset.py` - Dataset entity with state
- `src/kittiwake/widgets/dataset_tabs.py` - Tab UI widget
- `src/kittiwake/screens/main_screen.py` - State switching logic
- `src/kittiwake/app.py` - Dataset loading and notifications

### Specification Documents
- `specs/001-tui-data-explorer/spec.md` - Functional requirements (FR-051 to FR-063, FR-080 to FR-086)
- `specs/001-tui-data-explorer/data-model.md` - Entity definitions and relationships
- `specs/001-tui-data-explorer/contracts/saved-analysis-schema.sql` - Persistence schema

### Key Requirements
- **FR-053**: Support multiple datasets per session
- **FR-054**: One active dataset at a time
- **FR-055**: Keyboard shortcuts for dataset switching (Tab/Shift+Tab)
- **FR-059**: Independent operation state per dataset
- **FR-060**: Preserve state when switching
- **FR-063**: Maximum 10 datasets with visual indicators
- **FR-080 to FR-086**: Lazy/eager execution mode with queued/executed operations

---

**Report Version**: 1.0  
**Author**: Research Agent  
**Next Steps**: Review with implementation team, prioritize Phase 1 (lazy/eager support) and Phase 3 (memory warnings)
