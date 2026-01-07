# Changelog - TUI Data Explorer

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
