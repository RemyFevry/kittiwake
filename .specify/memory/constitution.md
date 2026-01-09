<!--
Sync Impact Report - Constitution Update
Version: 1.0.0 → 1.1.0
Date: 2026-01-07

Changes:
- MINOR: Added Documentation Standards section
- Added marimo as documentation tool for interactive examples
- Specified documentation structure and requirements
- Added dev dependencies clarification

Template Status:
- ✅ plan-template.md: Constitution Check section ready (gates will be populated per project)
- ✅ spec-template.md: Requirements structure aligns with constitution principles
- ✅ tasks-template.md: Task organization supports keyboard-first & TUI-native development
- ✅ Command files: Generic guidance (no agent-specific references)

Follow-up: None - all placeholders resolved
-->

# Kittiwake Constitution

## Core Principles

### I. Keyboard-First Interaction

Every feature MUST be fully accessible via keyboard shortcuts. Mouse/pointer support is
optional enhancement only. The TUI MUST provide:
- Clear visual feedback for all keyboard actions
- Consistent key bindings across all views
- Help overlay showing available shortcuts in current context
- No modal dialogs that trap focus without keyboard escape

**Universal Keybinding Standards:**
Keybindings MUST be universally compatible across keyboard layouts and operating systems:
- **PREFER** standard conventions (Ctrl+C/V/X, Ctrl+Z/Shift+Z, Ctrl+S, Ctrl+F, etc.)
- **AVOID** symbol keys that vary by layout (`/`, `\`, `[`, `]`, etc.)
- **AVOID** keybindings that conflict with terminal/shell shortcuts (Ctrl+C for SIGINT, Ctrl+D for EOF)
- **TEST** on multiple layouts: QWERTY (US), AZERTY (FR), QWERTZ (DE), etc.
- **DOCUMENT** why non-standard shortcuts are used (e.g., Ctrl+H for search instead of Ctrl+/ due to AZERTY layout)
- **PROVIDE** alternatives for actions when standard shortcuts conflict

**Rationale**: Terminal users expect efficient keyboard workflows. Mouse dependency breaks
the terminal-native experience and reduces productivity for power users. International
users on non-QWERTY layouts must have equal access to all features without hunting for
symbol keys or dealing with layout-specific issues.

### II. Data Source Agnostic

The application MUST work seamlessly with multiple data sources through narwhals'
unified API. Supported sources include:
- Local files (CSV, Parquet, JSON, etc.)
- Remote URLs (HTTP/HTTPS accessible data)
- Streaming sources where applicable
- Any backend narwhals supports (Pandas, Polars, etc.)

The user MUST NOT need to know or care about the underlying data engine. All operations
MUST work identically regardless of backend.

**Rationale**: Narwhals provides a unified interface abstracting execution engines.
Users should focus on data analysis, not technical implementation details.

### III. TUI-Native Design

UI components MUST be built using Textual framework primitives. The application MUST:
- Follow Textual's reactive programming model
- Use Textual's layout system (CSS-like styling)
- Leverage built-in widgets before creating custom ones
- Maintain responsive layouts that adapt to terminal size changes
- Respect terminal capabilities (color depth, dimensions)

**Rationale**: Textual provides a robust, tested foundation for building terminal UIs.
Custom rendering risks compatibility issues and maintenance burden.

### IV. Performance & Responsivity

The TUI MUST remain responsive during data operations. The application MUST:
- Never block the UI thread for more than 100ms
- Use async/await for I/O operations
- Show progress indicators for operations exceeding 500ms
- Support cancellation of long-running operations
- For supported engines/files respect the Lazyness and only compute on confirmation
- Implement lazy loading for large datasets (pagination, virtual scrolling)

**Rationale**: Terminal applications lack the visual richness of GUIs. Responsiveness
and feedback are critical to user confidence that the application is working.

### V. Composable Operations

Data operations MUST be composable and chainable. Users MUST be able to:
- Apply multiple operations in sequence (filter → group → aggregate)
- Save operation chains as reusable workflows
- Undo/redo operation sequences
- Preview operation results before applying
- Export both raw and transformed data

**Rationale**: Data analysis is exploratory and iterative. Users need to build complex
transformations step-by-step and easily backtrack when needed.

## Technology Stack

**Required Dependencies:**
- **Python**: >=3.13 (project uses modern Python features)
- **uv**: Package and project manager (fast, reliable, modern)
- **narwhals**: >=2.15.0 (unified dataframe API)
- **textual**: >=7.0.1 (TUI framework)

**Optional Dependencies:**
- Data backends: pandas, polars, pyarrow (narwhals will use what's available)
- File format support: Additional codec libraries as needed

**Development Dependencies:**
- **marimo**: >=0.18.4 (interactive documentation notebooks)

**Prohibited:**
- Direct use of pandas/polars APIs (MUST use narwhals abstraction)
- Blocking synchronous I/O in UI code (MUST use async)
- Custom terminal escape sequence handling (MUST use Textual primitives)

## Development Standards

**Code Organization:**
- Single project structure: `src/kittiwake/` for all source code
- Entry point: `kittiwake:main` (defined in pyproject.toml)
- Shorter cli entry point `kw`
- Tests in `tests/` with clear separation: unit, integration, contract tests

**Testing (when explicitly required):**
- Unit tests for data transformation logic
- Integration tests for narwhals backend compatibility
- Contract tests for saved workflow formats
- TUI interaction tests using Textual's testing utilities

**Documentation:**
- Keyboard shortcuts documented in-app and in README
- Data operation examples in user guide
- API documentation for composable operation functions

**Performance Benchmarks:**
- UI response time: <100ms for all user actions
- Progress feedback threshold: 500ms
- Large dataset handling: Test with 1M+ row datasets
- Memory efficiency: Stream processing for files exceeding available RAM

## Documentation Standards

**Interactive Documentation:**
Documentation MUST include both traditional text guides and interactive examples.
Use marimo notebooks for all code examples and tutorials.

**Documentation Structure:**
- `docs/guides/` - Traditional markdown guides and conceptual documentation
- `docs/examples/` - marimo notebooks (stored as `.py` files) demonstrating features
- `docs/api/` - API reference documentation
- `README.md` - Quick start guide with installation and basic usage

**marimo Notebook Requirements:**
All example notebooks MUST:
- Be stored as pure Python files (`.py` extension)
- Be executable standalone with `marimo run`
- Be exportable to static WASM HTML for browser-based interaction
- Include inline comments explaining key concepts
- Demonstrate real data operations using narwhals
- Be version controlled in git alongside code

**Interactive Examples:**
Each major feature MUST have at least one interactive marimo notebook showing:
- Basic usage with sample data
- Common operations and workflows
- Expected inputs and outputs
- Performance characteristics for large datasets

**Deployment Options:**
Documentation MAY be deployed as:
- Static WASM HTML on GitHub Pages
- Interactive marimo apps on a server
- Embedded in existing documentation sites

**Rationale**: Interactive documentation allows users to experiment with kittiwake
features immediately in their browser, reducing the barrier to understanding and
adoption. marimo's reactive notebook model aligns with modern documentation practices
and provides a superior learning experience compared to static code samples.

## Governance

**Amendment Process:**
This constitution is the authoritative guide for Kittiwake development. Changes require:
1. Written proposal with rationale
2. Impact analysis on existing features
3. Update to this document with version increment
4. Propagation to dependent templates (plan, spec, tasks)

**Versioning Policy:**
- MAJOR: Principle removal or incompatible governance changes
- MINOR: New principle addition or significant expansion
- PATCH: Clarifications, wording improvements, typo fixes

**Compliance:**
All feature specifications MUST verify compliance with these principles. The
Constitution Check section in plan-template.md enforces this requirement.
Violations MUST be explicitly justified and documented.

**Constitution Version**: 1.1.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
