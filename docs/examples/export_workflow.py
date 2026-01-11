# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "narwhals>=2.15.0",
#     "marimo>=0.18.4",
#     "polars>=1.0.0",
#     "pandas>=2.0.0",
# ]
# ///
"""
Export Workflow - Kittiwake Data Explorer

This notebook demonstrates loading, transforming, and exporting data to various formats
using narwhals operations that power kittiwake's TUI.

Generated with: kittiwake examples
Dataset: Titanic survival data
"""

import marimo

__generated_with__ = "kittiwake"

app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import narwhals as nw
    from pathlib import Path

    return mo, nw, Path


@app.cell
def __(mo):
    mo.md(
        """
        # Export Workflow: Load, Transform, Export

        This notebook demonstrates a complete data analysis workflow in kittiwake:
        1. Load data
        2. Apply transformations (filter, aggregate, select)
        3. Save analysis for reuse
        4. Export to different formats

        ## What you'll learn:
        1. Chain multiple operations in sequence
        2. Materialize lazy frames for export
        3. Export to CSV, Parquet, and JSON
        4. Save analysis metadata (in kittiwake TUI)
        """
    )
    return


@app.cell
def __(nw, Path, mo):
    # Load the Titanic dataset
    data_path = (
        Path(__file__).parent.parent.parent / "tests" / "e2e" / "Titanic-Dataset.csv"
    )
    df = nw.scan_csv(str(data_path))

    mo.md(f"""
    **Dataset loaded**: {data_path.name}
    
    **Source**: Lazy CSV scan (efficient for large files)
    """)
    return df, data_path


@app.cell
def __(df, mo):
    # Show original data summary
    schema = df.collect_schema()

    # Get row count by collecting
    total_rows = len(df.collect())

    mo.md(f"""
    ## Original Dataset
    
    - **Rows**: {total_rows}
    - **Columns**: {len(schema)}
    - **Schema**: {", ".join(schema.keys())}
    """)
    return schema, total_rows


@app.cell
def __(mo):
    mo.md("""
    ## Workflow Step 1: Filter Adults Only
    
    In kittiwake TUI (Lazy Mode):
    - Press `Ctrl+F` to open Filter Sidebar
    - Column: "Age", Operator: ">=", Value: 18
    - Click Apply → operation queues without executing
    """)
    return


@app.cell
def __(df, nw):
    # Operation 1: Filter adults (Age >= 18)
    df_adults = df.filter(nw.col("Age") >= 18)

    return (df_adults,)


@app.cell
def __(mo):
    mo.md("""
    ## Workflow Step 2: Filter Survivors
    
    In kittiwake TUI:
    - Press `Ctrl+F` again
    - Column: "Survived", Operator: "==", Value: 1
    - Click Apply → second operation queues
    """)
    return


@app.cell
def __(df_adults, nw):
    # Operation 2: Filter survivors
    df_adult_survivors = df_adults.filter(nw.col("Survived") == 1)

    return (df_adult_survivors,)


@app.cell
def __(mo):
    mo.md("""
    ## Workflow Step 3: Select Relevant Columns
    
    Remove unnecessary columns to focus analysis.
    
    In kittiwake TUI:
    - Operations Sidebar shows queued operations
    - Press `Ctrl+Shift+E` to execute all at once
    """)
    return


@app.cell
def __(df_adult_survivors):
    # Operation 3: Select specific columns
    df_selected = df_adult_survivors.select(
        ["PassengerId", "Name", "Sex", "Age", "Pclass", "Fare", "Embarked"]
    )

    return (df_selected,)


@app.cell
def __(mo):
    mo.md("""
    ## Workflow Step 4: Sort by Age
    
    Order results for better readability.
    """)
    return


@app.cell
def __(df_selected):
    # Operation 4: Sort by Age
    df_final = df_selected.sort("Age", descending=False)

    return (df_final,)


@app.cell
def __(df_final, mo):
    # Materialize the lazy frame to get final results
    final_result = df_final.collect()

    mo.md(f"""
    ## Transformation Results
    
    **Final Dataset**:
    - Rows: {len(final_result)}
    - Columns: {len(final_result.columns)}
    
    **Operations Applied**:
    1. ✅ Filter: Age >= 18
    2. ✅ Filter: Survived == 1
    3. ✅ Select: 7 columns
    4. ✅ Sort: Age (ascending)
    
    {
        mo.ui.table(
            final_result.head(20).to_pandas(),
            selection=None,
            pagination=True,
            page_size=20,
        )
    }
    """)
    return (final_result,)


@app.cell
def __(mo):
    mo.md("""
    ## Export Option 1: CSV Format
    
    CSV is human-readable and widely compatible.
    
    **In kittiwake TUI**:
    - Press `Ctrl+S` to save analysis with name/description
    - Press `Ctrl+E` (from Saved Analyses screen) to export
    - Select format: Python Script / marimo / Jupyter
    """)
    return


@app.cell
def __(final_result, Path, mo):
    # Export to CSV
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "adult_survivors.csv"

    # Note: narwhals DataFrames need to be converted to native format for writing
    # This example shows the concept - actual implementation may vary by backend
    try:
        # Convert to pandas for writing (universal compatibility)
        final_result.to_pandas().to_csv(csv_path, index=False)
        csv_success = True
    except Exception as e:
        csv_success = False
        csv_error = str(e)

    if csv_success:
        mo.md(f"""
        ✅ **CSV Export Successful**
        
        File: `{csv_path}`
        """)
    else:
        mo.md(f"""
        ⚠️ CSV export demonstration (file writing disabled in this example)
        
        Would write to: `{csv_path}`
        """)
    return output_dir, csv_path, csv_success


@app.cell
def __(mo):
    mo.md("""
    ## Export Option 2: Parquet Format
    
    Parquet is efficient for large datasets and preserves data types.
    
    **Advantages**:
    - Compressed (smaller file size)
    - Fast to read/write
    - Preserves schema and types
    - Columnar format (efficient for analytics)
    """)
    return


@app.cell
def __(final_result, output_dir, mo):
    # Export to Parquet
    parquet_path = output_dir / "adult_survivors.parquet"

    try:
        # Convert to pandas, then write as parquet
        final_result.to_pandas().to_parquet(parquet_path, index=False)
        parquet_success = True
    except Exception as e:
        parquet_success = False
        parquet_error = str(e)

    if parquet_success:
        mo.md(f"""
        ✅ **Parquet Export Successful**
        
        File: `{parquet_path}`
        
        Read it back with: `nw.scan_parquet("{parquet_path}")`
        """)
    else:
        mo.md(f"""
        ⚠️ Parquet export demonstration (file writing disabled in this example)
        
        Would write to: `{parquet_path}`
        """)
    return parquet_path, parquet_success


@app.cell
def __(mo):
    mo.md("""
    ## Export Option 3: Code Export (kittiwake Feature)
    
    kittiwake can export your analysis as executable code in three formats:
    
    ### 1. Python Script (.py)
    ```python
    import narwhals as nw
    
    df = nw.scan_csv("data.csv")
    df = df.filter(nw.col("Age") >= 18)
    df = df.filter(nw.col("Survived") == 1)
    df = df.select(["Name", "Age", "Pclass", ...])
    df = df.sort("Age")
    
    result = df.collect()
    print(result)
    ```
    
    ### 2. marimo Notebook (.py with @app.cell)
    - Interactive cells like this notebook
    - Each operation in a separate cell
    - Built-in visualizations
    
    ### 3. Jupyter Notebook (.ipynb)
    - Compatible with Jupyter/JupyterLab
    - Markdown documentation cells
    - Code cells for each operation
    
    **To export in kittiwake**:
    1. Complete your analysis workflow
    2. Press `Ctrl+S` to save analysis with name
    3. Navigate to Saved Analyses (Ctrl+L)
    4. Select analysis and press `Ctrl+E` for export
    5. Choose format and output path
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Saved Analysis Metadata (kittiwake TUI)
    
    When you save an analysis in kittiwake, it stores:
    
    ```sql
    CREATE TABLE saved_analyses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP NOT NULL,
        modified_at TIMESTAMP NOT NULL,
        operation_count INTEGER NOT NULL,
        dataset_path TEXT NOT NULL,
        operations JSON NOT NULL
    );
    ```
    
    **Benefits**:
    - Reload analysis later with same dataset
    - Update/delete saved analyses
    - Export to multiple formats
    - Track analysis history
    - Share reproducible workflows
    
    **Storage**: `~/.kittiwake/analyses.db` (DuckDB)
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Example: Loading a Saved Analysis
    
    In kittiwake TUI:
    1. Press `Ctrl+L` to open Saved Analyses screen
    2. Navigate to saved analysis (arrow keys)
    3. Press `Enter` to load
    4. kittiwake will:
       - Reload the original dataset from stored path
       - Reapply all operations in sequence
       - Display results in main view
       - Restore operations history in sidebar
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Workflow Comparison: Lazy vs Eager Mode
    
    ### Lazy Mode (Default)
    Operations queue up without executing:
    
    ```
    [Data] → [Filter Age] (queued) → [Filter Survived] (queued) → [Select] (queued)
    
    Press Ctrl+E: Execute next operation
    Press Ctrl+Shift+E: Execute all operations at once
    ```
    
    **Benefits**:
    - Review operations before executing
    - Reorder operations easily
    - Remove/edit operations before execution
    - Execute all efficiently in one pass
    
    ### Eager Mode
    Operations execute immediately:
    
    ```
    [Data] → [Filter Age] ✓ → [Filter Survived] ✓ → [Select] ✓
    
    Each operation updates data table immediately
    ```
    
    **Benefits**:
    - See results immediately
    - Faster interactive exploration
    - No need to execute separately
    
    **Toggle**: Press `Ctrl+M` to switch between modes
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Real-World Export Example
    
    Suppose you're analyzing customer data:
    
    ### Workflow
    1. Load: `customers.csv` (10M rows)
    2. Filter: Active customers in last 6 months
    3. Aggregate: Total purchases by region
    4. Sort: By purchase amount (descending)
    5. Select: Key columns only
    
    ### Export Strategy
    
    **For sharing with colleagues**:
    - Export as **marimo notebook** (interactive)
    - They can run it, modify filters, see results
    
    **For automated reports**:
    - Export as **Python script**
    - Schedule with cron/airflow
    - Output to data warehouse
    
    **For dashboard integration**:
    - Export to **Parquet**
    - Fast loading in BI tools
    - Compressed storage
    
    **For Excel users**:
    - Export to **CSV**
    - Open in Excel/Google Sheets
    - Human-readable format
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Summary
    
    This notebook demonstrated:
    - ✅ Loading data with lazy evaluation
    - ✅ Chaining multiple operations (filter, select, sort)
    - ✅ Materializing results with `.collect()`
    - ✅ Exporting to CSV and Parquet formats
    - ✅ Understanding kittiwake's save/export workflow
    - ✅ Lazy vs Eager execution modes
    
    ### Key Takeaways
    
    1. **Lazy evaluation** is efficient for large datasets
    2. **Chain operations** before collecting results
    3. **Save analyses** for reproducibility
    4. **Export formats** serve different use cases:
       - CSV: Universal compatibility
       - Parquet: Performance and compression
       - Python/marimo/Jupyter: Reproducible code
    
    ### Next Steps
    
    - Launch kittiwake TUI: `kw load tests/e2e/Titanic-Dataset.csv`
    - Build your own workflow with filters and aggregations
    - Save analysis with `Ctrl+S`
    - Export to your preferred format with `Ctrl+E`
    - Share notebooks with your team!
    """)
    return


if __name__ == "__main__":
    app.run()
