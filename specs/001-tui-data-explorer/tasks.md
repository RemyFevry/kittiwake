# Tasks: TUI Data Explorer

**Input**: Design documents from `/specs/001-tui-data-explorer/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, contracts/ (to be generated in Phase 1)

**Tests**: Tests are OPTIONAL - only included if explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

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
- [ ] T011 Update DatasetSession with memory warning methods (`warn_approaching_limit()`, `can_add_dataset()`)

### Execution Infrastructure

- [ ] T012 Create ExecutionManager service in `src/kittiwake/services/execution_manager.py`
  - Implement `execute_next(dataset)` → ExecutionResult
  - Implement `execute_all(dataset, progress_callback)` → list[ExecutionResult]
  - Implement `_friendly_error(operation, error)` for user-friendly error messages
  - Implement stop-on-error with queue preservation
- [ ] T013 Create ExecutionResult dataclass with fields: success, operation, error_message, execution_time_ms

### Persistence Infrastructure

- [ ] T014 [P] Create DuckDB schema for SavedAnalysis in `~/.kittiwake/analyses.db`
  - Table: saved_analyses (id, name, description, created_at, modified_at, operation_count, dataset_path, operations JSON)
  - Add indexes on name and created_at
- [ ] T015 [P] Implement DuckDBManager class in `src/kittiwake/services/persistence.py`
  - Thread-safe connection-per-thread pattern
  - Write lock for INSERT/UPDATE/DELETE
  - Methods: save_analysis(), load_analysis(), list_analyses(), update_analysis(), delete_analysis()
- [ ] T016 Create SavedAnalysis model in `src/kittiwake/models/saved_analysis.py` (or add to operations.py)

### TUI Infrastructure

- [x] T017 ✅ Create main App class in `src/kittiwake/app.py` with error clipboard functionality (ALREADY COMPLETE)
- [ ] T018 Add async worker methods to App for DuckDB operations:
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
- [ ] T024 Update MainScreen keybindings:
  - Add `Binding("ctrl+e", "execute_next", "Execute Next")`
  - Add `Binding("ctrl+shift+e", "execute_all", "Execute All")`
  - Add `Binding("ctrl+m", "toggle_execution_mode", "Toggle Mode")`
- [x] T025 ✅ [P] Implement DatasetTable widget in `src/kittiwake/widgets/dataset_table.py` with keyboard navigation (ALREADY COMPLETE)
- [ ] T026 Implement fast column navigation (Ctrl+Left/Right jumps 5 columns)
- [ ] T027 Implement auto-scroll when cursor moves beyond visible columns
- [ ] T028 Implement column width capping at 40 characters with ellipsis
- [ ] T029 Implement Enter key to view full cell content in modal
- [x] T030 ✅ [P] Implement DatasetTabs widget in `src/kittiwake/widgets/dataset_tabs.py` (ALREADY COMPLETE - needs update)
- [ ] T031 Update DatasetTabs to show operation counts in labels: `data.csv (3⏸/5✓)`
- [ ] T032 Implement 10-dataset limit enforcement with warnings at 8/9 datasets
- [ ] T033 [P] Implement split pane mode for side-by-side dataset comparison
- [ ] T034 Implement async data loading with progress indicators for 1M+ row datasets
- [ ] T035 Handle CLI bulk load (cap at 10 datasets, warn about skipped files)

**Checkpoint**: User Story 1 complete - can load, view, and navigate datasets independently

---

## Phase 4: User Story 2 - Filter and Search Data (Priority: P2)

**Goal**: Users can filter and search data using left sidebar forms, operations queue in lazy mode or execute in eager mode, view/edit/reorder operations in right sidebar

**Independent Test**: Load dataset, apply filters/searches, verify operations queue (lazy) or execute (eager), execute queued operations with Ctrl+E / Ctrl+Shift+E, edit/remove/reorder operations

### Implementation for User Story 2

#### Sidebar Architecture (Partially Complete)

- [x] T036 ✅ [P] Create FilterSidebar widget in `src/kittiwake/widgets/sidebars/filter_sidebar.py` (ALREADY COMPLETE)
- [x] T037 ✅ [P] Create SearchSidebar widget in `src/kittiwake/widgets/sidebars/search_sidebar.py` (ALREADY COMPLETE)
- [x] T038 ✅ Create OperationsSidebar widget in `src/kittiwake/widgets/sidebars/operations_sidebar.py` (ALREADY COMPLETE - needs major update)

#### Operations Sidebar Enhancement (Lazy/Eager Mode)

- [ ] T039 Add execution mode toggle button to OperationsSidebar header:
  - Button with reactive `execution_mode: str = "lazy"` attribute
  - Visual: `⚡ LAZY` (yellow/warning variant) or `▶ EAGER` (green/success variant)
  - Clickable button + Ctrl+M keyboard shortcut support
  - `watch_execution_mode()` to update button styling and notify user
- [x] T040 ✅ Update `refresh_operations()` in OperationsSidebar to use icon + color coding - COMPLETE 2026-01-09:
  - Queued: `⏳ {idx}. {operation.display}`
  - Executed: `✓ {idx}. {operation.display}`
  - Failed: `✗ {idx}. {operation.display}`
  - Fixed duplicate widget ID bug with index-based IDs
- [ ] T041 Implement operation edit functionality (reopen left sidebar with pre-filled form)
- [ ] T042 Implement operation remove functionality with confirmation
- [ ] T043 Implement operation reorder with Ctrl+Up/Down keyboard shortcuts
- [ ] T044 Implement re-apply operations in new sequence when order changes

#### Mode Toggle & Execution

- [ ] T045 Create ModeSwitchPromptModal widget in `src/kittiwake/widgets/modals/mode_switch_modal.py`:
  - 3-choice modal (Execute All / Clear All / Cancel)
  - Keyboard shortcuts: 1/E, 2/C, 3/Esc
  - Return choice to caller via `dismiss()`
- [ ] T046 Implement `action_toggle_execution_mode()` in MainScreen:
  - Check if switching lazy→eager with queued operations
  - Show ModeSwitchPromptModal if needed
  - Handle user choice (execute/clear/cancel)
  - Switch mode immediately if no queued operations or eager→lazy
- [x] T047 ✅ Implement `action_execute_next()` in MainScreen - COMPLETE 2026-01-09:
  - Check if queued operations exist (no-op if empty)
  - Call dataset.execute_next_queued() directly (no ExecutionManager yet)
  - Update UI with result (notification, refresh sidebar/table)
  - Handle execution errors (mark operation as failed, show error message)
- [x] T048 ✅ Implement `action_execute_all()` in MainScreen - COMPLETE 2026-01-09:
  - Check if queued operations exist (no-op if empty)
  - Call dataset.execute_all_queued() directly (no ExecutionManager yet)
  - Show summary notification (e.g., "Executed 3/5 operations")
  - Handle errors (stop on first failure, preserve remaining queue)

#### Operation Application

- [ ] T049 Update Dataset.apply_operation() to respect execution_mode:
  - If `eager`: call ExecutionManager.execute_next() immediately
  - If `lazy`: queue operation with `state="queued"`, append to `queued_operations`
- [ ] T050 Update FilterSidebar apply action to call Dataset.apply_operation()
- [ ] T051 Update SearchSidebar apply action to call Dataset.apply_operation()
- [ ] T052 Implement narwhals code generation in `src/kittiwake/services/narwhals_ops.py`:
  - `generate_filter_code(params)` → "df = df.filter(...)"
  - `generate_search_code(params)` → "df = df.filter(...)"
  - `generate_select_code(params)` → "df = df.select([...])"
  - (Add other operation types as needed)

#### Independent State Management

- [ ] T053 Ensure each Dataset preserves operations when switching datasets
- [ ] T054 Implement operations history restoration when switching back to dataset
- [ ] T055 Verify right sidebar shows correct operations for active dataset

**Checkpoint**: User Story 2 complete - filter/search with lazy/eager modes, execution controls work independently

---

## Phase 5: User Story 3 - Aggregate and Summarize Data (Priority: P3)

**Goal**: Users can compute summary statistics and grouped aggregations

**Independent Test**: Load dataset, select column, apply aggregation (sum/mean/count), verify results display correctly

### Implementation for User Story 3

- [ ] T056 [P] Create AggregateSidebar widget in `src/kittiwake/widgets/sidebars/aggregate_sidebar.py`:
  - Form: select column(s), choose aggregation functions (count, sum, mean, median, min, max, std)
  - Group-by column selection (optional)
  - Apply button to queue/execute aggregation operation
- [ ] T057 [P] Implement aggregation code generation in narwhals_ops.py:
  - `generate_aggregate_code(params)` → "df = df.group_by(...).agg(...)"
- [ ] T058 Create summary results panel widget in `src/kittiwake/widgets/summary_panel.py`
- [ ] T059 Implement aggregation results display in summary panel
- [ ] T060 Add keybinding to open AggregateSidebar (e.g., Ctrl+A)
- [ ] T061 Support exporting aggregation results to file

**Checkpoint**: User Story 3 complete - aggregation and summarization work independently

---

## Phase 6: User Story 4 - Create Pivot Tables (Priority: P4)

**Goal**: Users can create pivot tables with row/column dimensions and aggregations

**Independent Test**: Load dataset, activate pivot mode, select dimensions and values, verify pivot table displays with correct calculations

### Implementation for User Story 4

- [ ] T062 [P] Create PivotSidebar widget in `src/kittiwake/widgets/sidebars/pivot_sidebar.py`:
  - Form: select row dimensions, column dimensions, aggregation values
  - Aggregation function selection (sum, mean, count, etc.)
  - Apply button to queue/execute pivot operation
- [ ] T063 [P] Implement pivot code generation in narwhals_ops.py:
  - `generate_pivot_code(params)` → "df = df.pivot(...)"
- [ ] T064 Create PivotTableWidget in `src/kittiwake/widgets/pivot_table.py`
- [ ] T065 Implement expand/collapse functionality for pivot groups
- [ ] T066 Add keybinding to open PivotSidebar (e.g., Ctrl+P)
- [ ] T067 Support saving pivot configuration for later reload

**Checkpoint**: User Story 4 complete - pivot tables work independently

---

## Phase 7: User Story 5 - Merge and Join Datasets (Priority: P5)

**Goal**: Users can merge two loaded datasets with join operations

**Independent Test**: Load two datasets, activate merge mode, select join columns and type, verify preview and merged result

### Implementation for User Story 5

- [ ] T068 [P] Create JoinSidebar widget in `src/kittiwake/widgets/sidebars/join_sidebar.py`:
  - Form: select second dataset, join columns from each, join type (inner/left/right/outer)
  - Preview button to show sample merged result
  - Apply button to execute join
- [ ] T069 [P] Implement join code generation in narwhals_ops.py:
  - `generate_join_code(params)` → "df = df.join(...)"
- [ ] T070 Implement join type mismatch detection and warning
- [ ] T071 Implement automatic type conversion (int↔float, string→category) where possible
- [ ] T072 Add keybinding to open JoinSidebar (e.g., Ctrl+J)
- [ ] T073 Handle errors when join keys don't match or datasets not loaded

**Checkpoint**: User Story 5 complete - dataset merging works independently

---

## Phase 8: User Story 6 - Save Analysis Workflows (Priority: P6)

**Goal**: Users can save operation sequences as reusable workflows

**Independent Test**: Perform operations sequence, save workflow with name, load new dataset with same schema, apply workflow, verify operations execute

### Implementation for User Story 6

- [ ] T074 [P] Create SaveWorkflowModal widget in `src/kittiwake/widgets/modals/save_workflow_modal.py`:
  - Form: workflow name, optional description
  - Save button to persist workflow
- [ ] T075 Implement workflow serialization (save operations sequence to JSON/YAML)
- [ ] T076 Implement workflow loading and application to new datasets
- [ ] T077 Implement workflow editing (modify steps and re-save)
- [ ] T078 Add keybinding to save workflow (e.g., Ctrl+Shift+S)
- [ ] T079 Validate target dataset schema matches workflow requirements

**Checkpoint**: User Story 6 complete - workflows can be saved and reused independently

---

## Phase 9: User Story 7 - Manage and Export Saved Analyses (Priority: P3)

**Goal**: Users can save analyses, list/update/delete them, load analyses (reloads dataset + reapplies operations), export to Python/marimo/Jupyter notebooks

**Independent Test**: Perform operations, save analysis with metadata, list analyses, update/delete analyses, load analysis (verify dataset reloads), export to all three formats, verify generated code executes

### Implementation for User Story 7

#### Saved Analyses Management

- [ ] T080 [P] Create SaveAnalysisModal widget in `src/kittiwake/widgets/modals/save_analysis_modal.py`:
  - Form: analysis name, description
  - Save button to persist to DuckDB
  - Validation: unique name check
- [ ] T081 [P] Create SavedAnalysesListScreen in `src/kittiwake/screens/saved_analyses_list_screen.py`:
  - List all saved analyses with metadata (name, description, created_at, modified_at, operation_count)
  - Keyboard navigation (up/down to select)
  - Actions: Load, Update, Delete, Export
- [ ] T082 Implement `action_save_analysis()` in MainScreen:
  - Show SaveAnalysisModal
  - Create SavedAnalysis entity with current dataset operations
  - Call `DuckDBManager.save_analysis()` in worker thread
  - Show success/error notification
- [ ] T083 Implement `action_load_saved_analysis()` in MainScreen:
  - Show SavedAnalysesListScreen
  - User selects analysis
  - Reload dataset from `dataset_path` (async with progress)
  - Reapply all operations in sequence (respecting execution mode)
  - Show in main view
- [ ] T084 Implement update analysis functionality:
  - Allow editing name/description
  - Update `modified_at` timestamp
  - Call `DuckDBManager.update_analysis()` in worker thread
- [ ] T085 Implement delete analysis functionality:
  - Show confirmation modal
  - Call `DuckDBManager.delete_analysis()` in worker thread
  - Refresh analyses list

#### Export to Notebooks

- [ ] T086 Generate contract files in `specs/001-tui-data-explorer/contracts/`:
  - [P] `export-python.jinja2` - Python script template
  - [P] `export-marimo.jinja2` - marimo notebook template
  - [P] `export-jupyter.jinja2` - Jupyter notebook template
  - [P] `operations-schema.json` - Operation serialization schema
  - [P] `cli-interface.md` - CLI usage documentation
  - [P] `saved-analysis-schema.sql` - DuckDB table schema
- [ ] T087 [P] Create ExportModal widget in `src/kittiwake/widgets/modals/export_modal.py`:
  - Radio buttons: Python Script / marimo Notebook / Jupyter Notebook
  - File path input with browse button
  - Export button
- [ ] T088 [P] Implement export service in `src/kittiwake/services/export.py`:
  - Setup Jinja2 environment loading templates from contracts/
  - Method: `export_to_python(analysis)` → render Python template
  - Method: `export_to_marimo(analysis)` → render marimo template
  - Method: `export_to_jupyter(analysis)` → render Jupyter template
- [ ] T089 Implement `action_export_analysis()` in SavedAnalysesListScreen:
  - Require analysis to be saved first (show error if not)
  - Show ExportModal
  - User selects format and path
  - Check if file exists (prompt to overwrite/rename/cancel)
  - Render template and write to file
  - Show success notification with file path
- [ ] T090 Add keybinding to export analysis (e.g., Ctrl+X)

#### Edge Cases

- [ ] T091 Handle dataset path unavailable when loading analysis (show warning, allow updating path)
- [ ] T092 Handle DuckDB database corruption (display error, offer to reinitialize with data loss warning)
- [ ] T093 Prevent export of unsaved analyses (show "Save first" message)
- [ ] T094 Handle duplicate analysis names (auto-version with timestamp suffix or require unique name)

**Checkpoint**: User Story 7 complete - saved analyses and export functionality work independently

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T095 [P] Create quickstart.md in `specs/001-tui-data-explorer/`:
  - Installation instructions (uv install, pip install)
  - Basic workflow: launch kw, load data, apply operations, execute (lazy mode), toggle to eager
  - Save and export analysis
  - Keyboard shortcuts reference table
- [ ] T096 [P] Update README.md with feature overview and quickstart link
- [ ] T097 [P] Add docstrings to all public methods
- [ ] T098 Code cleanup: remove deprecated modal-based UI code (filter_modal.py, search_modal.py if fully replaced)
- [ ] T099 Performance optimization: profile large dataset operations (1M+ rows), optimize narwhals query generation
- [ ] T100 [P] Security review: validate user input in all sidebar forms, check for path traversal in file operations
- [ ] T101 Run through quickstart.md validation with fresh environment
- [ ] T102 [P] Create marimo documentation notebooks in `docs/examples/` (if documentation is explicitly requested):
  - basic-usage.py - Load, filter, visualize
  - lazy-eager-modes.py - Demonstrate mode toggle and execution
  - export-workflows.py - Save and export analyses

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
   - T024-T035: Complete data loading and viewing
4. Phase 4: US2 - Filter and Search with Lazy/Eager
   - T039-T055: Sidebar enhancements, mode toggle, execution controls

**Estimated MVP**: ~45 tasks (Foundational + US1 + US2)

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
- [ ] Phase 4: US2 - 🔄 **IN PROGRESS** (55% complete - sidebars work, T040, T047-T048 done; need mode toggle, edit/remove operations)
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
