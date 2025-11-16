# Marimo Apps

Interactive marimo notebooks demonstrating Dataset Generator capabilities with reactive UI elements and app deployment features.

## Available Marimo Apps

The `examples/marimo/` directory contains ready-to-run marimo applications:

### Core Examples

- **`ecommerce_overview.py`** - Interactive e-commerce data generation with sliders for real-time parameter adjustment
- **`ecommerce_overview_dl.py`** - Advanced example with DuckDB integration and S3 storage across multiple filesystems

## Setup

### 1. Install Dependencies

```bash
# Install with all extras
pip install dataset-generator[cli,delta,iceberg,ducklake]

# Install marimo
pip install marimo

# Or install marimo with additional dependencies for the examples
pip install marimo duckdb datafusion ibis
```

### 2. Start Marimo

```bash
# Navigate to examples directory
cd examples

# Start marimo in edit mode
marimo edit marimo/ecommerce_overview.py

# Or start in run mode for deployment
marimo run marimo/ecommerce_overview.py

# Start the marimo server to serve multiple apps
marimo run --host 0.0.0.0 --port 8000
```

### 3. Run the Applications

Open any marimo file in the `marimo/` directory and run the cells. Marimo automatically re-runs dependent cells when you modify inputs.

## Marimo Features

### Reactive UI Elements

- **Interactive Sliders** - Adjust generation parameters in real-time
- **Live Updates** - See data refresh automatically when parameters change
- **SQL Integration** - Execute SQL queries directly in notebooks
- **App Deployment** - Export notebooks as standalone web applications

### Multiple Data Engines

- **DuckDB** - Fast analytical SQL engine
- **DataFusion** - Apache Arrow-based query engine  
- **Ibis** - Python DataFrame API with multiple backends

### Cloud Storage Integration

- **S3-compatible storage** - MinIO, AWS S3, etc.
- **Multiple filesystems** - Compare data across different storage backends
- **Catalog support** - SQL and REST catalog integration

## Example: Quick Start with E-commerce Data

```python
# In a marimo notebook cell
import marimo as mo
import datetime
from dataset_generator import create_generator, create_writer, WriterOptions, write_dataset
import polars as pl
from pathlib import Path

# Create interactive controls
orders_per_day = mo.ui.slider(
    start=0, stop=1000, value=100, step=100, label="Orders per day"
)
file_rows_target = mo.ui.slider(
    start=50, stop=500_000, value=200_000, step=25_000, label="Rows per file"
)

# Display controls
mo.vstack([orders_per_day, file_rows_target])
```

```python
# Data generation cell (automatically re-runs when sliders change)
generator = create_generator(
    "ecommerce",
    seed=5,
    n_customers=123456,
    orders_per_day=orders_per_day.value,
    file_rows_target=file_rows_target.value,
    start_date=datetime.date(2023, 3, 1),
    end_date=datetime.date(2025, 3, 1),
)

output_dir = Path("examples/demo_output/marimo_parquet").resolve()
writer = create_writer("parquet", str(output_dir))
write_dataset(generator, writer)
```

```python
# Analysis with embedded SQL
con = duckdb.connect()
con.execute(f"CREATE VIEW orders AS SELECT * FROM read_parquet('{output_dir}/orders/**/*.parquet', hive_partitioning=true)")

# Interactive SQL query
revenue_by_day = mo.sql(
    """
    SELECT 
        o.order_date,
        SUM(o.amount) as total_revenue,
        COUNT(o.order_id) as order_count
    FROM orders o
    GROUP BY o.order_date
    ORDER BY total_revenue DESC
    LIMIT 10
    """,
    engine=con
)
```

## Advanced Examples

### S3 Storage with Multiple Filesystems

The `ecommerce_overview_dl.py` example demonstrates:
- **Multiple S3 endpoints** - Compare data across different MinIO instances
- **Cross-filesystem queries** - Join data from different storage backends
- **Schema organization** - Organize data by storage source

```python
# Configure multiple S3 endpoints
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

# Query across filesystems
df = mo.sql(
    """
    SELECT o.order_date, SUM(o.amount) as total_revenue
    FROM minio.orders o
    UNION ALL
    SELECT o.order_date, SUM(o.amount) as total_revenue  
    FROM rustfs.orders o
    ORDER BY total_revenue DESC
    """,
    engine=con
)
```

## Marimo vs Jupyter Notebooks

### Advantages of Marimo

- **Reactive execution** - Cells automatically re-run when dependencies change
- **Clean state management** - No hidden cell execution order dependencies
- **Built-in app deployment** - Export notebooks as standalone web apps
- **Better collaboration** - Git-friendly format and reproducible execution
- **Performance** - Faster startup and memory usage for large datasets
- **SQL integration** - Native SQL cell execution with syntax highlighting

### When to Use Each

**Choose Marimo for:**
- Interactive dashboards and data exploration
- Parameter tuning and sensitivity analysis
- Deployable data applications
- Teaching and demonstrations with live examples
- Real-time data visualization

**Choose Jupyter for:**
- Traditional scientific research workflows
- Complex multi-step analysis requiring manual control
- Compatibility with existing notebook ecosystems
- Advanced widget ecosystems beyond marimo's current offerings

## Best Practices

### Performance Optimization

```python
# Use appropriate slider ranges
orders_per_day = mo.ui.slider(
    start=10,      # Minimum realistic value
    stop=1000,     # Maximum practical value  
    value=100,     # Sensible default
    step=50,       # Reasonable increment
    label="Orders per day",
    debounce=True  # Prevent excessive re-runs
)
```

### Memory Management

```python
# Clear large datasets after use
import gc
large_df = generate_big_dataset()
# ... use the dataset ...
del large_df
gc.collect()
```

### App Deployment

```bash
# Deploy as standalone app
marimo export html marimo/ecommerce_overview.py --output app.html

# Or serve as web application
marimo run marimo/ecommerce_overview.py --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

**Marimo server not starting**
- Check port conflicts: `marimo run --port 8001`
- Verify installation: `pip list | grep marimo`

**Data not updating when sliders change**
- Ensure reactive variables are properly referenced
- Check for circular dependencies between cells

**SQL connection errors**
- Verify DuckDB installation: `pip install duckdb`
- Check data paths exist and are accessible

**S3 connection failures**
- Verify credentials and endpoint URLs
- Test with s3fs directly before using in marimo

### Debugging Tips

```python
# Add debug outputs to understand cell execution
print(f"Current slider value: {orders_per_day.value}")
print(f"Generator created with seed: {generator.seed}")
```

## Next Steps

- **[Jupyter Notebooks](jupyter.md)** - Traditional notebook examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides
- **[API Reference](../api/index.md)** - Complete documentation
- **[Configuration](../user-guide/configuration.md)** - Generator and writer options
