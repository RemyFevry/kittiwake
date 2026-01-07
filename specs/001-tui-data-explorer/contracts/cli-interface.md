# CLI Interface Contract

**Version**: 1.0.0  
**Feature**: 001-tui-data-explorer  
**Stability**: This contract is semver-stable. Breaking changes require major version bump.

---

## Overview

The `kw` command provides a keyboard-first TUI for interactive data exploration. The CLI supports launching with an empty workspace or pre-loading datasets from files and URLs.

---

## Commands

### `kw`

Launches TUI with empty workspace.

**Usage**:
```bash
kw
```

**Behavior**:
- Opens Textual TUI application
- Displays empty workspace with instructions to load data (FR-052)
- User can load datasets via keyboard shortcut (typically `Ctrl+O`)

**Exit Codes**:
- `0`: Normal exit (user quit via `q` or `Ctrl+C`)
- `1`: Fatal error (invalid config, terminal incompatibility, etc.)

**Examples**:
```bash
# Launch empty workspace
kw

# Launch and let user load files interactively
kw
```

---

### `kw load <paths...>`

Launches TUI and loads one or more datasets from files or URLs.

**Usage**:
```bash
kw load <path1> [<path2> ... <pathN>]
```

**Arguments**:
- `<paths...>`: One or more file paths or HTTP(S) URLs (positional, required)
  - Local files: Absolute or relative paths
  - Remote files: Full HTTP/HTTPS URLs
  - Supported formats: CSV (.csv), Parquet (.parquet), JSON (.json)

**Behavior**:
- Loads up to 10 datasets (FR-063)
- First dataset becomes active in main view (FR-057)
- Additional datasets accessible via tabs/keyboard shortcuts (FR-064)
- If >10 paths provided, loads first 10 and displays warning (edge case handled)
- If some files fail to load, continues with successful ones and shows errors
- Remote URLs download to `~/.kittiwake/cache/` then load (research.md decision)

**Exit Codes**:
- `0`: Normal exit (at least one dataset loaded successfully)
- `1`: Fatal error (all datasets failed to load, or CLI parse error)

**Examples**:
```bash
# Load single CSV file
kw load data.csv

# Load multiple local files
kw load sales.parquet customers.csv transactions.json

# Load mixed local and remote
kw load local.csv https://example.com/remote.parquet

# Load from URL
kw load https://raw.githubusercontent.com/org/repo/data.csv
```

**Error Handling**:
```bash
# Non-existent file - displays error, continues if other files valid
kw load valid.csv invalid.csv
# Output: "Error loading invalid.csv: File not found. Loaded 1 of 2 datasets."

# Unsupported format - displays error
kw load data.xlsx
# Output: "Error: Unsupported format '.xlsx'. Supported: .csv, .parquet, .json"

# Remote timeout - displays error, allows retry in TUI
kw load https://slow-server.com/data.csv
# Output: "Error downloading https://slow-server.com/data.csv: Timeout. Use 'Retry' in TUI to try again."

# More than 10 files - loads first 10, warns
kw load file{1..15}.csv
# Output: "Warning: Maximum 10 datasets. Loaded files 1-10. Remaining files ignored: file11.csv, ..."
```

---

## Keyboard Shortcuts

(Context-aware bindings defined in each screen. See `MainScreen.BINDINGS` in implementation.)

### Global Shortcuts (available in all screens)
- `?`: Show help overlay (FR-007)
- `q` or `Ctrl+C`: Quit application
- `Ctrl+O`: Open file browser to load dataset
- `Ctrl+1` through `Ctrl+9`, `Ctrl+0`: Switch to dataset 1-10 (FR-055)

### Main Screen Shortcuts
- `f`: Activate filter input (FR-016)
- `a`: Open aggregation menu (FR-021)
- `p`: Create pivot table (FR-025)
- `m`: Merge/join datasets (FR-029)
- `s`: Save current analysis (FR-040)
- `e`: Export analysis (FR-046)
- `u`: Undo last operation (FR-036)
- `r`: Redo undone operation (FR-036)
- `↑`/`↓`/`←`/`→`: Navigate table (FR-013)
- `PgUp`/`PgDn`: Page navigation (FR-011)
- `Ctrl+S`: Split pane mode (FR-056)

---

## Configuration

### Config File Location
`~/.kittiwake/config.toml` (optional, not required for v1.0.0)

### Cache Directory
`~/.kittiwake/cache/` - stores downloaded remote datasets

### Database
`~/.kittiwake/analyses.db` - DuckDB database for saved analyses (FR-041)

---

## Environment Variables

None required for v1.0.0. Future versions may support:
- `KITTIWAKE_CACHE_DIR`: Override default cache location
- `KITTIWAKE_DB_PATH`: Override default database path

---

## Versioning & Stability

### Stable (semver-protected):
- `kw` command (bare launch)
- `kw load <paths...>` command
- Exit codes (0 = success, 1 = error)
- Supported file formats (.csv, .parquet, .json)
- Config/cache/database file locations

### Unstable (may change in minor versions):
- Specific keyboard shortcuts (bindings may be reconfigured)
- Error message text (wording may improve)
- Progress indicator format
- TUI layout details

### Deprecated (none in v1.0.0):
None.

---

## Future Commands (Planned)

These are NOT part of v1.0.0 but reserved for future use:

- `kw analyze <name>`: Load and run saved analysis
- `kw export <format> <name>`: Export analysis without opening TUI
- `kw list`: List saved analyses
- `kw config`: Interactive configuration

---

## Testing Contract

CLI behavior is validated by:
- `tests/contract/test_cli_contract.py` - ensures stable interface
- Exit code validation
- Argument parsing correctness
- Error message presence (not specific text)

---

## Changelog

### v1.0.0 (2026-01-07)
- Initial CLI contract
- `kw` and `kw load` commands
- 10-dataset limit
- CSV, Parquet, JSON support
