---

description: "Task list for Modern Interactive TUI Design feature implementation"
---

# Tasks: Modern Interactive TUI Design

**Input**: Design documents from `/specs/002-modern-tui-design/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create theme management directory structure in src/kittiwake/ui/themes/
- [ ] T002 Create animation system directory structure in src/kittiwake/ui/animation/
- [ ] T003 [P] Create visual feedback system directory structure in src/kittiwake/ui/feedback/
- [ ] T004 [P] Create accessibility features directory structure in src/kittiwake/ui/accessibility/
- [ ] T005 [P] Create enhanced widgets directory structure in src/kittiwake/ui/widgets/
- [ ] T006 Install coloraide library for WCAG contrast validation
- [ ] T007 Configure pytest with Textual testing utilities

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 [P] Implement ThemeConfig data model in src/kittiwake/ui/themes/config.py
- [ ] T009 [P] Implement ColorPalette data model in src/kittiwake/ui/themes/colors.py
- [ ] T010 [P] Implement TypographyConfig and SpacingConfig in src/kittiwake/ui/themes/config.py
- [ ] T011 [P] Implement ThemeManager singleton in src/kittiwake/ui/themes/__init__.py
- [ ] T012 [P] Implement AnimationState data model in src/kittiwake/ui/animation/engine.py
- [ ] T013 [P] Implement AnimationEngine singleton in src/kittiwake/ui/animation/engine.py
- [ ] T014 [P] Implement EasingFunctions in src/kittiwake/ui/animation/easing.py
- [ ] T015 [P] Implement ContextualInfo data model in src/kittiwake/ui/feedback/contextual.py
- [ ] T016 [P] Implement VisualFeedback data model in src/kittiwake/ui/feedback/notifications.py
- [ ] T017 [P] Implement ProgressIndicator data model in src/kittiwake/ui/feedback/progress.py
- [ ] T018 [P] Implement reduced motion detection in src/kittiwake/ui/accessibility/reduced_motion.py
- [ ] T019 [P] Implement contrast validation utility in src/kittiwake/ui/accessibility/contrast.py
- [ ] T020 [P] Implement color-blind mode utilities in src/kittiwake/ui/accessibility/color_blind.py
- [ ] T021 Implement theme persistence to config file in src/kittiwake/ui/themes/config.py
- [ ] T022 Implement terminal color capability detection in src/kittiwake/ui/themes/config.py
- [ ] T023 Implement FPS monitoring for adaptive animations in src/kittiwake/ui/animation/engine.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visual Theme Customization (Priority: P1) 🎯 MVP

**Goal**: Allow users to switch between light and dark themes with WCAG AA compliant contrast ratios

**Independent Test**: Can be fully tested by launching the app, pressing Ctrl+T to toggle between light and dark themes, and verifying that all UI components update with appropriate colors that meet WCAG AA contrast standards (4.5:1 for normal text).

### Implementation for User Story 1

- [ ] T024 [P] [US1] Create light theme preset in src/kittiwake/ui/themes/presets.py
- [ ] T025 [P] [US1] Create dark theme preset in src/kittiwake/ui/themes/presets.py
- [ ] T026 [US1] Implement theme switching via Ctrl+T in KittiwakeApp
- [ ] T027 [US1] Implement smooth theme transition animation (300ms) in src/kittiwake/ui/themes/__init__.py
- [ ] T028 [US1] Implement WCAG AA contrast validation for all theme colors
- [ ] T029 [US1] Implement automatic theme detection based on terminal color capability
- [ ] T030 [US1] Implement theme persistence to ~/.kittiwake/config.json
- [ ] T031 [US1] Apply theme colors to existing DatasetTable widget
- [ ] T032 [US1] Apply theme colors to existing sidebar widgets
- [ ] T033 [US1] Apply theme colors to existing modal dialogs

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Smooth Visual Feedback (Priority: P1)

**Goal**: Provide smooth animations and visual feedback for UI interactions at 60fps

**Independent Test**: Can be tested by performing common actions (opening sidebars, switching tabs, showing modals) and verifying animations run smoothly at 60fps, or gracefully degrade if performance drops below 30fps.

### Implementation for User Story 2

- [ ] T034 [P] [US2] Implement sidebar slide animation (ease-out, 200-250ms) in src/kittiwake/ui/widgets/modal.py
- [ ] T035 [P] [US2] Implement tab switching fade animation (200ms) in src/kittiwake/ui/widgets/data_table.py
- [ ] T036 [US2] Implement modal open animation (fade + scale 90%→100%, 150ms) in src/kittiwake/ui/widgets/modal.py
- [ ] T037 [US2] Implement animation performance monitoring and degradation logic
- [ ] T038 [US2] Implement reduced motion support via environment variable detection
- [ ] T039 [US2] Implement animation cancellation to prevent queue buildup
- [ ] T040 [US2] Apply animations to existing sidebar open/close interactions
- [ ] T041 [US2] Apply animations to existing modal open/close interactions
- [ ] T042 [US2] Apply animations to existing tab switching interactions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Accessible Terminal Compatibility (Priority: P2)

**Goal**: Ensure app works properly across different terminal capabilities and accessibility needs

**Independent Test**: Can be tested by launching the app in terminals with different capabilities (true color, 256-color, 16-color) and with accessibility settings (reduced motion, color-blind modes) and verifying appropriate adaptations occur.

### Implementation for User Story 3

- [ ] T043 [P] [US3] Implement 256-color theme variant in src/kittiwake/ui/themes/colors.py
- [ ] T044 [P] [US3] Implement 16-color theme variant with high-contrast mode in src/kittiwake/ui/themes/colors.py
- [ ] T045 [US3] Implement protanopia (red-blind) color palette in src/kittiwake/ui/accessibility/color_blind.py
- [ ] T046 [US3] Implement deuteranopia (green-blind) color palette in src/kittiwake/ui/accessibility/color_blind.py
- [ ] T047 [US3] Implement tritanopia (blue-blind) color palette in src/kittiwake/ui/accessibility/color_blind.py
- [ ] T048 [US3] Implement terminal size detection and warning for <80x24 in src/kittiwake/ui/accessibility/__init__.py
- [ ] T049 [US3] Implement Unicode support detection and ASCII fallbacks in src/kittiwake/ui/accessibility/__init__.py
- [ ] T050 [US3] Apply color-blind modes to data type indicators in DatasetTable
- [ ] T051 [US3] Apply high-contrast mode to 16-color terminals
- [ ] T052 [US3] Implement accessibility mode persistence to config

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Standalone Status Bar Widget (Priority: P2)

**Goal**: Extract status bar from DataTable widget into a standalone widget with enhanced functionality

**Independent Test**: Can be tested by loading a dataset and observing the status bar shows: (1) dataset name and row count in left section, (2) contextual keyboard shortcuts and operation state in middle section that change based on current mode, (3) current row/column position in right section.

### Implementation for User Story 4

- [ ] T053 [US4] Extract StatusBar widget from DataTable into src/kittiwake/ui/widgets/status_bar.py
- [ ] T054 [US4] Implement three-section layout (dataset info, shortcuts/op state, cursor pos) in StatusBar
- [ ] T055 [US4] Implement dataset info section with name, total rows, filtered rows in StatusBar
- [ ] T056 [US4] Implement contextual shortcuts section that updates based on UI mode in StatusBar
- [ ] T057 [US4] Implement cursor position section showing current row/column in StatusBar
- [ ] T058 [US4] Implement operation state indicators (Preview, Applying..., Complete, Error) in StatusBar
- [ ] T059 [US4] Implement auto-clear behavior (2s for Complete, 5s for Error) in StatusBar
- [ ] T060 [US4] Implement progress display during long-running operations in StatusBar
- [ ] T061 [US4] Apply theme colors to StatusBar widget
- [ ] T062 [US4] Integrate StatusBar with existing UI components and operation workflow

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T063 [P] Update documentation with theme customization guide in docs/
- [ ] T064 [P] Update documentation with animation system guide in docs/
- [ ] T065 [P] Update documentation with accessibility features guide in docs/
- [ ] T066 [P] Add unit tests for ColorPalette contrast validation in tests/ui/test_themes.py
- [ ] T067 [P] Add unit tests for AnimationState FPS monitoring in tests/ui/test_animations.py
- [ ] T068 [P] Add unit tests for StatusBar functionality in tests/ui/test_feedback.py
- [ ] T069 [P] Add integration tests for theme switching in tests/ui/test_themes.py
- [ ] T070 [P] Add integration tests for animation degradation in tests/ui/test_animations.py
- [ ] T071 [P] Add accessibility integration tests in tests/ui/test_accessibility.py
- [ ] T072 [P] Run quickstart.md validation scenarios
- [ ] T073 Code cleanup and refactoring across all new modules
- [ ] T074 Performance optimization across all stories
- [ ] T075 Security hardening for config file access

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on theme system from US1
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May use theme system from US1

### Within Each User Story

- Core implementation before UI integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all theme preset implementations together:
Task: "Create light theme preset in src/kittiwake/ui/themes/presets.py"
Task: "Create dark theme preset in src/kittiwake/ui/themes/presets.py"

# Launch all theme application tasks together:
Task: "Apply theme colors to existing DatasetTable widget"
Task: "Apply theme colors to existing sidebar widgets"
Task: "Apply theme colors to existing modal dialogs"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Theme Customization)
4. Complete Phase 4: User Story 2 (Smooth Visual Feedback)
5. **STOP and VALIDATE**: Test US1 and US2 together independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence