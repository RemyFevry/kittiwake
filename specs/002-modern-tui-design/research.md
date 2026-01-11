# Research: Modern Interactive TUI Design

**Feature**: 002-modern-tui-design  
**Date**: 2026-01-08  
**Purpose**: Research design decisions for implementing modern, interactive TUI design with animations, accessibility, and visual polish

## Overview

This document consolidates research findings for implementing modern TUI design patterns in kittiwake. The research focuses on Textual framework capabilities, animation techniques for terminals, accessibility best practices, and visual design patterns from acclaimed TUI applications.

## Research Areas

### 1. Textual Animation System

**Decision**: Use Textual's built-in animation system with easing functions for all UI transitions.

**Rationale**:
- Textual 7.0+ provides native animation support via `animate()` method on widgets
- Built-in easing functions: `linear`, `in_out_cubic`, `in_out_expo`, `bounce_out`, etc.
- Automatically respects frame timing and terminal refresh rates
- Non-blocking: animations run in background without blocking event loop
- Cancellable: can stop animations mid-flight when needed

**Implementation approach**:
- Widget styles (opacity, offset, scale) are animatable
- Target 60fps by using `duration` parameter (e.g., `animate("opacity", 1.0, duration=0.2)`)
- Chain animations using `on_complete` callbacks
- Group related animations using `AnimationState` tracker

**Alternatives considered**:
- Custom frame-based animation: More control but reinvents Textual's tested system
- CSS-only transitions: Limited to style changes, not suitable for layout animations
- **Rejected because**: Textual's system is optimized for terminal rendering and handles edge cases (slow terminals, resize during animation)

**References**:
- Textual Animation API: https://textual.textualize.io/guide/animation/
- Textual Widget.animate() method: https://textual.textualize.io/api/widget/#textual.widget.Widget.animate

---

### 2. Terminal Color Detection and Adaptation

**Decision**: Use Textual's `detect_color_system()` and provide graceful degradation with preset palettes for each color mode.

**Rationale**:
- Terminals vary widely: true color (16M colors), 256-color, 16-color (ANSI), monochrome
- Textual automatically detects capabilities via `App.console.color_system`
- Can define separate color palettes per mode in CSS
- Use semantic color names (primary, accent, warning) mapped to mode-specific values

**Implementation approach**:
- Define 3 palette tiers:
  - **True color**: Full RGB values with gradients
  - **256-color**: Nearest ANSI 256 equivalents
  - **16-color**: Standard ANSI colors only
- Use Textual CSS variables: `$primary: #3b82f6;` (true color) → `$primary: blue;` (16-color)
- Test contrast ratios for each tier to maintain WCAG AA compliance

**Alternatives considered**:
- Manual escape sequence detection: Error-prone and misses edge cases
- Single palette with dithering: Looks poor in 16-color terminals
- **Rejected because**: Textual's detection is battle-tested and CSS variables provide clean abstraction

**References**:
- Textual Color System: https://textual.textualize.io/guide/design/#color-system
- Rich Console Detection: https://rich.readthedocs.io/en/stable/console.html#color-systems

---

### 3. WCAG Accessibility Compliance

**Decision**: Implement automated contrast ratio validation using `coloraide` library and provide reduced motion detection.

**Rationale**:
- WCAG AA requires 4.5:1 for normal text, 3:1 for large text (18pt+)
- Terminal text is typically small (12-14pt equivalent), needs 4.5:1
- Python's `coloraide` library provides accurate contrast calculations
- Reduced motion detected via environment variables (no standard terminal API)

**Implementation approach**:
- **Contrast validation**:
  - Validate all theme color pairs at build/test time
  - Use `coloraide.contrast()` for accurate ratios
  - Fail theme validation if any pair below threshold
- **Reduced motion**:
  - Check `REDUCE_MOTION=1` env var (user-set)
  - Check `NO_COLOR=1` as fallback indicator
  - When enabled: disable all animations (duration=0), use instant transitions

**Alternatives considered**:
- Manual contrast testing: Time-consuming and error-prone
- No reduced motion support: Excludes users with vestibular disorders
- **Rejected because**: Automated validation ensures compliance, reduced motion is accessibility requirement

**References**:
- WCAG 2.1 Contrast Guidelines: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- coloraide library: https://facelessuser.github.io/coloraide/
- Reduced Motion Best Practices: https://web.dev/prefers-reduced-motion/

---

### 4. Tooltip and Contextual Info Rendering

**Decision**: Use Textual's `Tooltip` class with custom positioning logic for smart edge avoidance.

**Rationale**:
- Textual 7.0+ provides `Tooltip` widget with automatic show/hide
- Triggers on hover/focus with configurable delay (300ms target)
- Supports multi-line content with automatic wrapping
- Can position relative to trigger widget or cursor

**Implementation approach**:
- Extend `Tooltip` class for cell-specific tooltips
- Position algorithm:
  1. Prefer above widget if space available
  2. Fall back to below if top clipped
  3. Align to left/right edge of trigger widget
  4. Wrap text if exceeds terminal width - 4 (margin)
- Cache tooltip content per cell to avoid re-computation
- Show after 300ms dwell time, hide on navigation/action

**Alternatives considered**:
- Status bar only: Can't show long cell values
- Separate overlay screen: Too heavy for simple tooltips
- **Rejected because**: `Tooltip` is purpose-built and handles edge cases (resize, fast navigation)

**References**:
- Textual Tooltip API: https://textual.textualize.io/api/widgets/tooltip/
- Textual Events (hover): https://textual.textualize.io/guide/events/#mouse-events

---

### 5. Progress Indicators and Async Operations

**Decision**: Use Textual's `ProgressBar` widget with custom overlay for descriptive messages and cancellation.

**Rationale**:
- Textual provides `ProgressBar` for determinate (0-100%) and indeterminate (spinner) progress
- Can update progress from background async tasks via reactive properties
- Constitution requires progress display for operations >500ms
- Users need ability to cancel long operations

**Implementation approach**:
- Create `OperationProgress` composite widget:
  - Top: Operation description text
  - Middle: `ProgressBar` (indeterminate or percentage)
  - Bottom: Estimated time / Cancel shortcut
- Update from async tasks using `call_from_thread()` for thread safety
- Cancel via `Ctrl+C` or ESC key → set cancellation flag → task checks flag periodically
- Show in overlay (modal-like) for <3s operations, move to status bar for longer ones

**Alternatives considered**:
- Spinner-only in status bar: Insufficient for long operations
- Blocking with synchronous progress: Violates <100ms UI blocking requirement
- **Rejected because**: Async with reactive updates maintains responsiveness

**References**:
- Textual ProgressBar: https://textual.textualize.io/widgets/progress_bar/
- Textual Workers (async): https://textual.textualize.io/guide/workers/
- Textual call_from_thread: https://textual.textualize.io/api/app/#textual.app.App.call_from_thread

---

### 6. Modal Dialog Design Patterns

**Decision**: Use Textual's `Screen` modal mode with custom `ModalDialog` base class for consistent styling and behavior.

**Rationale**:
- Textual screens can be pushed in modal mode, dimming background automatically
- Modal screens block interaction with underlying screen
- Can define custom base class for shared styling (shadow, borders, padding)
- Exit via ESC or cancel button

**Implementation approach**:
- Create `ModalDialog` base class extending `Screen`:
  - Center alignment via CSS: `align: center middle;`
  - Shadow via border and background colors
  - Standard footer with Apply/Cancel buttons
  - ESC key bound to cancel action
- Specific modals extend `ModalDialog`:
  - `FilterModal`, `AggregateModal`, `JoinModal`, etc.
  - Each defines form fields using Textual's `Input`, `Select`, etc.
  - Inline validation via reactive properties and `watch_*` methods
- Form navigation via Tab/Shift+Tab (built-in Textual behavior)

**Alternatives considered**:
- Overlay within same screen: More complex state management
- External dialog library: Adds dependency and may conflict with Textual
- **Rejected because**: Screen modal mode is idiomatic Textual pattern

**References**:
- Textual Screens: https://textual.textualize.io/guide/screens/
- Textual Modal Mode: https://textual.textualize.io/guide/screens/#modal-screens
- Textual Forms: https://textual.textualize.io/how-to/forms/

---

### 7. Sparklines and Inline Visualizations

**Decision**: Use Unicode block characters (▁▂▃▄▅▆▇█) for sparklines and progress bars, with ASCII fallback for limited terminals.

**Rationale**:
- Unicode block characters provide 8 levels of visual intensity
- Widely supported in modern terminals
- Single-character width keeps tables compact
- Can detect Unicode support via `console.encoding`

**Implementation approach**:
- **Sparklines** (column headers):
  - Calculate histogram bins (8 bins) from column data
  - Map bin heights to block characters: min=▁, max=█
  - Render inline in column header (e.g., "Sales ▂▄▆▇▅▃▁")
  - Fallback: ASCII `_-=^` for non-Unicode terminals
- **Heat maps** (pivot tables):
  - Calculate relative intensity (0.0-1.0) per cell
  - Map to color gradient: cool (blue) → neutral (white) → hot (red)
  - In 16-color mode: use background colors only (8 levels)
  - Fallback: ASCII density characters: ` .:+=X#`

**Alternatives considered**:
- Braille patterns (⣿): More compact but harder to read
- Color-only heat maps: Fail in monochrome terminals
- External charting library: Too heavy for inline visualizations
- **Rejected because**: Block characters are readable, compact, and widely supported

**References**:
- Unicode Block Elements: https://en.wikipedia.org/wiki/Block_Elements
- Rich Console Encoding: https://rich.readthedocs.io/en/stable/console.html#encoding

---

### 8. Performance Monitoring and Adaptive Animation

**Decision**: Track animation frame times and automatically disable non-essential animations if <30fps detected over 5-second window.

**Rationale**:
- Some terminals (SSH, screen multiplexers) have high latency
- 60fps target may be unrealistic in all environments
- Constitution allows performance-based degradation (FR-040)
- Essential animations (focus indicators) stay enabled, decorative ones (fades, slides) disable

**Implementation approach**:
- Track frame timestamps in ring buffer (last 300 frames = 5s at 60fps)
- Calculate rolling average FPS every second
- If FPS < 30 for 3 consecutive seconds → disable decorative animations
- Decorative: transitions, fades, bounces
- Essential: focus indicators, validation feedback, cursor movement
- User can force-enable via config: `KITTIWAKE_FORCE_ANIMATIONS=1`

**Alternatives considered**:
- No adaptation: Poor experience on slow terminals
- User-only config: Requires manual tuning, most users won't adjust
- **Rejected because**: Automatic adaptation provides best default experience

**References**:
- Textual Refresh Rate: https://textual.textualize.io/api/app/#textual.app.App.refresh_rate
- Performance Best Practices: https://textual.textualize.io/guide/performance/

---

## Design Patterns from Acclaimed TUIs

### Claude Code / OpenCode Patterns

**Key observations**:
- **Status bar context**: Shows current mode, file info, and contextual shortcuts
- **Breadcrumb navigation**: Clearly shows location and operation history
- **Smooth focus transitions**: Subtle highlighting that doesn't distract
- **Progressive disclosure**: Advanced options hidden until needed (keep primary UI clean)

**Applied to kittiwake**:
- FR-020: Contextual keyboard shortcuts in status bar
- FR-019: Operation breadcrumb trail
- FR-011: Smooth focus transitions (<100ms)
- Modal forms: Simple defaults, expand for advanced options

### Other Acclaimed TUIs (lazygit, btop, k9s)

**Key observations**:
- **Visual hierarchy**: Bold headers, dimmed secondary info, bright accents for actions
- **Color semantic meaning**: Red=destructive, green=success, yellow=warning (universal)
- **Responsive feedback**: Every action has immediate visual confirmation
- **Help always accessible**: `?` key shows help overlay (non-intrusive)

**Applied to kittiwake**:
- FR-006: Typography hierarchy (bold headers, regular content)
- FR-004: Semantic color palette (error, warning, success)
- FR-011: Immediate visual feedback (<100ms)
- Existing help overlay from feature 001

---

## Summary of Key Decisions

| Area | Decision | Primary Benefit |
|------|----------|----------------|
| Animations | Textual's native system | Non-blocking, terminal-optimized |
| Colors | 3-tier palettes with detection | Works across all terminal types |
| Accessibility | coloraide + env var detection | WCAG AA compliance + reduced motion |
| Tooltips | Extended Textual Tooltip | Smart positioning, auto-wrapping |
| Progress | ProgressBar + overlay | Responsive, cancellable |
| Modals | Screen modal mode | Idiomatic Textual pattern |
| Sparklines | Unicode block chars | Compact, readable, widely supported |
| Performance | Adaptive animation | Automatic degradation on slow terminals |

All decisions prioritize Textual's built-in capabilities, maintaining constitution compliance (TUI-Native Design) while achieving modern visual polish.
