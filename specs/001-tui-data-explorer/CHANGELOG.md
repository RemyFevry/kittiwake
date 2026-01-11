# Changelog: TUI Data Explorer

## 2026-01-10 - Added New User Story 1 Tasks (T036-T038)

### Context
User requested three new features for enhanced data viewing experience in Phase 3 (User Story 1: Load and View Data).

### New Tasks Added

#### T036: Cell Clipboard Copy
**Task**: `T036 [P] [US1] Implement clipboard copy on cell selection`
**File**: `src/kittiwake/widgets/dataset_table.py`
**Description**: 
- Copy cell value to system clipboard when user selects/clicks on a cell
- Show brief toast notification "Copied to clipboard"
- Use `pyperclip` library for cross-platform clipboard access
- Handle edge cases: null values (copy empty string), very long values (copy full content)

**Priority**: P1 (MVP) - Parallelizable
**User Story**: US1 (Load and View Data)

#### T037: Type-Based Column Coloring
**Task**: `T037 [P] [US1] Implement type-based column coloring`
**Files**: 
- `src/kittiwake/utils/type_colors.py` (color mapping)
- `src/kittiwake/widgets/dataset_table.py` (apply colors)

**Description**:
- Create color mapping for data types: list → cyan/blue, dict → magenta/purple
- Extend existing type color system to differentiate list and dict types
- Apply colors to column headers in DatasetTable widget
- Ensure colors work in both light and dark terminal themes

**Priority**: P1 (MVP) - Parallelizable
**User Story**: US1 (Load and View Data)

#### T038: Column Filtering UI
**Task**: `T038 [US1] Implement column filtering UI`
**File**: `src/kittiwake/widgets/dataset_table.py`
**Description**:
- Add keybinding (e.g., Ctrl+Shift+F) to open column filter overlay/modal
- Filter by column name (text search with regex support)
- Filter by column type (checkboxes: String, Int, Float, List, Dict, Boolean, Date, etc.)
- Show/hide columns based on filter criteria
- Display count of visible vs total columns (e.g., "Showing 5 of 20 columns")
- Add "Reset" button to show all columns again

**Priority**: P1 (MVP) - NOT Parallelizable (depends on T037 for type detection)
**User Story**: US1 (Load and View Data)

### Impact on Task List

**Total Tasks**: Increased from 102 → 105 tasks
**Progress**: 60 of 105 tasks complete (57%)
**MVP Size**: Increased from ~45 → ~48 tasks

**Task Renumbering**:
- Old T036-T102 → New T039-T105 (all Phase 4+ tasks shifted by +3)
- Phase 1-3 tasks T001-T035 unchanged
- New tasks T036-T038 inserted at end of Phase 3

### Integration Points

1. **T036 (Clipboard Copy)**:
   - Integrates with existing cell selection in DatasetTable
   - Uses Textual's toast notification system (already in use)
   - New dependency: `pyperclip` library

2. **T037 (Column Colors)**:
   - Extends existing `type_colors.py` utility
   - Integrates with column header rendering in DatasetTable
   - Builds on existing type detection from `services/type_detector.py`

3. **T038 (Column Filtering)**:
   - New modal/overlay widget (similar to existing FilterModal pattern)
   - Integrates with DatasetTable column visibility
   - Uses type information from T037

### Dependencies

```
T037 (Type Colors) ─┐
                    ├──> T038 (Column Filtering)
T025 (DatasetTable) ┘

T025 (DatasetTable) ──> T036 (Clipboard Copy)
```

### Testing Considerations

**T036 - Clipboard Copy**:
- Test: Select cell, verify clipboard contains cell value
- Test: Select null cell, verify clipboard contains empty string
- Test: Select cell with very long value, verify full content copied
- Test: Verify toast appears with "Copied to clipboard" message

**T037 - Type Colors**:
- Test: Load dataset with list columns, verify cyan/blue headers
- Test: Load dataset with dict columns, verify magenta/purple headers
- Test: Verify colors work in light theme
- Test: Verify colors work in dark theme

**T038 - Column Filtering**:
- Test: Open filter with Ctrl+Shift+F, verify overlay appears
- Test: Filter by name "age", verify only matching columns visible
- Test: Filter by type "Int", verify only integer columns visible
- Test: Verify counter shows "Showing N of M columns"
- Test: Click Reset, verify all columns reappear

### Related Documentation

- **spec.md**: User Story 1 acceptance scenarios cover data viewing fundamentals
- **plan.md**: Keyboard-first interaction principle (FR-006) supports these enhancements
- **data-model.md**: Dataset.schema provides type information for T037/T038

### Notes

- T036 and T037 are marked `[P]` for parallel implementation
- T038 depends on T037 for type detection, so cannot be parallelized
- All three tasks enhance User Story 1 without breaking existing functionality
- These are "nice-to-have" enhancements for MVP, could be deferred to post-MVP if timeline is tight

---

## Previous Changes

See git history for detailed changelog of tasks T001-T035 and their completion status.
