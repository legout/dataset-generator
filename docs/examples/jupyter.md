# Jupyter Notebooks

Interactive Jupyter notebooks demonstrating Dataset Generator capabilities.

## Available Notebooks

The `examples/jupyter/` directory contains ready-to-run notebooks:

### Core Examples

- **`ecommerce_parquet.ipynb`** - Generate e-commerce data and save as Parquet
- **`ecommerce_delta.ipynb`** - Use Delta Lake for ACID transactions
- **`s3_ducklake_minio.ipynb`** - DuckLake with MinIO S3 storage
- **`s3_iceberg_minio.ipynb`** - Apache Iceberg with MinIO

## Setup

### 1. Install Dependencies

```bash
# Install with all extras
pip install dataset-generator[cli,delta,iceberg,ducklake]

# Or install specific extras
pip install dataset-generator[delta,jupyter]
```

### 2. Start Jupyter

```bash
# Navigate to examples directory
cd examples

# Start Jupyter Lab
jupyter lab

# Or start classic notebook
jupyter notebook
```

### 3. Run the Notebooks

Open any notebook in the `jupyter/` directory and run the cells sequentially.

## Notebook Features

### Interactive Exploration

- **Parameter tuning** - Adjust generation parameters in real-time
- **Data visualization** - See the generated data immediately
- **Performance monitoring** - Track generation progress

### Multiple Formats

- **Parquet** - Columnar storage for analytics
- **Delta Lake** - ACID transactions and time travel
- **Apache Iceberg** - Massive dataset support
- **DuckLake** - DuckDB integration

### Cloud Integration

- **MinIO** - Local S3-compatible storage
- **AWS S3** - Cloud storage integration
- **Catalogs** - SQL and REST catalog support

## Example: Quick Start

```python
# In a Jupyter notebook
from dataset_generator import create_generator, create_writer, write_dataset
from datetime import date
import polars as pl

# Create generator
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=1000,
    orders_per_day=100,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 7),
)

# Create writer
writer = create_writer("parquet", output_uri="./data")

# Generate data
write_dataset(generator, writer)

# Read and explore
customers = pl.read_parquet("./data/customers/customers.parquet")
print(f"Generated {len(customers)} customers")
print(customers.head())
```

## Advanced Examples

### Performance Testing

```python
# Large dataset for benchmarking
generator = create_generator(
    "ecommerce",
    n_customers=100_000,
    orders_per_day=10_000,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
)

# Time the generation
import time
start = time.time()
write_dataset(generator, writer)
print(f"Generated in {time.time() - start:.2f} seconds")
```

### Data Analysis

```python
# Analyze generated data
orders = pl.read_parquet("./data/orders/year=2024/month=01/day=01/*.parquet")

# Daily order counts
daily_orders = (
    orders
    .group_by("order_date")
    .agg(pl.count("order_id").alias("order_count"))
    .sort("order_date")
)

print(daily_orders)
```

## Best Practices

### Memory Management

- **Start small** - Test with small datasets first
- **Monitor memory** - Use `%%memit` magic for memory profiling
- **Clear variables** - Delete large DataFrames when done

### Performance

- **Use appropriate file sizes** - 250K-1M rows per file
- **Choose right compression** - Snappy for speed, Zstd for size
- **Leverage partitioning** - Time-based partitions for queries

### Reproducibility

- **Set seeds** - Use fixed seeds for reproducible results
- **Document parameters** - Keep track of generation settings
- **Version control** - Store notebooks in git

## Troubleshooting

### Common Issues

**Kernel crashes**
- Reduce dataset size
- Increase available memory
- Use streaming for large datasets

**Slow performance**
- Check disk I/O
- Optimize file sizes
- Use appropriate compression

**Import errors**
- Verify installation
- Check virtual environment
- Restart kernel

## Next Steps

- **[Marimo Apps](marimo.md)** - Interactive web applications
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides
- **[API Reference](../api/core.md)** - Complete documentation