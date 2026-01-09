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
5. **Given** data is displayed, **When** user presses Left/Right arrow keys, **Then** cursor moves between columns with visual feedback
6. **Given** data is displayed, **When** user presses Up/Down arrow keys, **Then** cursor moves between rows with visual feedback
7. **Given** a dataset with 1M+ rows, **When** user loads the file, **Then** application remains responsive and shows loading progress
8. **Given** data is displayed, **When** user presses the page down key, **Then** next page of data loads within 100ms
9. **Given** user is viewing data, **When** they press the help key, **Then** keyboard shortcuts overlay appears
10. **Given** one dataset is loaded, **When** user loads a second dataset, **Then** both datasets are available and user can switch between them via keyboard shortcut
11. **Given** multiple datasets are loaded, **When** user activates split pane mode, **Then** two datasets display side-by-side for comparison
12. **Given** user has 10 datasets loaded, **When** user attempts to load an 11th dataset, **Then** system displays message prompting to close an existing dataset first
13. **Given** multiple datasets are loaded, **When** user views the interface, **Then** visual indicators (tabs or list) show all loaded datasets with active one highlighted
14. **Given** data is displayed with long column content, **When** user views columns, **Then** each column is capped at 40 characters with ellipsis for longer content
15. **Given** a cell contains truncated content and cursor is on that cell, **When** user presses Enter key, **Then** full content displays in a modal or overlay
16. **Given** dataset has more columns than fit on screen, **When** user navigates right beyond visible columns, **Then** viewport automatically scrolls to show the next columns
17. **Given** data is displayed with many columns, **When** user presses Ctrl+Right, **Then** cursor jumps 5 columns to the right
18. **Given** data is displayed with many columns, **When** user presses Ctrl+Left, **Then** cursor jumps 5 columns to the left
19. **Given** user has performed operations on a dataset, **When** source file is updated on disk and user reloads current dataset, **Then** source file is re-read, current operations (queued and executed) are preserved, and operations are re-applied in sequence to refreshed data
20. **Given** dataset source file is deleted or moved, **When** user tries to reload current dataset, **Then** error displays showing path and options: (a) Remove dataset from session, (b) Update dataset path
21. **Given** dataset source file has incompatible schema changes when user reloads, **When** an operation fails due to missing column, **Then** error displays with operation name and options: (a) Clear operations and use refreshed schema, (b) Cancel reload, keep old data view
22. **Given** user reloads dataset while operations are executing, **When** reload is triggered, **Then** system blocks reload until current execution completes, then queues reload as next operation or executes immediately depending on execution mode

---

### User Story 2 - Filter and Search Data (Priority: P2)

A user has loaded a dataset and wants to find specific records. They activate the filter function via keyboard, which opens the left sidebar with a filter configuration form. They select a column, choose an operator (e.g., "age > 25"), enter a value, and apply the filter. In lazy mode (default), the left sidebar dismisses and the operation appears in the right sidebar as "queued" without changing the data table. The user can continue adding more operations or execute them one-by-one or all at once using keyboard shortcuts. When executed, results update in the data table. In eager mode, operations execute immediately when applied. They can open the left sidebar again to add more filters, view the filter chain in the right sidebar, edit existing filters by clicking them in the right sidebar (which reopens the left sidebar with pre-filled values), or reorder filters using keyboard shortcuts. When switching to a different dataset, the filters remain on the original dataset and the new dataset displays with its own independent filter state and operations history.

**Why this priority**: Filtering is essential for data exploration and narrows down large datasets to relevant subsets. It's a prerequisite for meaningful analysis.

**Independent Test**: Load sample data, apply text search and column filters using left sidebar, verify operations appear in right sidebar as queued (lazy mode) or executed (eager mode), execute queued operations and verify filtered results display correctly in data table, verify filters can be edited/removed/reordered. Load a second dataset, verify first dataset's filters are preserved when switching back.

**Acceptance Scenarios**:

1. **Given** data is displayed in lazy mode (default), **When** user activates search mode (opens left sidebar) and types text in search form, **Then** left sidebar dismisses after apply, right sidebar shows search operation as "queued", and data table remains unchanged until execution
2. **Given** data is displayed in eager mode, **When** user activates search mode (opens left sidebar) and types text in search form, **Then** left sidebar dismisses after apply, right sidebar shows search operation as "executed", and rows matching the text in any column are highlighted while non-matching rows are hidden immediately
3. **Given** data is displayed in lazy mode, **When** user activates column filter (opens left sidebar) and configures column with conditions, **Then** left sidebar dismisses after apply, right sidebar shows filter operation as "queued", and data table remains unchanged until execution
4. **Given** data is displayed in eager mode, **When** user activates column filter (opens left sidebar) and configures column with conditions, **Then** left sidebar dismisses after apply, right sidebar shows filter operation as "executed", and only rows meeting the conditions remain visible immediately
3. **Given** multiple filters are active (shown in right sidebar), **When** user clears all filters via keyboard command, **Then** all operations are removed from right sidebar, right sidebar auto-hides, and full dataset is restored immediately
4. **Given** a large dataset with filters applied, **When** filters change, **Then** results update within 500ms with progress indicator for longer operations
5. **Given** filters are applied to dataset A (visible in right sidebar), **When** user switches to dataset B, **Then** dataset B displays without filters and dataset A's filters remain intact in its own operations history
6. **Given** user switches back to a previously filtered dataset, **When** dataset becomes active, **Then** previous filter state is restored and right sidebar shows previous operations history
7. **Given** operations are visible in right sidebar, **When** user selects an operation and chooses edit, **Then** left sidebar opens with pre-filled form values for that operation
8. **Given** multiple operations in right sidebar, **When** user reorders operations using keyboard shortcuts, **Then** operations re-apply in new sequence and data table updates accordingly

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

- What happens when user reloads current dataset? System re-reads source file from its stored path, preserves current operations queue (both queued and executed), then re-operations them in sequence to the refreshed data
- What happens when dataset source file is deleted or moved when user tries to reload? Display error: "Source file no longer accessible: <path>. Options: (a) Remove dataset from session, (b) Update dataset path"
- What happens when dataset source file changed in incompatible way (e.g., columns renamed, schema changed) when user reloads? Attempt to re-apply operations; if any operation fails due to schema mismatch, display error: "Reload failed: Operation '<op_name>' references column that no longer exists. Options: (a) Clear operations and use refreshed schema, (b) Cancel reload, keep old data view"
- What happens when reloading a dataset while operations are executing? Block reload operation until current execution completes, then queue reload as next operation or execute immediately depending on current execution mode
- What happens when a file is too large to fit in memory? System should use lazy evaluation (via narwhals) and paginate results.
- What happens when a remote data source is unreachable? Display clear error message with option to retry or switch to cached data.
- What happens when user tries to aggregate non-numeric columns? Show appropriate warning and suggest compatible operations (count, unique values).
- What happens when terminal window is resized during operation? Layout adapts immediately without losing state.
- What happens when user tries to load an unsupported file format? Display clear error with list of supported formats.
- What happens when join keys have mismatched data types? System attempts narwhals-supported automatic type conversion (int↔float, string→category). If conversion fails or types are incompatible (e.g., Int64 vs String), display modal: "Join key types differ: left=Int64, right=String. Options: (a) Cancel join (b) View type details (c) Manually select columns with correct types"
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
- What happens when dataset contains columns with very wide content (e.g., long text fields, URLs)? Column width is capped at 40 characters with ellipsis; users can view full content via keyboard shortcut.
- What happens when dataset has 100+ columns and user navigates horizontally? Viewport automatically scrolls to follow cursor; column headers remain visible; performance stays under 100ms per navigation step.
- What happens when user reorders operations and the new sequence produces an error (e.g., filtering on a column that was dropped in an earlier operation)? Display error message, revert to previous valid operation order, and highlight the problematic operation.
- What happens when user edits an operation in the middle of the operations chain? System re-applies all operations from the edited operation onward in sequence, updating the dataset view.
- What happens when user removes an operation that other operations depend on? System re-applies remaining operations in order; if subsequent operations fail due to missing dependencies, display error and allow user to fix or remove dependent operations.
- What happens when terminal width is too narrow to display both sidebars and data table? System enforces minimum terminal width (e.g., 80 columns); if terminal is resized below minimum, display warning overlay suggesting resize.
- What happens when user opens left sidebar while right sidebar is visible? Both sidebars display simultaneously (left overlays data at 30% width, right compresses data to 75% width, effective data viewing width is 45%).
- What happens when user closes left sidebar after applying operation? Left sidebar dismisses, data table remains at compressed width (75%) if right sidebar is visible, or returns to full width if right sidebar is hidden.
- What happens when user switches from lazy to eager mode with queued operations? System displays modal prompting user to choose: (a) Execute all queued operations and switch to eager mode, (b) Clear queued operations and switch to eager mode, (c) Cancel mode switch and stay in lazy mode. Modal uses keyboard shortcuts (1/2/3 or E/C/Esc) for selection.
- What happens when user switches from eager to lazy mode? Mode switches immediately; future operations queue without executing until user triggers execution.
- What happens when user switches datasets with queued operations in lazy mode? Queued operations remain associated with the original dataset; switching back restores the queued state.
- What happens when user executes operations one-by-one and an operation fails? Execution stops at the failed operation, error displays, and remaining queued operations stay queued for user to fix or remove the problematic operation.
- What happens when user tries to toggle execution mode while right sidebar is hidden? Ctrl+M keyboard shortcut still works to toggle mode; right sidebar auto-shows to display new mode state and allow further interaction.
- What happens when user presses Ctrl+E or Ctrl+Shift+E in eager mode? Keyboard shortcuts are ignored (no-op) since there are no queued operations in eager mode; optionally show brief message "No queued operations (eager mode active)".

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
- **FR-054**: System MUST maintain one "active" dataset displayed in main view at any time
- **FR-055**: System MUST provide keyboard shortcuts to switch between loaded datasets
- **FR-056**: System MUST support split pane mode to display two datasets side-by-side
- **FR-057**: System MUST load all CLI-specified datasets at startup via `kw load`, displaying the first in main view
- **FR-063**: System MUST enforce a maximum limit of 10 simultaneously loaded datasets with: (a) prevention when limit reached, (b) visual indicators (tabs or list) showing all loaded datasets with active one highlighted, (c) prompt to close existing dataset before adding new one
- **FR-064**: System MUST allow users to reload currently active dataset from its original source file while preserving the current operations queue, then re-apply those operations to the refreshed data

**User Interface:**
- **FR-006**: System MUST provide keyboard-only navigation for all features
- **FR-007**: System MUST display a help overlay showing keyboard shortcuts in current context
- **FR-008**: System MUST provide visual feedback for all keyboard actions within 100ms
- **FR-009**: System MUST adapt layout when terminal window is resized within 100ms without losing data view position by: (a) maintaining current row/column cursor position, (b) recalculating column widths proportionally, (c) reflowing panels using Textual's reactive layout system
- **FR-010**: System MUST support both light and dark terminal themes
- **FR-058**: System MUST apply all operations (filter, aggregate, pivot, etc.) only to the active dataset
- **FR-059**: System MUST maintain independent operation state for each loaded dataset
- **FR-060**: System MUST preserve operation state when switching between datasets
- **FR-071**: System MUST display a left sidebar for operation configuration (filter, search, aggregate, pivot, join forms) that overlays the data table (data remains full-width behind semi-transparent sidebar) with width of 30% of terminal width
- **FR-072**: System MUST display a right sidebar showing applied operations history that pushes/compresses the data table width, with width of 25% of terminal width
- **FR-073**: System MUST allow toggling left sidebar visibility via keyboard shortcut while maintaining data table visibility
- **FR-074**: System MUST allow toggling right sidebar visibility via keyboard shortcut
- **FR-075**: System MUST auto-show right sidebar when first operation is applied to a dataset and hide it when operations list becomes empty (cleared or all removed)
- **FR-076**: System MUST allow users to remove individual operations from the operations history list in right sidebar
- **FR-077**: System MUST allow users to edit operation parameters by selecting an operation from right sidebar, which reopens the left sidebar form with pre-filled values
- **FR-078**: System MUST allow users to reorder operations in the operations history using keyboard shortcuts (e.g., Ctrl+Up/Down to move selected operation)
- **FR-079**: System MUST re-apply operations in the new sequence when operation order changes, updating the dataset view accordingly
- **FR-080**: System MUST default to lazy execution mode where operations queue without executing until user triggers execution
- **FR-081**: System MUST provide a toggle to switch between lazy execution mode and eager execution mode
- **FR-082**: System MUST display current execution mode (lazy or eager) in right sidebar header with clickable toggle button and support Ctrl+M keyboard shortcut to switch modes
- **FR-083**: System MUST allow executing queued operations one-by-one in sequence via Ctrl+E keyboard shortcut
- **FR-084**: System MUST allow executing all queued operations at once via Ctrl+Shift+E keyboard shortcut
- **FR-085**: System MUST visually differentiate queued and executed operations in right sidebar using icon prefix (⏸ for queued, ✓ for executed) combined with color coding (yellow/amber for queued, green for executed)
- **FR-086**: System MUST prompt user with modal when switching from lazy to eager mode with queued operations, offering options to: (1) execute all and switch, (2) clear all and switch, or (3) cancel, with keyboard shortcuts for quick selection

**Data Viewing:**
- **FR-011**: System MUST display data in a paginated table with column headers
- **FR-012**: System MUST show row numbers and total row count
- **FR-013**: System MUST allow users to scroll horizontally and vertically through data with Left/Right arrow keys for column navigation, Up/Down arrow keys for row navigation, and active cell highlighted with clear visual indicator
- **FR-014**: System MUST display loading indicators for operations exceeding 500ms
- **FR-015**: System MUST allow users to cancel long-running operations via Esc key, discarding partial results and restoring dataset to pre-operation state
- **FR-066**: System MUST cap column width at 40 characters maximum
- **FR-067**: System MUST truncate column content exceeding 40 characters with ellipsis (...)
- **FR-068**: System MUST provide Enter key shortcut to view full content of truncated cells in a modal or overlay
- **FR-069**: System MUST support Ctrl+Left/Right to jump 5 columns at a time for fast horizontal navigation
- **FR-070**: System MUST automatically scroll viewport horizontally when cursor navigates beyond visible columns

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
- **FR-032**: System MUST warn when join keys have mismatched types or missing values. System attempts narwhals-supported automatic type conversion (int↔float, string→category); if conversion fails, display modal with options: (a) Cancel join, (b) View type mismatch details, (c) Manually select columns with correct types

**Workflow Management:**
- **FR-033**: System MUST allow users to save sequences of operations as reusable workflows
- **FR-034**: System MUST persist workflows to disk in a human-readable format
- **FR-035**: System MUST allow users to apply saved workflows to new datasets
- **FR-036**: System MUST provide undo/redo for individual operations

**Export:**
- **FR-037**: System MUST export current dataset view (filtered/aggregated data) to CSV format
- **FR-038**: System MUST export current dataset view to Parquet format for efficient storage
- **FR-039**: System MUST allow exporting pivot tables as separate files
- **Note**: FR-037 to FR-039 export *data files*. For exporting *executable code* (marimo/Python/Jupyter notebooks), see FR-046 to FR-048.

**Saved Analysis Management:**
- **FR-040**: System MUST allow users to save current analysis with name and description
- **FR-041**: System MUST store saved analyses in DuckDB database with metadata (name, description, created_at, modified_at, operation_count)
- **FR-042**: System MUST list all saved analyses with their metadata
- **FR-043**: System MUST allow users to update name and description of saved analyses
- **FR-044**: System MUST allow users to delete saved analyses
- **FR-045**: System MUST prevent export of analyses that haven't been saved
- **FR-046**: System MUST export saved analyses to marimo notebook format (.py with marimo cells) containing data loading and operation code
- **FR-047**: System MUST export saved analyses to Python script format (.py with narwhals operations) containing data loading and operation code
- **FR-048**: System MUST export saved analyses to Jupyter notebook format (.ipynb) containing data loading and operation code
- **FR-049**: System MUST include data loading code and all operations in exported notebooks/scripts
- **FR-050**: System MUST prompt for file overwrite confirmation when export path already exists
- **Note**: FR-046 to FR-048 export *executable code notebooks/scripts*. For exporting *data files*, see FR-037 to FR-039.
- **FR-061**: System MUST allow users to load a saved analysis, which reloads the original dataset and reapplies all operations
- **FR-062**: System MUST verify dataset path accessibility before loading saved analysis and warn if unavailable

### Key Entities

- **Dataset**: Represents loaded data with schema information (column names, types, row count), source location (file path or URL), backend engine (pandas/polars/etc. via narwhals), active status (whether currently displayed in main view), execution_mode (str: "lazy" or "eager" - controls whether operations execute immediately or queue), queued_operations (list of Operation objects pending execution in lazy mode), and executed_operations (list of Operation objects already applied to the dataset, previously called operation_history)

- **DatasetSession**: Represents the collection of all loaded datasets in the current session with list of Dataset objects (max 10), active dataset reference, and split pane configuration state

- **Operation**: Represents a single data transformation operation stored as:
  - `code` (str): Narwhals expression code string (e.g., `"df.filter(nw.col('age') > 25)"`)
  - `display` (str): Human-readable description (e.g., `"Filter: age > 25"`)
  - `operation_type` (str): Operation category (filter, aggregate, pivot, join, select, drop, rename, with_columns, sort, unique, fill_null, drop_nulls, head, tail, sample)
  - `params` (dict): Operation parameters for sidebar form editing (e.g., `{"column": "age", "operator": ">", "value": 25}`)
  - Generated by left sidebar forms (keyboard-driven configuration panels), never written by users directly
  - Validated immediately on creation and at runtime when applied
  - Displayed in right sidebar operations history list after application

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
- **SC-002**: Users can navigate between rows and columns using arrow keys with under 100ms response time
- **SC-016**: Users can jump 5 columns using Ctrl+Left/Right with under 100ms response time
- **SC-003**: Users can complete a filter → group → aggregate workflow in under 2 minutes on their first use (with help overlay)
- **SC-004**: System remains responsive with datasets containing 10M+ rows using lazy evaluation
- **SC-005**: Help overlay (FR-007) displays core keyboard shortcuts in context-aware sections. First-time users complete load and navigate workflow (User Story 1 acceptance scenario 4: load CSV file + arrow key navigation between rows/columns) within 5 minutes using only help overlay for guidance
- **SC-006**: Users can create and save a complex workflow (5+ operations) and reapply it to a new dataset in under 1 minute
- **SC-007**: System displays progress feedback for all operations taking longer than 500ms
- **SC-008**: Terminal layout adapts to window resize within 100ms without losing data view position
- **SC-009**: First-time users complete data joining tasks (User Story 5 acceptance scenarios 1-2: activate merge mode, select join columns/type, preview shows expected row count, confirm produces correct dataset) within 10 minutes using help overlay for guidance
- **SC-010**: System handles common errors (file not found, network timeout, type mismatches) with clear, actionable error messages that include: (a) What failed, (b) Why it failed, (c) Next action (e.g., "File not found: data.csv. Check path or use Ctrl+O to browse")
- **SC-011**: Users can save, update, and export an analysis to marimo/Python/Jupyter in under 30 seconds
- **SC-012**: Exported notebooks/scripts execute successfully without modification 95% of the time
- **SC-013**: DuckDB operations (save, list, update, delete analyses) complete within 200ms for databases with up to 1000 saved analyses
- **SC-014**: Users can switch between 10 loaded datasets with under 150ms response time
- **SC-015**: Visual dataset indicators (tabs/list) remain readable and navigable with up to 10 datasets loaded
- **SC-017**: Left sidebar opens/closes within 100ms; right sidebar auto-shows within 100ms when first operation applied
- **SC-018**: Operation reordering in right sidebar re-applies operations and updates data table within 500ms for datasets with up to 1M rows
- **SC-019**: Users can queue 10+ operations in lazy mode, execute them one-by-one (Ctrl+E) or all at once (Ctrl+Shift+E), and switch between lazy/eager modes within 3 total interactions

## Clarifications

### Session 2026-01-10 (Reload Current Dataset)

**Context**: User requested ability to reload currently active dataset from its original source file.

**Questions and Answers**:

1. **Q**: When user reloads current dataset, should operations be cleared or preserved?
   - **A**: Hot reload behavior - re-read source file while preserving current operations queue, then re-apply them to refreshed data

**Integration**:
- Added FR-064: System MUST allow users to reload currently active dataset from its original source file while preserving the current operations queue, then re-apply those operations to the refreshed data
- Added edge cases for reload functionality: source file deleted/moved, schema incompatibility, concurrent execution
- Added acceptance scenarios 19-22 for User Story 1 covering reload workflow

### Session 2026-01-09 (Lazy/Eager Execution Mode)

**Context**: User requested adding execution mode toggle where operations can queue up without executing (lazy mode) vs executing immediately (eager mode), with keyboard shortcuts to execute operations one-by-one or all at once.

**Questions and Answers**:

1. **Q**: What should be the default execution behavior when users first launch kittiwake?
   - **A**: Default to lazy mode (operations queue up until user executes them)

2. **Q**: Where and how should the lazy/eager mode toggle be displayed and controlled?
   - **A**: Right sidebar header (operations history) with visual toggle button + Ctrl+M keyboard shortcut

3. **Q**: Which keyboard shortcuts should trigger operation execution?
   - **A**: Ctrl+E (execute next queued operation), Ctrl+Shift+E (execute all queued operations)

4. **Q**: How should queued vs executed operations be visually differentiated in the right sidebar?
   - **A**: Icons/symbols prefix combined with colors - Queued: `⏸ Operation` (yellow/amber), Executed: `✓ Operation` (green)

5. **Q**: What should happen when the user switches from lazy to eager mode while there are queued operations?
   - **A**: Prompt user with modal offering three choices: (1) Execute all and switch to eager mode, (2) Clear queued operations and switch to eager mode, (3) Cancel (stay in lazy mode)

### Session 2026-01-09 (Sidebar UI Architecture)

**Context**: User requested replacing modal-based UI with sidebar-based UI for operations. Left sidebar for configuring operations (search, filter, etc.) and right sidebar showing applied operations history.

**Questions and Answers**:

1. **Q**: How should sidebars affect the data table viewport width?
   - **A**: Left sidebar (filter/search configuration) overlays data; right sidebar (applied operations) pushes/compresses data table

2. **Q**: What should be the default visibility state of the right sidebar (operations history)?
   - **A**: Auto-show when first operation applied, hidden when empty

3. **Q**: What interactions should be available in the right sidebar (operations history)?
   - **A**: View, remove, edit, and reorder operations (drag-and-drop or keyboard shortcuts to change sequence)

4. **Q**: How wide should the left sidebar (operation configuration) be?
   - **A**: 30% of terminal width

5. **Q**: How wide should the right sidebar (operations history) be?
   - **A**: 25% of terminal width

### Session 2026-01-09 (Column Navigation)

**Context**: User requested improved column navigation and capped column widths for better keyboard-driven data exploration.

**Questions and Answers**:

1. **Q**: What should be the maximum character width for table columns?
   - **A**: Fixed reasonable limit (e.g., 30-40 chars) with ellipsis truncation and tooltip/modal to view full content

2. **Q**: How should arrow key navigation work for moving between columns vs rows?
   - **A**: Left/Right arrows move between columns; Up/Down move between rows (standard spreadsheet behavior)

3. **Q**: When a dataset has more columns than fit on screen (with 40-char cap), how should horizontal scrolling work?
   - **A**: Horizontal scroll auto-triggers when navigating beyond viewport (cursor movement causes automatic column scrolling)

4. **Q**: What keyboard shortcut should trigger the full content view for truncated cells?
   - **A**: Enter key

5. **Q**: What keyboard shortcuts should enable fast column navigation (jumping multiple columns)?
   - **A**: Ctrl+Left/Right to jump 5 columns at a time (fixed increment)

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
   - **A**: Sidebar-based approach with forms (left sidebar with column dropdown, operator dropdown, value input for filter configuration; right sidebar displays applied operations history) - keyboard-driven.

3. **Q**: Which narwhals operations need TUI sidebar form support initially?
   - **A**: 13 operations with dedicated sidebar forms:
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
- All 13 operation types will have dedicated keyboard-driven sidebar forms in TUI (left sidebar for configuration, right sidebar for history)
- Validation occurs both at sidebar form submit time and runtime application
