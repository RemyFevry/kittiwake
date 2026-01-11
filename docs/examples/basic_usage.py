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
Basic Usage - Kittiwake Data Explorer

This notebook demonstrates basic data loading, filtering, sorting, and viewing
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
        # Basic Usage: Data Loading and Filtering

        This notebook shows how to use narwhals (the engine behind kittiwake)
        to perform basic data exploration tasks.

        ## What you'll learn:
        1. Load CSV data with lazy evaluation
        2. Apply column filters
        3. Sort data by columns
        4. View paginated results
        """
    )
    return


@app.cell
def __(nw, Path, mo):
    # Load the Titanic dataset using lazy evaluation
    # This mirrors kittiwake's data loading behavior

    # Find the dataset relative to this notebook
    data_path = (
        Path(__file__).parent.parent.parent / "tests" / "e2e" / "Titanic-Dataset.csv"
    )

    # Use scan_csv for lazy loading (efficient for large files)
    df = nw.scan_csv(str(data_path))

    mo.md(f"**Dataset loaded**: {data_path.name}")
    return df, data_path


@app.cell
def __(df, mo):
    # Display schema and basic info
    schema = df.collect_schema()

    mo.md(f"""
    ## Dataset Schema
    
    **Columns**: {len(schema)}
    
    {
        mo.as_html(
            mo.ui.table(
                [{"Column": col, "Type": str(dtype)} for col, dtype in schema.items()]
            )
        )
    }
    """)
    return (schema,)


@app.cell
def __(df, mo):
    # Show first 10 rows
    preview = df.head(10).collect()

    mo.md(f"""
    ## Preview (First 10 Rows)
    
    {mo.ui.table(preview.to_pandas(), selection=None)}
    """)
    return (preview,)


@app.cell
def __(mo):
    mo.md("""
    ## Filter Example 1: Age > 30
    
    In kittiwake's TUI, you would:
    - Press `Ctrl+F` to open filter sidebar
    - Select column: "Age"
    - Select operator: ">"
    - Enter value: 30
    - Click Apply (or press Enter)
    """)
    return


@app.cell
def __(df, nw):
    # Filter: Age > 30
    # This is the narwhals code that kittiwake generates
    df_filtered_age = df.filter(nw.col("Age") > 30)

    # Count results
    filtered_count = len(df_filtered_age.collect())
    return df_filtered_age, filtered_count


@app.cell
def __(df_filtered_age, filtered_count, mo):
    mo.md(f"""
    **Results**: {filtered_count} passengers aged > 30
    
    {
        mo.ui.table(
            df_filtered_age.head(10).collect().to_pandas(),
            selection=None,
            pagination=True,
        )
    }
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Filter Example 2: Survived = 1 (Survivors Only)
    
    Filtering by categorical/boolean columns.
    """)
    return


@app.cell
def __(df, nw):
    # Filter: Survived = 1
    df_survivors = df.filter(nw.col("Survived") == 1)

    survivor_count = len(df_survivors.collect())
    return df_survivors, survivor_count


@app.cell
def __(df_survivors, survivor_count, mo):
    mo.md(f"""
    **Results**: {survivor_count} survivors
    
    {
        mo.ui.table(
            df_survivors.head(10).collect().to_pandas(), selection=None, pagination=True
        )
    }
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Combining Multiple Filters
    
    Chain multiple filter operations (like queuing operations in kittiwake's lazy mode).
    """)
    return


@app.cell
def __(df, nw):
    # Multiple filters: Female passengers who survived
    df_female_survivors = df.filter(nw.col("Sex") == "female").filter(
        nw.col("Survived") == 1
    )

    female_survivor_count = len(df_female_survivors.collect())
    return df_female_survivors, female_survivor_count


@app.cell
def __(df_female_survivors, female_survivor_count, mo):
    mo.md(f"""
    **Results**: {female_survivor_count} female survivors
    
    {
        mo.ui.table(
            df_female_survivors.head(10).collect().to_pandas(),
            selection=None,
            pagination=True,
        )
    }
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Sorting Data
    
    Sort by columns to see patterns (kittiwake supports this via operations sidebar).
    """)
    return


@app.cell
def __(df):
    # Sort by Fare (descending) to see most expensive tickets
    df_sorted_fare = df.sort("Fare", descending=True)

    return (df_sorted_fare,)


@app.cell
def __(df_sorted_fare, mo):
    mo.md(f"""
    **Most Expensive Tickets**:
    
    {mo.ui.table(df_sorted_fare.head(10).collect().to_pandas(), selection=None)}
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Column Selection
    
    Select specific columns to focus on relevant data.
    """)
    return


@app.cell
def __(df):
    # Select only key columns
    df_selected = df.select(["Name", "Age", "Sex", "Survived", "Pclass", "Fare"])

    return (df_selected,)


@app.cell
def __(df_selected, mo):
    mo.md(f"""
    **Selected Columns View**:
    
    {
        mo.ui.table(
            df_selected.head(15).collect().to_pandas(),
            selection=None,
            pagination=True,
            page_size=15,
        )
    }
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Summary
    
    This notebook demonstrated:
    - ✅ Loading CSV data with `nw.scan_csv()` (lazy evaluation)
    - ✅ Filtering with comparison operators (`>`, `==`)
    - ✅ Chaining multiple filters
    - ✅ Sorting data
    - ✅ Selecting specific columns
    
    ### Next Steps
    
    - Try `aggregation_workflow.py` to learn about grouping and aggregations
    - Try `export_workflow.py` to learn about exporting analyses
    - Launch kittiwake TUI: `kw load tests/e2e/Titanic-Dataset.csv`
    """)
    return


if __name__ == "__main__":
    app.run()
