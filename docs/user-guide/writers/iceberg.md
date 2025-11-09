# Apache Iceberg Writer

The Apache Iceberg writer handles massive datasets with excellent performance and reliability at scale.

## Overview

Iceberg is designed for:
- **Petabyte-scale** datasets
- **Concurrent writes** from many processes
- **Schema evolution** without breaking changes
- **Hidden partitioning** with automatic optimization
- **Time travel** and rollback capabilities

## Configuration

```python
writer = create_writer(
    "iceberg",
    output_uri="./iceberg-tables",
    catalog=CatalogConfig(
        kind="sql",
        uri="sqlite:///iceberg_catalog.db",
        namespace="default",
    ),
    options=WriterOptions(
        file_rows_target=1_000_000,
        compression="snappy",
    ),
)
```

## Catalog Support

### SQL Catalog (SQLite)

```python
catalog=CatalogConfig(
    kind="sql",
    uri="sqlite:///iceberg_catalog.db",
    namespace="my_namespace",
)
```

### REST Catalog

```python
catalog=CatalogConfig(
    kind="rest",
    uri="http://iceberg-rest-catalog:8181",
    namespace="production",
)
```

## Usage Examples

### CLI

```bash
dataset-generator generate ecommerce \
  --format iceberg \
  --output ./iceberg-data \
  --catalog-kind sql \
  --catalog-uri sqlite:///iceberg.db \
  --catalog-name default \
  --n-customers 1000000 \
  --orders-per-day 50000
```

### Python

```python
writer = create_writer(
    "iceberg",
    output_uri="s3://bucket/iceberg-tables",
    catalog=CatalogConfig(
        kind="rest",
        uri="https://iceberg-catalog.example.com",
        namespace="analytics",
    ),
    s3=S3Config(uri="s3://bucket", key="...", secret="..."),
)
```

## Features

### Hidden Partitioning

Iceberg automatically handles partitioning:

```python
# Automatic partitioning by time
# No need to specify partition columns
# Optimized for query performance
```

### Schema Evolution

- **Add columns** without rewriting data
- **Rename columns** with metadata updates
- **Change types** (with compatibility checks)
- **Reorder columns** automatically

### Snapshots and Time Travel

```python
from iceberg import Table

table = Table.load("iceberg-tables.orders")

# Query as of timestamp
df = table.scan(as_of_ts=1704067200).to_pandas()

# Query specific snapshot
df = table.scan(snapshot_id=12345).to_pandas()
```

## Performance Optimization

### File Sizing

```python
# For large datasets (>1TB)
WriterOptions(file_rows_target=2_000_000)

# For medium datasets (100GB-1TB)
WriterOptions(file_rows_target=1_000_000)

# For smaller datasets (<100GB)
WriterOptions(file_rows_target=500_000)
```

### Compaction

Iceberg automatically handles:
- **Small file compaction**
- **Data clustering**
- **Partition evolution**

## Use Cases

- **Data warehousing** at enterprise scale
- **Machine learning** with massive feature stores
- **Real-time analytics** with streaming data
- **Multi-region** data replication

## Next Steps

- **[Delta Lake Writer](delta.md)** - ACID transactions
- **[Parquet Writer](parquet.md)** - Simple columnar storage
- **[DuckLake Writer](ducklake.md)** - DuckDB integration