# Implementation Plan: TUI Data Explorer

**Branch**: `001-tui-data-explorer` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-tui-data-explorer/spec.md`

**Note**: This plan reflects the complete TUI Data Explorer feature including all clarifications through 2026-01-09, including lazy/eager execution mode.

## Summary

Build a terminal-based data exploration tool using Textual, narwhals, and uv that allows users to:
- Load datasets from local files or remote URLs
- Filter, search, aggregate, pivot, and merge data using keyboard-driven interfaces
- Queue operations in lazy mode or execute immediately in eager mode
- Save and export analyses as executable Python/marimo/Jupyter notebooks
- Manage multiple datasets with independent operation histories

**Technical Approach**:
- Textual TUI framework for reactive keyboard-driven UI
- narwhals unified dataframe API for backend-agnostic data operations
- Sidebar-based architecture (left for configuration, right for operations history)
- DuckDB for persistent storage of saved analyses
- Lazy/eager execution modes with visual operation state indicators

## Technical Context

**Language/Version**: Python >=3.13 (as specified in constitution and pyproject.toml)  
**Primary Dependencies**: 
- textual >=7.0.1 (TUI framework)
- narwhals >=2.15.0 (unified dataframe API)
- duckdb (persistent analysis storage)
- httpx (async remote data loading)

**Storage**: 
- DuckDB database at `~/.kittiwake/analyses.db` for SavedAnalysis entities
- In-memory dataset storage via narwhals dataframes

**Testing**: pytest with Textual's testing utilities (pilot)  

**Target Platform**: Cross-platform terminal (Linux, macOS, Windows)

**Project Type**: Single project (CLI/TUI application)  

**Performance Goals**: 
- UI response time <100ms for all keyboard actions
- Data table updates <500ms for datasets up to 1M rows
- Load 1GB CSV and display first page within 3 seconds
- Operation reordering re-applies and updates within 500ms

**Constraints**: 
- Keyboard-only navigation (mouse optional)
- Support terminals with minimum 80 columns width
- Async I/O for all data loading (never block UI thread >100ms)
- Progress indicators for operations >500ms
- Maximum 10 simultaneously loaded datasets

**Scale/Scope**: 
- 13 operation types with dedicated sidebar forms
- 7 user stories (P1-P6 priorities)
- Support datasets with 1M+ rows and 100+ columns
- Handle remote data sources with retry logic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Keyboard-First Interaction
- **Status**: PASS
- **Evidence**: 
  - All features accessible via keyboard shortcuts (Ctrl+F filter, Ctrl+H search, Ctrl+E execute, etc.)
  - Help overlay (FR-007) shows context-aware shortcuts
  - No mouse dependency for any core functionality
  - Visual feedback for all actions <100ms (FR-008)
  - Keybindings already updated for French AZERTY Mac compatibility

### ✅ II. Data Source Agnostic
- **Status**: PASS
- **Evidence**:
  - FR-004: "System MUST use narwhals unified API for all data operations"
  - FR-001: Local files (CSV, Parquet, JSON)
  - FR-002: Remote HTTP/HTTPS URLs
  - FR-005: Lazy evaluation for large files
  - Users never see or configure underlying backend (pandas/polars abstracted)

### ✅ III. TUI-Native Design
- **Status**: PASS
- **Evidence**:
  - Built exclusively with Textual framework
  - Uses Textual widgets: DataTable, Containers, Screens, Modals
  - FR-009: Layout adapts to terminal resize within 100ms using Textual's reactive system
  - Sidebar architecture uses Textual's Container and CSS-based layout
  - Already implemented: MainScreen, FilterSidebar, SearchSidebar, OperationsSidebar

### ✅ IV. Performance & Responsivity
- **Status**: PASS
- **Evidence**:
  - FR-005: Lazy evaluation for files exceeding memory
  - FR-014: Loading indicators for operations >500ms
  - FR-015: Cancel long-running operations via Esc
  - FR-080: Default lazy mode respects narwhals lazy evaluation
  - SC-001: Load 1GB CSV within 3 seconds
  - SC-002: Navigate with <100ms response time
  - Async helpers already implemented in `src/kittiwake/utils/async_helpers.py`

### ✅ V. Composable Operations
- **Status**: PASS
- **Evidence**:
  - FR-079: Operations re-apply in sequence when reordered
  - FR-080-084: Lazy mode queues operations for sequential execution
  - FR-033-036: Save and reuse workflows
  - FR-040-050: Save/export analyses as notebooks
  - Operation entity stores code + display + params for editing
  - Operations chain visible in right sidebar with CRUD capabilities

**Overall Constitution Compliance**: ✅ PASS - All 5 core principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-tui-data-explorer/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── cli-interface.md           # CLI argument parsing and subcommands
│   ├── operations-schema.json     # Operation serialization format
│   ├── saved-analysis-schema.sql  # DuckDB table schema
│   ├── export-python.jinja2       # Python script export template
│   ├── export-marimo.jinja2       # Marimo notebook export template
│   └── export-jupyter.jinja2      # Jupyter notebook export template
├── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by this command)
├── CHANGELOG.md         # Implementation tracking
└── clarification-session-*.md  # Historical clarification sessions
```

### Source Code (repository root)

```text
src/kittiwake/
├── __init__.py
├── __main__.py          # Entry point for `python -m kittiwake`
├── cli.py               # CLI argument parsing (`kw load` subcommand)
├── app.py               # Main Textual App with error clipboard functionality
├── screens/
│   ├── __init__.py
│   ├── main_screen.py   # Primary dataset view with keybindings
│   └── saved_analyses_list_screen.py  # Saved analyses CRUD screen
├── widgets/
│   ├── __init__.py
│   ├── dataset_table.py      # DataTable wrapper with navigation
│   ├── dataset_tabs.py       # Multi-dataset tab switcher
│   ├── help_overlay.py       # Context-aware keyboard shortcuts
│   ├── modals/
│   │   ├── __init__.py
│   │   ├── filter_modal.py   # Column filter configuration (deprecated, replaced by sidebar)
│   │   ├── search_modal.py   # Text search configuration (deprecated, replaced by sidebar)
│   │   ├── save_analysis_modal.py  # Save analysis with name/description
│   │   └── export_modal.py   # Export format selection (Python/marimo/Jupyter)
│   └── sidebars/
│       ├── __init__.py
│       ├── filter_sidebar.py      # Left sidebar: filter configuration (30% width, overlay)
│       ├── search_sidebar.py      # Left sidebar: search configuration (30% width, overlay)
│       ├── operations_sidebar.py  # Right sidebar: operations history + mode toggle (25% width, push)
│       └── [future: aggregate_sidebar, pivot_sidebar, join_sidebar, etc.]
├── models/
│   ├── __init__.py
│   ├── dataset.py        # Dataset entity with execution_mode, queued/executed operations
│   ├── dataset_session.py  # DatasetSession managing up to 10 datasets
│   └── operations.py     # Operation entity (code, display, type, params)
├── services/
│   ├── __init__.py
│   ├── data_loader.py    # Load local/remote data via narwhals
│   ├── narwhals_ops.py   # Generate narwhals code from operation params
│   └── persistence.py    # DuckDB SavedAnalysis CRUD operations
└── utils/
    ├── __init__.py
    ├── async_helpers.py   # Async utilities for non-blocking operations
    └── keybindings.py     # Centralized keybinding registry

tests/
├── __init__.py
├── unit/
│   ├── test_app_notify_error.py      # Error clipboard functionality
│   ├── test_filter_modal.py          # Filter sidebar functionality
│   └── test_string_column_detection.py  # Column type detection
├── integration/
│   └── [narwhals backend compatibility tests - to be added]
└── e2e/
    ├── Titanic-Dataset.csv  # Test fixture
    └── [TUI interaction tests - to be added]
```

**Structure Decision**: Single project structure selected per constitution. All source code under `src/kittiwake/` with clear separation of concerns:
- `screens/` - Textual Screen subclasses (top-level views)
- `widgets/` - Reusable Textual widgets (sidebars, modals, tables)
- `models/` - Domain entities (Dataset, Operation, DatasetSession)
- `services/` - Business logic (data loading, persistence, code generation)
- `utils/` - Cross-cutting concerns (async, keybindings)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles satisfied.

---

## Phase 0: Research

**Objective**: Resolve all unknowns from Technical Context and gather best practices for implementation.

### Research Tasks

#### R1: Textual Sidebar Implementation Patterns
**Question**: What's the recommended pattern for implementing overlay vs push sidebars in Textual?

**Investigation Areas**:
- Textual Container and Grid layout for sidebar positioning
- CSS styling for overlay (z-index, absolute positioning) vs push (width adjustment)
- Animation/transition support for sidebar show/hide
- Handling simultaneous left overlay + right push sidebars

**Output**: Concrete implementation pattern for FilterSidebar (overlay) and OperationsSidebar (push)

#### R2: Execution Mode Toggle UI Patterns in TUI
**Question**: What are best practices for displaying and toggling modes (lazy/eager) in terminal UIs?

**Investigation Areas**:
- Status indicators in sidebar headers (color, icons, text)
- Toggle button implementation in Textual (Button widget with reactive state)
- Visual feedback for mode changes
- Keyboard shortcut handling for mode toggle (Ctrl+M)

**Output**: UI mockup and Textual widget hierarchy for mode toggle in right sidebar header

#### R3: Operation State Visualization (Queued vs Executed)
**Question**: How to implement icon + color coding for list items in Textual?

**Investigation Areas**:
- Rich text styling in Textual ListView/ListItem
- Unicode symbols rendering (⏸ pause, ✓ checkmark)
- Color themes (yellow for queued, green for executed) with terminal compatibility
- Accessibility considerations for colorblind users (icons provide non-color fallback)

**Output**: Textual Rich markup pattern for operation list items with icons and colors

#### R4: DuckDB Async Operations in Textual
**Question**: How to perform DuckDB operations without blocking Textual UI thread?

**Investigation Areas**:
- Textual's `run_worker()` for background tasks
- DuckDB Python API thread safety
- Error handling and progress feedback for database operations
- Connection pooling vs single connection strategy

**Output**: Async wrapper pattern for SavedAnalysis CRUD operations

#### R5: Modal Prompt for Mode Switch with Queued Operations
**Question**: Best pattern for multi-choice modal prompts in Textual?

**Investigation Areas**:
- Textual Screen vs ModalScreen for prompts
- Button layout for 3 options (Execute All / Clear All / Cancel)
- Keyboard shortcuts within modal (1/2/3 or E/C/Esc)
- Modal dismissal and result passing back to caller

**Output**: Reusable PromptModal widget pattern with keyboard navigation

#### R6: Export Template Generation (Python/marimo/Jupyter)
**Question**: What templating approach for generating executable notebooks from operations?

**Investigation Areas**:
- Jinja2 templates for code generation
- marimo cell format (Python file with `app = marimo.App()` structure)
- Jupyter notebook JSON structure (.ipynb format)
- Narwhals code serialization and escaping in templates

**Output**: Three Jinja2 templates in contracts/ directory

#### R7: Operation Execution Sequencing
**Question**: How to execute queued operations one-by-one with error handling?

**Investigation Areas**:
- Iterator pattern for stepping through queued operations
- State management (which operation is "next"?)
- Error recovery (stop on failure, mark operation as failed)
- Progress feedback during sequential execution

**Output**: ExecutionManager service class design

#### R8: Multi-Dataset Navigation with Independent States
**Question**: How to manage 10 datasets with independent operation histories?

**Investigation Areas**:
- DatasetSession state management
- Switching active dataset while preserving queued/executed states
- Tab widget or list widget for dataset selection
- Memory management when approaching 10 dataset limit

**Output**: DatasetSession API and state switching pattern

### Research Output Location

All research findings consolidated in: `specs/001-tui-data-explorer/research.md`

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### Design Artifacts

#### D1: Data Model (`data-model.md`)

**Entities to Document**:

1. **Dataset**
   - Fields: name, source_path, schema (columns + types), row_count, narwhals_df, backend_engine, is_active, execution_mode, queued_operations, executed_operations
   - Relationships: belongs to DatasetSession, has many Operations
   - State transitions: execution_mode (lazy ↔ eager with prompt if queued ops)

2. **DatasetSession**
   - Fields: datasets (max 10), active_dataset_id
   - Relationships: has many Datasets
   - Validation: MAX_DATASETS = 10 enforcement

3. **Operation**
   - Fields: code (str), display (str), operation_type (enum), params (dict), state (queued/executed/failed)
   - Relationships: belongs to Dataset
   - Validation: code generated by sidebar forms, never user-written

4. **SavedAnalysis** (DuckDB)
   - Fields: id, name, description, created_at, modified_at, operation_count, dataset_path, operations (JSON)
   - Storage: `~/.kittiwake/analyses.db`
   - Validation: unique name per user, operations JSON validates against schema

#### D2: API Contracts (`contracts/`)

**Contract Files to Generate**:

1. **cli-interface.md**
   - `kw` (bare) → Launch empty workspace
   - `kw load <paths...>` → Load datasets from paths/URLs
   - `kw --help` → Show usage
   - Exit codes and error messages

2. **operations-schema.json**
   - JSON schema for Operation serialization
   - Fields: code, display, operation_type, params, state
   - Used for SavedAnalysis.operations storage and export templates

3. **saved-analysis-schema.sql**
   - DuckDB CREATE TABLE statement
   - Indexes for performance (name, created_at)
   - Constraints (NOT NULL, unique name)

4. **export-python.jinja2**
   - Template: shebang, imports, load dataset, apply operations, print result
   - Variables: dataset_path, operations (list)

5. **export-marimo.jinja2**
   - Template: marimo imports, app = marimo.App(), cells for load + each operation
   - Variables: dataset_path, operations (list)

6. **export-jupyter.jinja2**
   - Template: JSON structure with metadata, cells (markdown intro + code cells)
   - Variables: analysis_name, description, dataset_path, operations (list)

#### D3: Quickstart Guide (`quickstart.md`)

**Sections**:
1. Installation (uv install, pip install)
2. Launch (`kw` vs `kw load data.csv`)
3. Basic workflow:
   - Load dataset
   - Open filter sidebar (Ctrl+F)
   - Apply filter → operation queues (lazy mode)
   - Execute operation (Ctrl+E)
   - Toggle to eager mode (Ctrl+M) for immediate execution
4. Save analysis (Ctrl+S)
5. Export to marimo (Ctrl+X → select marimo)
6. Keyboard shortcuts reference table

### Agent Context Update

After generating contracts and data-model.md, run:

```bash
.specify/scripts/bash/update-agent-context.sh opencode
```

This will update `AGENTS.md` with:
- DuckDB as new active technology
- Python >=3.13 confirmation
- Commands for running tests, linting, type checking

---

## Phase 2: Task Breakdown

**NOT INCLUDED IN THIS COMMAND**

Phase 2 is executed via `/speckit.tasks` command, which will:
- Read plan.md, research.md, data-model.md, contracts/
- Generate tasks.md with prioritized implementation tasks
- Create checklist from functional requirements

---

## Next Steps

1. **Execute Phase 0**: Generate research.md by dispatching research tasks R1-R8
2. **Execute Phase 1**: Generate data-model.md, contracts/, quickstart.md
3. **Update Agent Context**: Run update-agent-context.sh to add DuckDB to AGENTS.md
4. **Re-verify Constitution**: Confirm all gates still pass after design decisions
5. **Proceed to Phase 2**: Run `/speckit.tasks` to generate implementation task breakdown

---

## Appendix: Key Design Decisions from Clarifications

### Lazy/Eager Execution Mode (2026-01-09)
- **Default**: Lazy mode (operations queue without executing)
- **Toggle UI**: Right sidebar header with button + Ctrl+M shortcut
- **Execute Shortcuts**: Ctrl+E (next operation), Ctrl+Shift+E (all operations)
- **Visual State**: ⏸ (yellow) for queued, ✓ (green) for executed
- **Mode Switch**: Prompt modal with 3 choices when switching lazy→eager with queued ops

### Sidebar Architecture (2026-01-09)
- **Left Sidebar**: 30% width, overlays data table (semi-transparent)
- **Right Sidebar**: 25% width, pushes/compresses data table
- **Right Sidebar Visibility**: Auto-show when first operation applied, hide when empty
- **Operations CRUD**: View, remove, edit (reopens left sidebar), reorder (Ctrl+Up/Down)

### Column Navigation (2026-01-09)
- **Column Width**: Max 40 characters with ellipsis truncation
- **Full Content**: Enter key opens modal to view full cell content
- **Fast Navigation**: Ctrl+Left/Right jumps 5 columns
- **Auto-scroll**: Viewport scrolls when cursor navigates beyond visible columns

### Keybindings (French AZERTY Mac Compatibility)
- **Search**: Ctrl+H (was Ctrl+/, conflicts with Shift+: on AZERTY)
- **Clear All**: Ctrl+Shift+X (was Ctrl+C, conflicts with copy)
- **Mode Toggle**: Ctrl+M
- **Execute Next**: Ctrl+E
- **Execute All**: Ctrl+Shift+E
