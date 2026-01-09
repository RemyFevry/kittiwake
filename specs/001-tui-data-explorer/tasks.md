# Tasks: TUI Data Explorer

**Input**: Design documents from `/specs/001-tui-data-explorer/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Branch**: `001-tui-data-explorer`

**Tests**: Not explicitly requested in specification - test tasks are EXCLUDED per requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/kittiwake/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

**Status**: Already complete from previous sessions. Project structure, dependencies, and CLI entry points are functional.

- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Python 3.13+ project with uv and dependencies (narwhals, textual, typer, duckdb, httpx, jinja2, nbformat, polars)
- [x] T003 [P] Configure ruff for linting and formatting
- [x] T004 [P] Setup pytest with pytest-asyncio for testing framework
- [x] T005 Create CLI entry points (kw and kittiwake commands) in src/kittiwake/__main__.py
- [x] T006 Initialize DuckDB schema at ~/.kittiwake/analyses.db per contracts/saved-analysis-schema.sql

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Status**: Already complete from Phase 3 MVP implementation.

- [x] T007 Create Dataset model in src/kittiwake/models/dataset.py with schema, operations, lazy evaluation support
- [x] T008 Create DatasetSession model in src/kittiwake/models/dataset_session.py for managing up to 10 datasets
- [x] T009 Create Operation model in src/kittiwake/models/operations.py with OperationType enum (15 types)
- [x] T010 [P] Implement DataLoader service in src/kittiwake/services/data_loader.py for CSV/Parquet/JSON loading
- [x] T011 [P] Setup async helpers in src/kittiwake/utils/async_helpers.py for non-blocking I/O
- [x] T012 [P] Create centralized keybindings in src/kittiwake/utils/keybindings.py
- [x] T013 Create KittiwakeApp in src/kittiwake/app.py extending Textual App
- [x] T014 Create MainScreen in src/kittiwake/screens/main_screen.py with layout structure
- [x] T015 Create DatasetTable widget in src/kittiwake/widgets/dataset_table.py with pagination
- [x] T016 Create DatasetTabs widget in src/kittiwake/widgets/dataset_tabs.py for multi-dataset switching
- [x] T017 Create HelpOverlay widget in src/kittiwake/widgets/help_overlay.py showing keyboard shortcuts
- [x] T018 Implement Typer CLI in src/kittiwake/cli.py with kw and kw load subcommands

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and View Data (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users can load datasets from local files or remote URLs, view data in paginated tables with enhanced column navigation (40-char cap, arrow keys, Ctrl+jumps, Enter for full content, auto-scroll viewport), switch between up to 10 datasets, and use split pane mode.

**Independent Test**: Launch kittiwake with `kw` (empty workspace) and `kw load tests/e2e/Titanic-Dataset.csv`, verify data displays correctly with keyboard navigation, tab switching, split pane, and column navigation working per acceptance scenarios 1-18.

**Status**: ✅ COMPLETE - All 18 acceptance scenarios implemented and verified in previous sessions.

### Implementation for User Story 1 (All Complete)

- [x] T019 [P] [US1] Implement lazy evaluation detection (>100MB files) in src/kittiwake/models/dataset.py
- [x] T020 [P] [US1] Add pagination methods (get_page) to Dataset model
- [x] T021 [US1] Implement DatasetTable column width capping (40 chars) with ellipsis truncation
- [x] T022 [US1] Add arrow key navigation (Left/Right for columns, Up/Down for rows) to DatasetTable
- [x] T023 [US1] Implement Ctrl+Left/Right column jumping (5 columns) in DatasetTable
- [x] T024 [US1] Add Enter key handler to show full cell content in modal (CellContentModal)
- [x] T025 [US1] Implement auto-scroll viewport when cursor moves beyond visible columns
- [x] T026 [US1] Add dataset limit enforcement (max 10) in DatasetSession.add_dataset()
- [x] T027 [US1] Implement split pane mode (Ctrl+P) in MainScreen for side-by-side dataset comparison
- [x] T028 [US1] Add visual tab indicators for loaded datasets in DatasetTabs
- [x] T029 [US1] Implement keyboard shortcuts for dataset switching (Ctrl+T for next tab)
- [x] T030 [US1] Add loading indicators for operations >500ms per FR-014
- [x] T031 [US1] Implement progress feedback for large file loading (1GB CSV in <3s per SC-001)
- [x] T032 [US1] Add terminal resize handling to adapt layout per FR-009

**Checkpoint**: User Story 1 is fully functional and independently tested (verified with Titanic-Dataset.csv)

---

## Phase 4: User Story 2 - Filter and Search Data (Priority: P2) 🔄 IN PROGRESS

**Goal**: Users can activate search function via keyboard, apply text search across all columns, create column-specific filters with comparison operators (=, !=, >, <, >=, <=, contains), combine multiple filters with AND/OR logic, and clear filters quickly. Each dataset maintains independent filter state. **Architecture**: Sidebar-based (left overlay for forms, right push for operations history).

**Independent Test**: Load sample data (`kw load tests/e2e/Titanic-Dataset.csv`), apply text search for "male", apply column filter "Age > 25", verify filtered results display correctly, clear filters to restore full dataset. Load second dataset, verify first dataset's filters are preserved when switching back.

### Implementation for User Story 2

- [x] T033 [P] [US2] Create FilterSidebar widget in src/kittiwake/widgets/sidebars/filter_sidebar.py with Select (column, operator), Input (value), Button (Apply, Cancel) - **SIDEBAR ARCHITECTURE**
- [x] T034 [P] [US2] Create SearchSidebar widget in src/kittiwake/widgets/sidebars/search_sidebar.py for full-text search input - **SIDEBAR ARCHITECTURE**
- [x] T035 [US2] Implement filter operation code generation in FilterSidebar callback handler per research.md section 2
- [x] T036 [US2] Add text search operation code generation in SearchSidebar callback handler
- [ ] T037 [US2] Implement filter validation on sample data (first 100 rows) before applying
- [x] T038 [US2] Add keyboard shortcut (Ctrl+F) for FilterSidebar in MainScreen keybindings
- [x] T039 [US2] Add keyboard shortcut (Ctrl+/) for SearchSidebar in MainScreen keybindings
- [x] T039b [US2] Create OperationsSidebar widget in src/kittiwake/widgets/sidebars/operations_sidebar.py for operations history with CRUD (reorder, edit, delete) - **RIGHT PUSH SIDEBAR**
- [ ] T040 [US2] Implement AND/OR logic UI in FilterSidebar for combining multiple filters
- [x] T041 [US2] Add operations count display in OperationsSidebar showing applied operations
- [x] T042 [US2] Implement clear all operations keyboard shortcut (Ctrl+C when OperationsSidebar focused) in OperationsSidebar
- [ ] T043 [US2] Add filtered row count vs total row count display per FR-019
- [ ] T044 [US2] Update DatasetTable to refresh on filter application within 500ms per acceptance scenario 4
- [ ] T045 [US2] Verify independent filter state per dataset (acceptance scenario 5-6)

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 7 - Manage and Export Saved Analyses (Priority: P3) 🔄 IN PROGRESS

**Goal**: Users can save analyses with name and description to DuckDB, list all saved analyses, update/delete analyses, load a saved analysis (reloads dataset and reapplies operations), and export analyses to marimo/Python/Jupyter notebooks. **Architecture**: Modal-based for save/export dialogs (one-time actions), sidebar-based for operations history.

**Independent Test**: Perform operations on Titanic dataset (filter Age > 25), save analysis as "Adult Passengers", list saved analyses, update description, export to marimo/Python/Jupyter, verify generated code executes correctly, delete analysis, verify removal from list.

### Implementation for User Story 7

- [x] T046 [P] [US7] Implement PersistenceService.save_analysis() in src/kittiwake/services/persistence.py per research.md section 3
- [x] T047 [P] [US7] Implement PersistenceService.list_analyses() with DuckDB query sorted by modified_at DESC
- [x] T048 [P] [US7] Implement PersistenceService.load_analysis() to fetch analysis by ID
- [x] T049 [P] [US7] Implement PersistenceService.update_analysis() for name/description changes
- [x] T050 [P] [US7] Implement PersistenceService.delete_analysis() with DuckDB DELETE
- [x] T051 [P] [US7] Create SaveAnalysisModal widget in src/kittiwake/widgets/modals/save_analysis_modal.py with Input (name, description), Button (Save, Cancel)
- [x] T052 [P] [US7] Create SavedAnalysesListScreen in src/kittiwake/screens/saved_analyses_list_screen.py with DataTable listing analyses
- [x] T053 [P] [US7] Create ExportModal widget in src/kittiwake/widgets/modals/export_modal.py with Select (marimo, Python, Jupyter), Input (output path), Button (Export, Cancel)
- [ ] T054 [US7] Implement export_to_marimo() in PersistenceService using Jinja2 template from contracts/export-marimo.jinja2
- [ ] T055 [US7] Implement export_to_python() in PersistenceService using Jinja2 template from contracts/export-python.jinja2
- [ ] T056 [US7] Implement export_to_jupyter() in PersistenceService using nbformat per research.md section 4
- [ ] T057 [US7] Add keyboard shortcut (Ctrl+S) for SaveAnalysisModal in MainScreen
- [ ] T058 [US7] Add keyboard shortcut (Ctrl+O) for SavedAnalysesListScreen in MainScreen
- [ ] T059 [US7] Add keyboard shortcut (Ctrl+E) for ExportModal in MainScreen
- [ ] T060 [US7] Implement load saved analysis workflow: select from list → load dataset_path → apply operations in sequence
- [ ] T061 [US7] Add file overwrite confirmation prompt in ExportModal per FR-050
- [ ] T062 [US7] Add validation to prevent export without saving first per FR-045
- [ ] T063 [US7] Add dataset path accessibility check before loading saved analysis per FR-062
- [ ] T064 [US7] Add unique name validation in SaveAnalysisModal (DuckDB UNIQUE constraint)
- [ ] T065 [US7] Verify DuckDB operations complete within 200ms per SC-013

**Checkpoint**: User Stories 1, 2, AND 7 should all work independently

---

## Phase 6: User Story 3 - Aggregate and Summarize Data (Priority: P3)

**Goal**: Users can select columns via keyboard, activate aggregation menu, choose functions (count, sum, mean, median, min, max, std), see results in summary panel, and group by columns for grouped aggregations.

**Independent Test**: Load numeric data (Titanic Age column), activate aggregation, select Age column, choose sum/mean/count functions, verify summary statistics display correctly in panel. Group by Sex column, verify grouped aggregation results.

### Implementation for User Story 3

- [ ] T066 [P] [US3] Create AggregateModal widget in src/kittiwake/widgets/modals/aggregate_modal.py with Select (column), Checkbox (count, sum, mean, median, min, max, std), Select (group_by columns), Button (Apply, Cancel)
- [ ] T067 [US3] Implement aggregate operation code generation in AggregateModal._build_aggregate_operation() per research.md section 2
- [ ] T068 [US3] Add keyboard shortcut (Ctrl+A) for AggregateModal in MainScreen
- [ ] T069 [US3] Create AggregationPanel widget in src/kittiwake/widgets/aggregation_panel.py to display summary statistics
- [ ] T070 [US3] Implement group-by logic in AggregateModal with multiple group columns support
- [ ] T071 [US3] Add aggregation result display in dedicated panel per FR-024
- [ ] T072 [US3] Implement narwhals aggregate expressions (nw.col().sum(), .mean(), .median(), .min(), .max(), .std()) in NarwhalsOpsService
- [ ] T073 [US3] Add validation to prevent aggregation on non-numeric columns with helpful error message per edge case
- [ ] T074 [US3] Implement export aggregated results to CSV/Parquet per FR-037, FR-038

**Checkpoint**: User Stories 1, 2, 3, AND 7 should all work independently

---

## Phase 7: User Story 4 - Create Pivot Tables (Priority: P4)

**Goal**: Users create pivot tables by selecting row dimensions, column dimensions, and aggregation values using keyboard commands. Pivot tables display in interactive view with expand/collapse groups and dimension re-arrangement.

**Independent Test**: Load Titanic data, activate pivot mode, select row dimension (Sex), column dimension (Pclass), aggregation value (Age mean), verify pivot table displays with correct calculations. Test expand/collapse groups, save pivot configuration, reload later.

### Implementation for User Story 4

- [ ] T075 [P] [US4] Create PivotModal widget in src/kittiwake/widgets/modals/pivot_modal.py with MultiSelect (row_dimensions, column_dimensions), aggregation value selector, Button (Apply, Cancel)
- [ ] T076 [P] [US4] Create PivotTableWidget in src/kittiwake/widgets/pivot_table_widget.py for interactive pivot display
- [ ] T077 [US4] Implement pivot operation code generation in PivotModal._build_pivot_operation()
- [ ] T078 [US4] Add keyboard shortcut (Ctrl+V) for PivotModal in MainScreen
- [ ] T079 [US4] Implement narwhals pivot logic in NarwhalsOpsService (group_by + pivot operations)
- [ ] T080 [US4] Add expand/collapse functionality in PivotTableWidget for grouped rows
- [ ] T081 [US4] Implement pivot configuration save/load in PersistenceService per FR-028
- [ ] T082 [US4] Add dimension re-arrangement UI in PivotTableWidget (drag to reorder - keyboard alternative)
- [ ] T083 [US4] Implement export pivot tables to CSV/Parquet per FR-039

**Checkpoint**: User Stories 1, 2, 3, 4, AND 7 should all work independently

---

## Phase 8: User Story 5 - Merge and Join Datasets (Priority: P5)

**Goal**: Users activate merge mode, select join columns from each dataset, choose join type (inner, left, right, outer), preview merged result before applying, and see warnings for mismatched join keys.

**Independent Test**: Load two CSV files with common key column (e.g., Titanic dataset split by class), activate merge mode, select join columns (PassengerId), choose inner join, verify preview shows correct merged data, confirm merge, verify merged dataset replaces active view.

### Implementation for User Story 5

- [ ] T084 [P] [US5] Create JoinModal widget in src/kittiwake/widgets/modals/join_modal.py with Select (right_dataset, left_on, right_on, join_type: inner/left/right/outer), Button (Preview, Apply, Cancel)
- [ ] T085 [US5] Implement join operation code generation in JoinModal._build_join_operation()
- [ ] T086 [US5] Add keyboard shortcut (Ctrl+J) for JoinModal in MainScreen
- [ ] T087 [US5] Implement narwhals join logic in NarwhalsOpsService (df.join() with how parameter)
- [ ] T088 [US5] Add merge preview functionality in JoinModal showing first 100 rows of merged result
- [ ] T089 [US5] Implement join key type mismatch detection per FR-032: attempt narwhals auto-conversion (int↔float, string→category), display modal if conversion fails with options (Cancel/View details/Manually select columns)
- [ ] T090 [US5] Add validation to prevent join when second dataset isn't loaded per edge case
- [ ] T091 [US5] Implement missing value warning for join keys in JoinModal
- [ ] T092 [US5] Add cross join support in JoinModal per operations-schema.json

**Checkpoint**: User Stories 1, 2, 3, 4, 5, AND 7 should all work independently

---

## Phase 9: User Story 6 - Save Analysis Workflows (Priority: P6)

**Goal**: Users can save sequences of operations as reusable workflows, persist workflows to disk in human-readable format, and reapply workflows to new datasets with same schema.

**Independent Test**: Perform sequence of operations (filter Age > 25 → group by Sex → aggregate mean), save workflow as "Adult Gender Analysis", load new dataset with same schema, apply workflow, verify operations execute in sequence automatically. Edit workflow, save updated version.

### Implementation for User Story 6

- [ ] T093 [P] [US6] Create Workflow entity in src/kittiwake/models/workflow.py with name, description, operations list, target_schema
- [ ] T094 [P] [US6] Create WorkflowService in src/kittiwake/services/workflow_service.py for CRUD operations
- [ ] T095 [P] [US6] Create SaveWorkflowModal widget in src/kittiwake/widgets/modals/save_workflow_modal.py with Input (name, description), Button (Save, Cancel)
- [ ] T096 [P] [US6] Create WorkflowsListScreen in src/kittiwake/screens/workflows_list_screen.py with DataTable listing workflows
- [ ] T097 [US6] Implement workflow persistence to JSON files in ~/.kittiwake/workflows/ per FR-034
- [ ] T098 [US6] Add keyboard shortcut (Ctrl+Shift+S) for SaveWorkflowModal in MainScreen
- [ ] T099 [US6] Add keyboard shortcut (Ctrl+Shift+O) for WorkflowsListScreen in MainScreen
- [ ] T100 [US6] Implement workflow schema validation (match dataset schema) before application
- [ ] T101 [US6] Add workflow edit functionality (load workflow → modify operations → save)
- [ ] T102 [US6] Implement undo/redo for individual operations per FR-036
- [ ] T103 [US6] Add undo keyboard shortcut (Ctrl+Z) in MainScreen
- [ ] T104 [US6] Add redo keyboard shortcut (Ctrl+Y) in MainScreen
- [ ] T105 [US6] Implement operation stack history tracking in Dataset model

**Checkpoint**: All user stories should now be independently functional

---

## Phase 10: Remaining Operation Modals (Supporting All Stories)

**Purpose**: Complete the 13 operation types with dedicated modal forms per research.md section 2

**Note**: Filter (US2) and Aggregate (US3) modals already covered. This phase adds remaining 11 operation types.

- [ ] T106 [P] Create SelectModal widget in src/kittiwake/widgets/modals/select_modal.py with MultiSelect (columns), Button (Apply, Cancel)
- [ ] T107 [P] Create DropModal widget in src/kittiwake/widgets/modals/drop_modal.py with MultiSelect (columns to drop), Button (Apply, Cancel)
- [ ] T108 [P] Create RenameModal widget in src/kittiwake/widgets/modals/rename_modal.py with mapping UI (old_name → new_name pairs), Button (Apply, Cancel)
- [ ] T109 [P] Create WithColumnsModal widget in src/kittiwake/widgets/modals/with_columns_modal.py with Input (new_column name, expression), Button (Apply, Cancel)
- [ ] T110 [P] Create SortModal widget in src/kittiwake/widgets/modals/sort_modal.py with MultiSelect (columns), Checkbox (descending per column), Button (Apply, Cancel)
- [ ] T111 [P] Create UniqueModal widget in src/kittiwake/widgets/modals/unique_modal.py with MultiSelect (columns for uniqueness), Button (Apply, Cancel)
- [ ] T112 [P] Create FillNullModal widget in src/kittiwake/widgets/modals/fill_null_modal.py with Select (strategy: forward, backward, mean, median, zero, literal), Input (literal value), Button (Apply, Cancel)
- [ ] T113 [P] Create DropNullsModal widget in src/kittiwake/widgets/modals/drop_nulls_modal.py with MultiSelect (columns or all), Button (Apply, Cancel)
- [ ] T114 [P] Create HeadModal widget in src/kittiwake/widgets/modals/head_modal.py with Input (n rows), Button (Apply, Cancel)
- [ ] T115 [P] Create TailModal widget in src/kittiwake/widgets/modals/tail_modal.py with Input (n rows), Button (Apply, Cancel)
- [ ] T116 [P] Create SampleModal widget in src/kittiwake/widgets/modals/sample_modal.py with Input (n rows), Checkbox (random), Input (seed), Button (Apply, Cancel)
- [ ] T117 Implement NarwhalsOpsService.apply_operation() in src/kittiwake/services/narwhals_ops.py to execute operation code strings safely
- [ ] T118 Add keyboard shortcuts for all remaining operation modals in MainScreen

**Checkpoint**: All 13 operation types have modal forms and can be applied to datasets

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T119 [P] Add error handling for file not found, network timeout, type mismatches per SC-010 (include: what failed, why, next action)
- [ ] T120 [P] Implement cancellation for long-running operations per FR-015 (Esc key during progress indicator, discard partial results)
- [ ] T121 [P] Add memory usage warnings when loading multiple large datasets per edge case
- [ ] T122 [P] Implement unsupported file format error with list of supported formats
- [ ] T123 [P] Add DuckDB corruption detection and reinitialization offer per edge case
- [ ] T124 [P] Implement terminal color depth and dimension detection for compatibility
- [ ] T125 [P] Add CLI error handling for unrecognized subcommands per edge case
- [ ] T126 [P] Implement CSV/Parquet export for current view per FR-037, FR-038 (data file export)
- [ ] T127 [P] Implement light/dark theme detection (COLORFGBG env var, terminal queries) and CSS theme switching in KittiwakeApp per FR-010
- [ ] T128 [P] Create light.tcss and dark.tcss stylesheets for theme support per FR-010
- [ ] T129 Code cleanup and refactoring across all modules
- [ ] T130 Performance optimization: verify <100ms UI response per SC-002, SC-016
- [ ] T131 Performance optimization: verify <500ms data operations threshold per SC-007
- [ ] T132 Performance optimization: verify <3s for 1GB CSV first page per SC-001
- [ ] T133 Performance optimization: verify <200ms DuckDB queries per SC-013
- [ ] T134 Performance optimization: verify <150ms dataset switching per SC-014
- [ ] T135 Documentation: Update README.md with installation and usage
- [ ] T136 Documentation: Verify quickstart.md examples work end-to-end
- [ ] T137 Documentation: Create 3 marimo example notebooks in docs/examples/ (basic-workflow.py: load→filter→aggregate, pivot-analysis.py: load→pivot, multi-dataset-join.py: load 2 CSVs→join→export) with README.md
- [ ] T138 Security: Validate operation code execution safety (no arbitrary code injection)
- [ ] T139 Security: Add input validation for all modal forms
- [ ] T140 Accessibility: Verify keyboard-only navigation works for all features per FR-006

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ COMPLETE - No dependencies
- **Foundational (Phase 2)**: ✅ COMPLETE - Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: ✅ COMPLETE - Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can start now
- **User Story 7 (Phase 5)**: Depends on Foundational (Phase 2) - Can start now
- **User Story 3 (Phase 6)**: Depends on Foundational (Phase 2) - Can start now
- **User Story 4 (Phase 7)**: Depends on Foundational (Phase 2) and ideally US3 (aggregation logic)
- **User Story 5 (Phase 8)**: Depends on Foundational (Phase 2) - Can start now
- **User Story 6 (Phase 9)**: Depends on Foundational (Phase 2) and ideally US2-US5 (operations to save)
- **Remaining Modals (Phase 10)**: Can run in parallel with user stories
- **Polish (Phase 11)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ✅ COMPLETE - MVP foundation ready
- **User Story 2 (P2)**: Can start immediately - No dependencies on other stories
- **User Story 7 (P3)**: Can start immediately - Operates independently (save/load/export)
- **User Story 3 (P3)**: Can start immediately - No dependencies on other stories
- **User Story 4 (P4)**: Soft dependency on US3 (uses aggregation concepts) but can be built independently
- **User Story 5 (P5)**: Can start immediately - No dependencies on other stories
- **User Story 6 (P6)**: Soft dependency on US2-US5 (needs operations to save as workflows) but can be built independently

### Within Each User Story

- Tests NOT included (not requested in spec)
- Models before services (where applicable)
- Services before UI components
- Modals before screen integrations
- Core implementation before keyboard shortcuts
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 4 (US2) - Filter and Search**:
- T033 FilterModal, T034 SearchModal can run in parallel
- T035 filter code gen, T036 search code gen can run in parallel
- T038 FilterModal shortcut, T039 SearchModal shortcut can run in parallel

**Phase 5 (US7) - Saved Analyses**:
- T046 save, T047 list, T048 load, T049 update, T050 delete can all run in parallel (different methods)
- T051 SaveAnalysisModal, T052 SavedAnalysesListScreen, T053 ExportModal can run in parallel
- T054 export_marimo, T055 export_python, T056 export_jupyter can run in parallel

**Phase 6 (US3) - Aggregation**:
- T066 AggregateModal, T069 AggregationPanel can run in parallel

**Phase 7 (US4) - Pivot Tables**:
- T075 PivotModal, T076 PivotTableWidget can run in parallel

**Phase 10 (Remaining Modals)**:
- ALL T106-T116 (11 modal widgets) can run in parallel - different files, no dependencies

**Phase 11 (Polish)**:
- T119-T127 (error handling, performance, compatibility) can run in parallel
- T134-T136 (documentation) can run in parallel
- T137-T139 (security, accessibility) can run in parallel

**Cross-Phase Parallelism**:
- Once Foundational (Phase 2) is complete, User Stories 2, 3, 5, 7 can all start in parallel
- Phase 10 (Remaining Modals) can run in parallel with any user story phase
- Phase 11 (Polish) tasks can run in parallel once their target stories are complete

---

## Parallel Example: User Story 2 (Filter and Search)

```bash
# Launch modal widgets together:
Task T033: "Create FilterModal widget in src/kittiwake/widgets/modals/filter_modal.py"
Task T034: "Create SearchModal widget in src/kittiwake/widgets/modals/search_modal.py"

# Launch code generation functions together:
Task T035: "Implement filter operation code generation in FilterModal._build_filter_operation()"
Task T036: "Add text search operation code generation in SearchModal._build_search_operation()"

# Launch keyboard shortcut registrations together:
Task T038: "Add keyboard shortcut (Ctrl+F) for FilterModal in MainScreen keybindings"
Task T039: "Add keyboard shortcut (Ctrl+/) for SearchModal in MainScreen keybindings"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) ✅ COMPLETE

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational
3. ✅ Complete Phase 3: User Story 1
4. ✅ VALIDATED: Tested User Story 1 independently with Titanic dataset
5. Ready for deployment/demo

### Incremental Delivery (Next Steps)

1. **Next Priority (P2)**: Complete Phase 4 - User Story 2 (Filter and Search)
   - Builds on US1, adds essential data exploration capability
   - Independent test: Load data → filter → verify → clear filters
   - Deploy/Demo after completion

2. **P3 Stories (Parallel Opportunity)**:
   - Phase 5: User Story 7 (Manage and Export Saved Analyses)
   - Phase 6: User Story 3 (Aggregate and Summarize Data)
   - These can be developed in parallel by different team members
   - Both add significant value independently
   - Deploy/Demo each as completed

3. **Advanced Features**:
   - Phase 7: User Story 4 (Pivot Tables) - requires US3 concepts
   - Phase 8: User Story 5 (Merge and Join Datasets) - independent
   - Phase 9: User Story 6 (Save Analysis Workflows) - requires US2-US5

4. **Completion**:
   - Phase 10: Remaining Operation Modals (can run alongside user stories)
   - Phase 11: Polish & Cross-Cutting Concerns (final pass)

### Parallel Team Strategy

With multiple developers after User Story 1 completion:

**Scenario A: 2 Developers**
- Developer A: User Story 2 (Filter/Search) → User Story 4 (Pivot Tables)
- Developer B: User Story 7 (Saved Analyses) → User Story 3 (Aggregation)

**Scenario B: 3 Developers**
- Developer A: User Story 2 (Filter/Search) → User Story 5 (Merge/Join)
- Developer B: User Story 7 (Saved Analyses) → User Story 6 (Workflows)
- Developer C: User Story 3 (Aggregation) → User Story 4 (Pivot Tables)

**Scenario C: Solo Developer (Recommended Order)**
1. ✅ User Story 1 (Load/View) - COMPLETE
2. User Story 2 (Filter/Search) - Essential for exploration
3. User Story 7 (Saved Analyses) - Critical for reproducibility
4. User Story 3 (Aggregation) - Common analysis need
5. User Story 4 (Pivot Tables) - Advanced analysis
6. User Story 5 (Merge/Join) - Multi-dataset workflows
7. User Story 6 (Workflows) - Automation and reusability

---

## Task Summary

**Total Tasks**: 140 tasks

**By Phase**:
- Phase 1 (Setup): 6 tasks ✅ COMPLETE
- Phase 2 (Foundational): 12 tasks ✅ COMPLETE
- Phase 3 (US1 - Load/View): 14 tasks ✅ COMPLETE
- Phase 4 (US2 - Filter/Search): 13 tasks
- Phase 5 (US7 - Saved Analyses): 20 tasks
- Phase 6 (US3 - Aggregation): 9 tasks
- Phase 7 (US4 - Pivot Tables): 9 tasks
- Phase 8 (US5 - Merge/Join): 9 tasks
- Phase 9 (US6 - Workflows): 13 tasks
- Phase 10 (Remaining Modals): 13 tasks
- Phase 11 (Polish): 22 tasks

**By Story**:
- US1 (P1 - Load/View): 14 tasks ✅ COMPLETE
- US2 (P2 - Filter/Search): 13 tasks
- US3 (P3 - Aggregation): 9 tasks
- US7 (P3 - Saved Analyses): 20 tasks
- US4 (P4 - Pivot Tables): 9 tasks
- US5 (P5 - Merge/Join): 9 tasks
- US6 (P6 - Workflows): 13 tasks
- Infrastructure/Polish: 53 tasks (32 complete, 21 remaining)

**Completion Status**:
- ✅ Complete: 32 tasks (23%)
- 🔄 Remaining: 108 tasks (77%)

**MVP Scope** (✅ COMPLETE):
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 12 tasks
- Phase 3 (User Story 1): 14 tasks
- **Total MVP: 32 tasks complete and validated**

**Recommended Next Sprint** (High Value, Low Dependencies):
- Phase 4 (User Story 2): 13 tasks - Essential filtering capability
- Phase 5 (User Story 7): 20 tasks - Critical reproducibility and sharing
- **Total: 33 tasks** - Similar effort to MVP, adds major functionality

**Parallel Opportunities Identified**:
- 42 tasks marked [P] can run in parallel within their phases
- User Stories 2, 3, 5, 7 can all start simultaneously after Foundational phase
- Phase 10 (11 modals) highly parallelizable
- Phase 11 (Polish) - 15+ tasks can run in parallel

---

## Notes

- [P] tasks = different files, no dependencies within their phase
- [Story] label (US1-US7) maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests NOT included (not requested in specification)
- Focus on keyboard-first UX per constitution (all features accessible via keyboard)
- Maintain <100ms UI response time per performance goals
- Use narwhals API exclusively (no direct pandas/polars)
