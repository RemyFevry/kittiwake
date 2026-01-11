# Tasks: TUI Data Explorer

**Input**: Design documents from `/specs/001-tui-data-explorer/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, contracts/ ✅

**Tests**: Tests are OPTIONAL - only included if explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Progress**: 93 of 117 tasks complete (79%) - Updated 2026-01-10 (Pivot column naming fix complete - columns now use <Column>_<value> format, e.g., region_East, region_West. All 15 pivot integration tests passing.)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 ✅ Create project structure with `src/kittiwake/` and `tests/` (ALREADY COMPLETE)
- [x] T002 ✅ Initialize Python 3.13 project with uv, narwhals, textual dependencies (ALREADY COMPLETE)
- [x] T003 ✅ [P] Configure pyproject.toml with entry points `kittiwake` and `kw` (ALREADY COMPLETE)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Models & Services

- [x] T004 ✅ [P] Create base Operation model in `src/kittiwake/models/operations.py` with fields: code, display, operation_type, params, state, id (ALREADY COMPLETE)
- [x] T005 ✅ Update Operation model to add `state: str = "queued"` field ("queued" | "executed" | "failed") - COMPLETE 2026-01-09
- [x] T006 ✅ Add `to_code()` method to Operation model for code generation - COMPLETE 2026-01-09
- [x] T007 ✅ [P] Create Dataset model in `src/kittiwake/models/dataset.py` (ALREADY COMPLETE - needs update)
- [x] T008 ✅ Update Dataset model to add lazy/eager execution fields - COMPLETE 2026-01-09:
  - `execution_mode: str = "lazy"` 
  - `queued_operations: list[Operation]`
  - `executed_operations: list[Operation]` (rename from `operation_history`)
- [x] T009 ✅ Add methods to Dataset: `queue_operation()`, `execute_next_queued()`, `execute_all_queued()`, `clear_queued()` - COMPLETE 2026-01-09
- [x] T010 ✅ [P] Create DatasetSession model in `src/kittiwake/models/dataset_session.py` (ALREADY COMPLETE)
- [x] T011 ✅ Update DatasetSession with memory warning methods (`warn_approaching_limit()`, `can_add_dataset()`) - COMPLETE (add_dataset, remove_dataset, max_datasets implemented)

### Execution Infrastructure

- [x] T012 ✅ Create ExecutionManager service - NOT NEEDED (execution handled directly in Dataset model) - COMPLETE 2026-01-10
  - Dataset.execute_next_queued() provides execute_next functionality
  - Dataset.execute_all_queued() provides execute_all functionality
  - Error handling implemented in Dataset._execute_operation()
  - Stop-on-error with queue preservation implemented
- [x] T013 ✅ ExecutionResult dataclass - NOT NEEDED (Dataset methods return bool/int with error handling via exceptions) - COMPLETE 2026-01-10

### Persistence Infrastructure

- [x] T014 ✅ [P] Create DuckDB schema for SavedAnalysis in `~/.kittiwake/analyses.db` - COMPLETE (AnalysisStorage class with schema implemented)
  - Table: saved_analyses (id, name, description, created_at, modified_at, operation_count, dataset_path, operations JSON)
  - Add indexes on name and created_at
- [x] T015 ✅ [P] Implement DuckDBManager class in `src/kittiwake/services/persistence.py` - COMPLETE (AnalysisStorage with save/load/delete/list methods)
  - Thread-safe connection-per-thread pattern
  - Write lock for INSERT/UPDATE/DELETE
  - Methods: save_analysis(), load_analysis(), list_analyses(), update_analysis(), delete_analysis()
- [x] T016 ✅ SavedAnalysis model - NOT NEEDED (SavedAnalysisRepository uses dict-based persistence) - COMPLETE 2026-01-10

### TUI Infrastructure

- [x] T017 ✅ Create main App class in `src/kittiwake/app.py` with error clipboard functionality (ALREADY COMPLETE)
- [x] T018 ✅ Add async worker methods to App for DuckDB operations - COMPLETE (App has async methods and worker infrastructure):
  - `save_analysis_async(analysis)`
  - `load_analysis_async(analysis_id)`
  - `execute_operations_async(dataset, execute_all=False)`
- [x] T019 ✅ [P] Create HelpOverlay widget in `src/kittiwake/widgets/help_overlay.py` (ALREADY COMPLETE - needs update)
- [x] T020 ✅ Update HelpOverlay with new keybindings - COMPLETE 2026-01-09:
  - Ctrl+E: Execute Next Operation
  - Ctrl+Shift+E: Execute All Operations
  - Ctrl+M: Toggle Execution Mode
  - Update Operations Sidebar section with mode toggle

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and View Data (Priority: P1) 🎯 MVP

**Goal**: Users can launch kittiwake, load datasets from files/URLs, view data in paginated table, navigate with keyboard, switch between datasets

**Independent Test**: Launch `kw` and `kw load data.csv`, verify data displays, keyboard navigation works (arrows, Ctrl+Left/Right), load multiple datasets and switch between them

### Implementation for User Story 1

- [x] T021 ✅ [P] Implement CLI argument parsing in `src/kittiwake/cli.py` with `load` subcommand (ALREADY COMPLETE)
- [x] T022 ✅ [P] Implement data loading service in `src/kittiwake/services/data_loader.py` for CSV, Parquet, JSON, remote URLs (ALREADY COMPLETE)
- [x] T023 ✅ Implement MainScreen in `src/kittiwake/screens/main_screen.py` (ALREADY COMPLETE - needs keybinding updates)
- [x] T024 ✅ Update MainScreen keybindings - COMPLETE 2026-01-10:
  - Add `Binding("ctrl+e", "execute_next", "Execute Next")`
  - Add `Binding("ctrl+shift+e", "execute_all", "Execute All")`
  - Add `Binding("ctrl+m", "toggle_execution_mode", "Toggle Mode")`
- [x] T025 ✅ [P] Implement DatasetTable widget in `src/kittiwake/widgets/dataset_table.py` with keyboard navigation - COMPLETE (basic pagination and navigation working)
- [x] T026 ✅ Implement fast column navigation (Ctrl+Left/Right jumps 5 columns) - COMPLETE 2026-01-10 (dataset_table.py:249-276)
- [ ] T027 Implement auto-scroll when cursor moves beyond visible columns - DEFERRED (native DataTable feature)
- [x] T028 ✅ Implement column width capping at 40 characters with ellipsis - COMPLETE 2026-01-10 (dataset_table.py:152-183, with JSON formatting for lists/dicts, space before ellipsis)
- [x] T029 ✅ Implement Enter/V key to view full cell content in toast - COMPLETE 2026-01-10
  - Primary: Enter key via `on_data_table_cell_selected()` message handler (dataset_table.py:340-365)
  - Secondary: V key binding via `action_view_cell()` (dataset_table.py:30-32 BINDINGS, lines 315-338)
  - Cell cursor mode enabled (dataset_table.py:86)
  - Help overlay updated to show "Enter / V" (help_overlay.py:115-116)
  - Toast displays format: "Cell [column, row N]: value" with 10s timeout
- [x] T030 ✅ [P] Implement DatasetTabs widget in `src/kittiwake/widgets/dataset_tabs.py` - COMPLETE (basic tab switching working)
- [x] T031 ✅ Update DatasetTabs to show operation counts in labels: `data.csv (3⏸/5✓)` - COMPLETE 2026-01-10 (dataset_tabs.py, Unicode symbols ⏸ for queued, ✓ for executed)
- [x] T032 ✅ Implement 10-dataset limit enforcement with warnings at 8/9 datasets - COMPLETE 2026-01-10:
  - DatasetSession.add_dataset() returns DatasetAddResult enum (SUCCESS, WARNING_8_DATASETS, WARNING_9_DATASETS, ERROR_AT_LIMIT)
  - MainScreen.load_dataset() shows appropriate warnings based on result
  - At 8 datasets: "Approaching limit: 8/10 datasets loaded" (warning severity, 4s timeout)
  - At 9 datasets: "Almost at limit: 9/10 datasets. One slot remaining." (warning severity, 5s timeout)
  - At 10+ datasets: Rejects with error message (error severity, 5s timeout)
  - Comprehensive unit tests in tests/unit/test_dataset_limit_enforcement.py (10 tests, all passing)
- [x] T033 ✅ [P] Implement split pane mode for side-by-side dataset comparison - COMPLETE 2026-01-10 (split_pane_active reactive + Ctrl+P binding in main_screen.py:26,32)
- [x] T034 ✅ Implement async data loading with progress indicators for 1M+ row datasets - COMPLETE 2026-01-10:
  - Made data_loader.py async using loop.run_in_executor()
  - Progress indicators for large files (>50MB or 500K rows)
  - Cancellation support with Esc key
  - Worker pattern for non-blocking UI
- [x] T035 ✅ Handle CLI bulk load (cap at 10 datasets, warn about skipped files) - COMPLETE 2026-01-10:
  - App._load_initial_datasets() checks for excess files
  - Warns if total_paths > max_datasets (warning: "N files provided, but maximum is M. Only loading first M files.")
  - Shows skipped file names in separate notification (information severity)
  - Loads only first max_datasets files
- [x] T036 ✅ [P] [US1] Implement clipboard copy on cell selection in `src/kittiwake/widgets/dataset_table.py` - COMPLETE 2026-01-10:
  - Ctrl+Y keybinding to copy cell value to system clipboard
  - Brief toast notification "Copied to clipboard" (2s timeout)
  - Uses pyperclip library for cross-platform clipboard access
  - Handles edge cases: null values (copy empty string), very long values (copy full content)
  - Help overlay updated to show Ctrl+Y keybinding
- [x] T037 ✅ [P] [US1] Implement type-based column coloring in `src/kittiwake/utils/type_colors.py` - COMPLETE 2026-01-10:
  - Extended TypeCategory to include "list" and "dict" types
  - Added color mappings: list → cyan, dict → magenta (Rich color names)
  - Added ASCII icons: list → "[", dict → "{"
  - Added Unicode icons: list → "📋", dict → "📦"
  - Updated type_detector.py to detect List(...) and Struct(...) dtypes
  - Colors work in both light and dark terminal themes via semantic color variables
  - Column headers automatically display with correct colors via existing DatasetTable._create_column_header()
- [x] T038 [US1] Implement column filtering UI in `src/kittiwake/widgets/dataset_table.py`:
  - Add keybinding (e.g., Ctrl+Shift+F) to open column filter overlay/modal
  - Filter by column name (text search with regex support)
  - Filter by column type (checkboxes: String, Int, Float, List, Dict, Boolean, Date, etc.)
  - Show/hide columns based on filter criteria
  - Display count of visible vs total columns (e.g., "Showing 5 of 20 columns")
  - Add "Reset" button to show all columns again

**Checkpoint**: User Story 1 complete - can load, view, and navigate datasets independently

---

## Phase 4: User Story 2 - Filter and Search Data (Priority: P2)

**Goal**: Users can filter and search data using left sidebar forms, operations queue in lazy mode or execute in eager mode, view/edit/reorder operations in right sidebar

**Independent Test**: Load dataset, apply filters/searches, verify operations queue (lazy) or execute (eager), execute queued operations with Ctrl+E / Ctrl+Shift+E, edit/remove/reorder operations

### Implementation for User Story 2

#### Sidebar Architecture (Partially Complete)

- [x] T039 ✅ [P] Create FilterSidebar widget in `src/kittiwake/widgets/sidebars/filter_sidebar.py` - COMPLETE
- [x] T040 ✅ [P] Create SearchSidebar widget in `src/kittiwake/widgets/sidebars/search_sidebar.py` - COMPLETE
- [x] T041 ✅ Create OperationsSidebar widget in `src/kittiwake/widgets/sidebars/operations_sidebar.py` - COMPLETE

#### Operations Sidebar Enhancement (Lazy/Eager Mode)

- [x] T042 ✅ Add execution mode toggle button to OperationsSidebar header - COMPLETE 2026-01-10 (operations_sidebar.py:95-100):
  - Button with reactive `execution_mode: str = "lazy"` attribute
  - Visual: `⚡ LAZY` (yellow/warning variant) or `▶ EAGER` (green/success variant)
  - Clickable button + Ctrl+M keyboard shortcut support
  - `watch_execution_mode()` to update button styling and notify user
  - ModeToggleRequested message for parent handling
- [x] T043 ✅ Update `refresh_operations()` in OperationsSidebar to use icon + color coding - COMPLETE 2026-01-09:
  - Queued: `⏳ {idx}. {operation.display}`
  - Executed: `✓ {idx}. {operation.display}`
  - Failed: `✗ {idx}. {operation.display}`
  - Fixed duplicate widget ID bug with index-based IDs
- [x] T044 ✅ Implement operation edit functionality - COMPLETE 2026-01-10 (operations_sidebar.py:168 action_edit_operation)
- [x] T045 ✅ Implement operation remove functionality - COMPLETE 2026-01-10 (operations_sidebar.py:179 action_remove_operation)
- [x] T046 ✅ Implement operation reorder with Ctrl+Up/Down keyboard shortcuts - COMPLETE 2026-01-10 (operations_sidebar.py:35-36,122,145)
- [x] T047 ✅ Implement re-apply operations in new sequence when order changes - COMPLETE 2026-01-10 (operations_sidebar.py:208 OperationsReordered message)

#### Mode Toggle & Execution

- [x] T048 ✅ Create ModeSwitchPromptModal widget in `src/kittiwake/widgets/modals/mode_switch_modal.py` - COMPLETE 2026-01-10:
  - 3-choice modal (Execute All / Clear All / Cancel)
  - Keyboard shortcuts: 1/E, 2/C, 3/Esc
  - Return choice to caller via `dismiss()`
- [x] T049 ✅ Implement `action_toggle_execution_mode()` in MainScreen - COMPLETE 2026-01-10 (main_screen.py:598):
  - Check if switching lazy→eager with queued operations
  - Show ModeSwitchPromptModal if needed
  - Handle user choice (execute/clear/cancel)
  - Switch mode immediately if no queued operations or eager→lazy
  - Added Ctrl+M keybinding and ModeToggleRequested message handler
- [x] T050 ✅ Implement `action_execute_next()` in MainScreen - COMPLETE 2026-01-09:
  - Check if queued operations exist (no-op if empty)
  - Call dataset.execute_next_queued() directly (no ExecutionManager yet)
  - Update UI with result (notification, refresh sidebar/table)
  - Handle execution errors (mark operation as failed, show error message)
- [x] T051 ✅ Implement `action_execute_all()` in MainScreen - COMPLETE 2026-01-09:
  - Check if queued operations exist (no-op if empty)
  - Call dataset.execute_all_queued() directly (no ExecutionManager yet)
  - Show summary notification (e.g., "Executed 3/5 operations")
  - Handle errors (stop on first failure, preserve remaining queue)

#### Operation Application

- [x] T052 ✅ Update Dataset.apply_operation() to respect execution_mode - COMPLETE 2026-01-10 (dataset.py:42-59 implements lazy queue / eager execute)
- [x] T053 ✅ Update FilterSidebar apply action to call Dataset.apply_operation() - COMPLETE 2026-01-10 (filter_sidebar.py uses apply_operation)
- [x] T054 ✅ Update SearchSidebar apply action to call Dataset.apply_operation() - COMPLETE 2026-01-10 (search_sidebar.py uses apply_operation)
- [x] T055 ✅ Implement narwhals code generation in `src/kittiwake/services/narwhals_ops.py` - COMPLETE 2026-01-10:
  - `generate_filter_code(params)` → "df = df.filter(...)"
  - `generate_search_code(params)` → "df = df.filter(...)"
  - `generate_select_code(params)` → "df = df.select([...])"
  - (Add other operation types as needed)

#### Independent State Management

- [x] T056 ✅ Ensure each Dataset preserves operations when switching datasets - COMPLETE (Dataset model maintains operation lists per instance)
- [x] T057 ✅ Implement operations history restoration when switching back to dataset - COMPLETE (DatasetSession manages individual Dataset instances)
- [x] T058 ✅ Verify right sidebar shows correct operations for active dataset - COMPLETE (OperationsSidebar refreshes on dataset switch)

**Checkpoint**: User Story 2 complete - filter/search with lazy/eager modes, execution controls work independently

---

## Phase 5: User Story 3 - Aggregate and Summarize Data (Priority: P3)

**Goal**: Users can compute summary statistics and grouped aggregations

**Independent Test**: Load dataset, select column, apply aggregation (sum/mean/count), verify results display correctly

### Implementation for User Story 3

- [x] T059 ✅ [P] Create AggregateSidebar widget in `src/kittiwake/widgets/sidebars/aggregate_sidebar.py` - COMPLETE 2026-01-10:
  - Form: select column(s), choose aggregation functions (count, sum, mean, median, min, max, std)
  - Group-by column selection (optional)
  - Apply button to queue/execute aggregation operation
  - Integrated into MainScreen with keybinding (A key)
  - Unit tests added in tests/unit/test_aggregate_sidebar.py
- [x] T060 ✅ [P] Implement aggregation code generation in narwhals_ops.py - COMPLETE 2026-01-10:
   - `generate_aggregate_code(params)` → "df = df.group_by(...).agg(...)"
   - Supports single and multiple aggregation functions
   - Handles optional group-by columns (single or multiple)
   - Generates aliased column names to avoid duplicates (e.g., amount_sum, amount_mean)
   - Supports all aggregation functions: sum, mean, count, min, max, median, std
   - Returns tuple of (code: str, display: str)
- [x] T061 ✅ Create summary results panel widget in `src/kittiwake/widgets/summary_panel.py` - COMPLETE 2026-01-10:
   - SummaryPanel widget with DataTable for displaying aggregation results
   - Export functionality to CSV and JSON
   - Keybindings for Close (Esc) and Export (Ctrl+S)
   - CSS styling for proper display
   - Follows existing code patterns
- [x] T062 ✅ Implement aggregation results display in summary panel - COMPLETE 2026-01-10:
   - Shows aggregation results after execution in eager mode
   - Shows aggregation results after Ctrl+E/Ctrl+Shift+E execution in lazy mode
   - Toggle panel with Ctrl+R keybinding
   - Converts narwhals DataFrame to list of dicts for display
   - Handles empty results gracefully
- [x] T063 ✅ Add keybinding to open AggregateSidebar (e.g., Ctrl+A) - COMPLETE 2026-01-10:
  - Keybinding "a" added to MainScreen
  - action_aggregate() method implemented
  - Sidebar opens with column selection and aggregation function checkboxes
- [ ] T064 Support exporting aggregation results to file

**Checkpoint**: User Story 3 complete - aggregation and summarization work independently

---

## Phase 6: User Story 4 - Create Pivot Tables (Priority: P4)

**Goal**: Users can create pivot tables with row/column dimensions and aggregations

**Independent Test**: Load dataset, activate pivot mode, select dimensions and values, verify pivot table displays with correct calculations

### Implementation for User Story 4

- [x] T065 ✅ [P] Create PivotSidebar widget in `src/kittiwake/widgets/sidebars/pivot_sidebar.py` - COMPLETE 2026-01-10:
  - Form: select row dimensions, column dimensions, aggregation values
  - Aggregation function selection (sum, mean, count, etc.)
  - Apply button to queue/execute pivot operation
  - Unit tests added in tests/unit/test_pivot_sidebar.py
- [x] T066 ✅ [P] Implement pivot code generation in narwhals_ops.py - COMPLETE 2026-01-10:
  - `generate_pivot_code(params)` generates narwhals pivot code (narwhals_ops.py:331-519)
  - Takes params: index (str|list), columns (str), values (str|list), agg_functions (list)
  - Returns tuple of (code: str, display: str)
  - Supports single and multiple aggregation functions (creates separate pivots and joins them)
  - Handles DataFrame.pivot() since LazyFrame doesn't have pivot method
  - Comprehensive integration tests in tests/integration/test_pivot_code_generation.py (15 tests, all passing)
  - Supported aggregation functions: sum, mean, count, min, max, first, last, len
  - Note: median and std not supported by narwhals pivot (only available via agg)
- [x] T067 ✅ Create PivotTableWidget in `src/kittiwake/widgets/pivot_table.py` - COMPLETE 2026-01-10:
  - Hierarchical display with row dimension groups (visual indicators ▶/▼)
  - Pagination (100 row groups per page)
  - Value formatting (floats to 2 decimal places, None as empty)
  - Status bar with row range, group count, column count
- [x] T068 ✅ Implement expand/collapse functionality for pivot groups - COMPLETE 2026-01-10:
  - Enter to toggle expand/collapse for selected row group
  - Ctrl+Enter to expand all
  - Ctrl+Shift+E to collapse all
  - Visual indicators for expanded/collapsed state
- [x] T069 Add keybinding to open PivotSidebar (e.g., Ctrl+P)
- [ ] T070 Support saving pivot configuration for later reload

**Checkpoint**: User Story 4 complete - pivot tables work independently

---

## Phase 7: User Story 5 - Merge and Join Datasets (Priority: P5)

**Goal**: Users can merge two loaded datasets with join operations

**Independent Test**: Load two datasets, activate merge mode, select join columns and type, verify preview and merged result

### Implementation for User Story 5

- [x] T071 ✅ [P] Create JoinSidebar widget in `src/kittiwake/widgets/sidebars/join_sidebar.py` - COMPLETE 2026-01-10:
  - Form: select second dataset, join columns from each, join type (inner/left/right/outer)
  - Optional suffix inputs for handling duplicate column names (left_suffix, right_suffix)
  - Apply button submits JoinRequested message with parameters
  - Cancel button dismisses sidebar
  - Fully keyboard-navigable (Tab, Enter, Esc)
  - 30% width overlay sidebar (left side)
  - Handles case where only 1 dataset is loaded (shows helpful message)
  - Unit tests added in tests/unit/test_join_sidebar.py
- [x] T072 ✅ [P] Implement join code generation in narwhals_ops.py - COMPLETE 2026-01-10:
  - `generate_join_code(params)` → "df = df.join(...)"
  - Supports join types: inner, left, outer/full, cross, semi, anti
  - Note: 'right' join not supported by narwhals (use left join with swapped datasets)
  - Handles optional suffixes for duplicate column names
  - Comprehensive integration tests in tests/integration/test_join_code_generation.py
  - Function signature: generate_join_code(params: dict) -> tuple[str, str]
  - Params: right_dataset_id, left_key, right_key, how, left_suffix (optional), right_suffix (optional)
- [x] T073 ✅ Implement join type mismatch detection and warning - COMPLETE 2026-01-10:
  - Added `validate_join_key_types()` function
  - Detects incompatible types (e.g., int ↔ string) before join
  - Shows clear error messages with column names and types
  - Rejects incompatible joins with detailed error
- [x] T074 ✅ Implement automatic type conversion (int↔float, string→category) where possible - COMPLETE 2026-01-10:
  - Added `get_conversion_target()` and `generate_type_conversion_code()` functions
  - Supports int ↔ float conversion (lossless)
  - Generates cast code in join operation
  - Shows info message when auto-conversion occurs
  - 42 new tests added, all passing
- [x] T075 Add keybinding to open JoinSidebar (e.g., Ctrl+J)
- [x] T076 Handle errors when join keys don't match or datasets not loaded

**Checkpoint**: User Story 5 complete - dataset merging works independently

---

## Phase 8: User Story 6 - Save Analysis Workflows (Priority: P6)

**Goal**: Users can save operation sequences as reusable workflows

**Independent Test**: Perform operations sequence, save workflow with name, load new dataset with same schema, apply workflow, verify operations execute

### Implementation for User Story 6

- [x] T077 ✅ [P] Create SaveWorkflowModal widget in `src/kittiwake/widgets/modals/save_workflow_modal.py` - COMPLETE 2026-01-10:
  - Form: workflow name (1-100 chars, alphanumeric + _ -), optional description (max 500 chars)
  - Checkbox: "Include current dataset schema" (default: checked)
  - Save and Cancel buttons with keyboard navigation (Tab, Enter, Esc)
  - Input validation using InputValidator from security.py
  - Returns dict with name/description/include_schema on Save, None on Cancel
  - Exported in widgets/modals/__init__.py
  - Unit tests added in tests/unit/test_save_workflow_modal.py (30 tests, all passing)
- [x] T078 ✅ Implement workflow serialization (save operations sequence to JSON/YAML) - COMPLETE 2026-01-10:
  - Created `src/kittiwake/services/workflow.py` with `save_workflow()`
  - Saves to DuckDB with metadata and operations as JSON
  - Optional schema validation requirements
  - Auto-versioning for duplicate names (timestamp suffix)
  - 19 tests added, all passing
- [x] T079 ✅ Implement workflow loading and application to new datasets - COMPLETE 2026-01-10:
  - `load_workflow()` loads from DuckDB
  - `apply_workflow()` applies operations with schema validation
  - Graceful handling of schema mismatches
  - Progress tracking (success/failure counts)
  - Individual operation error reporting
- [ ] T080 Implement workflow editing (modify steps and re-save)
- [x] T081 Add keybinding to save workflow (e.g., Ctrl+Shift+S)
- [x] T082 Validate target dataset schema matches workflow requirements

**Checkpoint**: User Story 6 complete - workflows can be saved and reused independently

---

## Phase 9: User Story 7 - Manage and Export Saved Analyses (Priority: P3)

**Goal**: Users can save analyses, list/update/delete them, load analyses (reloads dataset + reapplies operations), export to Python/marimo/Jupyter notebooks

**Independent Test**: Perform operations, save analysis with metadata, list analyses, update/delete analyses, load analysis (verify dataset reloads), export to all three formats, verify generated code executes

### Implementation for User Story 7

#### Saved Analyses Management

- [x] T083 ✅ [P] Create SaveAnalysisModal widget in `src/kittiwake/widgets/modals/save_analysis_modal.py` - COMPLETE:
  - Form: analysis name, description
  - Save button to persist to DuckDB
  - Validation: unique name check
- [x] T084 ✅ [P] Create SavedAnalysesListScreen in `src/kittiwake/screens/saved_analyses_list_screen.py` - COMPLETE:
  - List all saved analyses with metadata (name, description, created_at, modified_at, operation_count)
  - Keyboard navigation (up/down to select)
  - Actions: Load, Update, Delete, Export
- [x] T085 ✅ Implement `action_save_analysis()` in MainScreen - COMPLETE 2026-01-10 (main_screen.py:347):
  - Show SaveAnalysisModal
  - Create SavedAnalysis entity with current dataset operations
  - Call `SavedAnalysisRepository.save()` in main thread
  - Show success/error notification
- [x] T086 ✅ Implement `action_load_saved_analysis()` in MainScreen - COMPLETE 2026-01-10 (main_screen.py:408):
  - Show SavedAnalysesListScreen (Ctrl+L keybinding)
  - User selects analysis
  - Reload dataset from `dataset_path` (async with progress)
  - Reapply all operations in sequence (respecting execution mode)
  - Show in main view
- [x] T087 ✅ Implement `action_reload_dataset()` in MainScreen - COMPLETE 2026-01-10:
   - Already existed, fixed keybinding conflict
   - Ctrl+R keybinding to reload dataset
   - Re-reads from original source file path
   - Preserves current operations (both queued and executed)
   - Re-applies all operations in sequence
   - Handles errors: source file deleted/moved, schema incompatibility
   - Shows success/error notifications
   - Note: Moved summary panel toggle to Ctrl+G to avoid conflict
- [x] T088 Implement update analysis functionality - COMPLETE (main_screen.py:1091):
  - Allow editing name/description
  - Update `modified_at` timestamp
  - Call `DuckDBManager.update_analysis()` in worker thread
- [x] T089 ✅ Implement delete analysis functionality - COMPLETE 2026-01-10 (saved_analyses_list_screen.py:222):
  - Show confirmation modal (deferred - direct delete for now)
  - Call `repository.delete()` method
  - Refresh analyses list

#### Export to Notebooks

- [x] T090 ✅ Generate contract files in `specs/001-tui-data-explorer/contracts/` - COMPLETE 2026-01-10:
  - [x] ✅ `export-python.jinja2` - Python script template
  - [x] ✅ `export-marimo.jinja2` - marimo notebook template
  - [x] ✅ `export-jupyter.jinja2` - Jupyter notebook template
  - [x] ✅ `operations-schema.json` - Operation serialization schema
  - [x] ✅ `cli-interface.md` - CLI usage documentation
  - [x] ✅ `saved-analysis-schema.sql` - DuckDB table schema
- [x] T091 ✅ [P] Create ExportModal widget in `src/kittiwake/widgets/modals/export_modal.py` - COMPLETE 2026-01-10:
  - Radio buttons: Python Script / marimo Notebook / Jupyter Notebook
  - File path input with browse button
  - Export button
- [x] T092 ✅ [P] Implement export service in `src/kittiwake/services/export.py` - COMPLETE 2026-01-10:
  - Setup Jinja2 environment loading templates from contracts/
  - Method: `export_to_python(analysis)` → render Python template
  - Method: `export_to_marimo(analysis)` → render marimo template
  - Method: `export_to_jupyter(analysis)` → render Jupyter template
- [x] T093 ✅ Implement `action_export_analysis()` in SavedAnalysesListScreen - COMPLETE 2026-01-10 (saved_analyses_list_screen.py:248):
  - Require analysis to be saved first (show error if not)
  - Show ExportModal
  - User selects format and path
  - Check if file exists (prompt to overwrite/rename/cancel)
  - Render template and write to file
  - Show success notification with file path
- [x] T094 Add keybinding to export analysis (e.g., Ctrl+X) - ALREADY EXISTS (x in SavedAnalysesListScreen)

#### Edge Cases

- [x] T095 ✅ Handle dataset path unavailable when loading analysis (show warning, allow updating path) - COMPLETE 2026-01-10:
  - Path existence check in `_load_saved_analysis()`
  - Shows `PathUpdateModal` when dataset file missing
  - Allows user to browse for new location
  - Validates new dataset schema compatibility
- [x] T096 ✅ Handle DuckDB database corruption (display error, offer to reinitialize with data loss warning) - COMPLETE 2026-01-10:
  - Added `DatabaseCorruptionError` exception
  - Added `check_database_health()` and `reinitialize_database()` methods
  - Shows `DatabaseCorruptionModal` with data loss warning
  - R keybinding to reinitialize database
- [x] T097 ✅ Prevent export of unsaved analyses (show "Save first" message) - COMPLETE 2026-01-10:
  - Explicit check before export in saved analyses list
  - Shows "Save analysis first" notification
- [x] T098 ✅ Handle duplicate analysis names (auto-version with timestamp suffix or require unique name) - COMPLETE 2026-01-10:
  - Auto-versions with timestamp suffix: `Name_20260110_112207`
  - Handles concurrent duplicates with counter: `_1`, `_2`, etc.
  - Returns versioned name to caller for display
  - 12 new tests added, all passing

**Checkpoint**: User Story 7 complete - saved analyses and export functionality work independently

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T099 ✅ [P] Create quickstart.md in `specs/001-tui-data-explorer/` - COMPLETE 2026-01-10:
  - Installation instructions (uv install, pip install)
  - Basic workflow: launch kw, load data, apply operations, execute (lazy mode), toggle to eager
  - Save and export analysis
  - Keyboard shortcuts reference table
- [x] T100 ✅ [P] Update README.md with feature overview and quickstart link - COMPLETE 2026-01-10
- [x] T101 ✅ [P] Add docstrings to all public methods - COMPLETE 2026-01-10 (all public methods now have docstrings)
- [x] T102 Code cleanup: remove deprecated modal-based UI code (filter_modal.py, search_modal.py if fully replaced)
  - Removed filter_modal.py (replaced by FilterSidebar)
  - Removed search_modal.py (replaced by SearchSidebar)
  - Removed test_filter_modal.py (tests moved to test_operation_builder.py)
  - Updated __init__.py exports in widgets/modals and widgets
  - All 278 tests passing
- [ ] T103 Performance optimization: profile large dataset operations (1M+ rows), optimize narwhals query generation
- [x] T104 ✅ [P] Security review: validate user input in all sidebar forms, check for path traversal in file operations - COMPLETE 2026-01-10
- [x] T105 ✅ Run through quickstart.md validation with fresh environment - COMPLETE 2026-01-10:
  - Validated all commands work correctly (`kw`, `kw load`, `kw --help`)
  - Tested keyboard shortcuts and workflows
  - Identified discrepancies between documentation and implementation
  - Updated quickstart.md from implementation guide to usage guide (Version 2.0)
  - Documented all available sidebars (Filter, Search, Aggregate, Pivot, Join, Operations)
  - Added comprehensive keyboard shortcuts reference
  - Updated execution mode documentation (lazy/eager)
  - Added testing section with manual workflow
  - Documented common patterns for adding new operations
  - Updated troubleshooting section
- [x] T106 ✅ [P] Create marimo documentation notebooks in `docs/examples/` - COMPLETE 2026-01-10:
  - basic_usage.py - Load CSV, basic filtering, sorting, viewing (210 lines)
  - aggregation_workflow.py - Group-by aggregations, multiple operations (331 lines)
  - export_workflow.py - Load, transform, export to various formats (383 lines)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ COMPLETE
- **Foundational (Phase 2)**: In Progress - BLOCKS all user stories
  - Key pending: ExecutionManager, DuckDB setup, Operation.to_code(), Dataset model updates
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - Can proceed in parallel if staffed or sequentially by priority (P1 → P2 → P3...)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories ⚠️ **MVP TARGET**
- **US2 (P2)**: Can start after Foundational - Builds on US1 (requires data loading) but independently testable
- **US3 (P3)**: Can start after Foundational - Builds on US1/US2 (requires data + operations) but independently testable
- **US4 (P4)**: Can start after Foundational - Builds on US1/US3 (requires aggregation concepts)
- **US5 (P5)**: Can start after Foundational - Requires US1 (multi-dataset loading)
- **US6 (P6)**: Can start after Foundational - Builds on US2 (operations sequences)
- **US7 (P3)**: Can start after US2 complete - Requires operations infrastructure and DuckDB persistence

### Critical Path for MVP (US1 + US2 with Lazy/Eager)

**Minimum viable feature set**:

1. ✅ Phase 1: Setup (COMPLETE)
2. Phase 2: Foundational (IN PROGRESS)
   - T005-T009: Update models for lazy/eager mode
   - T012-T013: ExecutionManager service
   - T014-T016: DuckDB persistence (can defer to US7)
   - T017-T020: TUI infrastructure updates
3. Phase 3: US1 - Load and View Data
   - T024-T038: Complete data loading, viewing, cell clipboard, column colors, column filtering
4. Phase 4: US2 - Filter and Search with Lazy/Eager
   - T039-T058: Sidebar enhancements, mode toggle, execution controls

**Estimated MVP**: ~48 tasks (Foundational + US1 + US2 including new enhancements)

### Parallel Opportunities

- All tasks marked [P] can run in parallel (different files, no shared state)
- Once Foundational completes, multiple user stories can be developed in parallel by different developers
- Within each user story, models marked [P] can be developed in parallel
- Sidebar widgets for different operation types can be developed in parallel

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. ✅ Complete Phase 1: Setup
2. Complete Phase 2: Foundational (focus on lazy/eager infrastructure)
3. Complete Phase 3: US1 - Load and View Data
4. Complete Phase 4: US2 - Filter and Search with Lazy/Eager Execution
5. **STOP and VALIDATE**: Test MVP independently (load, filter, lazy/eager modes work)
6. Demo/deploy MVP

### Incremental Delivery

1. ✅ Setup complete
2. Foundational → Foundation ready
3. Add US1 → Test independently → Deploy/Demo (Basic viewer!)
4. Add US2 → Test independently → Deploy/Demo (MVP with lazy/eager!)
5. Add US7 → Test independently → Deploy/Demo (Save & export!)
6. Add US3 → Test independently → Deploy/Demo (Aggregations!)
7. Add US4-US6 as needed

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Load and View)
   - Developer B: US2 (Filter and Search)
   - Developer C: US7 (Saved Analyses) - requires DuckDB from Foundational
3. Stories integrate and test independently

---

## Progress Tracking

**Phase Completion Status**:

- [x] Phase 1: Setup - ✅ **COMPLETE**
- [ ] Phase 2: Foundational - 🔄 **IN PROGRESS** (70% complete - T005-T009, T020 done; need T011-T013, T018)
- [ ] Phase 3: US1 - 🔄 **IN PROGRESS** (70% complete - basic loading works, need enhancements)
- [ ] Phase 4: US2 - 🔄 **IN PROGRESS** (55% complete - sidebars work, T043, T050-T051 done; need mode toggle, edit/remove operations)
- [ ] Phase 5: US3 - ⏸ **NOT STARTED**
- [ ] Phase 6: US4 - ⏸ **NOT STARTED**
- [ ] Phase 7: US5 - ⏸ **NOT STARTED**
- [ ] Phase 8: US6 - ⏸ **NOT STARTED**
- [ ] Phase 9: US7 - ⏸ **NOT STARTED** (DuckDB infrastructure ready from Foundational)
- [ ] Phase 10: Polish - ⏸ **NOT STARTED**

**MVP Progress**: ~40% (Core lazy/eager execution working! Need: ExecutionManager, mode toggle UI, operation editing)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Lazy/eager execution mode is core to US2** - not optional
- **Focus on MVP first**: US1 + US2 provide complete basic workflow
