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
Aggregation Workflow - Kittiwake Data Explorer

This notebook demonstrates group-by aggregations and multiple operation patterns
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
        # Aggregation Workflow: Group-By and Statistics

        This notebook demonstrates kittiwake's aggregation capabilities using narwhals.

        ## What you'll learn:
        1. Compute global aggregations (sum, mean, count, etc.)
        2. Group-by operations with aggregations
        3. Multiple aggregation functions at once
        4. Chaining filters with aggregations
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

    mo.md(f"**Dataset loaded**: {data_path.name}")
    return df, data_path


@app.cell
def __(mo):
    mo.md("""
    ## Example 1: Global Aggregation (No Grouping)
    
    Calculate summary statistics across the entire dataset.
    
    In kittiwake's TUI:
    - Press `A` to open Aggregate Sidebar
    - Select column: "Age"
    - Select functions: mean, min, max
    - Leave "Group By" empty for global aggregation
    - Click Apply
    """)
    return


@app.cell
def __(df, nw):
    # Global aggregation: mean, min, max of Age
    # This is the code that kittiwake generates
    df_age_stats = df.select(
        [
            nw.col("Age").mean().alias("Age_mean"),
            nw.col("Age").min().alias("Age_min"),
            nw.col("Age").max().alias("Age_max"),
            nw.col("Age").count().alias("Age_count"),
        ]
    )

    return (df_age_stats,)


@app.cell
def __(df_age_stats, mo):
    stats = df_age_stats.collect()

    mo.md(f"""
    **Age Statistics Across All Passengers**:
    
    {mo.ui.table(stats.to_pandas(), selection=None)}
    
    Observations:
    - Mean age: {stats["Age_mean"][0]:.1f} years
    - Age range: {stats["Age_min"][0]:.0f} - {stats["Age_max"][0]:.0f} years
    - Non-null age values: {stats["Age_count"][0]}
    """)
    return (stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 2: Group-By Single Column
    
    Calculate survival rate by passenger class.
    """)
    return


@app.cell
def __(df, nw):
    # Group by Pclass, calculate survival statistics
    df_survival_by_class = df.group_by("Pclass").agg(
        [
            nw.col("Survived").sum().alias("Survived_sum"),
            nw.col("Survived").count().alias("Survived_count"),
            nw.col("Survived").mean().alias("Survival_rate"),
        ]
    )

    return (df_survival_by_class,)


@app.cell
def __(df_survival_by_class, mo):
    survival_stats = df_survival_by_class.sort("Pclass").collect()

    mo.md(f"""
    **Survival Statistics by Passenger Class**:
    
    {mo.ui.table(survival_stats.to_pandas(), selection=None)}
    
    Insights:
    - First class had highest survival rate
    - Lower class passengers had significantly lower survival rates
    """)
    return (survival_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 3: Group-By Multiple Columns
    
    Analyze survival by both Sex and Passenger Class.
    """)
    return


@app.cell
def __(df, nw):
    # Group by Sex and Pclass
    df_survival_sex_class = df.group_by(["Sex", "Pclass"]).agg(
        [
            nw.col("Survived").count().alias("Total_passengers"),
            nw.col("Survived").sum().alias("Survivors"),
            nw.col("Survived").mean().alias("Survival_rate"),
        ]
    )

    return (df_survival_sex_class,)


@app.cell
def __(df_survival_sex_class, mo):
    sex_class_stats = df_survival_sex_class.sort(["Sex", "Pclass"]).collect()

    mo.md(f"""
    **Survival Statistics by Sex and Passenger Class**:
    
    {mo.ui.table(sex_class_stats.to_pandas(), selection=None)}
    
    Key Findings:
    - Female passengers had much higher survival rates across all classes
    - First class females had the highest survival rate
    - Third class males had the lowest survival rate
    """)
    return (sex_class_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 4: Multiple Aggregations on Same Column
    
    Comprehensive statistics for fare amounts by class.
    """)
    return


@app.cell
def __(df, nw):
    # Group by Pclass, calculate multiple fare statistics
    df_fare_stats = df.group_by("Pclass").agg(
        [
            nw.col("Fare").count().alias("Fare_count"),
            nw.col("Fare").sum().alias("Fare_sum"),
            nw.col("Fare").mean().alias("Fare_mean"),
            nw.col("Fare").median().alias("Fare_median"),
            nw.col("Fare").min().alias("Fare_min"),
            nw.col("Fare").max().alias("Fare_max"),
            nw.col("Fare").std().alias("Fare_std"),
        ]
    )

    return (df_fare_stats,)


@app.cell
def __(df_fare_stats, mo):
    fare_stats = df_fare_stats.sort("Pclass").collect()

    mo.md(f"""
    **Fare Statistics by Passenger Class**:
    
    {mo.ui.table(fare_stats.to_pandas(), selection=None)}
    
    Analysis:
    - First class fares were significantly higher (mean & median)
    - Large standard deviation indicates high fare variation within classes
    - Third class had the most consistent (low) fares
    """)
    return (fare_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 5: Filter + Aggregate Workflow
    
    Demonstrates lazy vs eager execution mode in kittiwake:
    
    **Lazy Mode** (default):
    1. Apply filter → queued
    2. Apply aggregation → queued
    3. Press Ctrl+Shift+E → execute all at once
    
    **Eager Mode**:
    1. Toggle mode with Ctrl+M
    2. Apply filter → executes immediately
    3. Apply aggregation → executes immediately
    """)
    return


@app.cell
def __(df, nw):
    # Filter: Adults only (Age >= 18)
    df_adults = df.filter(nw.col("Age") >= 18)

    # Then aggregate by Sex
    df_adult_survival = df_adults.group_by("Sex").agg(
        [
            nw.col("Survived").count().alias("Total_adults"),
            nw.col("Survived").sum().alias("Adult_survivors"),
            nw.col("Survived").mean().alias("Survival_rate"),
            nw.col("Age").mean().alias("Mean_age"),
            nw.col("Fare").mean().alias("Mean_fare"),
        ]
    )

    return df_adults, df_adult_survival


@app.cell
def __(df_adult_survival, mo):
    adult_stats = df_adult_survival.sort("Sex").collect()

    mo.md(f"""
    **Adult Survival Statistics by Sex** (Age ≥ 18):
    
    {mo.ui.table(adult_stats.to_pandas(), selection=None)}
    
    Observations:
    - Adult females had much higher survival rate than adult males
    - Mean age similar between sexes
    - Slight fare difference between male and female adult passengers
    """)
    return (adult_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 6: Aggregation with Column Expressions
    
    Create derived columns before aggregating.
    """)
    return


@app.cell
def __(df, nw):
    # Create age groups, then aggregate
    df_age_groups = (
        df.with_columns(
            [
                nw.when(nw.col("Age") < 18)
                .then(nw.lit("Child"))
                .when(nw.col("Age") < 60)
                .then(nw.lit("Adult"))
                .otherwise(nw.lit("Senior"))
                .alias("Age_group")
            ]
        )
        .group_by("Age_group")
        .agg(
            [
                nw.col("Survived").count().alias("Total"),
                nw.col("Survived").sum().alias("Survivors"),
                nw.col("Survived").mean().alias("Survival_rate"),
                nw.col("Fare").mean().alias("Mean_fare"),
            ]
        )
    )

    return (df_age_groups,)


@app.cell
def __(df_age_groups, mo):
    age_group_stats = df_age_groups.collect()

    mo.md(f"""
    **Survival Statistics by Age Group**:
    
    {mo.ui.table(age_group_stats.to_pandas(), selection=None)}
    
    Insights:
    - Children had relatively good survival rates
    - Senior passengers had lowest survival rate
    - Fare varied significantly by age group (seniors paid more on average)
    """)
    return (age_group_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Example 7: Count Unique Values
    
    Analyze embarkation port distribution.
    """)
    return


@app.cell
def __(df, nw):
    # Count passengers by embarkation port
    df_embarked_counts = df.group_by("Embarked").agg(
        [
            nw.col("PassengerId").count().alias("Passenger_count"),
            nw.col("Survived").mean().alias("Survival_rate"),
            nw.col("Fare").mean().alias("Mean_fare"),
        ]
    )

    return (df_embarked_counts,)


@app.cell
def __(df_embarked_counts, mo):
    embarked_stats = df_embarked_counts.sort(
        "Passenger_count", descending=True
    ).collect()

    mo.md(f"""
    **Statistics by Embarkation Port**:
    
    {mo.ui.table(embarked_stats.to_pandas(), selection=None)}
    
    Key Points:
    - Most passengers embarked at Southampton (S)
    - Cherbourg (C) had highest survival rate and mean fare
    - Queenstown (Q) had lowest survival rate
    """)
    return (embarked_stats,)


@app.cell
def __(mo):
    mo.md("""
    ## Summary
    
    This notebook demonstrated:
    - ✅ Global aggregations (no grouping)
    - ✅ Single column group-by
    - ✅ Multiple column group-by
    - ✅ Multiple aggregation functions
    - ✅ Filter + aggregate workflows
    - ✅ Derived columns with aggregations
    - ✅ Counting and summarizing categorical data
    
    ### Aggregation Functions Available
    
    - `count()`: Count non-null values
    - `sum()`: Sum numeric values
    - `mean()`: Average
    - `median()`: Median value
    - `min()`: Minimum value
    - `max()`: Maximum value
    - `std()`: Standard deviation
    
    ### Next Steps
    
    - Try `export_workflow.py` to learn about saving and exporting analyses
    - Launch kittiwake TUI and press `A` to open Aggregate Sidebar
    - Experiment with different combinations of columns and aggregation functions
    """)
    return


if __name__ == "__main__":
    app.run()
