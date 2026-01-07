## Clarification Session 2 - Operation Storage Simplification

**Context**: User feedback indicates current operation model is too complex. Operations should be stored as narwhals expression strings instead of structured classes.

**Date**: 2026-01-08

### Question 1: Storage Format
**Q**: How should narwhals expressions be serialized?
**A**: Store as Python code strings (Option A). TUI will translate user interactions into narwhals code, but users never write code directly.

### Question 2: TUI Interaction Pattern
**Q**: How should the TUI enable users to build narwhals expressions without writing code?
**A**: Modal-based approach with forms (filter modal with column dropdown, operator dropdown, value input)

### Question 3: Supported Operations
**Q**: Which narwhals operations need TUI modal support initially?

Given the spec requirements (FR-016 through FR-032), we need to support:
- Filtering (FR-016, FR-017, FR-018)
- Aggregation (FR-021, FR-022, FR-023)
- Pivot tables (FR-025, FR-026, FR-027)
- Joins/Merges (FR-029, FR-030, FR-031)

Should we also support:
- Column selection/projection (`df.select()`)
- Sorting (`df.sort()`)
- Column renaming (`df.rename()`)
- New calculated columns (`df.with_columns()`)

Which operations should have dedicated modals in the initial implementation?
**A**: Yes to all listed operations. Include the following with dedicated modals:
- Filtering (`df.filter()`)
- Aggregation (`df.group_by().agg()`)
- Pivot tables (using group_by + reshape)
- Joins/Merges (`df.join()`)
- Column selection (`df.select()`)
- Sorting (`df.sort()`)
- Column renaming (`df.rename()`)
- Calculated columns (`df.with_columns()`)

Additional relevant operations to include:
- Drop columns (`df.drop()`)
- Drop duplicates (`df.unique()`)
- Fill null values (`df.fill_null()`)
- Drop null values (`df.drop_nulls()`)
- Head/Tail/Sample (`df.head()`, `df.tail()`, `df.sample()`)

### Question 4: Operation Storage Schema
**Q**: How should operations be stored in the simplified model?

Current schema has structured objects with type/column/operator/value fields. With code strings, we could:

- Option A: Store just the code string
  ```json
  {
    "code": "df.filter(nw.col('age') > 25)"
  }
  ```

- Option B: Store code + minimal metadata for display
  ```json
  {
    "code": "df.filter(nw.col('age') > 25)",
    "display": "Filter: age > 25",
    "operation_type": "filter"
  }
  ```

- Option C: Store code + full parameters for editing
  ```json
  {
    "code": "df.filter(nw.col('age') > 25)",
    "display": "Filter: age > 25",
    "operation_type": "filter",
    "params": {
      "column": "age",
      "operator": ">",
      "value": 25
    }
  }
  ```

Option C allows users to edit operations later via the modal. Which approach should we use?
**A**: Option C - Store code + full parameters for editing. This enables users to edit operations later by reopening the modal with pre-filled values.

### Question 5: Code Validation and Safety
**Q**: How should we handle validation and safety of generated narwhals code?

Since operations are stored as executable code strings, we need to consider:

- **Validation timing**: 
  - Option A: Validate immediately when modal submits (try to execute on sample data)
  - Option B: Validate when operation is applied to dataset
  - Option C: Both immediate validation + runtime validation

- **Safety concerns**:
  - Should we restrict code execution to a safe subset of narwhals operations?
  - Should we use AST parsing to verify only allowed operations are in the code string?
  - Should we sandbox code execution?

- **Error handling**:
  - If generated code fails at runtime (e.g., column no longer exists after previous operation), how should we handle it?
  - Option A: Skip failed operation and continue with rest
  - Option B: Stop operation chain and show error
  - Option C: Offer to edit/remove the failing operation

What's your preferred approach for validation and safety?
**A**: 
- **Validation timing**: Option C - Both immediate validation (on modal submit with sample data) + runtime validation (when applying to dataset)
- **Safety**: Since TUI generates all code from modals, AST parsing is not required - trust the generator
- **Error handling**: Option B - Stop operation chain and show error to user

---

## Summary of Decisions

1. **Storage Format**: Operations stored as Python code strings (narwhals expressions)
2. **User Interaction**: Modal-based forms with dropdowns/inputs (keyboard-driven)
3. **Supported Operations** (13 total with dedicated modals):
   - Core: filter, aggregate, pivot, join
   - Selection: select, drop, rename
   - Transform: with_columns, sort
   - Data cleaning: unique, fill_null, drop_nulls
   - Sampling: head, tail, sample
4. **Storage Schema**: Code + display string + operation_type + params (for edit capability)
5. **Validation**: Immediate (modal submit) + runtime (operation apply), stop chain on error

## Integration Tasks

Files to update:
1. `spec.md` - Add clarifications to session, update Key Entities to remove complex operation classes
2. `data-model.md` - Simplify Operation entity, remove FilterOperation/AggregationOperation/PivotOperation
3. `contracts/operations-schema.json` - Replace with simplified schema for code storage
4. `contracts/export-*.jinja2` - Update templates to render code strings directly
5. Add new section to plan.md for modal specifications

---

**Status**: ✅ Clarification Complete
**Next Step**: Integrate clarifications into specification files
