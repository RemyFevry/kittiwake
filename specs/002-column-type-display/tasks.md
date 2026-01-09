# Tasks: Column Type Display and Quick Filter

**Feature**: 002-column-type-display  
**Input**: Design documents from `/specs/002-column-type-display/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Not explicitly requested in specification - tasks focus on implementation only

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure:
- Source: `src/kittiwake/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration for type display feature

- [X] T001 Review existing codebase structure in src/kittiwake/ for integration points
- [X] T002 Verify narwhals schema API availability in existing Dataset model

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Create type detection service in src/kittiwake/services/type_detector.py
- [X] T004 [P] Create type configuration constants in src/kittiwake/utils/type_colors.py
- [X] T005 Create contracts/type-mappings.json from TYPE_MAPPINGS configuration
- [X] T006 Validate type-mappings.json contract against configuration in src/kittiwake/utils/type_colors.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visual Column Type Identification (Priority: P1) 🎯 MVP

**Goal**: Display each column header with distinct color and icon based on data type, enabling instant visual recognition of column types without inspecting data

**Independent Test**: Load Titanic dataset and verify column headers show colored type indicators (# for numeric, " for text, ? for boolean) with appropriate colors (blue, green, purple)

### Implementation for User Story 1

- [X] T007 [US1] Implement detect_column_type_category() function in src/kittiwake/services/type_detector.py
- [X] T008 [US1] Define TYPE_MAPPINGS configuration with 5 type categories in src/kittiwake/utils/type_colors.py
- [X] T009 [US1] Define get_type_icon() helper function in src/kittiwake/utils/type_colors.py
- [X] T010 [US1] Define get_type_color() helper function in src/kittiwake/utils/type_colors.py
- [X] T011 [US1] Modify DatasetTable._create_column_header() to generate Rich Text headers with type styling in src/kittiwake/widgets/dataset_table.py
- [X] T012 [US1] Update DatasetTable.load_dataset() to use styled headers for all columns in src/kittiwake/widgets/dataset_table.py
- [X] T013 [US1] Add CSS classes for type colors in src/kittiwake/app.py (numeric, text, date, boolean, unknown)
- [X] T014 [US1] Add type legend section to help overlay in src/kittiwake/widgets/help_overlay.py

**Checkpoint**: Column headers should display with colored type icons when dataset is loaded. All 5 type categories should be visually distinct.

---

## Phase 4: User Story 2 - Quick Filter from Column Header (Priority: P2)

**Goal**: Enable users to create filters by clicking column headers, reducing filter creation from 5 steps to 3 steps

**Independent Test**: Click on "Age" column header and verify quick filter modal opens with Age pre-selected and numeric operators only. Submit filter and verify operation appears in sidebar.

### Implementation for User Story 2

- [X] T015 [P] [US2] Create ColumnHeaderQuickFilter modal widget in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [X] T016 [P] [US2] Create get_operators_for_type() helper function in src/kittiwake/utils/type_colors.py
- [X] T017 [US2] Add on_column_selected() message handler to DatasetTable in src/kittiwake/widgets/dataset_table.py
- [ ] T018 [US2] Implement keyboard handler for Enter key on focused column headers to trigger quick filter in src/kittiwake/widgets/dataset_table.py
- [X] T019 [US2] Implement ColumnHeaderQuickFilter.compose() with pre-populated column and type-filtered operators in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [X] T020 [US2] Implement ColumnHeaderQuickFilter operation creation logic (code, display, params) in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [X] T021 [US2] Implement ColumnHeaderQuickFilter submit handler to create Operation and invoke callback in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [X] T022 [US2] Implement ColumnHeaderQuickFilter cancel/escape handler in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [X] T023 [US2] Add validation for filter value input based on type category (FR-021) in src/kittiwake/widgets/modals/column_header_quick_filter.py
- [ ] T024 [US2] Verify quick filter operations integrate with lazy/eager execution modes
- [ ] T025 [US2] Verify quick filter operations appear in OperationsSidebar with correct state indicators

**Checkpoint**: Clicking column headers opens quick filter modal. Filters created from quick filter should be indistinguishable from Ctrl+F filters.

---

## Phase 5: User Story 3 - Column Type Display with Icon (Priority: P3)

**Goal**: Add icons alongside colors for accessibility, ensuring users with color blindness can identify column types

**Independent Test**: Load dataset and verify each column header shows both color AND icon (# for numeric, " for text, @ for date, ? for boolean, · for unknown). Icons should be readable even without color.

### Implementation for User Story 3

- [ ] T026 [US3] Update get_type_icon() to support Unicode fallback in src/kittiwake/utils/type_colors.py
- [ ] T027 [US3] Add terminal_supports_unicode() detection function in src/kittiwake/utils/type_colors.py
- [ ] T028 [US3] Modify DatasetTable._create_column_header() to include icon prefix in headers in src/kittiwake/widgets/dataset_table.py
- [ ] T029 [US3] Update help overlay type legend to show both ASCII and Unicode icons in src/kittiwake/widgets/help_overlay.py
- [ ] T030 [US3] Verify icons render correctly in ASCII-only terminals (fallback to ASCII icons)
- [ ] T031 [US3] Verify icons render correctly in Unicode-capable terminals (use Unicode emoji)

**Checkpoint**: All column headers should display with both color and icon. Icons should be visible and distinct even when viewed without color (colorblind simulation or grayscale).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T032 [P] Verify color contrast meets WCAG 2.1 AA standards (4.5:1 ratio) in both dark and light themes
- [ ] T033 [P] Test column type display with all narwhals backends (pandas, polars, pyarrow)
- [ ] T034 [P] Test edge cases: mixed types, null columns, nested types map to "unknown" category
- [ ] T035 Verify no performance regression on dataset loading with type detection
- [ ] T036 Verify keyboard-only navigation to column headers (Tab + Enter triggers quick filter)
- [ ] T037 [P] Manual accessibility test: colorblind simulation (verify icons work without color)
- [ ] T038 [P] Manual accessibility test: terminals with 16 colors (verify graceful degradation)
- [ ] T039 Run quickstart.md validation with Titanic dataset
- [ ] T040 Update AGENTS.md with new files via update-agent-context.sh script

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P2) depends on User Story 1 completion (needs styled headers to be clickable)
  - User Story 3 (P3) depends on User Story 1 completion (enhances existing headers with icons)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation for all other stories - implements type detection and visual styling
- **User Story 2 (P2)**: Depends on US1 - requires clickable type-styled headers
- **User Story 3 (P3)**: Depends on US1 - enhances headers with icons (can be done in parallel with US2 if US1 complete)

### Within Each User Story

**User Story 1** (Parallel opportunities):
- T007 (type detection) and T008-T010 (type config) can run in parallel initially
- T011-T012 (header styling) depend on T007-T010
- T013 (CSS) and T014 (help) can run in parallel after T011-T012

**User Story 2** (Parallel opportunities):
- T015-T016 (modal widget + operators) can start in parallel
- T017-T018 (click/keyboard handlers) depend on T015
- T019-T023 (modal implementation) must be sequential (same file)
- T024-T025 (integration verification) can run in parallel

**User Story 3** (Parallel opportunities):
- T026-T027 (icon functions) can run in parallel
- T028-T029 (update UI) can run in parallel after T026-T027
- T030-T031 (verification) can run in parallel

### Parallel Opportunities

- Phase 2: T003 and T004 can run in parallel (different files)
- Phase 3: T013 and T014 can run in parallel
- Phase 4: T015 and T016 can run in parallel, T024 and T025 can run in parallel
- Phase 5: T026 and T027 can run in parallel, T028 and T029 can run in parallel, T030 and T031 can run in parallel
- Phase 6: T032, T033, T034, T037, T038 can all run in parallel

---

## Parallel Example: User Story 1



## Parallel Example: User Story 2



---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Visual Column Type Identification)
4. **STOP and VALIDATE**: Load Titanic dataset and verify colored column headers
5. Demo visual type identification feature

**Deliverable**: Users can instantly see column types by color when loading any dataset

### Incremental Delivery

1. **Foundation** (Phase 1-2) → Type detection and configuration infrastructure ready
2. **MVP** (Phase 3) → Visual type identification with colors → Test independently → Demo
3. **Enhancement 1** (Phase 4) → Quick filter from headers → Test independently → Demo
4. **Enhancement 2** (Phase 5) → Icons for accessibility → Test independently → Demo
5. **Polish** (Phase 6) → Validation and refinement

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **All together**: Complete Setup + Foundational (Phase 1-2)
2. **After Foundational complete**:
   - Developer A: User Story 1 (P1) - Must complete first
3. **After User Story 1 complete**:
   - Developer B: User Story 2 (P2) - Quick filter
   - Developer C: User Story 3 (P3) - Icons (can run parallel with US2)
4. Stories integrate independently, minimal conflicts

---

## Task Summary

- **Total Tasks**: 40
- **Setup Phase**: 2 tasks
- **Foundational Phase**: 4 tasks (CRITICAL - blocks all stories)
- **User Story 1 (P1)**: 8 tasks - Visual type identification (MVP)
- **User Story 2 (P2)**: 11 tasks - Quick filter from headers (includes keyboard handler)
- **User Story 3 (P3)**: 6 tasks - Icons for accessibility
- **Polish Phase**: 9 tasks - Testing and validation

**Parallel Opportunities**: 15 tasks can run in parallel with others (marked with [P])

**MVP Scope**: Setup + Foundational + User Story 1 = 14 tasks

**Independent Test Criteria**:
- US1: Load dataset → see colored column headers
- US2: Click column header → quick filter opens → create filter → verify in sidebar
- US3: Load dataset → see both color and icon in headers

**Estimated Completion**:
- MVP (US1): 3-4 hours
- Full Feature (US1+US2+US3): 8-10 hours
- With Polish: 10-12 hours

---

## Notes

- All tasks include exact file paths for clarity
- Tasks marked [P] work on different files and can run in parallel
- Each user story is independently testable and deliverable
- Type mappings follow JSON schema contract in contracts/type-mappings.json
- No new external dependencies required (uses existing textual, narwhals)
- Reuses existing Operation model and execution pipeline (no changes needed)
- All keyboard shortcuts remain functional (click is enhancement, not requirement)
- Performance target: Type detection < 1ms per column, header rendering < 50ms
