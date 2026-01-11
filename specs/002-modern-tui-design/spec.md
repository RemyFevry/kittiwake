# Feature Specification: Modern TUI Design - Phase 0 Foundation

**Feature Branch**: `002-modern-tui-design`  
**Created**: 2026-01-11  
**Status**: Draft  
**Input**: User description: "Continue modern TUI design implementation with Phase 0 foundation components based on UI-VISION.md"

## Clarifications

### Session 2026-01-11

- Q: Should the status bar or animation system provide visual distinction between different types of user actions? → A: Status bar should show operation state (e.g., "Preview", "Applying...", "Complete") to reinforce operation-based workflow
- Q: How long should error messages remain visible in the status bar before clearing or reverting to normal display? → A: 5 seconds auto-clear

**Application Design Principle**: Data modification in kittiwake occurs exclusively through operations (filter, aggregate, join, etc.), not through per-cell editing. The UI must reinforce this operation-based workflow pattern.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visual Theme Customization (Priority: P1)

As a data analyst working in different lighting conditions, I need to switch between light and dark themes so that I can comfortably view data without eye strain regardless of my environment.

**Why this priority**: Theme support is foundational - it affects all subsequent UI development and directly impacts accessibility and user comfort. Without proper theme infrastructure, all other visual enhancements will be harder to implement consistently.

**Independent Test**: Can be fully tested by launching the app, pressing Ctrl+T to toggle between light and dark themes, and verifying that all UI components update with appropriate colors that meet WCAG AA contrast standards (4.5:1 for normal text).

**Acceptance Scenarios**:

1. **Given** the app is running in default theme, **When** user presses Ctrl+T, **Then** the entire UI smoothly transitions to the alternate theme (dark→light or light→dark) within 300ms
2. **Given** the app is in dark theme, **When** user examines text colors, **Then** all text meets WCAG AA contrast requirements (4.5:1 minimum for normal text, 3:1 for large text)
3. **Given** the user has a terminal with limited color support (16 colors), **When** the app launches, **Then** it automatically detects the limitation and applies a high-contrast theme variant
4. **Given** the user restarts the app, **When** the app loads, **Then** it remembers and applies the previously selected theme

---

### User Story 2 - Smooth Visual Feedback (Priority: P1)

As a power user performing rapid data operations, I need smooth animations and visual feedback so that I can understand what the application is doing and feel confident that my actions are being processed.

**Why this priority**: Animation and feedback systems are core infrastructure that make the app feel responsive and modern. This directly supports the "5-second discovery" and "keyboard flow state" UX goals from the vision document.

**Independent Test**: Can be tested by performing common actions (opening sidebars, switching tabs, showing modals) and verifying animations run smoothly at 60fps, or gracefully degrade if performance drops below 30fps.

**Acceptance Scenarios**:

1. **Given** the user opens a sidebar, **When** the animation plays, **Then** it slides in from the edge with ease-out easing over 200-250ms
2. **Given** the user switches between dataset tabs, **When** the content changes, **Then** the old content fades out and new content fades in over 200ms
3. **Given** the system is under heavy load (low FPS), **When** animations would drop below 30fps, **Then** decorative animations are automatically disabled while essential feedback remains
4. **Given** the user has set REDUCE_MOTION environment variable, **When** any UI transition occurs, **Then** all animations are instant (0ms duration) while maintaining functional state changes
5. **Given** the user opens a modal dialog, **When** the animation plays, **Then** it fades in and scales from 90% to 100% over 150ms

---

### User Story 3 - Accessible Terminal Compatibility (Priority: P2)

As a user with various terminal emulators and accessibility needs, I need the app to work properly across different color capabilities and motion preferences so that I can use the tool regardless of my terminal or accessibility requirements.

**Why this priority**: Accessibility is critical for inclusivity but can be built on top of the theme system. It's P2 because the basic theme system (P1) must exist first, but accessibility features should be added immediately after.

**Independent Test**: Can be tested by launching the app in terminals with different capabilities (true color, 256-color, 16-color) and with accessibility settings (reduced motion, color-blind modes) and verifying appropriate adaptations occur.

**Acceptance Scenarios**:

1. **Given** the user has a true color terminal, **When** the app displays data, **Then** it uses smooth gradients and full color range for type indicators
2. **Given** the user has a 16-color terminal, **When** the app displays data, **Then** it falls back to high-contrast mode with clear borders and patterns instead of subtle colors
3. **Given** the user enables protanopia mode (red-blind), **When** the app displays type-colored columns, **Then** it uses alternative color palettes that are distinguishable for red color blindness
4. **Given** the user has a terminal smaller than 80x24, **When** the app launches, **Then** it displays a warning message and renders a simplified layout
5. **Given** Unicode is not supported, **When** the app displays icons and special characters, **Then** it falls back to ASCII alternatives (✓ → [Y], ✗ → [N])

---

### User Story 4 - Standalone Status Bar Widget (Priority: P2)

As a user analyzing data through operations, I need a comprehensive status bar that shows dataset information, available shortcuts, operation state, and context-sensitive help so that I can understand the current state and discover available actions without leaving my workflow.

**Why this priority**: The status bar is currently embedded as a label in the DataTable widget. Extracting it as a standalone widget improves modularity and enables richer status information, including operation state tracking that reinforces the operation-based workflow. It's P2 because it depends on theme infrastructure and is less critical than core theme/animation systems.

**Independent Test**: Can be tested by loading a dataset and observing the status bar shows: (1) dataset name and row count in left section, (2) contextual keyboard shortcuts and operation state in middle section that change based on current mode, (3) current row/column position in right section.

**Acceptance Scenarios**:

1. **Given** the user has loaded a 1.2M row dataset named "sales.csv", **When** looking at the status bar, **Then** the left section displays "sales.csv | 1.2M rows"
2. **Given** the user applies filters reducing visible rows to 45K, **When** looking at the status bar, **Then** the left section displays "sales.csv | 1.2M rows | Filtered: 45K"
3. **Given** the user is navigating the data table, **When** the cursor moves, **Then** the right section updates to show "Row 1,234 | Col 12"
4. **Given** the user focuses on a filter sidebar, **When** the mode changes, **Then** the middle section updates to show filter-specific shortcuts like "Enter Apply | Esc Cancel"
5. **Given** a long operation is running, **When** progress is reported, **Then** the status bar middle section displays operation state (e.g., "Applying filter..." with percentage)
6. **Given** the user is previewing an operation in a sidebar, **When** the preview updates, **Then** the status bar middle section displays "Preview" to indicate no changes are applied yet
7. **Given** an operation completes successfully, **When** 2 seconds elapse, **Then** the "Complete" message auto-clears and status bar returns to showing contextual shortcuts
8. **Given** an operation fails with an error, **When** 5 seconds elapse, **Then** the "Error" message auto-clears and status bar returns to showing contextual shortcuts

---

### Edge Cases

- **What happens when terminal is resized during an animation?** Animation should gracefully adapt or complete early if layout changes significantly
- **What happens when theme switching occurs during a long operation?** Theme changes should apply immediately to visible elements without interrupting the operation
- **How does system handle extremely slow terminals (< 10 FPS)?** All animations should be disabled automatically, falling back to instant state changes
- **What happens when user's terminal doesn't support the selected theme?** System should fall back to the closest supported color depth automatically
- **How does the system handle theme persistence when config file is corrupted?** System should fall back to default theme and create a new valid config file
- **What happens when multiple accessibility modes conflict (e.g., color-blind mode + reduced motion)?** System should apply both adaptations simultaneously without conflict
- **How does animation engine handle rapid state changes (e.g., user spam-clicking tab switches)?** Animation should cancel previous animation and start fresh, preventing animation queue buildup

## Requirements *(mandatory)*

### Functional Requirements

#### Theme System

- **FR-001**: System MUST provide a ColorPalette class supporting three terminal color depths: true color (16.7M colors), 256-color, and 16-color
- **FR-002**: System MUST include pre-defined light and dark theme presets with all UI component colors specified
- **FR-003**: System MUST validate all theme colors meet WCAG AA contrast standards (4.5:1 for normal text, 3:1 for large text and UI components)
- **FR-004**: System MUST automatically detect terminal color capability on startup and select appropriate theme variant
- **FR-005**: System MUST allow users to switch themes via Ctrl+T keyboard shortcut
- **FR-006**: System MUST persist user's theme preference to configuration file (~/.kittiwake/config.json)
- **FR-007**: System MUST support color-blind modes: protanopia (red-blind), deuteranopia (green-blind), tritanopia (blue-blind)
- **FR-008**: System MUST provide theme colors for all semantic UI elements: primary, secondary, success, warning, error, info, background, surface, text, border

#### Animation Engine

- **FR-009**: System MUST provide an AnimationState tracking system that monitors animation performance (FPS)
- **FR-010**: System MUST implement standard easing functions: linear, ease-in, ease-out, ease-in-out, spring
- **FR-011**: System MUST support common animation patterns: fade (opacity), slide (position), scale (size), color transitions
- **FR-012**: System MUST monitor average FPS and automatically disable decorative animations when FPS drops below 30
- **FR-013**: System MUST disable all animations when FPS drops below 20, using instant transitions only
- **FR-014**: System MUST respect REDUCE_MOTION or NO_MOTION environment variables by disabling all animations (0ms duration)
- **FR-015**: System MUST allow user override of animation settings via KITTIWAKE_FORCE_ANIMATIONS environment variable
- **FR-016**: System MUST provide animation durations appropriate for interaction type: micro-interactions (100-200ms), macro-transitions (200-300ms)
- **FR-017**: System MUST prevent animation queue buildup by canceling previous animations when new conflicting animations start

#### Status Bar Widget

- **FR-018**: System MUST extract status bar from DatasetTable into standalone StatusBar widget
- **FR-019**: StatusBar MUST display three sections: dataset info (left 40%), contextual shortcuts and operation state (middle 40%), cursor position (right 20%)
- **FR-020**: StatusBar info section MUST show dataset name, total row count, and filtered row count when filters are active
- **FR-021**: StatusBar shortcuts section MUST update dynamically based on current UI mode (table navigation, sidebar open, modal active)
- **FR-022**: StatusBar middle section MUST display operation state indicators: "Preview" (when previewing operations), "Applying..." (during execution), "Complete" (after successful operation), "Error" (on failure)
- **FR-023**: StatusBar MUST auto-clear operation state messages after completion: "Complete" after 2 seconds, "Error" after 5 seconds, then return to contextual shortcuts
- **FR-024**: StatusBar position section MUST show current row number and column number when table is focused
- **FR-025**: StatusBar MUST display progress messages and percentages during long-running operations in middle section
- **FR-026**: StatusBar MUST dock to bottom of screen and adapt to theme colors

#### Accessibility & Terminal Compatibility

- **FR-027**: System MUST detect terminal size on startup and show warning if smaller than 80x24
- **FR-028**: System MUST detect Unicode support and fall back to ASCII alternatives when not available (✓→[Y], ✗→[N], ▁▂▃→_-=)
- **FR-029**: System MUST provide high-contrast theme variant for 16-color terminals
- **FR-030**: System MUST allow users to enable specific color-blind modes via configuration or command-line flag
- **FR-031**: System MUST never rely on color alone for information - always include text, icons, or patterns as alternative indicators

#### Integration & Configuration

- **FR-032**: System MUST integrate ThemeManager into KittiwakeApp initialization
- **FR-033**: System MUST integrate AnimationEngine into KittiwakeApp for all UI transitions
- **FR-034**: System MUST apply theme colors to all existing widgets: DatasetTable, sidebars, modals, tabs
- **FR-035**: System MUST apply animations to existing interactions: sidebar open/close, modal open/close, tab switching
- **FR-036**: System MUST create or update user configuration file at ~/.kittiwake/config.json with theme and animation preferences

### Key Entities

- **Theme**: Represents a complete color scheme including palette for different color depths, semantic color mappings, and accessibility variants
- **ColorPalette**: Collection of colors defined for specific terminal capability (true color, 256-color, or 16-color)
- **AnimationState**: Tracks current animations, performance metrics (FPS), and manages animation lifecycle
- **EasingFunction**: Mathematical function defining animation acceleration curve (linear, ease-in-out, spring, etc.)
- **StatusBarSection**: Individual section within status bar (info, shortcuts, context) with content and layout properties
- **OperationState**: Enumeration of operation lifecycle states: Preview, Applying, Complete, Error - displayed in status bar to reinforce operation-based workflow
- **AccessibilityMode**: Configuration for specific accessibility needs (reduced motion, color-blind type, contrast level)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All animations maintain 60 FPS on modern terminals with standard dataset sizes (up to 100K visible rows)
- **SC-002**: Users can switch themes via Ctrl+T and see the entire UI update within 300ms
- **SC-003**: 100% of text in both light and dark themes meets WCAG AA contrast standards (4.5:1 minimum), verified programmatically
- **SC-004**: Application correctly adapts to all three color depths (true color, 256-color, 16-color) without visual corruption
- **SC-005**: All UI interactions provide visual feedback within 100ms of user action
- **SC-006**: Animation system automatically degrades gracefully, disabling decorative animations when FPS drops below 30
- **SC-007**: Status bar correctly displays dataset information, operation state transitions (Preview→Applying→Complete), updates contextual shortcuts when UI mode changes, and shows accurate cursor position
- **SC-008**: Users with REDUCE_MOTION environment variable experience instant transitions (0ms) while maintaining all functional state changes
- **SC-009**: Application works correctly in terminals as small as 80x24 (with appropriate warnings for smaller sizes)
- **SC-010**: Color-blind modes provide distinguishable visual indicators for all data types without relying solely on color

## Assumptions

- Users have terminal emulators that support ANSI color codes (minimum 16-color support)
- Textual framework provides sufficient hooks for custom animation and theme systems
- Performance monitoring can be done via Textual's internal metrics or system time measurements
- Configuration file location (~/.kittiwake/) is acceptable and writable by users
- Users understand standard keyboard shortcuts (Ctrl+T for theme switching)
- Existing widgets (DatasetTable, sidebars, modals) can be refactored to accept theme colors without breaking functionality
- Animation frame budgets of 16ms (60fps) are achievable for most UI transitions on modern hardware

## Dependencies

- **Textual framework**: Version >=0.47.1 for widget composition and rendering
- **Existing codebase**: DatasetTable, sidebars, modals, MainScreen components must be refactorable
- **Configuration system**: Requires file I/O for theme persistence
- **Terminal capabilities**: ANSI color support detection (via environment variables or terminal queries)

## Scope Boundaries

**In Scope for Phase 0**:
- Theme system infrastructure with light/dark presets
- Animation engine with performance monitoring
- StatusBar widget extraction and enhancement
- Basic accessibility features (reduced motion, color-blind modes, contrast validation)
- Terminal compatibility detection and adaptation
- Integration of theme/animation systems into existing UI components

**Out of Scope for Phase 0** (future phases):
- Advanced widgets: ColumnManager, FilterBuilder, FormulaBar, DataProfiler
- Data operation enhancements: window functions, string transformations, expression builder
- Visualizations: sparklines, charts, heatmaps, conditional formatting
- Advanced features: query builder, workflow templates, comparison view, plugin system
- Custom keybinding configuration (will use default Ctrl+T for theme switching)

## UI/UX Considerations

### Animation Timing Guidelines

| Interaction Type | Duration | Easing | Purpose |
| ---------------- | -------- | ------ | ------- |
| Button press | 100ms | Ease-in-out | Tactile feedback |
| Sidebar slide | 200-250ms | Ease-out | Purposeful reveal |
| Modal open | 150ms | Ease-out with scale 90%→100% | Elegant entrance |
| Tab switch | 200ms | Cross-fade | Seamless context change |
| Toast notification | 150ms | Slide up + fade | Non-intrusive |
| Theme transition | 300ms | Color lerp | Unified experience |

### Theme Color Requirements

Each theme must define colors for:
- **Semantic states**: primary, secondary, success, warning, error, info
- **Surface colors**: background, surface (elevated), panel
- **Text colors**: primary text, secondary text, disabled text, inverse text
- **Border colors**: default border, focus border, divider
- **Data type colors**: string, numeric, boolean, date, null (with color-blind safe alternatives)

### Status Bar Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ sales.csv | 1.2M rows | Filtered: 45K │ Preview | ↑↓ Navigate | Enter Apply | Esc Cancel │ Row 1,234 | Col 12 │
└─────────────────────────────────────────────────────────────────────────────────────┘
     Info Section (40%)                  Operation State + Shortcuts (40%)              Context (20%)
```

**Operation State Examples**:
- **Preview**: Shown when user is configuring an operation in a sidebar (no data changes yet)
- **Applying...**: Shown during operation execution with optional progress percentage
- **Complete**: Briefly shown after successful operation (auto-clears after 2 seconds, then returns to shortcuts)
- **Error**: Shown when operation fails with brief error message (auto-clears after 5 seconds, allowing time to read)

**Auto-Clear Behavior**: Success messages clear quickly (2s) to avoid cluttering workflow, while errors persist longer (5s) to ensure users notice and can read the message.
┌─────────────────────────────────────────────────────────────────────────┐
│ sales.csv | 1.2M rows | Filtered: 45K │ ↑↓ Navigate | / Filter | ? Help │ Row 1,234 | Col 12 │
└─────────────────────────────────────────────────────────────────────────┘
     Info Section (40%)                   Shortcuts Section (40%)         Context (20%)
```

### Accessibility Priority Matrix

| Feature | Impact | Effort | Priority |
| ------- | ------ | ------ | -------- |
| WCAG AA contrast | High | Medium | P1 |
| Reduced motion | High | Low | P1 |
| Color-blind modes | Medium | Medium | P2 |
| Terminal compatibility | High | Low | P1 |
| Unicode fallbacks | Medium | Low | P2 |

## Testing Strategy

### Manual Testing Scenarios

1. **Theme Switching**: Launch app, press Ctrl+T repeatedly, verify smooth transitions and color consistency
2. **Animation Performance**: Perform rapid actions (open/close sidebars, switch tabs) and verify smooth 60fps animations
3. **Degradation**: Simulate low performance and verify animations disable appropriately
4. **Terminal Compatibility**: Test in different terminals (iTerm2, Terminal.app, Alacritty, kitty) with various color settings
5. **Accessibility**: Test with REDUCE_MOTION set, verify instant transitions
6. **Color Blind Modes**: Enable each mode and verify data type colors remain distinguishable
7. **Status Bar - Dataset Info**: Navigate data, open sidebars, apply filters - verify status bar updates correctly
8. **Status Bar - Operation States**: Open filter sidebar (verify "Preview"), apply filter (verify "Applying..." then "Complete"), trigger error (verify "Error" state)

### Automated Testing

- Unit tests for ColorPalette contrast validation (WCAG AA compliance)
- Unit tests for AnimationState FPS monitoring and degradation logic
- Unit tests for theme color interpolation during transitions
- Unit tests for StatusBar section content updates
- Unit tests for OperationState transitions (Preview→Applying→Complete→Error)
- Integration tests for theme persistence to config file
- Integration tests for animation cancellation on rapid state changes
- Integration tests for status bar operation state display during sidebar operations

### Acceptance Criteria Verification

- Contrast checker tool to verify all theme colors meet WCAG AA standards
- FPS monitoring during common operations to ensure 60fps target
- Terminal capability detection tests across different emulators
- Animation timing measurements to verify durations match specifications
- Theme persistence tests to ensure settings survive app restarts
