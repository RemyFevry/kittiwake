# Tasks: Modern Interactive TUI Design

**Input**: Design documents from `/specs/002-modern-tui-design/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure for new visual design subsystems

- [X] T001 Create themes directory structure at src/kittiwake/ui/themes/ with __init__.py
- [X] T002 Create animation directory structure at src/kittiwake/ui/animation/ with __init__.py
- [X] T003 Create feedback directory structure at src/kittiwake/ui/feedback/ with __init__.py
- [X] T004 Create accessibility directory structure at src/kittiwake/ui/accessibility/ with __init__.py
- [X] T005 Add coloraide>=3.0.0 dependency to pyproject.toml for contrast validation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core theme and color system that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement ColorPalette class in src/kittiwake/ui/themes/colors.py with 3-tier palette support (true color, 256-color, 16-color)
- [X] T007 Implement TypographyConfig class in src/kittiwake/ui/themes/config.py with font weight and alignment settings
- [X] T008 Implement SpacingConfig class in src/kittiwake/ui/themes/config.py with consistent spacing scale
- [X] T009 Implement ThemeConfig class in src/kittiwake/ui/themes/config.py integrating ColorPalette, TypographyConfig, SpacingConfig
- [X] T010 [P] Implement light theme preset in src/kittiwake/ui/themes/presets.py with WCAG AA validated colors
- [X] T011 [P] Implement dark theme preset in src/kittiwake/ui/themes/presets.py with WCAG AA validated colors
- [X] T012 Implement theme loader function in src/kittiwake/ui/themes/__init__.py with color system detection
- [X] T013 [P] Implement WCAG contrast validation function in src/kittiwake/ui/accessibility/contrast.py using coloraide library
- [X] T014 [P] Implement reduced motion detection in src/kittiwake/ui/accessibility/reduced_motion.py checking REDUCE_MOTION and NO_COLOR env vars
- [X] T015 Integrate ThemeConfig into main app in src/kittiwake/__init__.py with automatic theme loading on startup

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Responsive and Fluid Animations (Priority: P1) 🎯 MVP

**Goal**: Every interaction provides immediate visual feedback through smooth animations and transitions with 60fps target performance

**Independent Test**: Perform various UI interactions (opening modals, switching tabs, scrolling data, applying operations) and verify each has appropriate animation timing (100-300ms) and visual feedback without lag

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement AnimationState class in src/kittiwake/ui/animation/engine.py with id, target_widget, property, duration, easing, progress tracking
- [X] T017 [P] [US1] Implement easing functions wrapper in src/kittiwake/ui/animation/easing.py mapping to Textual's built-in easings
- [X] T018 [US1] Implement AnimationEngine singleton in src/kittiwake/ui/animation/engine.py managing concurrent animations (max 20)
- [X] T019 [US1] Implement common transition patterns in src/kittiwake/ui/animation/transitions.py (fade_in, fade_out, slide_in, slide_out, cross_fade)
- [X] T020 [US1] Enhance existing DataTable widget in src/kittiwake/ui/widgets/data_table.py with smooth row highlighting animations (<100ms)
- [X] T021 [US1] Add modal slide-in animation to existing modal base in src/kittiwake/ui/widgets/modal.py with fade + slide effect (200ms total)
- [X] T022 [US1] Add dataset tab transition animations in src/kittiwake/ui/widgets/data_table.py with cross-fade effect (150ms)
- [X] T023 [US1] Add filter operation data update animations in src/kittiwake/ui/widgets/data_table.py with fade in/out for rows
- [X] T024 [US1] Add smooth scrollbar animation in src/kittiwake/ui/widgets/data_table.py maintaining 60fps performance
- [X] T025 [US1] Add terminal resize layout animation in src/kittiwake/ui/widgets/data_table.py with smooth repositioning (150ms)
- [X] T026 [US1] Implement performance monitor in src/kittiwake/ui/animation/engine.py tracking frame times in ring buffer
- [X] T027 [US1] Implement adaptive animation system in src/kittiwake/ui/animation/engine.py auto-disabling decorative animations at <30fps

**Checkpoint**: At this point, all UI interactions should have smooth animations with visual feedback

---

## Phase 4: User Story 2 - Rich Visual Hierarchy and Typography (Priority: P1)

**Goal**: Interface clearly communicates information hierarchy through visual design with WCAG AA compliant colors and consistent typography

**Independent Test**: Load sample data and verify visual distinction between headers/content, appropriate alignment for different data types, readable contrast ratios (WCAG AA minimum 4.5:1), and consistent typography across all interface elements

### Implementation for User Story 2

- [X] T028 [P] [US2] Apply bold weight to column headers in src/kittiwake/ui/widgets/data_table.py using TypographyConfig
- [X] T029 [P] [US2] Implement data type detection and alignment in src/kittiwake/ui/widgets/data_table.py (numeric=right, text=left, dates=left)
- [X] T030 [US2] Apply color palette to existing status bar in src/kittiwake/ui/widgets/status_bar.py using ThemeConfig semantic colors
- [X] T031 [US2] Add visual panel borders in src/kittiwake/ui/widgets/data_table.py using border color from palette
- [X] T032 [US2] Implement status indicator styling in src/kittiwake/ui/widgets/status_bar.py using color + symbols (error=red+✗, success=green+✓, warning=yellow+⚠)
- [X] T033 [US2] Apply spacing config to all widgets in src/kittiwake/ui/widgets/ using SpacingConfig (1 cell vertical, 2 cells horizontal padding)
- [X] T034 [US2] Add theme switching command in src/kittiwake/__main__.py with keyboard shortcut to toggle light/dark themes
- [X] T035 [US2] Implement theme validation on load in src/kittiwake/ui/themes/config.py verifying all contrast ratios meet WCAG AA

**Checkpoint**: Interface should have clear visual hierarchy with accessible colors and consistent typography

---

## Phase 5: User Story 3 - Interactive Data Exploration Enhancements (Priority: P2)

**Goal**: Users see contextual information (tooltips, stats, quick actions, previews) when navigating data cells and column headers

**Independent Test**: Navigate to various data cells and column headers, verify contextual information appears appropriately, test quick actions menu functionality, and confirm operation previews display correctly before application

### Implementation for User Story 3

- [X] T036 [P] [US3] Implement ContextualInfo class in src/kittiwake/ui/feedback/contextual.py with element_type, primary_text, secondary_details, tooltip_content
- [X] T037 [P] [US3] Implement Position class in src/kittiwake/ui/feedback/contextual.py with smart positioning logic (prefer above, fallback below, edge avoidance)
- [X] T038 [US3] Implement LRU cache for ContextualInfo in src/kittiwake/ui/feedback/contextual.py (max 100 entries)
- [X] T039 [US3] Implement tooltip renderer in src/kittiwake/ui/feedback/tooltips.py extending Textual Tooltip with 300ms delay and text wrapping
- [ ] T040 [US3] Add cell focus handler in src/kittiwake/ui/widgets/data_table.py showing tooltips for truncated content
- [ ] T041 [US3] Add numeric cell stats calculator in src/kittiwake/ui/widgets/data_table.py computing % of total and rank
- [ ] T042 [US3] Integrate contextual stats display in src/kittiwake/ui/widgets/status_bar.py showing stats for focused numeric cells
- [ ] T043 [US3] Implement quick actions menu in src/kittiwake/ui/widgets/data_table.py for column headers with data-type-specific operations
- [ ] T044 [US3] Implement operation preview mode in src/kittiwake/ui/widgets/data_table.py highlighting affected rows before confirmation
- [ ] T045 [US3] Add preview accept/cancel handlers in src/kittiwake/ui/widgets/data_table.py clearing highlights and applying or reverting operation

**Checkpoint**: Users should see helpful contextual information and previews when exploring data

---

## Phase 6: User Story 4 - Modern Layout with Status and Context Awareness (Priority: P2)

**Goal**: Users always have clear context about their current state through status bar, breadcrumbs, progress indicators, and modern spacing

**Independent Test**: Perform various workflows and verify status bar updates correctly, operation breadcrumbs display accurately, progress indicators appear for long operations, and layout spacing feels comfortable and modern

### Implementation for User Story 4

- [ ] T046 [P] [US4] Enhance status bar in src/kittiwake/ui/widgets/status_bar.py to show dataset name, row counts, and filter status
- [ ] T047 [P] [US4] Implement breadcrumbs widget in src/kittiwake/ui/widgets/breadcrumbs.py showing operation sequence trail
- [ ] T048 [US4] Implement ProgressIndicator class in src/kittiwake/ui/feedback/progress.py with determinate/indeterminate modes, ETA calculation, cancellation support
- [ ] T049 [US4] Create OperationProgress composite widget in src/kittiwake/ui/feedback/progress.py with description, ProgressBar, ETA, and cancel shortcut
- [ ] T050 [US4] Implement progress manager in src/kittiwake/ui/feedback/progress.py with show/update/hide functions using call_from_thread
- [ ] T051 [US4] Add contextual keyboard shortcuts display in src/kittiwake/ui/widgets/status_bar.py updating based on current mode
- [ ] T052 [US4] Integrate progress indicators in src/kittiwake/operations/ for all operations >500ms with descriptive messages
- [ ] T053 [US4] Add ETA calculation in src/kittiwake/ui/feedback/progress.py for operations >3s based on progress rate
- [ ] T054 [US4] Integrate breadcrumbs widget in src/kittiwake/__main__.py updating when operations are applied
- [ ] T055 [US4] Apply consistent spacing from SpacingConfig to main layout in src/kittiwake/__main__.py (minimum 1 vertical, 2 horizontal cells)

**Checkpoint**: Users should always know their context with clear status, breadcrumbs, and progress feedback

---

## Phase 7: User Story 5 - Elegant Modal Dialogs and Forms (Priority: P3)

**Goal**: Modal dialogs are centered with shadows, have clear visual hierarchy, smooth keyboard navigation, inline validation, and distinct primary actions

**Independent Test**: Open various modal dialogs (filter, aggregate, join), test form field navigation, trigger validation errors, and verify clear visual hierarchy and helpful error messages

### Implementation for User Story 5

- [ ] T056 [US5] Implement ModalDialog base class in src/kittiwake/ui/widgets/modal.py extending Screen with center alignment, shadow, and dimmed background
- [ ] T057 [US5] Add modal slide-in animation to ModalDialog in src/kittiwake/ui/widgets/modal.py with fade + slide from center (200ms total)
- [ ] T058 [US5] Implement form field styling in src/kittiwake/ui/widgets/modal.py with labels, placeholder text, and focus highlighting
- [ ] T059 [US5] Add inline validation to ModalDialog in src/kittiwake/ui/widgets/modal.py with red error messages and specific guidance
- [ ] T060 [US5] Implement smooth Tab/Shift+Tab navigation in ModalDialog in src/kittiwake/ui/widgets/modal.py with visible focus indicators
- [ ] T061 [US5] Style primary/cancel action buttons in ModalDialog in src/kittiwake/ui/widgets/modal.py with distinct colors and positions
- [ ] T062 [US5] Add ESC key handler to ModalDialog in src/kittiwake/ui/widgets/modal.py for cancel action
- [ ] T063 [US5] Implement scrollable modal support in ModalDialog in src/kittiwake/ui/widgets/modal.py for content exceeding terminal height
- [ ] T064 [US5] Add field tooltips to ModalDialog in src/kittiwake/ui/widgets/modal.py with helpful context for operators and formats
- [ ] T065 [US5] Update existing filter/aggregate/join modals to extend new ModalDialog base class

**Checkpoint**: Modal dialogs should be elegant, intuitive, and keyboard-friendly

---

## Phase 8: User Story 6 - Data Visualization and Inline Charts (Priority: P4)

**Goal**: Numeric columns show sparklines in headers, aggregations show inline bar charts, pivot tables support heat-maps, visualizations can be toggled and degrade gracefully

**Independent Test**: Load numeric data and verify sparklines appear in headers, create aggregations and verify inline bar charts, create pivot table and test heat-map visualization, confirm visualizations can be toggled

### Implementation for User Story 6

- [ ] T066 [P] [US6] Implement sparkline generator in src/kittiwake/ui/widgets/data_table.py using Unicode block characters (▁▂▃▄▅▆▇█) with 8-bin histogram
- [ ] T067 [P] [US6] Implement ASCII sparkline fallback in src/kittiwake/ui/widgets/data_table.py using (_-=^) for non-Unicode terminals
- [ ] T068 [P] [US6] Implement inline bar chart renderer in src/kittiwake/ui/widgets/data_table.py for aggregation results showing relative magnitude
- [ ] T069 [US6] Implement heat-map coloring in src/kittiwake/ui/widgets/data_table.py for pivot tables with blue→white→red gradient
- [ ] T070 [US6] Add Unicode support detection in src/kittiwake/ui/widgets/data_table.py checking console.encoding
- [ ] T071 [US6] Implement ASCII density fallback in src/kittiwake/ui/widgets/data_table.py using ( .:+=X#) for heat-maps
- [ ] T072 [US6] Add sparklines to column headers in src/kittiwake/ui/widgets/data_table.py for numeric columns
- [ ] T073 [US6] Add visualization toggle command in src/kittiwake/__main__.py with keyboard shortcut to show/hide visualizations
- [ ] T074 [US6] Implement 16-color mode degradation in src/kittiwake/ui/widgets/data_table.py using background colors only for heat-maps
- [ ] T075 [US6] Implement narrow column handling in src/kittiwake/ui/widgets/data_table.py scaling down or hiding sparklines gracefully

**Checkpoint**: Data visualizations should enhance comprehension and degrade gracefully across terminals

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality enhancements

- [ ] T076 [P] Implement VisualFeedback class in src/kittiwake/ui/feedback/notifications.py with highlight, flash, pulse, shake effects
- [ ] T077 [P] Implement feedback engine in src/kittiwake/ui/feedback/notifications.py managing concurrent feedback (max 10)
- [ ] T078 [P] Add visual feedback to user actions in src/kittiwake/ui/widgets/ (row selection=highlight, save success=green flash, validation error=shake)
- [ ] T079 [P] Implement color-blind palette generator in src/kittiwake/ui/accessibility/color_blind.py for protanopia, deuteranopia, tritanopia
- [ ] T080 [P] Add minimum terminal size check in src/kittiwake/__main__.py displaying warning for <80x24 terminals
- [ ] T081 [P] Add terminal resize adaptation in src/kittiwake/__main__.py triggering color system re-detection
- [ ] T082 [P] Implement status bar truncation in src/kittiwake/ui/widgets/status_bar.py with ellipsis and expand shortcut
- [ ] T083 [P] Add tooltip position clamping in src/kittiwake/ui/feedback/tooltips.py ensuring tooltips stay within terminal bounds
- [ ] T084 [P] Add KITTIWAKE_FORCE_ANIMATIONS env var support in src/kittiwake/ui/animation/engine.py allowing user override
- [ ] T085 Validate quickstart.md examples by running sample code from documentation
- [ ] T086 Performance test animations with large datasets ensuring 60fps maintained
- [ ] T087 Accessibility audit of all color combinations verifying WCAG AA compliance
- [ ] T088 Terminal compatibility testing across true color, 256-color, and 16-color terminals

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2 → P3 → P4)
- **Polish (Phase 9)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Animations)**: Depends on Foundational (Phase 2) - No dependencies on other stories - RECOMMENDED MVP
- **User Story 2 (P1 - Typography)**: Depends on Foundational (Phase 2) - No dependencies on other stories - RECOMMENDED MVP
- **User Story 3 (P2 - Interactive)**: Depends on Foundational (Phase 2) and US1 (animations for tooltips) - Should integrate with US1
- **User Story 4 (P2 - Context)**: Depends on Foundational (Phase 2) and US1 (animations for progress) - Should integrate with US1
- **User Story 5 (P3 - Modals)**: Depends on Foundational (Phase 2) and US1 (modal animations) - Should integrate with US1/US2
- **User Story 6 (P4 - Visualizations)**: Depends on Foundational (Phase 2) and US2 (typography for charts) - Can be added last

### Within Each User Story

- Tasks flow: Classes/entities → Integration → Enhancements → Edge cases
- Parallel tasks [P] can run concurrently (different files)
- Sequential tasks must wait for dependencies
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All 5 tasks can run in parallel (creating different directories)
- **Phase 2 (Foundational)**: Tasks T010-T011 (presets), T013-T014 (accessibility) can run in parallel after T006-T009 complete
- **Phase 3 (US1)**: Tasks T016-T017 (animation classes), T020-T025 (widget enhancements) can run in parallel after T018-T019 complete
- **Phase 4 (US2)**: Tasks T028-T029 (typography), T030-T032 (colors) can run in parallel
- **Phase 5 (US3)**: Tasks T036-T038 (classes), T039-T041 (integration) can run in parallel
- **Phase 6 (US4)**: Tasks T046-T047 (widgets), T048-T050 (progress) can run in parallel
- **Phase 7 (US5)**: Tasks within modal enhancements can run after T056 completes
- **Phase 8 (US6)**: Tasks T066-T068 (visualization renderers) can run in parallel
- **Phase 9 (Polish)**: Most polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Animations)

```bash
# After T018-T019 complete, launch widget enhancements in parallel:
Task T020: "Enhance DataTable with row highlighting"
Task T021: "Add modal slide-in animation"
Task T022: "Add dataset tab transitions"
Task T023: "Add filter operation animations"
Task T024: "Add smooth scrollbar animation"
Task T025: "Add terminal resize animation"

# These 6 tasks work on different animation integration points
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only - Both P1)

1. Complete Phase 1: Setup (5 tasks)
2. Complete Phase 2: Foundational (10 tasks - CRITICAL)
3. Complete Phase 3: User Story 1 - Animations (12 tasks)
4. Complete Phase 4: User Story 2 - Typography (8 tasks)
5. **STOP and VALIDATE**: Test smooth animations and visual hierarchy independently
6. Deploy/demo modern TUI with animations and typography

**Result**: MVP delivers core visual modernization (smooth animations + clear hierarchy) - most impactful user stories

### Incremental Delivery (Recommended)

1. **Foundation** (Phases 1-2): Setup + themes/colors → 15 tasks
2. **MVP** (Phases 3-4): US1 (animations) + US2 (typography) → 20 tasks → Deploy!
3. **Interactive** (Phase 5): US3 (tooltips, stats, previews) → 10 tasks → Deploy!
4. **Context** (Phase 6): US4 (status, breadcrumbs, progress) → 10 tasks → Deploy!
5. **Modals** (Phase 7): US5 (elegant dialogs) → 10 tasks → Deploy!
6. **Visualizations** (Phase 8): US6 (sparklines, charts) → 10 tasks → Deploy!
7. **Polish** (Phase 9): Final enhancements → 13 tasks → Final deploy!

Each deployment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

- **Developer A**: User Story 1 (Animations) - 12 tasks
- **Developer B**: User Story 2 (Typography) - 8 tasks
- **Developer C**: User Story 3 (Interactive) - 10 tasks (depends on US1 for animations)

Stories 1 and 2 can proceed immediately in parallel. Story 3 can start after Story 1 completes animations infrastructure.

---

## Task Summary

**Total Tasks**: 88 tasks

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 10 tasks - BLOCKS all user stories
- Phase 3 (US1 - Animations): 12 tasks
- Phase 4 (US2 - Typography): 8 tasks
- Phase 5 (US3 - Interactive): 10 tasks
- Phase 6 (US4 - Context): 10 tasks
- Phase 7 (US5 - Modals): 10 tasks
- Phase 8 (US6 - Visualizations): 10 tasks
- Phase 9 (Polish): 13 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-4 (US1 + US2) = 35 tasks delivers smooth animations and clear visual hierarchy

**Independent Tests Per Story**:
- US1: Perform UI interactions, verify animation timing and visual feedback
- US2: Load data, verify typography, alignment, contrast ratios, and colors
- US3: Navigate cells/headers, verify tooltips, stats, quick actions, previews
- US4: Perform workflows, verify status bar, breadcrumbs, progress indicators
- US5: Open modals, verify styling, navigation, validation, button distinction
- US6: Load numeric data, verify sparklines, bar charts, heat-maps, toggle

---

## Notes

- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] tasks work on different files and can run concurrently
- [Story] labels map tasks to specific user stories from spec.md
- Each user story is independently testable per acceptance scenarios
- Tests are NOT included (not requested in specification)
- Foundation phase (Phase 2) must complete before any user story work begins
- Recommended MVP: Complete through Phase 4 (US1 + US2) for maximum impact
- All timing constraints from spec.md are preserved in task descriptions
