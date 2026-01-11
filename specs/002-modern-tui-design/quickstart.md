# Quickstart: Modern Interactive TUI Design

**Feature**: 002-modern-tui-design  
**Audience**: Developers implementing visual design enhancements  
**Prerequisites**: Feature 001 (TUI Data Explorer) implemented

## Overview

This quickstart guide demonstrates how to integrate modern visual design elements into kittiwake's TUI. It covers theme application, animation usage, contextual feedback, and accessibility features.

## 1. Theme Configuration

### Apply a Theme

```python
from kittiwake.ui.themes import ThemeConfig, load_preset

# Load preset theme (auto-detects terminal color capability)
theme = load_preset("dark")

# Apply to app
app.theme = theme

# Theme automatically adapts to terminal:
# - True color terminals: Full RGB palette
# - 256-color terminals: ANSI 256 equivalent
# - 16-color terminals: Standard ANSI colors
```

### Create Custom Theme

```python
from kittiwake.ui.themes import ThemeConfig, ColorPalette, TypographyConfig, SpacingConfig

# Define custom palette
palette = ColorPalette(
    primary="#3b82f6",      # Blue
    secondary="#8b5cf6",    # Purple
    background="#0f172a",   # Dark slate
    surface="#1e293b",
    foreground="#f1f5f9",   # Light text
    muted="#94a3b8",        # Gray
    accent="#06b6d4",       # Cyan
    error="#ef4444",        # Red
    warning="#f59e0b",      # Amber
    success="#10b981",      # Green
    border="#334155",
    shadow="#00000080"      # Semi-transparent
)

# Define typography
typography = TypographyConfig(
    header_weight="bold",
    content_weight="normal",
    monospace=True,
    text_align_numeric="right",
    text_align_text="left",
    text_align_date="left"
)

# Define spacing
spacing = SpacingConfig(
    unit=1,
    padding_vertical=1,
    padding_horizontal=2,
    gap_small=1,
    gap_medium=2,
    gap_large=4
)

# Create theme
custom_theme = ThemeConfig(
    name="custom",
    color_system=app.console.color_system,
    palette=palette,
    typography=typography,
    spacing=spacing,
    animation_enabled=True,
    animation_duration_scale=1.0,
    reduced_motion=False
)

# Validate contrast ratios (raises if WCAG AA not met)
custom_theme.validate_contrast()

# Apply theme
app.theme = custom_theme
```

## 2. Animations

### Animate Widget Properties

```python
from textual.widgets import Static

class FadeInWidget(Static):
    def on_mount(self) -> None:
        # Start with opacity 0
        self.styles.opacity = 0.0
        
        # Fade in over 200ms
        self.animate(
            "opacity", 
            1.0, 
            duration=0.2,
            easing="in_out_cubic"
        )

class SlideInModal(Screen):
    def on_mount(self) -> None:
        # Start off-screen
        self.styles.offset = (0, -10)
        
        # Slide in from top
        self.animate(
            "offset",
            (0, 0),
            duration=0.25,
            easing="out_expo"
        )
```

### Chain Animations

```python
class SequenceExample(Static):
    def on_mount(self) -> None:
        # Fade in, then slide
        self.styles.opacity = 0.0
        self.styles.offset = (0, -5)
        
        # First animation
        self.animate(
            "opacity",
            1.0,
            duration=0.15,
            on_complete=self.slide_in  # Callback
        )
    
    def slide_in(self) -> None:
        # Second animation
        self.animate(
            "offset",
            (0, 0),
            duration=0.2,
            easing="out_bounce"
        )
```

### Respect Reduced Motion

```python
from kittiwake.ui.accessibility import should_reduce_motion

class AccessibleAnimation(Static):
    def on_mount(self) -> None:
        if should_reduce_motion():
            # Instant transition
            self.styles.opacity = 1.0
        else:
            # Smooth animation
            self.styles.opacity = 0.0
            self.animate("opacity", 1.0, duration=0.2)
```

## 3. Contextual Information

### Show Tooltips

```python
from kittiwake.ui.feedback import show_tooltip
from textual.widgets import DataTable

class EnhancedDataTable(DataTable):
    def on_cell_highlighted(self, event) -> None:
        row, col = event.coordinate
        cell_value = self.get_cell_value(row, col)
        
        # Show tooltip if cell content is truncated
        if len(str(cell_value)) > self.column_width(col):
            show_tooltip(
                target=self,
                content=str(cell_value),
                position=(row, col),
                timeout=5.0
            )
```

### Display Contextual Stats

```python
from kittiwake.ui.feedback import ContextualInfo, show_contextual_info

def on_numeric_cell_focus(cell_value: float, column_data: list[float]) -> None:
    # Compute stats
    total = sum(column_data)
    percentage = (cell_value / total) * 100
    rank = sorted(column_data, reverse=True).index(cell_value) + 1
    
    # Create contextual info
    info = ContextualInfo(
        element_type="cell",
        element_id=f"cell-{row}-{col}",
        primary_text=f"{cell_value:,.2f}",
        secondary_details=[
            f"{percentage:.1f}% of total",
            f"Rank #{rank} in column"
        ],
        display_timeout=5.0
    )
    
    # Display in status bar
    show_contextual_info(info)
```

## 4. Visual Feedback

### Highlight User Actions

```python
from kittiwake.ui.feedback import VisualFeedback, apply_feedback

def on_row_selected(row_widget):
    # Flash selection feedback
    feedback = VisualFeedback(
        id=uuid4(),
        feedback_type="highlight",
        target_widget=row_widget,
        duration=0.3,
        intensity=0.8,
        auto_dismiss=True
    )
    apply_feedback(feedback)

def on_save_success(save_button):
    # Green flash on success
    feedback = VisualFeedback(
        id=uuid4(),
        feedback_type="flash",
        target_widget=save_button,
        color_override="#10b981",  # Green
        duration=0.5,
        intensity=1.0,
        auto_dismiss=True
    )
    apply_feedback(feedback)
```

### Error Shake Animation

```python
def on_validation_error(input_field):
    # Shake input field
    feedback = VisualFeedback(
        id=uuid4(),
        feedback_type="shake",
        target_widget=input_field,
        color_override="#ef4444",  # Red
        duration=0.4,
        intensity=0.6,
        auto_dismiss=True
    )
    apply_feedback(feedback)
```

## 5. Progress Indicators

### Show Operation Progress

```python
from kittiwake.ui.feedback import ProgressIndicator, show_progress, update_progress

async def long_running_operation():
    # Show indeterminate progress
    progress_id = show_progress(
        operation_name="Loading dataset...",
        progress_type="indeterminate",
        cancellable=True
    )
    
    try:
        # Simulate work
        await asyncio.sleep(2)
        
        # Switch to determinate progress
        for i in range(100):
            if check_cancelled(progress_id):
                return  # User cancelled
            
            update_progress(
                progress_id,
                percentage=i + 1,
                progress_type="determinate"
            )
            await asyncio.sleep(0.05)
    
    finally:
        # Remove progress indicator
        hide_progress(progress_id)
```

### Progress with ETA

```python
async def large_file_load():
    progress_id = show_progress(
        operation_name="Loading 1GB file...",
        progress_type="determinate",
        cancellable=True
    )
    
    start_time = time.time()
    
    for i in range(100):
        # Update progress
        elapsed = time.time() - start_time
        estimated_total = elapsed / (i + 1) * 100
        estimated_remaining = estimated_total - elapsed
        
        update_progress(
            progress_id,
            percentage=i + 1,
            estimated_seconds=estimated_remaining
        )
        
        await asyncio.sleep(0.1)
    
    hide_progress(progress_id)
```

## 6. Modal Dialogs

### Create Custom Modal

```python
from kittiwake.ui.widgets import ModalDialog
from textual.widgets import Input, Select, Button

class FilterModal(ModalDialog):
    """Modal for configuring filters."""
    
    def compose(self):
        yield Static("Filter Configuration", classes="modal-title")
        yield Input(placeholder="Column name", id="column-input")
        yield Select(
            options=[("equals", "="), ("greater", ">"), ("less", "<")],
            id="operator-select"
        )
        yield Input(placeholder="Value", id="value-input")
        yield Button("Apply", variant="primary", id="apply-btn")
        yield Button("Cancel", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-btn":
            # Validate inputs
            if not self.validate():
                # Show validation error
                self.show_error("All fields are required")
                return
            
            # Apply filter
            self.dismiss(self.get_filter_config())
        else:
            # Cancel
            self.dismiss(None)
    
    def validate(self) -> bool:
        # Check required fields
        column = self.query_one("#column-input", Input).value
        value = self.query_one("#value-input", Input).value
        return bool(column) and bool(value)

# Usage
async def show_filter_dialog():
    result = await app.push_screen_wait(FilterModal())
    if result:
        apply_filter(result)
```

## 7. Accessibility Features

### Check Contrast Ratios

```python
from kittiwake.ui.accessibility import check_contrast_ratio

# Validate color pair
fg_color = "#ffffff"
bg_color = "#0f172a"

ratio = check_contrast_ratio(fg_color, bg_color)
if ratio < 4.5:
    print(f"Warning: Contrast ratio {ratio:.2f} fails WCAG AA (4.5:1)")
```

### Color-Blind Friendly Alternatives

```python
from kittiwake.ui.accessibility import get_colorblind_palette

# Get alternative palette for protanopia
cb_palette = get_colorblind_palette("protanopia", theme.palette)

# Apply to theme
theme.palette = cb_palette
```

## 8. Performance Monitoring

### Track Animation Performance

```python
from kittiwake.ui.animation import AnimationEngine

# Get engine instance
engine = AnimationEngine.instance()

# Check current FPS
current_fps = engine.get_average_fps()

if current_fps < 30:
    print("Low FPS detected, consider disabling decorative animations")
    app.theme.animation_enabled = False
```

## Common Patterns

### Pattern: Fade-in Data Table

```python
class DataView(Static):
    def on_mount(self) -> None:
        # Initial state
        self.styles.opacity = 0.0
        
        # Fade in table
        table = self.query_one(DataTable)
        table.animate("opacity", 1.0, duration=0.2)
```

### Pattern: Modal with Blur Background

```python
class BlurredModal(ModalDialog):
    DEFAULT_CSS = """
    BlurredModal {
        background: $surface 80%;
        border: solid $border;
        width: 60%;
        height: auto;
        align: center middle;
    }
    """
    
    def on_mount(self) -> None:
        # Slide in from center
        self.styles.opacity = 0.0
        self.styles.offset = (0, -5)
        
        self.animate("opacity", 1.0, duration=0.15)
        self.animate("offset", (0, 0), duration=0.2, easing="out_expo")
```

### Pattern: Status Bar with Contextual Shortcuts

```python
class ContextAwareStatusBar(Static):
    def update_context(self, mode: str) -> None:
        shortcuts = {
            "view": "↑↓ Navigate | / Filter | ? Help",
            "filter": "Enter Apply | Esc Cancel | Tab Next Field",
            "modal": "Enter Confirm | Esc Close"
        }
        
        self.update(shortcuts.get(mode, ""))
```

## Best Practices

1. **Always respect reduced motion**: Check `should_reduce_motion()` before animating
2. **Keep animations short**: Max 300ms for UI transitions
3. **Use semantic colors**: error=red, warning=yellow, success=green
4. **Validate contrast**: All color pairs must meet WCAG AA (4.5:1)
5. **Provide keyboard navigation**: Every modal must support Tab/Shift+Tab and ESC
6. **Show progress for >500ms operations**: Users expect feedback
7. **Test in 16-color terminals**: Ensure graceful degradation

## Next Steps

- Read [data-model.md](./data-model.md) for entity details
- Review [contracts/](./contracts/) for JSON schemas
- Implement Phase 2 tasks (see `/speckit.tasks` command output)
