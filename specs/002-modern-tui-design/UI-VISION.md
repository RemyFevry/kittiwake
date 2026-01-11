# Kittiwake UI Vision & Roadmap
## World-Class Data Analysis TUI

**Version**: 1.0
**Date**: 2026-01-11
**Goal**: Transform kittiwake into the definitive terminal-based data analysis tool

---

## Executive Summary

Kittiwake has a **solid foundation** with 51 source files implementing core data operations (filter, aggregate, pivot, join) and a functional sidebar-based UI. This document charts the path to becoming a **world-class data analysis TUI** by:

1. **Learning from the best**: VisiData's speed, Excel's power-user features, csvlens' clarity
2. **Leveraging Textual**: Using all 30+ built-in widgets plus custom components
3. **Focusing on workflows**: Keyboard-first, discoverable, efficient
4. **Modern polish**: Animations, themes, contextual feedback, visualizations

---

## Current State Assessment

### ✅ What Works Well

**Data Operations** (14 operations implemented):
- Filter, aggregate, pivot, join, sort, search
- Queue-based execution (lazy/eager modes)
- Multi-dataset tabs (up to 10)
- Undo/redo with checkpoints
- DuckDB persistence for analysis/workflows

**UI Architecture**:
- Clean sidebar pattern (left overlay + right push)
- Type-colored column headers with icons
- Pagination (500-1000 rows)
- Split-pane comparison mode
- Modular, maintainable code

### ⚠️ What Needs Enhancement

**Missing Core Features**:
- No in-cell formulas or expressions
- Limited string/date transformations
- No window functions (rank, lag, lead)
- No data profiling/quality reports
- No visualizations (charts, sparklines)

**UI Gaps**:
- Status bar is embedded Label, not standalone widget
- No column freeze/pinning
- No multi-level sorting UI
- No find & replace
- Pagination lacks "jump to page X"
- Filter UI limited to single conditions

**Visual Design**:
- No theme system (hardcoded Textual colors)
- No animations or transitions
- No tooltips or contextual help
- No progress indicators for long operations
- No accessibility features (reduced motion, color-blind modes)

---

## Vision: The Ultimate Data Analysis TUI

### Guiding Principles

1. **Fast Like csvlens**: Instant file loading, responsive scrolling, quick previews
2. **Powerful Like VisiData**: Complex operations, extensibility, format support
3. **Intuitive Like Excel**: Discoverable features, helpful UI, familiar patterns
4. **Modern Like Claude Code**: Smooth animations, beautiful typography, polish

### User Experience Goals

**5-Second Discovery**: New users open a CSV and understand how to filter/sort/pivot within 5 seconds

**Keyboard Flow State**: Power users chain operations without touching the mouse

**Visual Clarity**: Data types, row states, column relationships visible at a glance

**Performance**: 60fps animations, <100ms feedback, millions of rows handled gracefully

---

## Textual Widget Capabilities

### Built-in Widgets Available

| Widget | Use Case in Kittiwake |
|--------|------------------------|
| **DataTable** | ✅ Already used (dataset_table.py) - Main data display |
| **TabbedContent** | ✅ Already used (dataset tabs) - Multi-dataset workspace |
| **Tree** | 🆕 Column picker, hierarchical pivot display |
| **ListView** | ✅ Already used (operations sidebar) - Operation queue |
| **SelectionList** | 🆕 Multi-column selection, filter builder |
| **OptionList** | 🆕 Quick actions menu from headers |
| **TextArea** | 🆕 Formula editor, expression builder |
| **MaskedInput** | 🆕 Date/number format input validation |
| **RadioSet** | ✅ Already used (join types) - Mutually exclusive options |
| **Checkbox** | ✅ Already used (aggregate functions) |
| **ProgressBar** | 🆕 Long-running operation progress |
| **LoadingIndicator** | ✅ Already used (loading modal) |
| **Sparkline** | 🆕 Inline data distribution in headers |
| **Collapsible** | 🆕 Grouped operations, collapsed sidebar sections |
| **MarkdownViewer** | 🆕 Help system, operation documentation |
| **RichLog** | 🆕 Operation history with syntax highlighting |
| **Toast** | 🆕 Non-intrusive notifications |
| **Tooltip** | 🆕 Contextual help everywhere |
| **DirectoryTree** | 🆕 File browser for loading datasets |
| **Digits** | 🆕 Large metric display in summary panels |

### Custom Widgets Needed

**High Priority**:
- **StatusBarPro**: Multi-section status (dataset info, shortcuts, context)
- **ColumnManager**: Show/hide, reorder, freeze columns with drag-drop
- **FilterBuilder**: Visual AND/OR logic with multiple conditions
- **FormulaBar**: Excel-like formula editor with autocomplete
- **DataProfiler**: Column statistics, type distribution, null counts
- **MiniChart**: Inline histograms, bar charts, heatmaps

**Medium Priority**:
- **BreadcrumbTrail**: Operation chain visualization
- **ComparisonView**: Side-by-side dataset diff
- **QueryBuilder**: Visual SQL-like query construction
- **ExpressionEditor**: Python expression builder with field picker
- **ConditionalFormatter**: Cell highlighting rules

**Nice-to-Have**:
- **CorrelationMatrix**: Heatmap of numeric column correlations
- **TimeSeriesPreview**: Line chart for date-indexed data
- **GeoViewer**: ASCII map for geographic data
- **RegexTester**: Live regex pattern testing

---

## Feature Roadmap by Priority

### 🔴 P0: Foundation (Weeks 1-2)

**Theme System**
- [ ] ColorPalette with 3-tier support (true color, 256, 16)
- [ ] Light/dark theme presets with WCAG AA validation
- [ ] Theme switching (Ctrl+T)
- [ ] Terminal capability detection

**Animation Engine**
- [ ] AnimationState tracking with performance monitoring
- [ ] Easing functions (ease-in-out, spring, etc.)
- [ ] Transition patterns (fade, slide, blur)
- [ ] Adaptive animation (auto-disable at <30fps)
- [ ] Reduced motion support

**StatusBar Widget** (Extract from DatasetTable)
- [ ] Dataset info section (name, rows, filters)
- [ ] Contextual shortcuts section (changes per mode)
- [ ] Progress/message section
- [ ] Integrate with main_screen.py

### 🟠 P1: Core UI Enhancements (Weeks 3-4)

**Column Management**
- [ ] ColumnManager widget with Tree view
- [ ] Show/hide columns with checkboxes
- [ ] Reorder columns with keyboard (Alt+Left/Right)
- [ ] Freeze columns (left anchor, scroll independent)
- [ ] Column width adjustment (Auto-fit, Manual)
- [ ] Keyboard shortcut: Ctrl+Shift+C

**Enhanced Filtering**
- [ ] FilterBuilder widget with AND/OR logic
- [ ] Multi-condition support (up to 10 conditions per group)
- [ ] Condition groups (nested AND/OR)
- [ ] Quick filter from cell value (right-click context)
- [ ] Filter templates (save/load common filters)
- [ ] Visual filter chips showing active filters

**Sorting Improvements**
- [ ] Multi-level sort UI (priority order 1-5)
- [ ] Sort direction indicators in headers (▲▼)
- [ ] Keyboard shortcuts: Alt+↑/↓ for column sort
- [ ] Clear all sorts (Escape)

**Search & Replace**
- [ ] Find dialog (Ctrl+F) with regex support
- [ ] Replace dialog (Ctrl+H) with preview
- [ ] Find in column vs all columns
- [ ] Highlight all matches
- [ ] Navigate matches (F3/Shift+F3)

### 🟡 P2: Data Operations (Weeks 5-6)

**Formula Bar** (Excel-like)
- [ ] FormulaBar widget at top of screen
- [ ] Syntax: `=expr(column1, column2)`
- [ ] Autocomplete for column names
- [ ] Function library: string, math, date, logical
- [ ] Error highlighting with helpful messages
- [ ] Formula history (recent expressions)

**Expression Builder**
- [ ] ExpressionEditor modal for complex operations
- [ ] Field picker (click to insert column)
- [ ] Function palette (categorized: string, date, math, agg)
- [ ] Live preview with sample rows
- [ ] Save expressions as custom operations

**Window Functions**
- [ ] WindowSidebar for lag, lead, row_number, rank
- [ ] Partition by columns (multi-select)
- [ ] Order by columns
- [ ] Window frame specification (rows/range)
- [ ] Preview impact before execution

**String Transformations**
- [ ] StringSidebar with operations:
  - Split column (delimiter, into N columns)
  - Extract (regex capture groups)
  - Replace (find/replace with regex)
  - Case (upper, lower, title, capitalize)
  - Trim (leading, trailing, all whitespace)
  - Pad (left, right, center)
- [ ] Batch apply to multiple columns

**Date/Time Operations**
- [ ] DateSidebar for temporal operations:
  - Extract (year, month, day, hour, minute, second, dayofweek)
  - Format (custom strftime patterns)
  - Arithmetic (add/subtract days, hours, etc.)
  - Parse (smart date parsing from strings)
- [ ] Date range filtering with calendar picker

### 🟢 P3: Visualization & Insights (Weeks 7-8)

**Inline Visualizations**
- [ ] Sparklines in column headers (distribution preview)
- [ ] MiniChart widget for aggregation results
- [ ] Heatmap mode for pivot tables (color gradient)
- [ ] Bar charts in cells (% of max visualization)
- [ ] Toggle visualizations (Ctrl+V)

**Data Profiling Panel**
- [ ] DataProfiler widget (overlay panel, Ctrl+I)
- [ ] Per-column statistics:
  - Numeric: min, max, mean, median, std, quartiles
  - String: unique count, most common, avg length
  - Date: min, max, range
  - All: null count, null %, distinct count
- [ ] Type distribution (auto-detected types)
- [ ] Missing data heatmap
- [ ] Outlier detection (IQR method)

**Summary Visualizations**
- [ ] Histogram viewer (binned frequency)
- [ ] Scatter plot (2-column ASCII art)
- [ ] Box plot (quartile visualization)
- [ ] Correlation matrix (heatmap)

**Conditional Formatting**
- [ ] ConditionalFormatter modal
- [ ] Rules: value-based, formula-based
- [ ] Styles: background color, text color, bold, icon
- [ ] Gradient scales (min→max color ramp)
- [ ] Top N / Bottom N highlighting
- [ ] Data bars in cells

### 🔵 P4: Advanced Features (Weeks 9-10)

**Query Builder** (Visual SQL)
- [ ] QueryBuilder widget (SQL-like UI)
- [ ] Drag-drop columns to SELECT
- [ ] Visual WHERE builder (same as FilterBuilder)
- [ ] GROUP BY with aggregations
- [ ] HAVING clause support
- [ ] ORDER BY with multi-column
- [ ] LIMIT/OFFSET
- [ ] Export to SQL query text

**Workflow Enhancements**
- [ ] Workflow templates (common analysis patterns)
- [ ] Parameterized workflows (variables)
- [ ] Workflow branching (conditional logic)
- [ ] Workflow visualization (flowchart)
- [ ] Schedule workflows (cron-like)

**Collaboration Features**
- [ ] Export to Excel with formatting
- [ ] Export to Google Sheets (via clipboard)
- [ ] Generate shareable HTML report
- [ ] Export to SQL (CREATE TABLE + INSERT)
- [ ] Export to dbt models

**Performance Tools**
- [ ] Query optimizer hints
- [ ] Memory usage monitor (live gauge)
- [ ] Operation profiler (timing breakdown)
- [ ] Lazy evaluation visualizer (show query plan)
- [ ] Cache manager (intermediate results)

### 🟣 P5: Power User Features (Weeks 11-12)

**Advanced Keyboard Shortcuts**
- [ ] Vim-style navigation mode (hjkl)
- [ ] Custom keybindings (user config)
- [ ] Macro recording (record sequence, replay)
- [ ] Quick command palette (Ctrl+P)
- [ ] Jump to row by number (Ctrl+G)

**Comparison & Diff**
- [ ] ComparisonView widget (side-by-side)
- [ ] Cell-level diff highlighting (changed, added, removed)
- [ ] Schema diff (column changes)
- [ ] Row matching strategies (key columns vs row order)
- [ ] Export diff report

**Data Quality**
- [ ] Duplicate detection (fuzzy matching)
- [ ] Schema validation (expected vs actual)
- [ ] Constraint checker (custom rules)
- [ ] Data lineage (track transformations)
- [ ] Quality score per column

**Extensibility**
- [ ] Plugin system (Python modules)
- [ ] Custom operation types
- [ ] Custom exporters
- [ ] Custom visualizations
- [ ] API for programmatic access

---

## Textual Widget Mapping

### Immediate Use (No Custom Work)

| Need | Textual Widget | Implementation |
|------|----------------|----------------|
| Progress for long ops | ProgressBar | Wrap narwhals_ops operations |
| Operation notifications | Toast | Success/error feedback |
| Contextual help | Tooltip | On column headers, buttons |
| File browser | DirectoryTree | Load dataset dialog |
| Help system | MarkdownViewer | Keyboard shortcuts, guides |
| Operation history | RichLog | Syntax-highlighted log |
| Metric display | Digits | Large numbers in summary |
| Grouped sidebars | Collapsible | Collapse sidebar sections |

### Custom Widget Development

**StatusBarPro** (extends Container):
```python
class StatusBarPro(Container):
    """Three-section status bar: Info | Shortcuts | Context"""

    DEFAULT_CSS = """
    StatusBarPro {
        dock: bottom;
        height: 3;
        background: $panel;
        layout: horizontal;
    }
    #info { width: 40%; }
    #shortcuts { width: 40%; }
    #context { width: 20%; }
    """

    def compose(self):
        yield Label(id="info")      # "sales.csv | 1.2M rows | Filtered: 45K"
        yield Label(id="shortcuts") # "↑↓ Navigate | / Filter | ? Help"
        yield Label(id="context")   # "Row 1,234 | Col 12"
```

**ColumnManager** (extends Container with Tree):
```python
class ColumnManager(Container):
    """Column visibility, order, freeze control"""

    def compose(self):
        yield Tree("Columns")  # Checkbox tree
        yield Button("Freeze Selected")
        yield Button("Auto-fit Widths")
```

**FilterBuilder** (extends Container):
```python
class FilterBuilder(Container):
    """Visual AND/OR filter construction"""

    # Nested groups: [Group1 AND Group2] OR [Group3]
    # Each group: [cond1 AND cond2 AND cond3]

    def compose(self):
        yield ListView(id="filter_groups")
        yield Horizontal(
            Button("+ AND Group"),
            Button("+ OR Group"),
            Button("Clear All")
        )
```

**FormulaBar** (extends Container with TextArea):
```python
class FormulaBar(Container):
    """Excel-like formula editor"""

    DEFAULT_CSS = """
    FormulaBar {
        dock: top;
        height: 3;
        background: $surface;
    }
    """

    def compose(self):
        yield Label("fx", classes="formula-icon")
        yield TextArea(id="formula_input")  # Autocomplete enabled
        yield Button("✓", variant="success")
```

**DataProfiler** (extends Container):
```python
class DataProfiler(Container):
    """Column statistics and data quality"""

    def compose(self):
        yield TabbedContent(
            TabPane("Statistics", StatisticsPanel()),
            TabPane("Distribution", HistogramPanel()),
            TabPane("Quality", QualityPanel()),
            TabPane("Sample", SamplePanel())
        )
```

**MiniChart** (extends Static with custom render):
```python
class MiniChart(Static):
    """Inline bar chart, sparkline, heatmap"""

    def render_line(self, y: int) -> Strip:
        # High-performance line-by-line rendering
        # Use Unicode block chars: ▁▂▃▄▅▆▇█
        # Or ASCII: _-=^#
        pass
```

---

## UI Patterns & Workflows

### Pattern 1: Quick Filter from Cell

**User Flow**:
1. Navigate to cell with cursor
2. Press **Ctrl+Shift+F**
3. Context menu appears:
   - Filter column = this value
   - Filter column != this value
   - Filter column > this value (numeric)
   - Filter column contains this (string)
4. Select option → filter applied instantly

**Implementation**:
- Detect cursor position in DatasetTable
- Extract cell value and column name
- Show OptionList with context-appropriate operators
- Build filter Operation and execute

### Pattern 2: Column Manager Workflow

**User Flow**:
1. Press **Ctrl+Shift+C**
2. ColumnManager sidebar slides in (left overlay)
3. Tree view shows all columns with checkboxes
4. User actions:
   - Uncheck to hide columns
   - Drag to reorder (keyboard: Alt+Up/Down)
   - Select + "Freeze" to anchor left
5. Press **Escape** → sidebar dismisses with smooth animation

**Implementation**:
- Tree widget with `can_focus_children=True`
- Custom drag-drop via keyboard (Alt + arrows)
- Update DatasetTable column visibility
- Persist column state per dataset

### Pattern 3: Formula Bar Expression

**User Flow**:
1. Press **Ctrl+Shift+=** to focus formula bar
2. Type: `=upper(name)`
3. Autocomplete suggests column names
4. Preview shows: "John" → "JOHN" for sample rows
5. Press **Enter** → new column added with formula result

**Implementation**:
- TextArea with autocomplete (column names, functions)
- Parse expression using Python AST
- Execute in sandbox (same as operation_builder)
- Show preview in modal before applying
- Store formula for re-execution on data changes

### Pattern 4: Multi-Level Sort

**User Flow**:
1. Click column header (or press **Alt+↑** on column)
2. Header shows ▲ indicator (ascending)
3. Click another header (or Alt+↑ on different column)
4. Headers show ①▲ and ②▲ (sort priority)
5. Press **Escape** → clear all sorts

**Implementation**:
- Track sort order in list: [(col, dir), (col, dir)]
- Update DataTable header renderable with indicators
- Apply sort via narwhals: `df.sort(col1, col2)`
- Animation: cross-fade rows on sort

### Pattern 5: Data Profiling

**User Flow**:
1. Press **Ctrl+I** → DataProfiler panel slides in (right overlay)
2. See tabs: Statistics | Distribution | Quality | Sample
3. Statistics tab shows:
   - Column list (select to see stats)
   - For selected column: min, max, mean, median, std, quartiles
   - Null count, distinct count
   - Type distribution
4. Distribution tab: ASCII histogram
5. Quality tab: Missing data heatmap, outliers
6. Sample tab: Random 100 rows

**Implementation**:
- DataProfiler widget with TabbedContent
- Compute stats lazily (on tab activate)
- Use Narwhals aggregations
- Cache results (invalidate on data change)
- Sparkline widget for distribution

---

## Animation & Feedback Strategy

### Micro-Interactions (100-200ms)

| Interaction | Animation | Feel |
|-------------|-----------|------|
| Row highlight | Fade background color | Smooth, confident |
| Button press | Scale down → up | Tactile feedback |
| Checkbox toggle | Check mark draws in | Satisfying |
| Modal open | Fade + scale from 90% → 100% | Elegant entrance |
| Sidebar slide | Ease-out from left/right | Purposeful reveal |
| Toast appear | Slide up from bottom + fade | Non-intrusive |
| Filter chip | Pop in with bounce | Playful confirmation |

### Macro-Transitions (200-300ms)

| Transition | Animation | Purpose |
|------------|-----------|---------|
| Tab switch | Cross-fade content | Seamless context change |
| Data update | Fade out old → Fade in new rows | Clear state change |
| Sort rows | Stagger fade (cascade effect) | Show data movement |
| Theme switch | Color lerp across UI | Unified experience |
| Split pane toggle | Width animate with easing | Spatial clarity |

### Progress Feedback

| Duration | Feedback |
|----------|----------|
| <100ms | None (feels instant) |
| 100-500ms | Cursor change + subtle pulse |
| 500ms-3s | ProgressBar (indeterminate spinner) |
| >3s | ProgressBar with % and ETA |
| >10s | ProgressBar + Cancel button |

### Performance Monitoring

```python
# AnimationEngine auto-throttles based on FPS
if avg_fps < 30:
    disable_decorative_animations()  # Keep essential only
if avg_fps < 20:
    disable_all_animations()  # Instant transitions
```

---

## Accessibility Requirements

### WCAG AA Compliance

**Color Contrast**:
- Normal text: 4.5:1 minimum
- Large text (18pt+): 3.1 minimum
- UI components: 3:1 minimum
- Validate with coloraide library

**Reduced Motion**:
- Detect: `REDUCE_MOTION` env var or `NO_MOTION`
- Fallback: Instant transitions (0ms duration)
- User override: `KITTIWAKE_FORCE_ANIMATIONS=1`

**Color Blindness**:
- Protanopia mode (red-blind)
- Deuteranopia mode (green-blind)
- Tritanopia mode (blue-blind)
- Never use color alone (add icons/patterns)

**Keyboard Navigation**:
- All features accessible via keyboard
- Visible focus indicators (border or background)
- Logical tab order
- Skip navigation shortcuts

### Terminal Compatibility

**Color Support Detection**:
- True color (16.7M colors): Best experience
- 256-color: Acceptable gradients
- 16-color: High contrast mode
- Monochrome: Patterns instead of colors

**Unicode Fallbacks**:
- Sparklines: ▁▂▃▄▅▆▇█ → _-=^# (ASCII)
- Icons: ✓✗⚠ → [Y][N][!]
- Box drawing: ┌─┐ → +--+

**Size Constraints**:
- Minimum: 80x24 (show warning + basic UI)
- Recommended: 120x40
- Optimal: 160x50+

---

## Implementation Strategy

### Phase 0: Foundation (Weeks 1-2)

**Goal**: Build the plumbing that everything else needs

- [x] Create `ui/` hierarchy
- [x] Implement theme system (colors, typography, spacing)
- [x] Implement animation engine with performance monitoring
- [x] Implement accessibility features (reduced motion, contrast check, color-blind modes)
- [ ] Extract StatusBarPro widget from DatasetTable
- [ ] Integrate theme system into KittiwakeApp
- [ ] Add animation support to DatasetTable and modals

### Phase 1: Core UX (Weeks 3-4)

**Goal**: Fix the biggest pain points first

- [ ] ColumnManager widget (show/hide, reorder, freeze)
- [ ] Enhanced FilterBuilder (AND/OR logic, multi-condition)
- [ ] Multi-level sort UI with indicators
- [ ] Find & Replace dialog
- [ ] Tooltips on column headers and buttons
- [ ] Toast notifications for operations

### Phase 2: Data Operations (Weeks 5-6)

**Goal**: Close the feature gap with Excel/VisiData

- [ ] FormulaBar widget with autocomplete
- [ ] Window functions sidebar (lag, lead, rank)
- [ ] String transformations sidebar
- [ ] Date/time operations sidebar
- [ ] Expression editor with live preview

### Phase 3: Insights (Weeks 7-8)

**Goal**: Make data patterns visible

- [ ] Sparklines in column headers
- [ ] DataProfiler panel
- [ ] Conditional formatting
- [ ] Heatmap mode for pivot tables
- [ ] Summary visualizations (histogram, box plot)

### Phase 4: Power Features (Weeks 9-10)

**Goal**: Advanced workflows for power users

- [ ] Query builder (visual SQL)
- [ ] Comparison view (dataset diff)
- [ ] Workflow templates
- [ ] Performance monitoring tools
- [ ] Enhanced export options

### Phase 5: Polish (Weeks 11-12)

**Goal**: Refinement and edge cases

- [ ] Macro recording
- [ ] Custom keybindings
- [ ] Plugin system
- [ ] Comprehensive help system
- [ ] Performance optimization
- [ ] Accessibility audit

---

## Success Metrics

### Quantitative

- **Performance**: 60fps maintained during all animations
- **Responsiveness**: <100ms feedback for all user actions
- **Contrast**: 100% of text meets WCAG AA (4.5:1)
- **Coverage**: 100% of features accessible via keyboard
- **Compatibility**: Works on 16-color, 256-color, true color terminals

### Qualitative

- **5-Second Test**: New users can filter/sort within 5 seconds
- **Power User Flow**: Chain 5 operations without leaving keyboard
- **Discoverability**: 80% of features discoverable without documentation
- **Beauty**: "Wow" reaction on first launch (theme, animations)
- **Reliability**: Zero crashes in 1-hour analysis session

---

## Technical Architecture

### Component Hierarchy

```
KittiwakeApp (app.py)
├── ThemeManager (ui/themes/)
├── AnimationEngine (ui/animation/)
└── MainScreen (screens/main_screen.py)
    ├── Header (Textual built-in)
    ├── FormulaBar (NEW: ui/widgets/formula_bar.py)
    ├── Horizontal (content_area)
    │   ├── ColumnManager (NEW: overlay left)
    │   ├── FilterBuilder (NEW: overlay left)
    │   ├── DatasetTabs (existing)
    │   ├── DatasetTable (existing, enhanced)
    │   ├── DataProfiler (NEW: overlay right)
    │   └── OperationsSidebar (existing)
    ├── StatusBarPro (NEW: ui/widgets/status_bar.py)
    └── Footer (Textual built-in)
```

### Data Flow Enhancement

```
User Input (keyboard/mouse)
    ↓
Event Handler (MainScreen, Widget)
    ↓
Animation (if UI change)
    ↓
Operation Builder (if data operation)
    ↓
Validation & Preview
    ↓
Execution (lazy queue or eager apply)
    ↓
Narwhals Operation (sandboxed)
    ↓
Result
    ↓
UI Update (with animation)
    ↓
Status Bar Update
    ↓
Toast Notification (if significant)
```

### State Management

**Current**: Reactive variables in widgets + DatasetSession

**Enhanced**:
- UI state: Theme, column visibility, sort order, filters
- Data state: Frame, operations queue, execution mode
- Preference state: Keybindings, animation settings, color mode
- Session state: Persist to `~/.kittiwake/session.json`

---

## Open Questions

1. **Formula language**: Python expressions vs custom DSL?
   - **Recommendation**: Python (leverage existing sandbox, user familiarity)

2. **Plugin system**: Load from `~/.kittiwake/plugins/`?
   - **Recommendation**: Yes, use Python importlib for dynamic loading

3. **Performance budget**: Max animation budget per frame?
   - **Recommendation**: 16ms (60fps) - AnimationEngine enforces

4. **Keybinding conflicts**: How to handle conflicts with terminal emulator?
   - **Recommendation**: Detect conflicts, show warning, offer alternatives

5. **Large datasets**: Lazy evaluation visualization?
   - **Recommendation**: Show query plan, estimated rows, execution time

6. **Export formats**: What's most important?
   - **Recommendation**: Priority: Excel > SQL > Jupyter > HTML > Google Sheets

---

## References & Inspiration

### Tools Analyzed

- **VisiData**: [visidata.org](https://www.visidata.org/) - Multi-format support, keyboard-first design
- **csvlens**: [GitHub](https://github.com/YS-L/csvlens) - Fast viewing, clean UI
- **Excel**: [Keyboard Shortcuts Guide](https://chandoo.org/wp/35-tips-data-analysis-in-excel/) - Power user workflows

### Textual Documentation

- **Widgets Guide**: [textual.textualize.io/guide/widgets/](https://textual.textualize.io/guide/widgets/)
- **Custom Widgets**: [textual.textualize.io](https://textual.textualize.io/)

### Design Principles

- **Keyboard-First**: Every feature accessible via keyboard
- **Progressive Disclosure**: Simple by default, power available
- **Immediate Feedback**: <100ms for all interactions
- **Undo-Friendly**: All operations reversible
- **Fail Gracefully**: Errors are helpful, not punishing

---

## Next Steps

1. **Review this vision** with stakeholders
2. **Prioritize features** based on user needs
3. **Update spec.md** to reflect chosen features
4. **Revise tasks.md** with actual file paths and priorities
5. **Begin Phase 0** implementation (theme + animation foundation)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-11
**Maintained By**: Kittiwake Development Team
