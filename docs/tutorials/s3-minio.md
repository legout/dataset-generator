# S3 with MinIO Tutorial

Learn how to store generated datasets in S3-compatible storage using MinIO for local development and testing.

## Overview

MinIO provides an S3-compatible object storage server that's perfect for local development and testing of cloud storage workflows. This tutorial shows how to configure Dataset Generator to work with MinIO.

## Prerequisites

- Python 3.12+
- Dataset Generator installed with S3 support
- Docker and Docker Compose
- Basic understanding of S3 concepts

## Setting Up MinIO

### 1. Docker Compose Configuration

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"  # API port
      - "9001:9001"  # Console port
    environment:
      - MINIO_ROOT_USER=demo
      - MINIO_ROOT_PASSWORD=demo1234
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

volumes:
  minio_data:
```

### 2. Start MinIO

```bash
# Start MinIO in the background
docker-compose up -d

# Check that it's running
docker-compose ps
```

### 3. Access MinIO Console

Open your browser and navigate to:
- **Console**: http://localhost:9001
- **API**: http://localhost:9000

Login with:
- **Username**: `demo`
- **Password**: `demo1234`

### 4. Create Buckets

Using the MinIO console or CLI:

```bash
# Create buckets
mc alias set local http://localhost:9000 demo demo1234
mc mb local/dataset-generator
mc mb local/test-data
mc ls local/
```

## Basic S3 Configuration

### 1. S3Config Object

```python
from dataset_generator import S3Config

# Configure MinIO connection
s3_config = S3Config(
    uri="s3://dataset-generator/data/",
    endpoint_url="http://localhost:9000",
    key="demo",
    secret="demo1234",
    region="us-east-1",  # Default region
    secure=False,  # Use HTTP for local development
)
```

### 2. Generator with S3 Output

```python
from dataset_generator import create_generator, create_writer, write_dataset
from datetime import date

# Create generator
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=1000,
    orders_per_day=100,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
)

# Create writer with S3 configuration
writer = create_writer(
    "parquet",
    output_uri="s3://dataset-generator/data/",
    s3=s3_config,
)

# Generate dataset to S3
write_dataset(generator, writer)
```

## Advanced S3 Configuration

### 1. Multiple S3 Endpoints

```python
# Configure multiple MinIO instances for testing
s3_configs = []

# Primary storage
s3_configs.append(S3Config(
    uri="s3://dataset-generator/primary/",
    endpoint_url="http://localhost:9000",
    key="demo",
    secret="demo1234",
))

# Backup storage  
s3_configs.append(S3Config(
    uri="s3://dataset-generator/backup/",
    endpoint_url="http://localhost:9001",
    key="demo",
    secret="demo1234",
))

# Use first config for generation
writer = create_writer("parquet", s3_config=s3_configs[0])
```

### 2. Catalog Integration

```python
from dataset_generator import CatalogConfig

# Configure with catalog
catalog_config = CatalogConfig(
    type="sql",
    connection="sqlite:///lakehouse.db",
    warehouse="lakehouse"
)

writer = create_writer(
    "iceberg",
    output_uri="s3://dataset-generator/iceberg/",
    s3=s3_config,
    catalog=catalog_config,
)
```

### 3. Writer Options

```python
from dataset_generator import WriterOptions

writer_options = WriterOptions(
    file_rows_target=250_000,
    compression="snappy",
    partition_by=["year", "month", "day"],
)

writer = create_writer(
    "parquet",
    output_uri="s3://dataset-generator/data/",
    s3=s3_config,
    options=writer_options,
)
```

## Working with S3 Data

### 1. Reading from S3

```python
import polars as pl
import s3fs

# Connect to S3
fs = s3fs.S3FileSystem(
    endpoint_url="http://localhost:9000",
    key="demo",
    secret="demo1234",
    client_kwargs={'region_name': 'us-east-1'},
    anon=False
)

# Read data from S3
customers = pl.read_parquet("s3://dataset-generator/data/customers/*.parquet", 
                           filesystem=fs)
orders = pl.read_parquet("s3://dataset-generator/data/orders/**/*.parquet",
                         filesystem=fs)

print(f"Loaded {len(customers)} customers")
print(f"Loaded {len(orders)} orders")
```

### 2. DuckDB Integration

```python
import duckdb

# Create DuckDB connection with S3 support
con = duckdb.connect()

# Install and load S3 extension
con.execute("INSTALL httpfs")
con.execute("LOAD httpfs")

# Configure S3 credentials
con.execute("""
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='demo';
    SET s3_secret_access_key='demo1234';
    SET s3_region='us-east-1';
    SET s3_url_style='path';
    SET s3_use_ssl=false;
""")

# Query data directly from S3
result = con.execute("""
    SELECT 
        COUNT(*) as total_orders,
        SUM(amount) as total_revenue,
        DATE_TRUNC('month', order_date) as month
    FROM read_parquet('s3://dataset-generator/data/orders/**/*.parquet')
    GROUP BY month
    ORDER BY month
""").fetchall()

print(result)
```

### 3. DataFusion Integration

```python
from datafusion import SessionContext
import s3fs

# Create DataFusion context
ctx = SessionContext()

# Register S3 filesystem
fs = s3fs.S3FileSystem(
    endpoint_url="http://localhost:9000",
    key="demo", 
    secret="demo1234",
    client_kwargs={'region_name': 'us-east-1'},
    anon=False
)

# Register S3 data as tables
ctx.register_parquet(
    "customers", 
    "s3://dataset-generator/data/customers/*.parquet",
    filesystem=fs
)

ctx.register_parquet(
    "orders",
    "s3://dataset-generator/data/orders/**/*.parquet", 
    filesystem=fs
)

# Execute SQL queries
df = ctx.sql("""
    SELECT 
        c.segment,
        COUNT(o.order_id) as order_count,
        AVG(o.amount) as avg_order_value
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY c.segment
""").to_pandas()

print(df)
```

## Monitoring and Debugging

### 1. Check S3 Upload Progress

```python
from dataset_generator import create_generator, create_writer, write_dataset
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create generator and writer
generator = create_generator("ecommerce", seed=42)
writer = create_writer("parquet", s3_config=s3_config)

# Monitor progress
try:
    write_dataset(generator, writer)
    logger.info("Dataset generation completed successfully")
except Exception as e:
    logger.error(f"Generation failed: {e}")
```

### 2. Verify S3 Uploads

```python
import boto3
from botocore.config import Config

# Create S3 client for MinIO
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='demo',
    aws_secret_access_key='demo1234',
    region_name='us-east-1',
    config=Config(s3={'addressing_style': 'path'}),
    verify=False
)

# List uploaded files
response = s3_client.list_objects_v2(
    Bucket='dataset-generator',
    Prefix='data/'
)

for obj in response.get('Contents', []):
    print(f"{obj['Key']}: {obj['Size']} bytes")
```

### 3. Check MinIO Logs

```bash
# View MinIO logs
docker-compose logs -f minio

# Check specific operations
docker-compose logs minio | grep "PUT\|GET"
```

## Best Practices

### 1. Data Organization

```python
# Use consistent naming conventions
output_uri = "s3://dataset-generator/{domain}/{source}/{version}/"

# Examples:
# s3://dataset-generator/ecommerce/production/v1/
# s3://dataset-generator/market_data/test/v2/
```

### 2. Error Handling

```python
from botocore.exceptions import ClientError
import time

def upload_with_retry(writer, generator, max_retries=3):
    """Upload with retry logic for transient errors"""
    for attempt in range(max_retries):
        try:
            write_dataset(generator, writer)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'SlowDown' and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
            raise
    return False
```

### 3. Performance Optimization

```python
# Use appropriate file sizes
writer_options = WriterOptions(
    file_rows_target=1_000_000,  # Larger files for S3
    compression="zstd",          # Better compression for network transfer
)

# Use multipart upload for large files
writer_options.multipart_threshold = 100 * 1024 * 1024  # 100MB
```

## Production Considerations

### 1. Security

```python
# Use IAM roles in production
s3_config = S3Config(
    uri="s3://production-data/",
    # No key/secret when using IAM roles
    region="us-west-2",
    secure=True,  # Use HTTPS
)

# Use SSL certificates
s3_client = boto3.client(
    's3',
    verify='/path/to/ca-bundle.crt'
)
```

### 2. Monitoring

```python
# Add CloudWatch metrics (in AWS)
import cloudwatch

cloudwatch.put_metric_data(
    Namespace='DatasetGenerator',
    MetricData=[
        {
            'MetricName': 'RowsGenerated',
            'Value': total_rows,
            'Unit': 'Count'
        },
        {
            'MetricName': 'UploadTime', 
            'Value': upload_time,
            'Unit': 'Seconds'
        }
    ]
)
```

### 3. Cost Optimization

```python
# Use lifecycle policies
lifecycle_policy = {
    'Rules': [
        {
            'ID': 'DeleteOldBackups',
            'Status': 'Enabled',
            'Transitions': [
                {
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'Days': 90,
                    'StorageClass': 'GLACIER'
                }
            ]
        }
    ]
}
```

## Troubleshooting

### Common Issues

**Connection timeouts**
```python
# Increase timeout settings
s3_config = S3Config(
    endpoint_url="http://localhost:9000",
    timeout=300,  # 5 minutes
    retries=10,
)
```

**Authentication failures**
```python
# Verify credentials
s3_client = boto3.client('s3', **s3_config.to_boto3_kwargs())
try:
    s3_client.list_buckets()
except Exception as e:
    print(f"Authentication failed: {e}")
```

**Performance issues**
```python
# Monitor with CloudWatch or MinIO metrics
# Check network bandwidth and latency
# Use multipart uploads for large files
```

## Next Steps

- **[Custom Generator](custom-generator.md)** - Create domain-specific generators
- **[E-commerce Dataset](ecommerce-dataset.md)** - Detailed e-commerce examples
- **[Examples](../examples/jupyter.md)** - Interactive notebook examples
- **[API Reference](../api/core.md)** - Complete API documentation

## Related Resources

- [MinIO Documentation](https://docs.min.io/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [DuckDB S3 Integration](https://duckdb.org/docs/guides/import/s3_import.html)
- [Apache Arrow S3FS](https://github.com/fsspec/s3fs)
