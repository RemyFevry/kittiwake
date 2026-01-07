# Feature Specification: TUI Data Explorer

**Feature Branch**: `001-tui-data-explorer`  
**Created**: 2026-01-07  
**Status**: Draft  
**Input**: User description: "Build a Python TUI package using uv, narwhals, and textual that allows users to interact with data stored in files or remote sources using narwhals and perform data analysis, pivot tables, summarization, search, aggregation, and merging primarily using keyboard interactions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load and View Data (Priority: P1)

A data analyst opens kittiwake in their terminal using the `kw` command. They can launch with `kw load` followed by file paths or URLs (e.g., `kw load data.csv sales.parquet https://example.com/data.json`) to load datasets from their local filesystem or remote sources. If launched with bare `kw` without the load subcommand, they are presented with an empty workspace where they can load data via keyboard shortcut. They can load up to 10 datasets during a session, with visual indicators (tabs/list) showing all loaded datasets. They can immediately view the data in a paginated table, scroll through rows, and see column headers with data types. The interface responds instantly to keyboard commands for navigation. The TUI displays one active dataset at a time, with keyboard shortcuts to switch between loaded datasets or open them in split panes.

**Why this priority**: This is the foundational capability - users must be able to load and view data before performing any analysis. Without this, the application has no purpose.

**Independent Test**: Can be fully tested by launching kittiwake (both with and without the load subcommand), loading a CSV file, and verifying that data displays correctly with keyboard navigation working. Test loading multiple datasets and switching between them.

**Acceptance Scenarios**:

1. **Given** kittiwake is launched without arguments (`kw`), **When** user views the interface, **Then** an empty workspace is displayed with instructions to load data
2. **Given** kittiwake is launched with load subcommand and file paths (`kw load file1.csv file2.json`), **When** application starts, **Then** all specified files load automatically and the first displays in the main view
3. **Given** kittiwake is launched with mixed local and remote sources (`kw load local.csv https://example.com/data.parquet`), **When** application starts, **Then** both datasets load and are available for viewing
4. **Given** kittiwake is launched, **When** user presses the file open shortcut and selects a local CSV file, **Then** data loads and displays in a paginated table with column headers
5. **Given** data is displayed, **When** user presses arrow keys, **Then** cursor moves between rows and columns with visual feedback
6. **Given** a dataset with 1M+ rows, **When** user loads the file, **Then** application remains responsive and shows loading progress
7. **Given** data is displayed, **When** user presses the page down key, **Then** next page of data loads within 100ms
8. **Given** user is viewing data, **When** they press the help key, **Then** keyboard shortcuts overlay appears
9. **Given** one dataset is loaded, **When** user loads a second dataset, **Then** both datasets are available and user can switch between them via keyboard shortcut
10. **Given** multiple datasets are loaded, **When** user activates split pane mode, **Then** two datasets display side-by-side for comparison
11. **Given** user has 10 datasets loaded, **When** user attempts to load an 11th dataset, **Then** system displays message prompting to close an existing dataset first
12. **Given** multiple datasets are loaded, **When** user views the interface, **Then** visual indicators (tabs or list) show all loaded datasets with active one highlighted

---

### User Story 2 - Filter and Search Data (Priority: P2)

A user has loaded a dataset and wants to find specific records. They activate the search function via keyboard, type filter criteria (e.g., "age > 25"), and see results update in real-time. They can combine multiple filters and clear them quickly. When switching to a different dataset, the filters remain on the original dataset and the new dataset displays with its own independent filter state.

**Why this priority**: Filtering is essential for data exploration and narrows down large datasets to relevant subsets. It's a prerequisite for meaningful analysis.

**Independent Test**: Load sample data, apply text search and column filters, verify filtered results display correctly and can be cleared. Load a second dataset, verify first dataset's filters are preserved when switching back.

**Acceptance Scenarios**:

1. **Given** data is displayed, **When** user activates search mode and types text, **Then** rows matching the text in any column are highlighted and non-matching rows are hidden
2. **Given** data is displayed, **When** user activates column filter and selects a column with conditions, **Then** only rows meeting the conditions remain visible
3. **Given** multiple filters are active, **When** user clears filters, **Then** full dataset is restored immediately
4. **Given** a large dataset with filters applied, **When** filters change, **Then** results update within 500ms with progress indicator for longer operations
5. **Given** filters are applied to dataset A, **When** user switches to dataset B, **Then** dataset B displays without filters and dataset A's filters remain intact
6. **Given** user switches back to a previously filtered dataset, **When** dataset becomes active, **Then** previous filter state is restored

---

### User Story 3 - Aggregate and Summarize Data (Priority: P3)

A user wants to understand summary statistics about their data. They select a column via keyboard, activate the aggregation menu, choose functions (sum, mean, count, etc.), and see results displayed in a summary panel. They can group by columns and see grouped aggregations.

**Why this priority**: Aggregation provides insights into data patterns and distributions, essential for exploratory data analysis.

**Independent Test**: Load numeric data, select columns, apply aggregation functions (sum, mean, count), verify correct calculations display.

**Acceptance Scenarios**:

1. **Given** data is displayed, **When** user selects a numeric column and activates aggregation, **Then** summary statistics (count, mean, median, min, max) appear in a panel
2. **Given** data is displayed, **When** user selects group-by column and aggregation column, **Then** grouped results display with aggregation values for each group
3. **Given** aggregations are displayed, **When** user exports results, **Then** aggregated data is saved to a new file

---

### User Story 4 - Create Pivot Tables (Priority: P4)

A user creates a pivot table by selecting row dimensions, column dimensions, and aggregation values using keyboard commands. The pivot table displays in an interactive view where they can expand/collapse groups and re-arrange dimensions.

**Why this priority**: Pivot tables enable multi-dimensional analysis, but build on core filtering and aggregation capabilities.

**Independent Test**: Load sample data with categorical and numeric columns, create pivot table with row/column groupings, verify calculations are correct.

**Acceptance Scenarios**:

1. **Given** data is loaded, **When** user activates pivot mode and selects row/column dimensions with aggregation value, **Then** pivot table displays with correct calculations
2. **Given** pivot table is displayed, **When** user collapses/expands groups, **Then** detail rows hide/show smoothly
3. **Given** pivot table is created, **When** user saves the pivot configuration, **Then** configuration can be reloaded later

---

### User Story 5 - Merge and Join Datasets (Priority: P5)

A user has two datasets loaded and wants to combine them. They activate merge mode, select join columns from each dataset, choose join type (inner, left, right, outer), and preview the merged result before applying.

**Why this priority**: Merging combines data from multiple sources, but depends on loading and viewing capabilities being stable.

**Independent Test**: Load two CSV files with a common key column, perform inner join, verify merged dataset contains correct rows.

**Acceptance Scenarios**:

1. **Given** two datasets are loaded, **When** user activates merge mode and selects matching columns with join type, **Then** preview of merged data appears
2. **Given** merge preview is displayed, **When** user confirms merge, **Then** merged dataset replaces active view
3. **Given** merge is performed, **When** join keys don't match, **Then** user sees warning and can adjust join settings

---

### User Story 6 - Save Analysis Workflows (Priority: P6)

A user has performed a sequence of operations (filter → group → aggregate) and wants to save this workflow. They name the workflow, save it, and can reapply it to new datasets with the same schema.

**Why this priority**: Workflow saving enables reproducibility and efficiency, but requires core operations to be mature first.

**Independent Test**: Perform a sequence of operations, save workflow, load new dataset with same schema, apply workflow, verify same operations execute.

**Acceptance Scenarios**:

1. **Given** user has performed multiple operations, **When** they save workflow with a name, **Then** workflow is persisted to disk
2. **Given** a saved workflow exists, **When** user loads a new dataset and applies the workflow, **Then** operations execute in sequence automatically
3. **Given** a workflow is applied, **When** user wants to modify it, **Then** they can edit individual steps and save the updated version

---

### User Story 7 - Manage and Export Saved Analyses (Priority: P3)

A user has performed several exploratory analyses and wants to save specific analyses for future reference or sharing. They can name analyses with descriptions, view all saved analyses, update existing ones, and delete those no longer needed. When they load a saved analysis, the system automatically reloads the original dataset from its stored path and reapplies all saved operations in sequence. Users can then export saved analyses as executable marimo notebooks, Python scripts, or Jupyter notebooks to share with colleagues or integrate into automated workflows.

**Why this priority**: Saving and exporting analyses is critical for reproducibility, collaboration, and transitioning from exploration to production. This enables users to document their work and share insights. Priority P3 places it after core viewing and filtering but before advanced pivot/merge features.

**Independent Test**: Perform operations, save analysis with metadata, list saved analyses, update/delete analyses, load a saved analysis and verify original dataset reloads with operations applied, export to all three formats (marimo/Python/Jupyter), verify generated code executes correctly.

**Acceptance Scenarios**:

1. **Given** user has performed operations on a dataset, **When** they save the analysis with name and description, **Then** analysis is stored in DuckDB with timestamp, operation count, and dataset path
2. **Given** multiple saved analyses exist, **When** user views the saved analyses list, **Then** all analyses display with name, description, created/modified dates, and operation count
3. **Given** a saved analysis exists, **When** user updates its name or description, **Then** changes persist and modified timestamp updates
4. **Given** a saved analysis exists, **When** user deletes it, **Then** analysis is removed from storage and no longer appears in list
5. **Given** a saved analysis exists, **When** user loads it, **Then** original dataset reloads from stored path and all saved operations apply in sequence
6. **Given** a loaded saved analysis, **When** dataset or operations complete, **Then** user can view results and continue with additional operations
7. **Given** a saved analysis exists, **When** user exports to marimo notebook, **Then** a .py file with marimo cells is generated containing data loading and all operations
8. **Given** a saved analysis exists, **When** user exports to Python script, **Then** a standalone .py file is generated with narwhals operations
9. **Given** a saved analysis exists, **When** user exports to Jupyter notebook, **Then** a .ipynb file is generated with code cells for each operation
10. **Given** user tries to export without saving analysis first, **Then** system prompts to save before export

---

### Edge Cases

- What happens when a file is too large to fit in memory? System should use lazy evaluation (via narwhals) and paginate results.
- What happens when a remote data source is unreachable? Display clear error message with option to retry or switch to cached data.
- What happens when user tries to aggregate non-numeric columns? Show appropriate warning and suggest compatible operations (count, unique values).
- What happens when terminal window is resized during operation? Layout adapts immediately without losing state.
- What happens when user tries to load an unsupported file format? Display clear error with list of supported formats.
- What happens when join keys have mismatched data types? Attempt automatic conversion or warn user to manually cast columns.
- What happens when user tries to export an unsaved analysis? System prompts to save analysis first before allowing export.
- What happens when DuckDB database is corrupted or inaccessible? Display error and offer to reinitialize database (with warning about data loss).
- What happens when exporting to a file path that already exists? Prompt user to overwrite, rename, or cancel.
- What happens when saved analysis references a dataset that no longer exists? Display warning when loading, allow user to update dataset path or delete analysis.
- What happens when trying to save an analysis with duplicate name? Either warn and require unique name, or auto-version with timestamp suffix.
- What happens when user tries to load multiple datasets that exceed available memory combined? Display warning showing memory usage and suggest closing datasets or using lazy evaluation.
- What happens when switching between datasets with different active filters/operations? Each dataset maintains its own operation state independently.
- What happens when user tries to merge datasets that aren't both loaded? Display error and prompt to load the second dataset first.
- What happens when CLI argument points to a non-existent file? Display error message for that file and continue loading other valid files, or launch with empty workspace if all fail.
- What happens when user provides both local and remote sources as CLI arguments and remote sources time out? Load available local files immediately, show loading indicator for remote sources, and allow user to retry or cancel remote loads.
- What happens when user tries to load more than 10 datasets? Display message indicating limit reached and prompt to close an existing dataset before loading new one.
- What happens when user launches with more than 10 files in `kw load` command? Load first 10 datasets and display warning listing datasets that were not loaded due to limit.
- What happens when user runs `kw` with an unrecognized subcommand? Display error message with list of valid subcommands and usage help.

## Requirements *(mandatory)*

### Functional Requirements

**Data Loading:**
- **FR-001**: System MUST load data from local files (CSV, Parquet, JSON formats)
- **FR-002**: System MUST load data from remote HTTP/HTTPS URLs
- **FR-003**: System MUST detect and display data types for each column automatically
- **FR-004**: System MUST use narwhals unified API for all data operations (no direct pandas/polars usage)
- **FR-005**: System MUST support lazy evaluation for large files exceeding available memory
- **FR-051**: System MUST support `kw load` subcommand accepting file path(s) and URL(s) as positional arguments (e.g., `kw load file1.csv file2.json https://example.com/data.parquet`)
- **FR-052**: System MUST display an empty workspace with load instructions when launched with bare `kw` command
- **FR-053**: System MUST allow users to load multiple datasets during a session
- **FR-054**: System MUST maintain one "active" dataset displayed in the main view at any time
- **FR-055**: System MUST provide keyboard shortcuts to switch between loaded datasets
- **FR-056**: System MUST support split pane mode to display two datasets side-by-side
- **FR-057**: System MUST load all CLI-specified datasets at startup via `kw load`, displaying the first in the main view
- **FR-063**: System MUST enforce a maximum limit of 10 simultaneously loaded datasets
- **FR-064**: System MUST display visual indicators (tabs or list) showing all loaded datasets with the active one highlighted
- **FR-065**: System MUST prevent loading additional datasets when limit is reached and prompt user to close existing datasets

**User Interface:**
- **FR-006**: System MUST provide keyboard-only navigation for all features
- **FR-007**: System MUST display a help overlay showing keyboard shortcuts in current context
- **FR-008**: System MUST provide visual feedback for all keyboard actions within 100ms
- **FR-009**: System MUST adapt layout when terminal window is resized
- **FR-010**: System MUST support both light and dark terminal themes
- **FR-058**: System MUST apply all operations (filter, aggregate, pivot, etc.) only to the active dataset
- **FR-059**: System MUST maintain independent operation state for each loaded dataset
- **FR-060**: System MUST preserve operation state when switching between datasets

**Data Viewing:**
- **FR-011**: System MUST display data in a paginated table with column headers
- **FR-012**: System MUST show row numbers and total row count
- **FR-013**: System MUST allow users to scroll horizontally and vertically through data
- **FR-014**: System MUST display loading indicators for operations exceeding 500ms
- **FR-015**: System MUST allow users to cancel long-running operations

**Filtering and Search:**
- **FR-016**: System MUST support text search across all columns
- **FR-017**: System MUST support column-specific filters with comparison operators (=, !=, >, <, >=, <=, contains)
- **FR-018**: System MUST allow combining multiple filters with AND/OR logic
- **FR-019**: System MUST show count of filtered rows vs total rows
- **FR-020**: System MUST allow clearing all filters with single keyboard command

**Aggregation and Summarization:**
- **FR-021**: System MUST compute summary statistics (count, sum, mean, median, min, max, std) for numeric columns
- **FR-022**: System MUST support group-by operations with aggregation functions
- **FR-023**: System MUST allow users to select multiple aggregation functions simultaneously
- **FR-024**: System MUST display aggregation results in a dedicated panel

**Pivot Tables:**
- **FR-025**: System MUST allow users to create pivot tables with configurable row and column dimensions
- **FR-026**: System MUST support multiple aggregation values in pivot tables
- **FR-027**: System MUST allow expanding/collapsing grouped rows in pivot views
- **FR-028**: System MUST allow users to save and reload pivot configurations

**Merging and Joining:**
- **FR-029**: System MUST support inner, left, right, and outer joins
- **FR-030**: System MUST allow users to select join columns from each dataset
- **FR-031**: System MUST preview merge results before applying
- **FR-032**: System MUST warn when join keys have mismatched types or missing values

**Workflow Management:**
- **FR-033**: System MUST allow users to save sequences of operations as reusable workflows
- **FR-034**: System MUST persist workflows to disk in a human-readable format
- **FR-035**: System MUST allow users to apply saved workflows to new datasets
- **FR-036**: System MUST provide undo/redo for individual operations

**Export:**
- **FR-037**: System MUST export current view (filtered/aggregated) to CSV format
- **FR-038**: System MUST export to Parquet format for efficient storage
- **FR-039**: System MUST allow exporting pivot tables as separate files

**Saved Analysis Management:**
- **FR-040**: System MUST allow users to save current analysis with name and description
- **FR-041**: System MUST store saved analyses in DuckDB database with metadata (name, description, created_at, modified_at, operation_count)
- **FR-042**: System MUST list all saved analyses with their metadata
- **FR-043**: System MUST allow users to update name and description of saved analyses
- **FR-044**: System MUST allow users to delete saved analyses
- **FR-045**: System MUST prevent export of analyses that haven't been saved
- **FR-046**: System MUST export saved analyses to marimo notebook format (.py with marimo cells)
- **FR-047**: System MUST export saved analyses to Python script format (.py with narwhals operations)
- **FR-048**: System MUST export saved analyses to Jupyter notebook format (.ipynb)
- **FR-049**: System MUST include data loading code and all operations in exported notebooks/scripts
- **FR-050**: System MUST prompt for file overwrite confirmation when export path already exists
- **FR-061**: System MUST allow users to load a saved analysis, which reloads the original dataset and reapplies all operations
- **FR-062**: System MUST verify dataset path accessibility before loading saved analysis and warn if unavailable

### Key Entities

- **Dataset**: Represents loaded data with schema information (column names, types, row count), source location (file path or URL), backend engine (pandas/polars/etc. via narwhals), active status (whether currently displayed in main view), and operation history (narwhals expressions applied to this dataset)

- **DatasetSession**: Represents the collection of all loaded datasets in the current session with list of Dataset objects (max 10), active dataset reference, and split pane configuration state

- **Operation**: Represents a single data transformation operation stored as:
  - `code` (str): Narwhals expression code string (e.g., `"df.filter(nw.col('age') > 25)"`)
  - `display` (str): Human-readable description (e.g., `"Filter: age > 25"`)
  - `operation_type` (str): Operation category (filter, aggregate, pivot, join, select, drop, rename, with_columns, sort, unique, fill_null, drop_nulls, head, tail, sample)
  - `params` (dict): Operation parameters for modal editing (e.g., `{"column": "age", "operator": ">", "value": 25}`)
  - Generated by TUI modals (keyboard-driven forms), never written by users directly
  - Validated immediately on creation and at runtime when applied

- **Workflow**: Represents a saved sequence of operations with name, description, operation steps (list of Operation objects), and target dataset schema

- **SavedAnalysis**: Represents a saved analysis stored in DuckDB with:
  - `id` (INTEGER PRIMARY KEY): Unique identifier
  - `name` (TEXT NOT NULL): User-provided analysis name
  - `description` (TEXT): Optional description of analysis purpose
  - `created_at` (TIMESTAMP NOT NULL): Timestamp when analysis was first saved
  - `modified_at` (TIMESTAMP NOT NULL): Timestamp of last modification
  - `operation_count` (INTEGER NOT NULL): Number of operations in the analysis
  - `dataset_path` (TEXT NOT NULL): Source dataset file path or URL
  - `operations` (JSON NOT NULL): Serialized list of Operation objects (code + display + type + params)
  - Storage: DuckDB database file at `~/.kittiwake/analyses.db`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load a 1GB CSV file and view first page of data within 3 seconds
- **SC-002**: Users can navigate between rows using arrow keys with under 100ms response time
- **SC-003**: Users can complete a filter → group → aggregate workflow in under 2 minutes on their first use (with help overlay)
- **SC-004**: System remains responsive with datasets containing 10M+ rows using lazy evaluation
- **SC-005**: 90% of users can discover and use core features (load, filter, aggregate) without reading documentation
- **SC-006**: Users can create and save a complex workflow (5+ operations) and reapply it to a new dataset in under 1 minute
- **SC-007**: System displays progress feedback for all operations taking longer than 500ms
- **SC-008**: Terminal layout adapts to window resize within 100ms without losing data view position
- **SC-009**: Users successfully complete data joining tasks 85% of the time on first attempt
- **SC-010**: System handles common errors (file not found, network timeout, type mismatches) with clear, actionable error messages
- **SC-011**: Users can save, update, and export an analysis to marimo/Python/Jupyter in under 30 seconds
- **SC-012**: Exported notebooks/scripts execute successfully without modification 95% of the time
- **SC-013**: DuckDB operations (save, list, update, delete analyses) complete within 200ms for databases with up to 1000 saved analyses
- **SC-014**: Users can switch between 10 loaded datasets with under 150ms response time
- **SC-015**: Visual dataset indicators (tabs/list) remain readable and navigable with up to 10 datasets loaded

## Clarifications

### Session 2026-01-07

**Context**: User requested adding capability to export analyses to Python/marimo notebooks.

**Questions and Answers**:

1. **Q**: Should users be able to export any analysis at any time, or only saved analyses? Should there be a notion of "saved analyses" that users can manage (create, update, delete)?
   - **A**: Users should be able to manage saved analyses (create, update, delete). Only saved analyses can be exported.

2. **Q**: What export formats should be supported? Just marimo notebooks, or also plain Python scripts and/or Jupyter notebooks?
   - **A**: All three formats - marimo notebooks, Python scripts, AND Jupyter notebooks.

3. **Q**: Where should saved analyses be stored? Options: (a) JSON files in ~/.kittiwake/, (b) SQLite/DuckDB database, (c) TOML configuration files?
   - **A**: DuckDB database for storing saved analyses.

4. **Q**: What metadata should be stored with each saved analysis? (name, description, timestamps, tags, operation count, dataset reference, etc.)
   - **A**: Name, description, creation timestamp, modified timestamp, and operation count.

5. **Q**: How should multiple datasets be managed within the active session?
   - **A**: Multiple datasets are loaded but the TUI shows one "active" dataset at a time, with keyboard shortcuts to switch between them or open them in split panes.

6. **Q**: What CLI syntax should be used to specify data sources at launch?
   - **A**: Subcommand-based with positional arguments: `kw load file1.csv file2.parquet https://example.com/data.json` (using `load` subcommand for extensibility; bare `kw` launches empty workspace)

7. **Q**: When a user applies an operation (filter, aggregate, pivot), does it apply only to the active dataset or can users apply operations across multiple datasets?
   - **A**: Operations apply only to the active dataset; each dataset maintains independent operation state.

8. **Q**: When a user loads/applies a saved analysis, what dataset does it operate on?
   - **A**: Saved analysis automatically reloads the original dataset from the stored dataset_path and applies operations to it.

9. **Q**: What should be the maximum number of datasets that can be loaded simultaneously in a session?
   - **A**: Practical limit of 10 datasets with visual indicators (tabs/list) showing all loaded datasets.

**Integration**:
- Added User Story 7: "Manage and Export Saved Analyses" (Priority: P3)
- Added FR-040 through FR-050 for saved analysis CRUD and export operations
- Added SavedAnalysis entity with DuckDB schema specification
- Updated edge cases for export scenarios (unsaved analyses, file conflicts, database issues, duplicate names)
- Added SC-011, SC-012, SC-013 for export and DuckDB performance criteria

---

### Session 2026-01-08

**Context**: Simplification of operation storage model based on user feedback that operations should be stored as narwhals expression strings instead of complex structured classes.

**Questions and Answers**:

1. **Q**: How should narwhals expressions be serialized?
   - **A**: Store as Python code strings. TUI will translate user interactions into narwhals code, but users never write code directly.

2. **Q**: How should the TUI enable users to build narwhals expressions without writing code?
   - **A**: Modal-based approach with forms (filter modal with column dropdown, operator dropdown, value input) - keyboard-driven.

3. **Q**: Which narwhals operations need TUI modal support initially?
   - **A**: 13 operations with dedicated modals:
     - Core: filter, aggregate, pivot, join
     - Selection: select, drop, rename
     - Transform: with_columns, sort
     - Data cleaning: unique, fill_null, drop_nulls
     - Sampling: head, tail, sample

4. **Q**: How should operations be stored in the simplified model?
   - **A**: Store code + display string + operation_type + params (for edit capability). This enables users to edit operations later by reopening the modal with pre-filled values.

5. **Q**: How should we handle validation and safety of generated narwhals code?
   - **A**: 
     - **Validation timing**: Both immediate validation (on modal submit with sample data) + runtime validation (when applying to dataset)
     - **Safety**: Since TUI generates all code from modals, trust the generator (no AST parsing required)
     - **Error handling**: Stop operation chain and show error to user

**Integration**:
- Simplified Key Entities: Removed Filter, Aggregation, PivotTable classes; replaced with single Operation entity
- Operation stores: code (narwhals expression string), display (human-readable), operation_type, params (for editing)
- Updated SavedAnalysis.operations field description to reflect code-based storage
- All 13 operation types will have dedicated keyboard-driven modal forms in TUI
- Validation occurs both at modal submit time and runtime application
