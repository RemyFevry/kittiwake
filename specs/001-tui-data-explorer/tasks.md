# Tasks: TUI Data Explorer

**Feature**: 001-tui-data-explorer  
**Input**: Design documents from `/specs/001-tui-data-explorer/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Test tasks are NOT included since the specification does not explicitly request TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6, US7)
- All tasks include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: src/kittiwake/{models,widgets,screens,services,utils}/ and tests/{contract,integration,unit}/
- [ ] T002 Initialize Python project with pyproject.toml dependencies: textual>=7.0.1, narwhals>=2.15.0, typer>=0.9.0, duckdb>=0.10.0, httpx>=0.27.0, nbformat>=5.10.0, jinja2>=3.1.0
- [ ] T003 [P] Configure ruff linting and formatting in pyproject.toml
- [ ] T004 [P] Create pytest configuration in pyproject.toml with test paths and pytest-asyncio dependency

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create CLI entry point with Typer in src/kittiwake/cli.py (bare `kw` command and `kw load` subcommand)
- [ ] T006 [P] Create main Textual App class in src/kittiwake/app.py with DatasetSession initialization
- [ ] T007 [P] Implement DatasetSession entity in src/kittiwake/models/dataset.py (manages up to 10 datasets, active dataset tracking, split pane state)
- [ ] T008 [P] Implement Dataset entity in src/kittiwake/models/dataset.py (with UUID, name, source, backend, frame, schema, operation_history fields)
- [ ] T009 [P] Implement Operation entity in src/kittiwake/models/operations.py (code, display, operation_type, params storage with to_dict/from_dict/apply/validate methods)
- [ ] T010 Create async DataLoader service in src/kittiwake/services/data_loader.py (supports CSV/Parquet/JSON from local and HTTP/HTTPS URLs with httpx streaming)
- [ ] T011 [P] Create NarwhalsOps service in src/kittiwake/services/narwhals_ops.py (get_page function for pagination with narwhals lazy frames)
- [ ] T012 [P] Setup DuckDB schema initialization in src/kittiwake/services/persistence.py (create analyses.db with saved_analyses table, enable WAL mode)
- [ ] T013 [P] Create utility for keyboard bindings registry in src/kittiwake/utils/keybindings.py
- [ ] T014 [P] Create async/worker helper utilities in src/kittiwake/utils/async_helpers.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and View Data (Priority: P1) 🎯 MVP

**Goal**: Enable users to launch kittiwake, load datasets (local files and remote URLs), view data in paginated table, and switch between multiple datasets (up to 10)

**Independent Test**: Launch `kw` bare and with `kw load file.csv`, verify data displays, keyboard navigation works, load multiple datasets and switch between them

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement DatasetTable widget in src/kittiwake/widgets/dataset_table.py (extends Textual DataTable with pagination support, 500-1000 rows per page)
- [ ] T016 [P] [US1] Implement DatasetTabs widget in src/kittiwake/widgets/dataset_tabs.py (shows loaded datasets with active one highlighted, keyboard shortcuts for switching)
- [ ] T017 [P] [US1] Implement HelpOverlay widget in src/kittiwake/widgets/help_overlay.py (keyboard shortcuts help with context-aware bindings from active screen)
- [ ] T018 [US1] Create MainScreen in src/kittiwake/screens/main_screen.py (primary data exploration screen with DatasetTable, DatasetTabs, status bar, keyboard bindings)
- [ ] T019 [US1] Implement dataset loading workflow in MainScreen: handle CLI args from `kw load`, load files async with progress indicators
- [ ] T020 [US1] Add keyboard navigation bindings to MainScreen: arrow keys for data navigation, Tab for dataset switching, ? for help overlay
- [ ] T021 [US1] Implement split pane mode in MainScreen (keyboard shortcut to display two datasets side-by-side using Textual Horizontal/Vertical containers)
- [ ] T022 [US1] Add 10-dataset limit enforcement in DatasetSession with user prompts when limit reached
- [ ] T023 [US1] Implement loading indicators and progress tracking for datasets >500ms load time using Textual reactive variables
- [ ] T024 [US1] Add error handling for file not found, unsupported formats, network timeouts with clear error messages
- [ ] T025 [US1] Wire up CLI commands in src/kittiwake/cli.py to launch MainScreen with empty workspace or pre-loaded datasets

**Checkpoint**: At this point, User Story 1 should be fully functional - users can load, view, and switch between datasets

---

## Phase 4: User Story 2 - Filter and Search Data (Priority: P2)

**Goal**: Enable users to filter datasets with text search and column-specific conditions, combine multiple filters, and maintain independent filter state per dataset

**Independent Test**: Load sample data, apply text search and column filters, verify filtered results, load second dataset and verify first dataset's filters are preserved

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create FilterModal widget in src/kittiwake/widgets/filter_modal.py (modal form with column dropdown, operator dropdown, value input per Modal Specifications section)
- [ ] T027 [P] [US2] Implement CodeGenerator class in src/kittiwake/services/code_generator.py (generate_filter method that creates narwhals filter code from modal params)
- [ ] T028 [P] [US2] Implement DisplayGenerator class in src/kittiwake/services/code_generator.py (format_filter method that creates human-readable filter descriptions)
- [ ] T029 [US2] Add filter keyboard binding (f key) to MainScreen that opens FilterModal for active dataset
- [ ] T030 [US2] Implement modal submit validation in FilterModal using sample data (first 10 rows) to verify filter code is valid
- [ ] T031 [US2] Implement apply_operation method in Dataset entity to add Operation to operation_history and update current_frame
- [ ] T032 [US2] Add Textual worker in MainScreen to execute filter operations in background thread (using @work decorator with exclusive=True)
- [ ] T033 [US2] Display operation history in UI (sidebar or footer showing applied operations with clear all keyboard shortcut)
- [ ] T034 [US2] Add text search across all columns (separate keyboard shortcut) that generates contains filter for each column with OR logic
- [ ] T035 [US2] Implement clear filters keyboard shortcut that resets Dataset to original frame
- [ ] T036 [US2] Add filtered row count display in status bar (e.g., "Showing 250 of 1000 rows")

**Checkpoint**: User Story 2 complete - filtering works independently on each dataset with preserved state

---

## Phase 5: User Story 3 - Aggregate and Summarize Data (Priority: P3)

**Goal**: Enable users to compute summary statistics and grouped aggregations on numeric columns

**Independent Test**: Load numeric data, select column, apply aggregation functions (sum, mean, count), verify correct calculations display

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create AggregationPanel widget in src/kittiwake/widgets/aggregation_panel.py (displays aggregation results in dedicated panel)
- [ ] T038 [P] [US3] Create AggregationModal widget in src/kittiwake/widgets/aggregation_modal.py (modal form with column dropdown, multi-select functions checklist, group_by multi-select)
- [ ] T039 [P] [US3] Add generate_aggregate method to CodeGenerator in src/kittiwake/services/code_generator.py (generates narwhals group_by().agg() code)
- [ ] T040 [P] [US3] Add format_aggregate method to DisplayGenerator in src/kittiwake/services/code_generator.py
- [ ] T041 [US3] Add aggregation keyboard binding (a key) to MainScreen that opens AggregationModal
- [ ] T042 [US3] Implement modal validation for numeric column requirements (sum/mean/std require numeric dtype)
- [ ] T043 [US3] Wire up AggregationModal submit to create Operation and apply via worker thread
- [ ] T044 [US3] Display aggregation results in AggregationPanel (can toggle between table view and aggregated view)
- [ ] T045 [US3] Add export aggregation results keyboard shortcut (writes aggregated data to CSV)

**Checkpoint**: User Story 3 complete - aggregation and summarization work independently

---

## Phase 6: User Story 7 - Manage and Export Saved Analyses (Priority: P3)

**Goal**: Enable users to save analyses with metadata, manage saved analyses (list/update/delete), load saved analyses, and export to marimo/Python/Jupyter formats

**Independent Test**: Perform operations, save analysis with metadata, list saved analyses, update/delete, load saved analysis and verify dataset reloads with operations, export to all three formats and verify generated code executes

### Implementation for User Story 7

- [ ] T046 [P] [US7] Implement SavedAnalysis entity in src/kittiwake/models/saved_analysis.py (id, name, description, timestamps, operation_count, dataset_path, operations fields with to_dict/from_dict methods)
- [ ] T047 [P] [US7] Implement SavedAnalysisRepository in src/kittiwake/services/persistence.py (save, update, delete, list_all, load_by_id methods with DuckDB WAL mode and threading.Lock for writes)
- [ ] T048 [P] [US7] Implement ExportService in src/kittiwake/services/export_service.py (export_marimo, export_python, export_jupyter methods using Jinja2 templates)
- [ ] T049 [P] [US7] Create SaveAnalysisModal widget in src/kittiwake/widgets/save_analysis_modal.py (form with name and description inputs)
- [ ] T050 [P] [US7] Create SavedAnalysesScreen in src/kittiwake/screens/saved_analyses_screen.py (list all saved analyses with keyboard navigation, update/delete actions)
- [ ] T051 [US7] Add save analysis keyboard binding (Ctrl+S) to MainScreen that opens SaveAnalysisModal
- [ ] T052 [US7] Implement save workflow: validate name uniqueness, create SavedAnalysis from active dataset, persist to DuckDB
- [ ] T053 [US7] Add view saved analyses keyboard binding to MainScreen that opens SavedAnalysesScreen
- [ ] T054 [US7] Implement load saved analysis workflow: verify dataset_path accessible, reload dataset async, apply operations in sequence
- [ ] T055 [US7] Add export keyboard binding in SavedAnalysesScreen (opens export modal with format selection: marimo/Python/Jupyter)
- [ ] T056 [US7] Implement export workflow: check analysis is saved, prompt for output path, render template, handle file overwrite confirmation
- [ ] T057 [US7] Add update analysis functionality in SavedAnalysesScreen (edit name/description, update modified_at timestamp)
- [ ] T058 [US7] Add delete analysis functionality with confirmation prompt
- [ ] T059 [US7] Add error handling for dataset_path not accessible when loading saved analysis (warn user, allow update path or delete)

**Checkpoint**: User Story 7 complete - saved analyses management and export work end-to-end

---

## Phase 7: User Story 4 - Create Pivot Tables (Priority: P4)

**Goal**: Enable users to create pivot tables with configurable row/column dimensions and aggregation values

**Independent Test**: Load sample data with categorical and numeric columns, create pivot table with row/column groupings, verify calculations

### Implementation for User Story 4

- [ ] T060 [P] [US4] Create PivotModal widget in src/kittiwake/widgets/pivot_modal.py (modal form with row dimensions multi-select, column dimensions multi-select, values list with column+function pairs)
- [ ] T061 [P] [US4] Add generate_pivot method to CodeGenerator in src/kittiwake/services/code_generator.py (generates narwhals pivot code or group_by workaround)
- [ ] T062 [P] [US4] Add format_pivot method to DisplayGenerator in src/kittiwake/services/code_generator.py
- [ ] T063 [US4] Add pivot keyboard binding (p key) to MainScreen that opens PivotModal
- [ ] T064 [US4] Implement pivot modal validation (at least one dimension required, value columns must exist)
- [ ] T065 [US4] Wire up PivotModal submit to create Operation and apply via worker
- [ ] T066 [US4] Implement expand/collapse functionality for grouped rows in pivot table view (if narwhals supports or using custom rendering)
- [ ] T067 [US4] Add save pivot configuration option (stores params for later reuse)

**Checkpoint**: User Story 4 complete - pivot tables work independently

---

## Phase 8: User Story 5 - Merge and Join Datasets (Priority: P5)

**Goal**: Enable users to combine two loaded datasets with inner/left/right/outer joins

**Independent Test**: Load two CSV files with common key column, perform inner join, verify merged dataset

### Implementation for User Story 5

- [ ] T068 [P] [US5] Create JoinModal widget in src/kittiwake/widgets/join_modal.py (modal form with right dataset dropdown, left_on/right_on column selectors, join type radio buttons)
- [ ] T069 [P] [US5] Create MergeScreen in src/kittiwake/screens/merge_screen.py (join wizard with preview before applying)
- [ ] T070 [P] [US5] Add generate_join method to CodeGenerator in src/kittiwake/services/code_generator.py (generates narwhals join code)
- [ ] T071 [P] [US5] Add format_join method to DisplayGenerator in src/kittiwake/services/code_generator.py
- [ ] T072 [US5] Add join keyboard binding (j key) to MainScreen that opens JoinModal or MergeScreen
- [ ] T073 [US5] Implement join modal validation (check columns exist in respective datasets, warn on type mismatches)
- [ ] T074 [US5] Implement merge preview in MergeScreen (show first 100 rows of merged result before applying)
- [ ] T075 [US5] Wire up merge confirmation to create Operation and apply to active dataset
- [ ] T076 [US5] Add error handling for join key mismatches and missing values

**Checkpoint**: User Story 5 complete - dataset merging works independently

---

## Phase 9: User Story 6 - Save Analysis Workflows (Priority: P6)

**Goal**: Enable users to save operation sequences as reusable workflows and apply to new datasets

**Independent Test**: Perform sequence of operations, save workflow, load new dataset with same schema, apply workflow, verify operations execute

### Implementation for User Story 6

- [ ] T077 [P] [US6] Implement Workflow entity in src/kittiwake/models/workflow.py (id, name, description, operations, required_columns, timestamps with to_dict/from_dict/apply_to_dataset/validate_schema methods)
- [ ] T078 [P] [US6] Create workflow persistence in ~/.kittiwake/workflows/ directory as JSON files
- [ ] T079 [P] [US6] Create SaveWorkflowModal widget in src/kittiwake/widgets/save_workflow_modal.py (form with name and description inputs)
- [ ] T080 [P] [US6] Create WorkflowsScreen in src/kittiwake/screens/workflows_screen.py (list all workflows with apply/edit/delete actions)
- [ ] T081 [US6] Add save workflow keyboard binding to MainScreen that opens SaveWorkflowModal
- [ ] T082 [US6] Implement save workflow: capture operations from active dataset, extract required columns, persist as JSON
- [ ] T083 [US6] Add view workflows keyboard binding to MainScreen that opens WorkflowsScreen
- [ ] T084 [US6] Implement apply workflow: validate target dataset schema, show schema compatibility report, apply operations in sequence
- [ ] T085 [US6] Add edit workflow functionality (modify individual operations, re-save)
- [ ] T086 [US6] Implement workflow validation with clear error messages for missing/incompatible columns

**Checkpoint**: User Story 6 complete - workflow management works end-to-end

---

## Phase 10: Additional Operations Modals (Cross-Cutting)

**Purpose**: Implement remaining 9 operation type modals from Modal Specifications (Phase 1.5 in plan.md)

- [ ] T087 [P] Create SortModal in src/kittiwake/widgets/sort_modal.py (columns multi-select with descending checkboxes) with keyboard binding (s key)
- [ ] T088 [P] Create SelectColumnsModal in src/kittiwake/widgets/select_modal.py (columns multi-select checklist) with keyboard binding (c key)
- [ ] T089 [P] Create DropColumnsModal in src/kittiwake/widgets/drop_modal.py (columns multi-select checklist) with keyboard binding (d+c sequence)
- [ ] T090 [P] Create RenameColumnsModal in src/kittiwake/widgets/rename_modal.py (key-value pairs: old→new) with keyboard binding (r key)
- [ ] T091 [P] Create CalculatedColumnModal in src/kittiwake/widgets/calculated_modal.py (new column name + expression builder) with keyboard binding (w key)
- [ ] T092 [P] Create DropDuplicatesModal in src/kittiwake/widgets/unique_modal.py (subset columns, keep radio) with keyboard binding (u key)
- [ ] T093 [P] Create FillNullModal in src/kittiwake/widgets/fill_null_modal.py (strategy dropdown, literal value) with keyboard binding (n+f sequence)
- [ ] T094 [P] Create DropNullsModal in src/kittiwake/widgets/drop_nulls_modal.py (subset columns) with keyboard binding (n+d sequence)
- [ ] T095 [P] Create SampleModal in src/kittiwake/widgets/sample_modal.py (n input, random/seed for sample) with keyboard bindings (h/t/m keys for head/tail/sample)
- [ ] T096 Add corresponding generate_* methods to CodeGenerator for all 9 operation types in src/kittiwake/services/code_generator.py
- [ ] T097 Add corresponding format_* methods to DisplayGenerator for all 9 operation types in src/kittiwake/services/code_generator.py

**Checkpoint**: All 13 operation types have working modals and code generation

---

## Phase 11: Undo/Redo & Operation Editing (Cross-Cutting)

**Purpose**: Enable operation history management

- [ ] T098 [P] Implement undo method in Dataset entity (pop operation, restore from checkpoint or replay from start)
- [ ] T099 [P] Implement redo method in Dataset entity (reapply undone operation)
- [ ] T100 [P] Implement checkpoint strategy in Dataset (cache DataFrame state every 10 operations)
- [ ] T101 Add undo/redo keyboard bindings to MainScreen (Ctrl+Z, Ctrl+Shift+Z)
- [ ] T102 Implement operation editing: click operation in history → reopen modal with pre-filled params → update operation on submit
- [ ] T103 Add visual operation history panel in MainScreen showing all applied operations with edit/delete actions

**Checkpoint**: Operation history management complete

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T104 [P] Add terminal resize handling in MainScreen (layout adapts within 100ms per SC-008)
- [ ] T105 [P] Implement light/dark theme toggle with keyboard shortcut
- [ ] T106 [P] Add comprehensive error messages for all edge cases from spec.md Edge Cases section
- [ ] T107 [P] Optimize DataTable rendering for large datasets (verify <100ms response per SC-002)
- [ ] T108 [P] Add memory usage monitoring and warnings when approaching limits
- [ ] T109 [P] Implement operation cancellation UI (progress modal with cancel button for >500ms operations)
- [ ] T110 [P] Add dataset close functionality (keyboard shortcut to remove dataset from session and free memory)
- [ ] T111 [P] Update README.md with installation instructions, quickstart examples, and feature overview
- [ ] T112 [P] Generate API documentation from docstrings using Sphinx or similar
- [ ] T113 [P] Add logging throughout application using Python logging module (DEBUG/INFO/ERROR levels)
- [ ] T114 [P] Performance profiling: verify SC-001 (1GB CSV first page <3s), SC-013 (DuckDB <200ms), SC-014 (dataset switching <150ms)
- [ ] T115 Run through quickstart.md validation with fresh environment
- [ ] T116 Code review and refactoring pass for consistency and maintainability
- [ ] T117 Security audit: ensure eval() in Operation.apply uses restricted namespace, no SQL injection in DuckDB queries

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Additional Operations (Phase 10)**: Can start after US1-US2 complete (requires MainScreen and CodeGenerator foundation)
- **Undo/Redo (Phase 11)**: Can start after US2 complete (requires Operation infrastructure)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Load and View**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Filter and Search**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 3 (P3) - Aggregate**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 7 (P3) - Saved Analyses**: Can start after Foundational (Phase 2) - Independent of other stories (uses existing operations)
- **User Story 4 (P4) - Pivot Tables**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 5 (P5) - Merge/Join**: Requires US1 complete (needs multiple datasets loaded)
- **User Story 6 (P6) - Workflows**: Requires US2-US4 complete (needs operations to create workflows from)

### Within Each User Story

- Models before services
- Services before widgets/screens
- Widgets before screen integration
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T001, T002, T003, T004 can all run in parallel

**Phase 2 (Foundational)**:
- T006, T007, T008, T009, T011, T012, T013, T014 can run in parallel
- T005 and T010 depend on nothing and can run in parallel with others

**Phase 3 (US1)**: T015, T016, T017 can run in parallel (different widget files)

**Phase 4 (US2)**: T026, T027, T028 can run in parallel (different files)

**Phase 5 (US3)**: T037, T038, T039, T040 can run in parallel (different files)

**Phase 6 (US7)**: T046, T047, T048, T049, T050 can run in parallel (different files)

**Phase 7 (US4)**: T060, T061, T062 can run in parallel

**Phase 8 (US5)**: T068, T069, T070, T071 can run in parallel

**Phase 9 (US6)**: T077, T078, T079, T080 can run in parallel

**Phase 10 (Modals)**: T087-T095 can all run in parallel (different widget files)

**Phase 11 (Undo/Redo)**: T098, T099, T100 can run in parallel (same file but different methods)

**Phase 12 (Polish)**: T104-T114, T116, T117 can run in parallel (different concerns)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (10 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (11 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo MVP

**Total MVP tasks**: 25 tasks

### Incremental Delivery (Recommended)

1. **Foundation** (Phase 1-2): 14 tasks → Foundation ready
2. **MVP** (Phase 3 - US1): 11 tasks → Basic data loading and viewing works
3. **Filtering** (Phase 4 - US2): 11 tasks → Data exploration capability added
4. **Analysis** (Phase 5 - US3): 9 tasks → Summarization capabilities added
5. **Persistence** (Phase 6 - US7): 14 tasks → Save and export work
6. **Advanced Features** (Phase 7-9): 29 tasks → Pivot, join, workflows
7. **Complete Operations** (Phase 10): 11 tasks → All operation types
8. **History Management** (Phase 11): 6 tasks → Undo/redo complete
9. **Polish** (Phase 12): 14 tasks → Production ready

**Total tasks**: 119 tasks

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (Phase 3) → User Story 4 (Phase 7) → Phase 10 modals (T087-T091)
- **Developer B**: User Story 2 (Phase 4) → User Story 5 (Phase 8) → Phase 10 modals (T092-T095)
- **Developer C**: User Story 3 (Phase 5) + User Story 7 (Phase 6) → User Story 6 (Phase 9) → Phase 11 undo/redo

Then all converge on Phase 12 (Polish)

---

## Summary

- **Total Tasks**: 119
- **Tasks per User Story**:
  - US1 (Load and View): 11 tasks
  - US2 (Filter and Search): 11 tasks
  - US3 (Aggregate): 9 tasks
  - US7 (Saved Analyses): 14 tasks
  - US4 (Pivot): 8 tasks
  - US5 (Merge/Join): 9 tasks
  - US6 (Workflows): 10 tasks
  - Additional Operations: 11 tasks
  - Undo/Redo: 6 tasks
  - Setup + Foundation: 14 tasks
  - Polish: 14 tasks

- **Parallel Opportunities**: 42 tasks marked [P] can run in parallel within their phases
- **Independent Test Criteria**: Each user story has clear acceptance criteria from spec.md
- **MVP Scope**: Phase 1-3 (User Story 1: Load and View Data) = 25 tasks
- **Format Validation**: ✅ All tasks follow checklist format with checkbox, ID, [P]/[Story] markers, and file paths

---

## Notes

- All tasks include exact file paths for clarity
- [P] marker indicates parallelizable tasks (different files, no dependencies)
- [Story] marker maps tasks to user stories for traceability
- Each phase has clear checkpoints for validation
- Task IDs are sequential (T001-T117) for easy reference
- Tasks are sized to be completable in 2-4 hours each
- Commit after completing each task or logical group
