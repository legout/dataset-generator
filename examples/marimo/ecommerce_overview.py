import marimo

__generated_with = "0.16.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import datetime
    from dataset_generator import create_generator, create_writer, WriterOptions, write_dataset
    import polars as pl
    from pathlib import Path
    return (
        Path,
        WriterOptions,
        create_generator,
        create_writer,
        datetime,
        mo,
        pl,
        write_dataset,
    )


@app.cell
def _(mo):
    orders_per_day = (
        mo.ui.slider(
            start=0, stop=1000, value=100, step=100, label="Orders per day"
        )
    )
    file_rows_target = mo.ui.slider(
        start=50, stop=500_000, value=200_000, step=25_000, label="Rows per file"
    )

    mo.vstack(
        [
            mo.md("""
    ### Parameter controls

    Adjust how many records the generator produces per day and target rows per output file.
    Smaller numbers keep generation quick for interactive exploration.
    """),
            orders_per_day,
            file_rows_target,
        ]
    )
    return (file_rows_target,)


@app.cell
def _(
    Path,
    WriterOptions,
    create_generator,
    create_writer,
    datetime,
    file_rows_target,
    write_dataset,
):
    """Materialize data using the current slider settings."""
    generator = create_generator(
        "ecommerce",
        seed=5,
        n_customers=123456,
        n_products=12000,
        orders_per_day=5000,
        order_items_mean=2.1,
        file_rows_target=200_000,
        start_date=datetime.date(2023, 3, 1),
        end_date=datetime.date(2025, 3, 1),
    )
    output_dir = Path("examples/demo_output/marimo_parquet").resolve()
    writer = create_writer(
        "parquet",
        str(output_dir),
        s3=None,
        catalog=None,
        options=WriterOptions(file_rows_target=file_rows_target.value),
    )
    write_dataset(generator, writer)
    return (output_dir,)


app._unparsable_cell(
    r"""
    file_rows_target.value\"\"\"Grab one orders partition for preview.\"\"\"
    orders_sample = pl.read_parquet(next(output_dir.joinpath(\"orders\").rglob(\"*.parquet\")))
    """,
    name="_"
)


@app.cell
def _(orders_sample, pl):
    """Summarize order statuses for a high-level view."""
    orders_summary = (
        orders_sample
        .group_by("status")
        .agg([pl.len().alias("cnt"), pl.col("amount").mean().alias("avg_amount")])
        .sort("cnt", descending=True)
    )
    return (orders_summary,)


@app.cell
def _(mo, orders_sample, orders_summary):
    mo.vstack([
        mo.hstack([mo.md("### Orders preview"), mo.md("Adjust sliders and rerun to refresh")]),
        orders_sample,
        mo.md("### Status summary"),
        orders_summary,
    ])
    return


@app.cell
def _(output_dir):
    import duckdb  
    con = duckdb.connect()
    con.execute(f"CREATE VIEW orders AS SELECT * FROM read_parquet('{output_dir}/orders/**/*.parquet', hive_partitioning=true)")
    con.execute(f"CREATE VIEW order_items AS SELECT * FROM read_parquet('{output_dir}/order_items/**/*.parquet', hive_partitioning=true)")
    con.execute(f"CREATE VIEW customers AS SELECT * FROM read_parquet('{output_dir}/customers/*.parquet')")
    con.execute(f"CREATE VIEW products AS SELECT * FROM read_parquet('{output_dir}/products/*.parquet')")
    return (con,)


@app.cell
def _():
    from datafusion import SessionContext
    import ibis

    ctx = SessionContext()
    # Sample table
    _ = ctx.from_pydict({"a": [1, 2, 3]}, "my_table")

    con2 = ibis.datafusion.connect(ctx)
    return


@app.cell
def _(con, mo, order_items):
    _df = mo.sql(
        f"""
        SELECT
            *
        from
            order_items
        """,
        engine=con
    )
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(con, mo, order_items, orders):
    revenue_by_day = mo.sql(
        """
        SELECT 
            o.order_date,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as order_count,
            COUNT(DISTINCT oi.product_id) as unique_items
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_date
        ORDER BY total_revenue DESC
        LIMIT 10
        """,
        engine=con
    )

    revenue_by_day
    return


@app.cell
def _():
    return


@app.cell
def _(con, mo, order_items, orders):
    _df = mo.sql(
        f"""
        SELECT 
            o.order_date,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as order_count,
            COUNT(DISTINCT oi.product_id) as unique_items,
            COUNT(o.customer_id) as customers,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.order_date
        ORDER BY total_revenue DESC
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
