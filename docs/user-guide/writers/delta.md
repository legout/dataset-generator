# Delta Lake Writer

The Delta Lake writer provides ACID transactions, time travel, and schema enforcement for reliable data lake operations.

## Overview

Delta Lake adds these capabilities to Parquet:
- **ACID transactions** with isolation guarantees
- **Time travel** to query historical versions
- **Schema enforcement** and evolution
- **Upsert and merge** operations
- **Optimized writes** with Z-ordering

## Configuration

```python
writer = create_writer(
    "delta",
    output_uri="./delta-tables",
    options=WriterOptions(
        file_rows_target=250_000,
        compression="snappy",
    ),
)
```

## Usage Examples

### CLI

```bash
dataset-generator generate ecommerce \
  --format delta \
  --output ./delta-data \
  --start 2024-01-01 \
  --end 2024-01-31
```

### Python

```python
writer = create_writer(
    "delta",
    output_uri="s3://bucket/delta-tables",
    s3=S3Config(uri="s3://bucket", key="...", secret="..."),
)
```

## Features

### Time Travel

```python
import delta

# Query as of specific timestamp
df = delta.DeltaTable("./delta-tables/orders").as_of(1704067200).to_pandas()

# Query specific version
df = delta.DeltaTable("./delta-tables/orders").version_as_of(5).to_pandas()
```

### Schema Evolution

Delta Lake automatically handles:
- Adding new columns
- Relaxing data types
- Renaming columns (with explicit operations)

### Vacuum and Optimization

```python
# Remove old files
table = delta.DeltaTable("./delta-tables/orders")
table.vacuum(retention_hours=24)

# Optimize file sizes
table.optimize.z_order(["order_date", "customer_id"])
```

## Use Cases

- **Streaming data** with exactly-once guarantees
- **Machine learning** with feature versioning
- **Compliance** with data audit trails
- **Concurrent access** from multiple processes

## Next Steps

- **[Parquet Writer](parquet.md)** - Basic columnar storage
- **[Iceberg Writer](iceberg.md)** - For massive datasets
- **[Configuration](../configuration.md)** - Advanced options