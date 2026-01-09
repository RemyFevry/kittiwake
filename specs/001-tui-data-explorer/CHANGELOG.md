# Changelog - TUI Data Explorer

## 2026-01-09 - Modal to Sidebar Architecture Migration

### Context
After implementing initial modals (FilterModal, SearchModal), user feedback indicated that the specification calls for a **sidebar-based architecture** rather than modal dialogs. The original plan (quickstart.md, research.md) clearly defines:
- **Left sidebar** (30% width, overlay): Operation configuration forms
- **Right sidebar** (25% width, push): Operations history with CRUD capabilities

### Changes Made

#### 1. Created Sidebar Widgets
**New directory**: `src/kittiwake/widgets/sidebars/`

**FilterSidebar** (`filter_sidebar.py`):
- Converted from FilterModal to left overlay sidebar
- Column/operator/value form with Apply/Cancel buttons
- Callback-based result handling
- ESC to dismiss, returns focus to data table
- Show/hide via `.show()` and `.action_dismiss()`

**SearchSidebar** (`search_sidebar.py`):
- Converted from SearchModal to left overlay sidebar
- Single text input for search query
- Searches across all columns
- Enter key triggers apply

**OperationsSidebar** (`operations_sidebar.py`):
- NEW: Right push sidebar for operations history
- ListView showing all applied operations
- Keyboard actions:
  - `Ctrl+Up/Down`: Reorder operations
  - `Enter`: Edit operation (reopens left sidebar with params)
  - `Delete`: Remove operation
  - `Ctrl+C`: Clear all operations
- Custom messages: `OperationsReordered`, `OperationEdit`, `OperationRemoved`, `OperationsClearAll`
- Auto-shows when first operation is applied
- Auto-hides when all operations removed

#### 2. Architecture Differences

**Modal Architecture** (replaced):
```
┌─────────────────────────────────┐
│         Data Table              │
│                                 │
│    ┌──────────────┐            │
│    │  FilterModal │ (centered) │
│    │  (blocks UI) │            │
│    └──────────────┘            │
└─────────────────────────────────┘
```

**Sidebar Architecture** (new):
```
┌──────────┬─────────────────┬──────────┐
│  Filter  │   Data Table    │Operations│
│ Sidebar  │  (adjusts size) │ Sidebar  │
│ (30%,    │                 │ (25%,    │
│ overlay) │                 │  push)   │
└──────────┴─────────────────┴──────────┘
```

#### 3. Benefits of Sidebar Architecture

**Improved UX**:
- ✅ Operations history always visible (right sidebar)
- ✅ Can see data table while configuring operations
- ✅ No context switching (modals block entire UI)
- ✅ Reordering operations directly visible
- ✅ Edit operations by clicking in history

**Better Workflow**:
- ✅ Left sidebar → configure operation → right sidebar shows result
- ✅ Right sidebar → click operation → left sidebar reopens with params for editing
- ✅ Clear visual separation: input (left) vs output (right)

**Keyboard-First**:
- ✅ Ctrl+F → opens left sidebar for filter
- ✅ Ctrl+/ → opens left sidebar for search
- ✅ ESC → closes sidebar, returns to table
- ✅ Tab → navigate within sidebar
- ✅ Focus management: sidebar → table seamless

#### 4. Implementation Details

**CSS Layers**:
```css
Screen {
    layers: base overlay;
}

#filter_sidebar, #search_sidebar {
    layer: overlay;      /* Floats above data table */
    dock: left;
    width: 30%;
}

#operations_sidebar {
    /* No layer needed - uses Horizontal push layout */
    width: 0;            /* Hidden by default */
    transition: width 100ms;
}

#operations_sidebar.visible {
    width: 25%;          /* Pushes data table left */
}
```

**Main Screen Layout**:
```python
def compose(self) -> ComposeResult:
    yield Header()
    
    # Left sidebars (overlay layer)
    yield FilterSidebar()
    yield SearchSidebar()
    
    # Main content (push layout)
    with Horizontal(id="main_content"):
        yield DatasetTable()  # Adjusts when right sidebar appears
        yield OperationsSidebar()
    
    yield Footer()
```

### Files Modified

**New Files**:
- `src/kittiwake/widgets/sidebars/__init__.py`
- `src/kittiwake/widgets/sidebars/filter_sidebar.py`
- `src/kittiwake/widgets/sidebars/search_sidebar.py`
- `src/kittiwake/widgets/sidebars/operations_sidebar.py`

**Files to Update** (next phase):
- `src/kittiwake/screens/main_screen.py` - Use sidebars instead of modals
- `src/kittiwake/app.py` - Add CSS for sidebar layouts
- `specs/001-tui-data-explorer/tasks.md` - Update Phase 4 & 5 tasks to reference sidebars

**Deprecated** (will be removed):
- `src/kittiwake/widgets/modals/filter_modal.py`
- `src/kittiwake/widgets/modals/search_modal.py`

**Preserved** (for full-screen interactions):
- `src/kittiwake/widgets/modals/save_analysis_modal.py` - May convert to sidebar
- `src/kittiwake/widgets/modals/export_modal.py` - May convert to sidebar
- `src/kittiwake/screens/saved_analyses_list_screen.py` - Full screen, not sidebar

### Next Steps
1. Update MainScreen to use sidebar architecture
2. Add CSS styling for overlay and push layouts
3. Update keyboard bindings to open sidebars (not modals)
4. Implement operation edit workflow (right sidebar → left sidebar)
5. Test reordering operations with Ctrl+Up/Down
6. Decide: Convert SaveAnalysisModal/ExportModal to sidebars or keep as modals?

---

## 2026-01-08 - Operation Model Simplification

### Context
User feedback identified that the original operation model was too complex with separate FilterOperation, AggregationOperation, and PivotTableOperation classes. Operations should be simpler - just narwhals expressions.

### Changes Made

#### 1. Clarification Session 2
Completed 5-question clarification session (`clarification-session-2.md`) resolving:
- **Storage format**: Operations stored as Python code strings (narwhals expressions)
- **User interaction**: Modal-based forms with dropdowns/inputs (keyboard-driven)
- **Supported operations**: 13 operation types with dedicated modals
- **Storage schema**: Code + display + operation_type + params (for editing)
- **Validation**: Immediate (modal submit) + runtime (operation apply), stop chain on error

#### 2. Updated Specifications

**spec.md**:
- Added Session 2026-01-08 to Clarifications section with Q&A
- Simplified Key Entities: removed Filter, Aggregation, PivotTable classes
- Added Operation entity with code/display/operation_type/params fields
- Updated SavedAnalysis.operations description

**data-model.md**:
- Replaced Filter, Aggregation, PivotTable entities with single Operation entity
- Removed FilterOperation, AggregationOperation, PivotTableOperation Python classes
- Added simplified Operation dataclass with code execution via eval()
- Added 6 example operation instances (filter, aggregate, sort, select, drop_nulls, with_columns)

**contracts/operations-schema.json**:
- Replaced v1 schema with v2 (simplified)
- New schema version: 2.0.0
- Single Operation object with: code, display, operation_type, params
- Added param schemas for all 13 operation types
- 13 operation_type enum values

**contracts/export-*.jinja2** (3 templates):
- export-python.jinja2: Now renders `{{ operation.code }}` directly
- export-marimo.jinja2: Renders code with df chaining (df_1, df_2, ...)
- export-jupyter.jinja2: Renders code + display in markdown cells

**plan.md**:
- Added Phase 1.5: Modal Specifications section
- Detailed specs for all 13 modal types with:
  - Trigger keys
  - Field layouts
  - Code generation examples
  - Validation rules
  - Display string patterns
- Added CodeGenerator and DisplayGenerator class architectures
- Defined two-phase validation strategy

#### 3. Supported Operation Types (13 total)

**Core Operations**:
1. filter - `f` key
2. aggregate - `a` key
3. pivot - `p` key
4. join - `j` key

**Selection Operations**:
5. select - `c` key
6. drop - `d`+`c` sequence
7. rename - `r` key

**Transform Operations**:
8. with_columns - `w` key
9. sort - `s` key

**Data Cleaning**:
10. unique - `u` key
11. fill_null - `n`+`f` sequence
12. drop_nulls - `n`+`d` sequence

**Sampling**:
13. head, tail, sample - `h`, `t`, `m` keys

### Impact Assessment

**Simplified**:
- ✅ Operation storage (single entity vs 3+ specialized classes)
- ✅ Export templates (no complex conditional logic)
- ✅ Serialization (uniform JSON structure)

**Added Complexity**:
- ⚠️ Code generation logic (13 modal-specific generators needed)
- ⚠️ Code validation (eval-based execution requires sandboxing)
- ⚠️ Modal UI implementation (13 keyboard-driven forms)

**Benefits**:
- ✅ More flexible - easy to add new operation types
- ✅ Simpler data model - one Operation class
- ✅ Direct narwhals code in exports (more transparent)
- ✅ Edit capability via params storage

**Risks**:
- ⚠️ Code injection if eval() not properly sandboxed (mitigated: controlled namespace)
- ⚠️ More complex TUI modal logic (13 forms vs generic approach)

### Files Modified
- specs/001-tui-data-explorer/spec.md
- specs/001-tui-data-explorer/data-model.md
- specs/001-tui-data-explorer/plan.md
- specs/001-tui-data-explorer/clarification-session-2.md (new)
- specs/001-tui-data-explorer/contracts/operations-schema.json
- specs/001-tui-data-explorer/contracts/export-python.jinja2
- specs/001-tui-data-explorer/contracts/export-marimo.jinja2
- specs/001-tui-data-explorer/contracts/export-jupyter.jinja2

### Next Steps
1. Begin Phase 2 implementation with simplified Operation model
2. Implement 13 modal screens in Textual
3. Build CodeGenerator and DisplayGenerator classes
4. Implement eval-based Operation.apply() with proper sandboxing
5. Update SavedAnalysis CRUD to use new operations schema v2
