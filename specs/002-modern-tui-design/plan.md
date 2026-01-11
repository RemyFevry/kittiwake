# Implementation Plan: Modern Interactive TUI Design

**Branch**: `002-modern-tui-design` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-modern-tui-design/spec.md`

**Note**: This plan enhances the existing TUI data explorer (001) with modern visual design, smooth animations, and interactive elements.

## Summary

This feature modernizes the kittiwake TUI with contemporary design patterns inspired by Claude Code, OpenCode, and other acclaimed TUI applications. The implementation focuses on smooth animations (60fps target, <300ms duration), rich visual hierarchy with WCAG AA compliance, interactive exploration features (tooltips, contextual stats, previews), modern layout with status awareness, elegant modal dialogs, and inline data visualizations. The design system includes comprehensive theme support, accessibility features (reduced motion, color-blind modes), and graceful degradation for limited terminal capabilities.

## Technical Context

**Language/Version**: Python >=3.13 (from constitution)  
**Primary Dependencies**: textual >=7.0.1 (TUI framework from constitution), narwhals >=2.15.0 (data operations)  
**Storage**: N/A (visual design layer, no data persistence)  
**Testing**: pytest with Textual testing utilities (from constitution)  
**Target Platform**: Terminal environments (Linux, macOS, Windows) with varying color support (true color, 256-color, 16-color)
**Project Type**: Single project (enhances existing src/kittiwake/)  
**Performance Goals**: 60fps animations, <100ms visual feedback, <300ms animation completion, <500ms operation progress display  
**Constraints**: Must work in 80x24 minimum terminal size, WCAG AA contrast ratios (4.5:1 text), respect reduced motion preferences, no blocking UI thread >100ms  
**Scale/Scope**: 40 functional requirements, 6 priority-ordered user stories, 5 key visual entities (ThemeConfig, AnimationState, ContextualInfo, VisualFeedback, ProgressIndicator)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Keyboard-First Interaction ✓ PASS

**Requirement**: Every feature fully accessible via keyboard, clear visual feedback, consistent key bindings, help overlay, no focus traps.

**Compliance**:
- ✓ FR-011: Immediate visual feedback (<100ms) for all keyboard interactions
- ✓ FR-017: Focus indicators with clear visual distinction
- ✓ FR-020: Contextual keyboard shortcuts in status bar
- ✓ FR-028: Smooth keyboard navigation between form fields
- ✓ Modal dialogs (FR-024-030) designed with keyboard-first navigation
- ✓ All user stories emphasize keyboard interaction patterns

**Verification**: All 40 functional requirements specify keyboard-driven workflows. No mouse-dependent features.

### II. Data Source Agnostic ✓ PASS

**Requirement**: Work seamlessly with multiple data sources through narwhals, user doesn't need to know backend.

**Compliance**:
- ✓ This feature is a visual design layer that doesn't interact with data sources directly
- ✓ Enhances existing narwhals-based operations (filter, aggregate, pivot) from feature 001
- ✓ Operation previews (FR-015) and contextual stats (FR-013) work with any narwhals backend
- ✓ No direct pandas/polars API usage

**Verification**: Feature focuses on presentation and interaction, delegates all data operations to narwhals layer.

### III. TUI-Native Design ✓ PASS

**Requirement**: Built using Textual framework primitives, reactive model, CSS-like styling, built-in widgets, responsive layouts.

**Compliance**:
- ✓ All visual design requirements (FR-001-010) map to Textual capabilities:
  - Animations via Textual's animation system
  - Themes via Textual CSS variables
  - Typography via Textual styles (bold, alignment)
  - Layouts via Textual's layout system
- ✓ FR-038: Adapt to terminal resize (Textual's reactive layout)
- ✓ FR-010: Detect terminal color capabilities (Textual's terminal detection)
- ✓ FR-039: Minimum terminal size warning (Textual's screen size awareness)

**Verification**: All 40 FRs are implementable using Textual primitives without custom escape sequences.

### IV. Performance & Responsivity ✓ PASS

**Requirement**: Never block UI >100ms, async I/O, progress indicators >500ms, cancellation support, lazy loading.

**Compliance**:
- ✓ FR-001: 60fps target performance explicitly specified
- ✓ FR-002: Max 300ms animation duration (non-blocking)
- ✓ FR-011: <100ms feedback for user actions (meets <100ms blocking threshold)
- ✓ FR-021: Progress indicators for operations >500ms
- ✓ FR-022: Estimated completion time for operations >3s
- ✓ FR-040: Auto-disable animations on performance degradation
- ✓ SC-002: 60fps maintained during animations and scrolling

**Verification**: All timing requirements align with constitution thresholds. Animations are non-blocking visual transitions.

### V. Composable Operations ✓ PASS

**Requirement**: Operations chainable, save workflows, undo/redo, preview results, export transformed data.

**Compliance**:
- ✓ FR-015: Operation previews with highlighting before confirmation (supports composability)
- ✓ FR-019: Operation breadcrumb trail showing sequence (visualizes composition)
- ✓ This feature enhances the visual presentation of composable operations from feature 001
- ✓ Modal dialogs (FR-024-030) provide UI for configuring operations before chaining
- ✓ Contextual stats (FR-013) help users understand operation impacts

**Verification**: Feature provides visual scaffolding for operation composition defined in feature 001.

### Post-Design Re-check ✓ COMPLETE

**Phase 1 artifacts reviewed**: data-model.md, contracts/, quickstart.md

**Re-verification**:
- ✓ **Keyboard-First**: All entities (ThemeConfig, AnimationState, etc.) support keyboard-only workflows. No mouse-dependent state.
- ✓ **Data Source Agnostic**: No entities interact with data backends. Visual layer is independent of narwhals operations.
- ✓ **TUI-Native**: All entities use Textual primitives (Widget properties, reactive updates, CSS styling). No custom escape sequences.
- ✓ **Performance**: AnimationState tracks non-blocking animations. ProgressIndicator uses async updates. All timing constraints met.
- ✓ **Composable**: VisualFeedback and ContextualInfo enhance operation composition from feature 001. No breaking changes.

**Conclusion**: Design maintains full constitution compliance. Ready for Phase 2 (task breakdown).

## Project Structure

### Documentation (this feature)

```text
specs/002-modern-tui-design/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── theme-config.json       # ThemeConfig schema
│   ├── animation-state.json    # AnimationState schema
│   └── visual-feedback.json    # VisualFeedback schema
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/kittiwake/
├── ui/                          # TUI components (from feature 001)
│   ├── themes/                  # NEW: Theme management
│   │   ├── __init__.py
│   │   ├── config.py           # ThemeConfig implementation
│   │   ├── colors.py           # Color palette definitions
│   │   └── presets.py          # Light/dark theme presets
│   ├── animation/               # NEW: Animation system
│   │   ├── __init__.py
│   │   ├── engine.py           # AnimationState and engine
│   │   ├── easing.py           # Easing functions
│   │   └── transitions.py      # Common transition patterns
│   ├── feedback/                # NEW: Visual feedback system
│   │   ├── __init__.py
│   │   ├── contextual.py       # ContextualInfo implementation
│   │   ├── tooltips.py         # Tooltip rendering
│   │   ├── progress.py         # ProgressIndicator implementation
│   │   └── notifications.py    # VisualFeedback implementation
│   ├── widgets/                 # Textual widget extensions (existing)
│   │   ├── data_table.py       # Enhanced with animations/tooltips
│   │   ├── modal.py            # Enhanced with modern styling
│   │   ├── status_bar.py       # Enhanced with contextual shortcuts
│   │   └── breadcrumbs.py      # NEW: Operation breadcrumb widget
│   └── accessibility/           # NEW: Accessibility features
│       ├── __init__.py
│       ├── reduced_motion.py   # Detect and respect motion preferences
│       ├── contrast.py         # WCAG contrast validation
│       └── color_blind.py      # Color-blind friendly alternatives
├── operations/                  # Data operations (from feature 001)
├── models/                      # Data models (from feature 001)
└── __main__.py                  # Entry point (existing)

tests/
├── ui/                          # NEW: UI component tests
│   ├── test_themes.py
│   ├── test_animations.py
│   ├── test_feedback.py
│   └── test_accessibility.py
├── integration/                 # Integration tests (from feature 001)
└── unit/                        # Unit tests (from feature 001)
```

**Structure Decision**: Single project structure (default). This feature enhances the existing `src/kittiwake/` with new UI subsystems (themes, animation, feedback, accessibility). All new code integrates into the existing TUI layer under `src/kittiwake/ui/`. Test structure mirrors source organization.

## Complexity Tracking

No constitution violations. This section is empty per template instructions.
