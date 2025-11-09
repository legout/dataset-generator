# Parquet Writer

The Parquet writer outputs data in Apache Parquet format, the most widely used columnar format for analytics workloads.

## Overview

Parquet is ideal for:
- **Analytics queries** with column pruning
- **Big data processing** with Spark/Presto/Trino
- **Cost-effective storage** with excellent compression
- **Schema evolution** with backward compatibility

## Configuration

### Basic Setup

```python
writer = create_writer(
    "parquet",
    output_uri="./data",
    options=WriterOptions(
        file_rows_target=250_000,    # Target rows per file
        compression="snappy",        # Compression codec
    ),
)
```

### Advanced Options

```python
writer = create_writer(
    "parquet",
    output_uri="s3://bucket/prefix",
    s3=S3Config(
        uri="s3://bucket",
        key="your-access-key",
        secret="your-secret-key",
        endpoint_url="https://s3.amazonaws.com",
    ),
    options=WriterOptions(
        file_rows_target=1_000_000,
        compression="zstd",          # Better compression, slower
    ),
)
```

## Compression Options

| Codec | Ratio | Speed | Use Case |
|-------|-------|-------|----------|
| `snappy` | Good | Fastest | General purpose |
| `gzip` | Better | Slower | Storage optimization |
| `zstd` | Best | Medium | Balance of speed/ratio |
| `brotli` | Excellent | Slowest | Maximum compression |

## Usage Examples

### CLI

```bash
# Basic Parquet output
dataset-generator generate ecommerce \
  --format parquet \
  --output ./ecommerce-data \
  --compression snappy \
  --file-rows-target 250000

# S3 with custom compression
dataset-generator generate ecommerce \
  --format parquet \
  --output s3://my-bucket/ecommerce \
  --s3-uri s3://my-bucket \
  --s3-key $AWS_ACCESS_KEY_ID \
  --s3-secret $AWS_SECRET_ACCESS_KEY \
  --compression zstd \
  --file-rows-target 1000000
```

### Python API

```python
from dataset_generator import create_writer, WriterOptions

# Local filesystem
writer = create_writer(
    "parquet",
    output_uri="./data",
    options=WriterOptions(
        file_rows_target=500_000,
        compression="snappy",
    ),
)

# S3-compatible storage
writer = create_writer(
    "parquet",
    output_uri="s3://bucket/data",
    s3=S3Config(
        uri="s3://bucket",
        key="access-key",
        secret="secret-key",
        endpoint_url="https://minio.example.com",
    ),
)
```

## Output Structure

Data is organized by table and partition:

```
data/
├── customers/
│   └── customers.parquet
├── products/
│   └── products.parquet
├── orders/
│   ├── year=2024/month=01/day=01/
│   │   ├── part-00000.parquet
│   │   └── part-00001.parquet
│   └── year=2024/month=01/day=02/
│       └── part-00000.parquet
└── order_items/
    ├── year=2024/month=01/day=01/
    │   └── part-00000.parquet
    └── ...
```

## Performance Considerations

### File Size Optimization

```python
# For large datasets (analytics workloads)
WriterOptions(file_rows_target=1_000_000, compression="zstd")

# For small datasets (development)
WriterOptions(file_rows_target=50_000, compression="snappy")
```

### Memory Usage

- **Streaming**: Data is written in batches, not all at once
- **Memory footprint**: Typically 100-500MB regardless of dataset size
- **Compression**: Happens during write, minimal memory impact

### I/O Patterns

- **Local storage**: Limited by disk speed
- **S3**: Uses multipart uploads for large files
- **Network**: Consider compression for remote storage

## Schema Handling

### Schema Evolution

Parquet supports schema evolution:

```python
# New columns are automatically added
# Existing columns maintain compatibility
# Data types can be relaxed (int → float)
```

### Data Types

All Polars data types are supported:

- **Numeric**: Int8, Int16, Int32, Int64, Float32, Float64
- **Temporal**: Date, Datetime, Duration
- **String**: Utf8
- **Boolean**: Boolean
- **Struct**: Nested structures
- **List**: Arrays

## Best Practices

### File Organization

```python
# Good: Daily partitions for recent data
PartitionSpec(columns=("year", "month", "day"))

# Good: Monthly partitions for historical data
PartitionSpec(columns=("year", "month"))

# Avoid: Too many small files
WriterOptions(file_rows_target=250_000)
```

### Compression Selection

```python
# Development/testing
WriterOptions(compression="snappy")

# Production analytics
WriterOptions(compression="zstd")

# Archive/cold storage
WriterOptions(compression="gzip")
```

### S3 Optimization

```python
# Enable S3 multipart for large files
WriterOptions(file_rows_target=1_000_000)

# Use appropriate region
S3Config(endpoint_url="https://s3.us-west-2.amazonaws.com")
```

## Querying Parquet Files

### DuckDB

```sql
-- Query specific partitions
SELECT * FROM read_parquet('data/orders/year=2024/month=01/*.parquet')
WHERE order_date >= '2024-01-15';

-- Query entire dataset
SELECT * FROM read_parquet('data/**/*.parquet');
```

### Pandas

```python
import pandas as pd

# Read specific files
df = pd.read_parquet('data/orders/year=2024/month=01/day=01/')

# Read with partition filtering
df = pd.read_parquet('data/orders/', filters=[
    ('year', '=', 2024),
    ('month', '=', 1)
])
```

### Spark

```scala
// Read with schema inference
val df = spark.read.parquet("data/orders/")

// Read with partition pruning
val df = spark.read
  .option("basePath", "data/orders/")
  .parquet("data/orders/year=2024/month=01/")
```

## Troubleshooting

### Common Issues

**Large number of small files**
- Increase `file_rows_target`
- Use coarser partitioning

**Slow writes to S3**
- Check network connectivity
- Use larger file sizes
- Consider compression

**Memory errors**
- Reduce batch size in generator
- Check for memory leaks in custom code

### Performance Tuning

```python
# For high-throughput generation
WriterOptions(
    file_rows_target=2_000_000,  # Larger files
    compression="snappy",        # Faster compression
)

# For storage optimization
WriterOptions(
    file_rows_target=500_000,    # Moderate files
    compression="zstd",          # Better compression
)
```

## Next Steps

- **[Delta Lake Writer](delta.md)** - ACID transactions and time travel
- **[Iceberg Writer](iceberg.md)** - For massive datasets
- **[DuckLake Writer](ducklake.md)** - DuckDB integration
- **[S3 Integration](../s3.md)** - Cloud storage setup