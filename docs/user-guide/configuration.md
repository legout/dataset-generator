# Configuration

This guide covers advanced configuration options for Dataset Generator.

## Core Configuration

### Generator Configuration

```python
from dataset_generator import create_generator, WriterOptions

# Basic configuration
generator = create_generator(
    "ecommerce",
    seed=42,                    # Reproducibility
    n_customers=10_000,         # Number of customers
    n_products=1_000,           # Number of products
    orders_per_day=5_000,       # Daily order volume
    start_date=date(2024, 1, 1), # Start date
    end_date=date(2024, 1, 31), # End date
    file_rows_target=250_000,   # File size target
)
```

### Writer Configuration

```python
from dataset_generator import create_writer, WriterOptions, S3Config, CatalogConfig

# Writer options
options = WriterOptions(
    file_rows_target=250_000,   # Target rows per file
    compression="snappy",       # Compression codec
)

# S3 configuration
s3_config = S3Config(
    uri="s3://my-bucket",
    key="access-key",
    secret="secret-key",
    endpoint_url="https://s3.amazonaws.com",
    region="us-west-2",
)

# Catalog configuration
catalog_config = CatalogConfig(
    kind="sql",                 # Catalog type
    uri="sqlite:///catalog.db", # Catalog connection
    namespace="default",        # Namespace/Database
)

# Create writer
writer = create_writer(
    "delta",
    output_uri="s3://my-bucket/data",
    s3=s3_config,
    catalog=catalog_config,
    options=options,
)
```

## Partitioning

### Time-based Partitioning

```python
from dataset_generator.core.interfaces import PartitionSpec

# Daily partitions (default)
partition_spec = PartitionSpec(columns=("year", "month", "day"))

# Monthly partitions
partition_spec = PartitionSpec(columns=("year", "month"))

# Yearly partitions
partition_spec = PartitionSpec(columns=("year"))

# Custom partitioning
partition_spec = PartitionSpec(columns=("region", "year", "month"))
```

### Partition Selection Guidelines

| Dataset Size | Recommended Partitioning |
|--------------|-------------------------|
| < 1GB        | No partitioning or yearly |
| 1GB - 100GB  | Monthly partitions |
| 100GB - 1TB  | Daily partitions |
| > 1TB        | Hourly or daily partitions |

## Performance Tuning

### Memory Optimization

```python
# For memory-constrained environments
generator = create_generator(
    "ecommerce",
    n_customers=1_000,          # Fewer customers
    orders_per_day=100,         # Fewer orders
    file_rows_target=50_000,    # Smaller files
)
```

### Speed Optimization

```python
# For faster generation
generator = create_generator(
    "ecommerce",
    file_rows_target=1_000_000, # Larger files
    # ... other params
)

writer = create_writer(
    "parquet",
    options=WriterOptions(
        compression="snappy",   # Fast compression
    ),
)
```

### Storage Optimization

```python
# For storage efficiency
writer = create_writer(
    "parquet",
    options=WriterOptions(
        file_rows_target=500_000,
        compression="zstd",     # Better compression
    ),
)
```

## S3 Configuration

### AWS S3

```python
s3_config = S3Config(
    uri="s3://my-bucket",
    key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region="us-west-2",
)
```

### MinIO

```python
s3_config = S3Config(
    uri="s3://minio-bucket",
    key="minioadmin",
    secret="minioadmin",
    endpoint_url="http://localhost:9000",
    region="us-east-1",
)
```

### Other S3-compatible Services

```python
s3_config = S3Config(
    uri="s3://bucket-name",
    key="access-key",
    secret="secret-key",
    endpoint_url="https://s3-provider.com",
    region="auto",
)
```

## Catalog Configuration

### SQLite Catalog (Local)

```python
catalog_config = CatalogConfig(
    kind="sql",
    uri="sqlite:///catalog.db",
    namespace="production",
)
```

### PostgreSQL Catalog

```python
catalog_config = CatalogConfig(
    kind="sql",
    uri="postgresql://user:pass@localhost:5432/iceberg",
    namespace="analytics",
)
```

### REST Catalog

```python
catalog_config = CatalogConfig(
    kind="rest",
    uri="https://iceberg-catalog.example.com",
    namespace="data_warehouse",
)
```

## Environment Variables

```bash
# AWS credentials
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-west-2

# Alternative S3 credentials
export S3_ACCESS_KEY=your-access-key
export S3_SECRET_KEY=your-secret-key
export S3_ENDPOINT=https://s3.amazonaws.com
export S3_REGION=us-west-2
```

## Advanced Options

### Custom Seeds

```python
# Use timestamp for unique datasets
import time
generator = create_generator("ecommerce", seed=int(time.time()))

# Use fixed seed for reproducible testing
generator = create_generator("ecommerce", seed=12345)
```

### Batch Processing

```python
# Process in chunks for very large datasets
from datetime import timedelta

start_date = date(2024, 1, 1)
end_date = date(2024, 12, 31)

# Generate month by month
current_date = start_date
while current_date <= end_date:
    month_end = min(current_date + timedelta(days=30), end_date)
    
    generator = create_generator(
        "ecommerce",
        start_date=current_date,
        end_date=month_end,
        # ... other params
    )
    
    write_dataset(generator, writer)
    current_date = month_end + timedelta(days=1)
```

## Troubleshooting

### Common Issues

**Memory errors with large datasets**
- Reduce `n_customers` and `n_products`
- Decrease `file_rows_target`
- Process in smaller time chunks

**Slow S3 uploads**
- Check network connectivity
- Increase `file_rows_target` for fewer files
- Use appropriate S3 endpoint

**Catalog connection errors**
- Verify catalog URI is accessible
- Check credentials and permissions
- Ensure catalog service is running

### Performance Monitoring

```python
import time
from dataset_generator import write_dataset

start_time = time.time()
write_dataset(generator, writer, show_progress=True)
end_time = time.time()

print(f"Generation completed in {end_time - start_time:.2f} seconds")
```

## Best Practices

1. **Start small** - Test with small datasets first
2. **Use appropriate compression** - Balance speed vs. storage
3. **Choose right partitioning** - Based on query patterns
4. **Monitor resources** - Memory and disk usage
5. **Use environment variables** - For sensitive credentials

## Next Steps

- **[S3 Integration](s3.md)** - Cloud storage setup
- **[User Guide](index.md)** - Complete usage guide
- **[API Reference](../api/core.md)** - Advanced API usage