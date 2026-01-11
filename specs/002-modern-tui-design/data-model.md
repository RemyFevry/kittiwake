# Data Model: Modern Interactive TUI Design

**Feature**: 002-modern-tui-design  
**Date**: 2026-01-08  
**Purpose**: Define data structures and state management for visual design entities

## Overview

This feature introduces visual design entities that enhance the presentation layer of kittiwake. These entities manage theme configuration, animation state, contextual feedback, and progress tracking. All entities are ephemeral (in-memory only) and do not require persistence.

## Core Entities

### 1. ThemeConfig

**Purpose**: Represents complete visual theme configuration including colors, typography, spacing, and animation preferences.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `name` | `str` | Theme identifier | Required. Values: "light", "dark", "custom" |
| `color_system` | `ColorSystem` | Detected terminal capability | Required. Enum: TRUECOLOR, STANDARD, EIGHT_BIT, LEGACY_WINDOWS |
| `palette` | `ColorPalette` | Color definitions | Required. See ColorPalette structure |
| `typography` | `TypographyConfig` | Font styling rules | Required. See TypographyConfig structure |
| `spacing` | `SpacingConfig` | Layout spacing scale | Required. See SpacingConfig structure |
| `animation_enabled` | `bool` | Master animation toggle | Required. Default: True |
| `animation_duration_scale` | `float` | Animation speed multiplier | Required. Range: 0.1-2.0, Default: 1.0 |
| `reduced_motion` | `bool` | Accessibility mode flag | Required. Auto-detected from env vars |

**Relationships**:
- Owned by `App` instance (singleton)
- Referenced by all visual widgets for styling
- Updated when user switches themes or terminal is resized

**State Transitions**:
1. **Initialization**: Load default theme based on terminal color system
2. **Theme Switch**: User changes theme → validate new palette → update all widgets
3. **Accessibility Change**: Detect reduced motion env var → disable animations
4. **Terminal Resize**: Re-detect color system → adapt palette if changed

**Validation Rules**:
- All palette colors must meet WCAG AA contrast ratios (4.5:1 for text)
- `animation_duration_scale` must be positive
- If `reduced_motion=True`, `animation_enabled` must be False

---

### 2. ColorPalette

**Purpose**: Defines semantic color mappings with fallbacks for different terminal capabilities.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `primary` | `Color` | Main brand/accent color | Required. RGB/hex or ANSI name |
| `secondary` | `Color` | Secondary accents | Required |
| `background` | `Color` | Default background | Required |
| `surface` | `Color` | Widget surfaces | Required |
| `foreground` | `Color` | Default text color | Required |
| `muted` | `Color` | Dimmed/secondary text | Required |
| `accent` | `Color` | Interactive elements | Required |
| `error` | `Color` | Error states | Required. Red-ish |
| `warning` | `Color` | Warning states | Required. Yellow-ish |
| `success` | `Color` | Success states | Required. Green-ish |
| `border` | `Color` | Borders and dividers | Required |
| `shadow` | `Color` | Shadow overlays | Required. Semi-transparent |

**Validation Rules**:
- Contrast ratio `foreground:background` >= 4.5:1
- Contrast ratio `accent:background` >= 3.0:1
- Contrast ratio `error:background` >= 4.5:1
- Color values must be valid for detected `color_system`

**Color Resolution**:
- True color: Use RGB values directly
- 256-color: Map to nearest ANSI 256 color
- 16-color: Map to standard ANSI names (red, blue, green, etc.)

---

### 3. TypographyConfig

**Purpose**: Defines text styling rules for different UI elements.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `header_weight` | `str` | Header font weight | Required. Values: "normal", "bold" |
| `content_weight` | `str` | Content font weight | Required. Default: "normal" |
| `monospace` | `bool` | Use monospace for data | Required. Default: True |
| `text_align_numeric` | `str` | Numeric column alignment | Required. Values: "left", "right", "center" |
| `text_align_text` | `str` | Text column alignment | Required. Default: "left" |
| `text_align_date` | `str` | Date column alignment | Required. Default: "left" |

**Validation Rules**:
- Weights must be valid CSS font-weight values
- Alignment values must be one of: left, right, center

---

### 4. SpacingConfig

**Purpose**: Defines consistent spacing scale for layout and padding.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `unit` | `int` | Base spacing unit (cells) | Required. Default: 1 |
| `padding_vertical` | `int` | Vertical padding (units) | Required. Min: 1 |
| `padding_horizontal` | `int` | Horizontal padding (units) | Required. Min: 2 |
| `gap_small` | `int` | Small element gap (units) | Required. Default: 1 |
| `gap_medium` | `int` | Medium element gap (units) | Required. Default: 2 |
| `gap_large` | `int` | Large element gap (units) | Required. Default: 4 |

**Validation Rules**:
- All spacing values must be positive integers
- `padding_horizontal` >= `padding_vertical` (terminals are wider than tall)

---

### 5. AnimationState

**Purpose**: Tracks ongoing animation state for a single animated property.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `id` | `str` | Unique animation identifier | Required. UUID format |
| `target_widget` | `Widget` | Widget being animated | Required. Reference to Textual Widget |
| `property` | `str` | Property name being animated | Required. e.g., "opacity", "offset_x" |
| `start_value` | `float` | Starting value | Required |
| `end_value` | `float` | Target value | Required |
| `duration` | `float` | Animation duration (seconds) | Required. Range: 0.0-1.0 |
| `easing` | `str` | Easing function name | Required. Values: "linear", "in_out_cubic", "bounce_out" |
| `elapsed` | `float` | Time elapsed (seconds) | Required. Range: 0.0-duration |
| `progress` | `float` | Completion percentage | Computed. Range: 0.0-1.0 |
| `on_complete` | `Callable` | Callback on completion | Optional. Function reference |

**Relationships**:
- Managed by animation engine singleton
- Multiple AnimationStates can target same widget (different properties)
- Removed from engine when complete or cancelled

**State Transitions**:
1. **Created**: Animation starts → register with engine → begin ticking
2. **Running**: Each frame → increment elapsed → compute progress → update widget property
3. **Complete**: Progress reaches 1.0 → call `on_complete` → remove from engine
4. **Cancelled**: User action interrupts → remove from engine without completion callback

**Validation Rules**:
- `duration` must be positive (0.0 for instant transitions)
- `property` must exist on target widget
- `easing` must be a valid Textual easing function

---

### 6. ContextualInfo

**Purpose**: Represents contextual information displayed for UI elements (tooltips, stats, hints).

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `element_type` | `str` | Type of element | Required. Values: "cell", "column", "row", "panel" |
| `element_id` | `str` | Unique element identifier | Required |
| `primary_text` | `str` | Main information | Required. Max 200 chars |
| `secondary_details` | `list[str]` | Additional stats/hints | Optional. Max 5 items |
| `tooltip_content` | `str` | Full text for tooltips | Optional. Max 1000 chars |
| `display_timeout` | `float` | Auto-hide delay (seconds) | Optional. Default: 5.0 |
| `position` | `Position` | Preferred display position | Required. See Position structure |

**Relationships**:
- Created on-demand when user focuses/hovers element
- Cached for recently viewed elements (LRU cache, max 100 entries)
- Destroyed when element scrolls out of view or timeout expires

**Validation Rules**:
- `primary_text` cannot be empty
- `tooltip_content` wraps at terminal width - 4
- `display_timeout` must be positive

---

### 7. Position

**Purpose**: Represents 2D position for tooltip/overlay placement.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `row` | `int` | Row coordinate (0-based) | Required. Min: 0 |
| `column` | `int` | Column coordinate (0-based) | Required. Min: 0 |
| `anchor` | `str` | Anchor point | Required. Values: "top", "bottom", "left", "right", "center" |
| `offset_x` | `int` | Horizontal offset (cells) | Optional. Default: 0 |
| `offset_y` | `int` | Vertical offset (cells) | Optional. Default: 0 |

**Validation Rules**:
- Position must be within terminal bounds
- Anchor determines alignment relative to position

---

### 8. VisualFeedback

**Purpose**: Represents transient visual feedback for user actions (highlights, flashes, pulses).

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `id` | `str` | Unique feedback identifier | Required. UUID format |
| `feedback_type` | `str` | Type of feedback | Required. Values: "highlight", "flash", "pulse", "shake" |
| `target_widget` | `Widget` | Widget receiving feedback | Required. Reference to Textual Widget |
| `color_override` | `Color` | Custom color (optional) | Optional. Uses theme accent by default |
| `duration` | `float` | Feedback duration (seconds) | Required. Range: 0.1-2.0 |
| `intensity` | `float` | Effect intensity | Required. Range: 0.0-1.0 |
| `auto_dismiss` | `bool` | Auto-remove on completion | Required. Default: True |

**Relationships**:
- Managed by feedback engine singleton
- Multiple feedbacks can target same widget (visual composition)
- Removed when duration expires or dismissed manually

**State Transitions**:
1. **Created**: User action triggers feedback → register with engine → apply effect
2. **Active**: Effect renders each frame (e.g., pulsing opacity)
3. **Complete**: Duration expires → remove effect → clean up

**Validation Rules**:
- `duration` must be positive
- `intensity` affects opacity/color saturation
- `feedback_type` determines animation pattern

---

### 9. ProgressIndicator

**Purpose**: Represents long-running operation progress with status and cancellation support.

**Attributes**:

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `id` | `str` | Unique operation identifier | Required. UUID format |
| `operation_name` | `str` | User-facing description | Required. Max 80 chars |
| `progress_type` | `str` | Progress mode | Required. Values: "determinate", "indeterminate" |
| `percentage` | `float` | Completion percentage | Required if determinate. Range: 0.0-100.0 |
| `estimated_seconds` | `float` | ETA in seconds | Optional. Computed from progress rate |
| `cancellable` | `bool` | Can user cancel | Required. Default: True |
| `cancelled` | `bool` | Cancellation requested | Required. Default: False |
| `spinner_state` | `int` | Spinner frame index | Required if indeterminate. Range: 0-7 |

**Relationships**:
- Created when operation starts (>500ms expected)
- Updated by background async task via reactive properties
- Removed when operation completes or is cancelled

**State Transitions**:
1. **Created**: Operation starts → show progress indicator
2. **Updating**: Task updates progress → update UI (percentage, ETA)
3. **Cancelled**: User presses cancel key → set `cancelled=True` → task checks flag
4. **Complete**: Task finishes → remove indicator → show result

**Validation Rules**:
- Determinate progress must have `percentage` field
- Indeterminate progress must have `spinner_state` field
- `operation_name` must be concise and descriptive

---

## Entity Lifecycle Summary

| Entity | Lifecycle | Persistence | Owner |
|--------|-----------|-------------|-------|
| `ThemeConfig` | App lifetime | In-memory | App singleton |
| `ColorPalette` | Part of ThemeConfig | In-memory | ThemeConfig |
| `TypographyConfig` | Part of ThemeConfig | In-memory | ThemeConfig |
| `SpacingConfig` | Part of ThemeConfig | In-memory | ThemeConfig |
| `AnimationState` | Animation duration | In-memory | AnimationEngine |
| `ContextualInfo` | Element focus + timeout | Cached (LRU) | ContextualInfoManager |
| `VisualFeedback` | Feedback duration | In-memory | FeedbackEngine |
| `ProgressIndicator` | Operation duration | In-memory | ProgressManager |

All entities are ephemeral and recreated on app restart. No database or file persistence required.

## Interaction Patterns

### Pattern 1: Theme Application

```text
User switches theme
└─> App.set_theme(name)
    ├─> Load ThemeConfig from presets
    ├─> Validate ColorPalette contrast ratios
    ├─> Apply to all widgets via CSS variables
    └─> Trigger re-render
```

### Pattern 2: Animation Execution

```text
User action (e.g., open modal)
└─> Widget.animate(property, target, duration, easing)
    ├─> Create AnimationState
    ├─> Register with AnimationEngine
    ├─> Engine ticks each frame (16ms @ 60fps)
    │   ├─> Compute progress via easing function
    │   └─> Update widget property
    └─> On complete: call callback, remove state
```

### Pattern 3: Contextual Info Display

```text
User navigates to cell
└─> on_focus(cell)
    ├─> Check ContextualInfo cache
    ├─> If miss: compute stats (%, rank, etc.)
    ├─> Create ContextualInfo instance
    ├─> Display tooltip at smart position
    └─> Set auto-hide timer (5s)
```

### Pattern 4: Progress Tracking

```text
Operation starts (estimated >500ms)
└─> Create ProgressIndicator
    ├─> Show in overlay with spinner
    ├─> Task updates progress via reactive property
    │   └─> UI updates automatically (Textual reactive)
    ├─> If >3s: compute ETA and display
    └─> On complete/cancel: remove indicator
```

## Validation and Error Handling

### ThemeConfig Validation

```text
On theme load:
1. Validate all color contrast ratios
2. If any fail: log warning + use fallback colors
3. Verify spacing values are positive
4. Check animation_duration_scale in range
```

### AnimationState Validation

```text
On animation start:
1. Verify property exists on widget
2. Check duration is non-negative
3. Validate easing function name
4. If invalid: skip animation (instant transition)
```

### ContextualInfo Validation

```text
On info creation:
1. Truncate primary_text if >200 chars
2. Wrap tooltip_content at terminal width - 4
3. Clamp position to terminal bounds
4. If position invalid: use fallback (center screen)
```

### ProgressIndicator Validation

```text
On progress update:
1. Clamp percentage to 0-100 range
2. Validate estimated_seconds is positive
3. Check operation_name length
4. If invalid: show generic "Working..." message
```

## Performance Considerations

- **ThemeConfig**: Loaded once, cached for app lifetime
- **AnimationState**: Maximum 20 concurrent animations (performance limit)
- **ContextualInfo**: LRU cache (100 entries) to avoid recomputation
- **VisualFeedback**: Maximum 10 concurrent feedbacks (visual clarity)
- **ProgressIndicator**: One active indicator at a time (shown in overlay)

All entities use Textual's reactive properties for efficient UI updates (only re-render affected widgets).
