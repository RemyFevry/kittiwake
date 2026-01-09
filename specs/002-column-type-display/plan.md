# Implementation Plan: Column Type Display and Quick Filter

**Branch**: `002-column-type-display` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-column-type-display/spec.md`

**Note**: This plan builds on the existing TUI Data Explorer (001) by adding visual type indicators and direct column header filtering.

## Summary

Enhance the existing DatasetTable widget to:
- Display each column header with distinct colors and icons based on data type (numeric, text, date, boolean, unknown)
- Enable quick filtering by clicking on column headers, opening a contextual filter interface
- Maintain accessibility through dual visual indicators (color + icon) for users with color blindness
- Integrate seamlessly with existing lazy/eager execution modes and operation management

**Technical Approach**:
- Extend existing `DatasetTable` widget to add clickable column headers with type styling
- Create a new `ColumnHeaderQuickFilter` widget (similar to existing FilterModal pattern)
- Add data type detection utility that maps narwhals schema types to visual categories
- Define type color scheme in CSS/TCSS following Textual's theming system
- Reuse existing `Operation` model and execution pipeline for consistency

## Technical Context

**Language/Version**: Python >=3.13 (as specified in constitution and pyproject.toml)  

**Primary Dependencies**: 
- textual >=7.0.1 (TUI framework - already in use)
- narwhals >=2.15.0 (dataframe API with schema introspection - already in use)
- Existing project dependencies (no new external deps required)

**Storage**: 
- No additional storage needed (reuses existing Operation persistence)
- Type mappings stored as configuration constants in source code

**Testing**: pytest with Textual's testing utilities (pilot) - already configured

**Target Platform**: Cross-platform terminal (Linux, macOS, Windows)

**Project Type**: Single project (CLI/TUI application) - enhancement to existing feature  

**Performance Goals**: 
- Column header rendering with type colors <50ms (included in existing <100ms UI response goal)
- Type detection on dataset load <100ms for schemas up to 100 columns
- Quick filter interface opens in <50ms after column header click
- No impact on existing data table pagination performance

**Constraints**: 
- Must maintain keyboard-only navigation (mouse clicks on headers are enhancement, not requirement)
- Type colors must meet WCAG 2.1 AA contrast ratio (4.5:1) against terminal background
- Icons must be ASCII-compatible for maximum terminal compatibility
- Must work with all existing narwhals-supported backends (pandas, polars, pyarrow)
- Maximum 5 distinct data type categories to avoid color confusion

**Scale/Scope**: 
- 3 prioritized user stories (P1: colors, P2: quick filter, P3: icons)
- 5 data type categories to support
- Reuse existing filter operation model (20+ operators already implemented)
- Integration with existing 97 tests (new tests additive, not disruptive)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Keyboard-First Interaction

- **Status**: PASS
- **Evidence**:
  - Column header clicking is OPTIONAL enhancement (keyboard shortcuts already exist)
  - Existing Ctrl+F filter workflow remains primary path (FR-016)
  - Quick filter interface MUST support Escape to cancel (FR-014)
  - All functionality accessible via existing keyboard shortcuts
  - Type colors/icons are visual aids, not functional requirements for keyboard users
- **Design Decision**: Quick filter accessible via keyboard by focusing on header cell and pressing Enter (alternative to clicking)

### ✅ II. Data Source Agnostic

- **Status**: PASS
- **Evidence**:
  - FR-002: Type detection works with "at least" 5 categories, extensible to narwhals schema types
  - Uses narwhals schema introspection API (backend-agnostic)
  - No backend-specific type handling logic
  - Unknown/mixed types map to generic "unknown" category (FR-002)
  - Operators for each type already implemented in existing filter modals

### ✅ III. TUI-Native Design

- **Status**: PASS
- **Evidence**:
  - Extends existing `DatasetTable` widget (Textual component)
  - Quick filter uses Textual's overlay/modal pattern (like existing FilterModal)
  - Type colors defined in TCSS (Textual CSS) following existing theme system
  - Icons rendered as text in column headers (Textual Label/Static widgets)
  - No custom terminal escape sequences needed

### ✅ IV. Performance & Responsivity

- **Status**: PASS
- **Evidence**:
  - Type detection runs once on dataset load (cached in schema)
  - Column header rendering async (doesn't block UI)
  - Quick filter interface loads <50ms (faster than existing modal forms)
  - No impact on existing pagination/lazy loading (type info in header only)
  - Filter operations reuse existing execution pipeline (already optimized)

### ✅ V. Composable Operations

- **Status**: PASS
- **Evidence**:
  - Column header filters create standard `Operation` objects (FR-012)
  - Integrate with lazy/eager execution modes (FR-013)
  - Appear in operations sidebar with state indicators (FR-018)
  - Fully undoable/redoable (FR-019)
  - Chainable with existing operations (no special cases)

## Project Structure

### Documentation (this feature)

```text
specs/002-column-type-display/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── type-mappings.json  # Data type to color/icon mappings
├── checklists/          # Quality validation (completed)
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/kittiwake/
├── models/
│   ├── dataset.py       # MODIFY: Add type detection cache
│   └── operations.py    # NO CHANGE: Reuse existing Operation model
├── widgets/
│   ├── dataset_table.py # MODIFY: Add type styling to headers, click handlers
│   ├── modals/
│   │   ├── filter_modal.py  # REFERENCE: Pattern for quick filter
│   │   └── column_header_quick_filter.py  # NEW: Quick filter widget
│   └── help_overlay.py  # MODIFY: Add type legend section
├── services/
│   └── type_detector.py # NEW: Narwhals schema → visual type mapping
├── utils/
│   └── type_colors.py   # NEW: Type color/icon configuration
└── app.py               # MODIFY: Register new CSS for type colors

tests/
├── unit/
│   ├── test_type_detector.py  # NEW: Type detection logic
│   ├── test_dataset_table.py  # NEW: Header rendering with types
│   └── test_column_header_quick_filter.py  # NEW: Quick filter widget
└── integration/
    └── test_column_type_workflow.py  # NEW: End-to-end type display + filtering
```

**Structure Decision**: Single project structure maintained. This is an enhancement to existing `src/kittiwake/widgets/dataset_table.py` with supporting utilities. No new top-level modules or architectural changes needed.

## Complexity Tracking

> No Constitution violations. No justifications needed.

This feature strictly enhances existing functionality without introducing new paradigms, dependencies, or architectural patterns. All integration points reuse established patterns from the 001-tui-data-explorer feature.

## Phase 0: Research & Design Decisions

### Research Topics

1. **Narwhals Schema Introspection API** (`NEEDS CLARIFICATION → research.md`)
   - How to extract data types from narwhals LazyFrame/DataFrame schema
   - Mapping narwhals dtypes to visual categories (numeric, text, date, boolean, unknown)
   - Handling edge cases: mixed types, nested types, null columns
   
2. **Textual Color Theming Best Practices** (`NEEDS CLARIFICATION → research.md`)
   - WCAG 2.1 AA compliant color schemes for terminal UIs
   - Textual CSS variables for theme consistency
   - Color schemes that work in both dark and light terminal themes
   
3. **Accessible ASCII Icon Set** (`NEEDS CLARIFICATION → research.md`)
   - ASCII characters for type icons that render in all terminals
   - Unicode fallback strategy for enhanced terminals
   - Icon positioning within Textual DataTable headers
   
4. **Textual DataTable Header Customization** (`NEEDS CLARIFICATION → research.md`)
   - How to style individual column headers in Textual DataTable
   - Click event handling for table headers
   - Rendering custom content (icons + colors) in headers

5. **Quick Filter UI Pattern** (reference existing code)
   - Reuse FilterModal/SearchModal overlay pattern
   - Contextual positioning near clicked header
   - Pre-population with selected column

### Outputs

All research findings consolidated in `research.md` with decisions documented.

## Phase 1: Data Model & Contracts

### Data Model (`data-model.md`)

#### Type Mapping Configuration

```text
Entity: ColumnTypeMapping
- type_category: str (one of: "numeric", "text", "date", "boolean", "unknown")
- narwhals_dtypes: list[str] (e.g., ["Int64", "Float64"] for numeric)
- color_name: str (Textual CSS variable, e.g., "$type-numeric")
- icon_char: str (ASCII character, e.g., "#")
- icon_unicode: str (Unicode fallback, e.g., "🔢")
- filter_operators: list[str] (e.g., [">", "<", ">=", "<=", "=", "!="])

Relationships:
- One mapping per type_category
- Each Dataset.schema column maps to one ColumnTypeMapping
```

#### Enhanced Column Header

```text
Entity: ColumnHeader (logical extension of existing DataTable column)
- name: str (column name from Dataset.schema)
- data_type: str (from ColumnTypeMapping.type_category)
- color_style: str (CSS class name)
- icon: str (display character)
- clickable: bool (true if quick filter enabled)

Relationships:
- Belongs to one Dataset
- References one ColumnTypeMapping
- Triggers one ColumnHeaderQuickFilter on click
```

#### Column Header Quick Filter Widget

```text
Entity: ColumnHeaderQuickFilter (Textual ModalScreen)
- selected_column: str (pre-populated from clicked header)
- data_type: str (from ColumnTypeMapping)
- available_operators: list[str] (filtered by data_type)
- value_input: str (user-entered filter value)
- callback: callable (receives Operation object on submit)

Relationships:
- Created by DatasetTable on header click
- Returns Operation object to MainScreen
- Reuses existing Operation.apply() execution pipeline
```

### Contracts (`contracts/`)

#### Type Mappings Contract (`type-mappings.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Column Type Mappings",
  "description": "Mapping from narwhals data types to visual indicators",
  "type": "object",
  "properties": {
    "type_categories": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["category", "narwhals_dtypes", "color", "icon_ascii", "operators"],
        "properties": {
          "category": {
            "type": "string",
            "enum": ["numeric", "text", "date", "boolean", "unknown"]
          },
          "narwhals_dtypes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Narwhals dtype names that map to this category"
          },
          "color": {
            "type": "string",
            "pattern": "^\\$[a-z-]+$",
            "description": "Textual CSS variable name"
          },
          "icon_ascii": {
            "type": "string",
            "maxLength": 1,
            "description": "ASCII character for icon"
          },
          "icon_unicode": {
            "type": "string",
            "maxLength": 2,
            "description": "Unicode character fallback"
          },
          "operators": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Available filter operators for this type"
          }
        }
      },
      "minItems": 5,
      "maxItems": 5
    }
  }
}
```

#### Quick Filter Interface Contract

Reuses existing `Operation` contract from 001-tui-data-explorer. No new contract needed.

The quick filter widget produces standard `Operation` objects identical to those created by FilterModal:

```python
Operation(
    code="df = df.filter(nw.col('column_name') > 100)",
    display="Filter: column_name > 100",
    operation_type="filter",
    params={"column": "column_name", "operator": ">", "value": "100"},
    state="queued"  # or "executed" depending on execution mode
)
```

### Quickstart Guide (`quickstart.md`)

**Prerequisites**: User has completed 001-tui-data-explorer quickstart and is familiar with loading datasets and basic filtering.

**Time to Complete**: 5 minutes

**Learning Objectives**:
1. Identify column data types by color and icon
2. Create filters by clicking column headers
3. Understand type-specific filter operators

**Steps**:
1. Load Titanic dataset (existing test data)
2. Observe column header colors (Age=numeric blue, Name=text green, etc.)
3. Click on "Age" header → quick filter opens with numeric operators
4. Select ">" operator, enter "30" → filter created
5. Observe operation in sidebar with ⏳ indicator
6. Press Ctrl+E to execute → see filtered results
7. Test with different column types (text, boolean)

## Phase 2: Task Breakdown

**IMPORTANT**: Phase 2 (task breakdown) is NOT performed by `/speckit.plan`. It is delegated to the `/speckit.tasks` command which:
- Reads this plan.md and spec.md
- Generates detailed tasks.md with T-### identifiers
- Includes acceptance criteria, dependencies, and time estimates

See `tasks-template.md` for task structure. Do NOT create tasks.md in this command.

## Research Phase Output (Phase 0)

The following topics require research before implementation planning:

### R1: Narwhals Schema Introspection

**Question**: How do we map narwhals data types to our 5 visual categories?

**Research Needed**:
- Review narwhals schema API documentation
- Identify all possible dtype values returned by `frame.schema`
- Create mapping rules for edge cases (nested types, unknown types, mixed types)
- Test with pandas, polars, and pyarrow backends for consistency

**Expected Output**: 
- Complete dtype mapping in `research.md`
- Python function signature: `detect_column_type(dtype: narwhals.Dtype) -> Literal["numeric", "text", "date", "boolean", "unknown"]`

### R2: WCAG-Compliant Terminal Colors

**Question**: What colors meet accessibility standards in both dark and light terminal themes?

**Research Needed**:
- Review WCAG 2.1 Level AA contrast requirements (4.5:1)
- Test color combinations in common terminal emulators (iTerm2, Windows Terminal, Gnome Terminal)
- Verify with both dark and light themes
- Consider colorblind-friendly palettes (Deuteranopia, Protanopia, Tritanopia)

**Expected Output**:
- 5 color specifications in `research.md` with hex values and CSS variable names
- Contrast ratio calculations documented
- Screenshot examples in both dark/light themes

### R3: ASCII Icon Selection

**Question**: Which ASCII characters best represent each data type?

**Research Needed**:
- Survey existing data tools (pandas, DuckDB CLI, etc.) for icon conventions
- Test character rendering in multiple terminal fonts
- Consider mnemonic value (easy to remember/recognize)
- Unicode fallback options for enhanced terminals

**Expected Output**:
- 5 icon specifications in `research.md`
- ASCII primary + Unicode fallback for each type
- Rendering test results across terminals

### R4: Textual DataTable Header Customization

**Question**: How do we add custom styling and click handlers to DataTable column headers?

**Research Needed**:
- Review Textual DataTable source code and documentation
- Identify header customization APIs (CSS classes, Rich renderables, etc.)
- Test click event handling on headers
- Explore alternative approaches if DataTable doesn't support (custom header row)

**Expected Output**:
- Implementation approach documented in `research.md`
- Code examples showing header styling and click handling
- Performance implications noted

### R5: Contextual Quick Filter Positioning

**Question**: How should the quick filter UI be positioned relative to the clicked column header?

**Research Needed**:
- Review Textual overlay/modal positioning options
- Consider terminal size constraints (minimum 80 columns)
- Test with headers at different horizontal positions
- Evaluate dropdown vs modal vs sidebar approaches

**Expected Output**:
- UI pattern decision in `research.md`
- Mockup or ASCII art showing layout
- Fallback behavior for narrow terminals documented

## Agent Context Update (Phase 1)

After completing Phase 1 (data model and contracts), run:

```bash
.specify/scripts/bash/update-agent-context.sh opencode
```

This will update `AGENTS.md` with:
- New source files: `type_detector.py`, `type_colors.py`, `column_header_quick_filter.py`
- Modified files: `dataset_table.py`, `help_overlay.py`
- Technology additions: (none - reuses existing stack)
- Testing commands: New test file patterns

## Dependencies & Integration Points

### Existing Features (001-tui-data-explorer)

**Direct Dependencies**:
- `Dataset.schema` - source of column type information
- `DatasetTable` widget - target for type styling enhancement
- `Operation` model - reused for quick filter operations
- `MainScreen` - receives Operation objects from quick filter
- `OperationsSidebar` - displays quick filter operations with state indicators
- Lazy/Eager execution modes - quick filters respect current mode

**Integration Requirements**:
- Quick filter operations MUST be indistinguishable from Ctrl+F operations
- Type colors MUST NOT interfere with existing DataTable selection/focus colors
- Column header clicks MUST NOT conflict with existing keyboard navigation
- Type legend MUST integrate with existing help overlay (?)

### No External Dependencies

This feature requires NO new external Python packages. All functionality builds on:
- Existing Textual widgets and patterns
- Existing narwhals schema API
- Existing operation execution pipeline

## Risk Assessment

### Low Risk
- **Type Detection**: Narwhals provides stable schema API
- **Color Theming**: Textual CSS system is well-documented
- **Operation Integration**: Reuses proven Operation model

### Medium Risk
- **DataTable Header Customization**: May require workarounds if Textual API is limited
  - *Mitigation*: Phase 0 research will identify implementation approach early
  - *Fallback*: Custom header row if DataTable headers not customizable
  
- **Color Accessibility**: Terminal color rendering varies by emulator
  - *Mitigation*: Test on multiple terminals during research phase
  - *Fallback*: Icons provide non-color identification

### Zero Risk
- **Backward Compatibility**: All existing workflows remain unchanged
- **Performance**: Minimal overhead (type detection cached, styling is CSS)

## Success Validation

After implementation, verify against spec success criteria:

- **SC-001**: Time users to identify column types (target: <2 seconds)
- **SC-002**: Time users to create filter via header click (target: <5 seconds)
- **SC-003**: Verify all 5 types distinguishable by color AND icon
- **SC-004**: Count steps for quick filter (target: 2-3 steps vs 5 for Ctrl+F)
- **SC-005**: Measure color contrast ratios (target: >=4.5:1)
- **SC-006**: Test icon-only identification with colorblind simulation
- **SC-007**: User testing: 90% success rate on first attempt

Run full test suite (97 existing + new tests) to ensure no regressions.

## Next Steps

1. **Run `/speckit.plan` research phase**: Generate `research.md` with all NEEDS CLARIFICATION resolved
2. **Review research findings**: Validate technical approach before proceeding
3. **Generate data model and contracts**: Complete Phase 1 outputs
4. **Update agent context**: Run `update-agent-context.sh` script
5. **Run `/speckit.tasks`**: Generate detailed task breakdown in `tasks.md`
6. **Begin implementation**: Start with P1 (type colors) as foundation for P2/P3
