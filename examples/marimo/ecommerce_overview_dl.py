import marimo

__generated_with = "0.16.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import datetime
    from dataset_generator import (
        create_generator,
        create_writer,
        WriterOptions,
        write_dataset,
        S3Config,
    )
    import polars as pl
    from pathlib import Path
    import s3fs
    import duckdb
    import pyarrow.dataset as pds
    import pyarrow.parquet as pq
    return S3Config, duckdb, mo, pds, pq, s3fs


@app.cell
def _(S3Config):
    s3c1 = S3Config(
        uri="s3://demo/demo/ducklake",
        endpoint_url="http://localhost:9000",
        key="demo",
        secret="demo1234",
    )

    s3c2 = S3Config(
        uri="s3://demo/demo/ducklake",
        endpoint_url="http://localhost:9010",
        key="demo",
        secret="demo1234",
    )

    s3c3 = S3Config(
        uri="s3://demo/demo/ducklake",
        endpoint_url="http://localhost:9020",
        key="demo",
        secret="demo1234",
    )
    return s3c1, s3c2, s3c3


@app.cell
def _(s3c1, s3c2, s3c3, s3fs):
    fs1 = s3fs.S3FileSystem(**s3c1.to_fsspec_kwargs())
    fs2 = s3fs.S3FileSystem(**s3c2.to_fsspec_kwargs())
    fs3 = s3fs.S3FileSystem(**s3c3.to_fsspec_kwargs())
    return fs1, fs2, fs3


@app.cell
def _(fs1, fs2, fs3, pds, pq):
    m_orders = pds.dataset(
        "demo/demo/ducklake/orders/",
        filesystem=fs1,
        format="parquet",
        partitioning=None,
    )
    m_products = pq.read_table(
        "demo/demo/ducklake/products/",
        filesystem=fs1,
        partitioning=None,
    )
    m_order_items = pds.dataset(
        "demo/demo/ducklake/order_items/",
        filesystem=fs1,
        format="parquet",
        partitioning=None,
    )
    m_customers = pq.read_table(
        "demo/demo/ducklake/customers/",
        filesystem=fs1,
        partitioning=None,
    )

    r_orders = pds.dataset(
        "demo/demo/ducklake/orders/",
        filesystem=fs2,
        format="parquet",
        partitioning=None,
    )
    r_products = pq.read_table(
        "demo/demo/ducklake/products/",
        filesystem=fs2,
        partitioning=None,
    )
    r_order_items = pds.dataset(
        "demo/demo/ducklake/order_items/",
        filesystem=fs2,
        format="parquet",
        partitioning=None,
    )
    r_customers = pq.read_table(
        "demo/demo/ducklake/customers/",
        filesystem=fs2,
        partitioning=None,
    )

    s_orders = pds.dataset(
        "demo/demo/ducklake/orders/",
        filesystem=fs3,
        format="parquet",
        partitioning=None,
    )
    s_products = pq.read_table(
        "demo/demo/ducklake/products/",
        filesystem=fs3,
        partitioning=None,
    )
    s_order_items = pds.dataset(
        "demo/demo/ducklake/order_items/",
        filesystem=fs3,
        format="parquet",
        partitioning=None,
    )
    s_customers = pq.read_table(
        "demo/demo/ducklake/customers/",
        filesystem=fs2,
        partitioning=None,
    )
    return (
        m_customers,
        m_order_items,
        m_orders,
        m_products,
        r_customers,
        r_order_items,
        r_orders,
        r_products,
        s_customers,
        s_order_items,
        s_orders,
        s_products,
    )


@app.cell
def _(
    duckdb,
    m_customers,
    m_order_items,
    m_orders,
    m_products,
    r_customers,
    r_order_items,
    r_orders,
    r_products,
    s_customers,
    s_order_items,
    s_orders,
    s_products,
):
    con = duckdb.connect()
    con.register("m_orders2", m_orders)
    con.register("m_products2", m_products)
    con.register("m_order_items2", m_order_items)
    con.register("m_customers2", m_customers)
    con.register("r_orders2", r_orders)
    con.register("r_products2", r_products)
    con.register("r_order_items2", r_order_items)
    con.register("r_customers2", r_customers)
    con.register("s_orders2", s_orders)
    con.register("s_products2", s_products)
    con.register("s_order_items2", s_order_items)
    con.register("s_customers2", s_customers)
    return (con,)


@app.cell
def _(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS minio")
    con.execute(
        "CREATE VIEW IF NOT EXISTS minio.products AS SELECT * FROM m_products2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS minio.customers AS SELECT * FROM m_customers2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS minio.orders AS SELECT * FROM m_orders2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS minio.order_items AS SELECT * FROM m_order_items2"
    )
    con.execute("CREATE SCHEMA IF NOT EXISTS rustfs")
    con.execute(
        "CREATE VIEW IF NOT EXISTS rustfs.products AS SELECT * FROM r_products2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS rustfs.customers AS SELECT * FROM r_customers2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS rustfs.orders AS SELECT * FROM r_orders2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS rustfs.order_items AS SELECT * FROM r_order_items2"
    )
    con.execute("CREATE SCHEMA IF NOT EXISTS swfs")
    con.execute(
        "CREATE VIEW IF NOT EXISTS swfs.products AS SELECT * FROM s_products2"
    )
    con.execute(
        "CREATE VIEW IF NOT EXISTS swfs.customers AS SELECT * FROM s_customers2"
    )
    con.execute("CREATE VIEW IF NOT EXISTS swfs.orders AS SELECT * FROM s_orders2")
    con.execute(
        "CREATE VIEW IF NOT EXISTS swfs.order_items AS SELECT * FROM s_order_items2"
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            o.order_date,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as order_count,
            COUNT(DISTINCT oi.product_id) as unique_items,
            COUNT(o.customer_id) as customers,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM
            minio.orders o
            LEFT JOIN minio.order_items oi ON o.order_id = oi.order_id
        GROUP BY
            o.order_date
        ORDER BY
            total_revenue DESC
        LIMIT
            100
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            o.order_date,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as order_count,
            COUNT(DISTINCT oi.product_id) as unique_items,
            COUNT(o.customer_id) as customers,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM
            rustfs.orders o
            LEFT JOIN rustfs.order_items oi ON o.order_id = oi.order_id
        GROUP BY
            o.order_date
        ORDER BY
            total_revenue DESC
        LIMIT
            100
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            o.order_date,
            SUM(o.amount) as total_revenue,
            COUNT(o.order_id) as order_count,
            COUNT(DISTINCT oi.product_id) as unique_items,
            COUNT(o.customer_id) as customers,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM
            swfs.orders o
            LEFT JOIN swfs.order_items oi ON o.order_id = oi.order_id
        GROUP BY
            o.order_date
        ORDER BY
            total_revenue DESC
        LIMIT
            100
        """,
        engine=con
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
