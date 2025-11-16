# Troubleshooting

Common issues and solutions for Dataset Generator.

## Quick Reference

| Problem | Category | Solution |
|---------|----------|----------|
| `ImportError: No module named 'dataset_generator'` | Installation | Install the package: `pip install dataset-generator` |
| `FileNotFoundError` | Configuration | Check file paths and permissions |
| Memory errors | Performance | Reduce dataset size or use streaming |
| S3 connection failures | Storage | Verify credentials and endpoint |
| Schema validation errors | Data | Check generator configuration |

## Installation Issues

### ImportError: No module named 'dataset_generator'

**Symptoms:**
```python
ImportError: No module named 'dataset_generator'
```

**Causes:**
- Package not installed
- Wrong virtual environment
- Python path issues

**Solutions:**

1. Install the package:
```bash
pip install dataset-generator
```

2. Install with extras for specific features:
```bash
# For CLI tools
pip install dataset-generator[cli]

# For Delta Lake support
pip install dataset-generator[delta]

# For Apache Iceberg
pip install dataset-generator[iceberg]

# For DuckLake support
pip install dataset-generator[ducklake]

# Install all features
pip install dataset-generator[cli,delta,iceberg,ducklake]
```

3. Check virtual environment:
```bash
# Verify current environment
which python
pip list | grep dataset-generator

# Activate correct environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Missing Optional Dependencies

**Symptoms:**
```python
ImportError: No module named 'delta'
ImportError: No module named 'pyarrow'
ImportError: No module named 's3fs'
```

**Solutions:**

1. Install required extras:
```bash
# For Delta Lake
pip install dataset-generator[delta]

# For Iceberg
pip install dataset-generator[iceberg]

# For S3 support
pip install s3fs
```

2. Install manually:
```bash
pip install deltalake pyarrow s3fs duckdb
```

## Configuration Issues

### FileNotFoundError

**Symptoms:**
```python
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/output'
PermissionError: [Errno 13] Permission denied: '/protected/path'
```

**Solutions:**

1. Create output directory:
```python
import os
from pathlib import Path

output_path = Path("./my_data")
output_path.mkdir(parents=True, exist_ok=True)
```

2. Check permissions:
```bash
# Check directory permissions
ls -la /path/to/output

# Fix permissions (if needed)
chmod 755 /path/to/output
```

3. Use absolute paths:
```python
from pathlib import Path

# Use absolute paths to avoid ambiguity
output_path = Path("/absolute/path/to/data").resolve()
writer = create_writer("parquet", str(output_path))
```

### Invalid Configuration Parameters

**Symptoms:**
```python
ValueError: Invalid generator type: invalid_generator
ValueError: Unknown writer type: unknown_writer
```

**Solutions:**

1. Check valid generator types:
```python
from dataset_generator.core.factory import GENERATOR_REGISTRY
print(list(GENERATOR_REGISTRY.keys()))
# Output: ['ecommerce', 'market_ohlcv', 'market_quotes', 'sensors', 'weather']
```

2. Check valid writer types:
```python
from dataset_generator.core.factory import WRITER_REGISTRY
print(list(WRITER_REGISTRY.keys()))
# Output: ['parquet', 'delta', 'iceberg', 'ducklake']
```

3. Use proper configuration:
```python
# Correct configuration
generator = create_generator("ecommerce", seed=42, n_customers=1000)
writer = create_writer("parquet", "./output")
```

## Performance Issues

### Memory Errors

**Symptoms:**
```python
MemoryError: Unable to allocate array
OutOfMemoryError: Python is out of memory
```

**Solutions:**

1. Reduce dataset size:
```python
# Use smaller datasets
generator = create_generator("ecommerce", 
    seed=42,
    n_customers=1000,      # Reduce from 10000
    orders_per_day=100,    # Reduce from 1000
)
```

2. Use file targeting:
```python
from dataset_generator import WriterOptions

writer_options = WriterOptions(
    file_rows_target=50_000,  # Smaller files
    compression="snappy"      # Efficient compression
)

writer = create_writer("parquet", "./output", options=writer_options)
```

3. Process in chunks:
```python
# Generate data in smaller time ranges
from datetime import date, timedelta

start_date = date(2024, 1, 1)
for i in range(12):  # 12 months
    end_date = start_date + timedelta(days=30)
    
    partition_spec = PartitionSpec(start_date=start_date, end_date=end_date)
    write_dataset(generator, writer, partition_spec)
    
    start_date = end_date
```

### Slow Performance

**Symptoms:**
- Generation takes many hours
- High CPU usage
- Slow file I/O

**Solutions:**

1. Optimize file sizes:
```python
writer_options = WriterOptions(
    file_rows_target=250_000,  # Optimal for Parquet
    compression="zstd",         # Better compression
)

writer = create_writer("parquet", "./output", options=writer_options)
```

2. Use appropriate compression:
```python
# For speed
writer_options = WriterOptions(compression="snappy")

# For size
writer_options = WriterOptions(compression="zstd")
```

3. Parallel processing:
```python
import multiprocessing as mp

# Dataset Generator automatically uses available cores
# Monitor usage with: htop or Activity Monitor
```

## Storage Issues

### S3 Connection Failures

**Symptoms:**
```python
botocore.exceptions.NoCredentialsError: Unable to locate credentials
botocore.exceptions.ClientError: An error occurred (403)
ConnectionError: Failed to establish connection
```

**Solutions:**

1. Verify S3 configuration:
```python
from dataset_generator import S3Config

# Check configuration
s3_config = S3Config(
    uri="s3://my-bucket/data/",
    endpoint_url="https://s3.amazonaws.com",  # For AWS S3
    key="your-access-key",
    secret="your-secret-key",
    region="us-east-1",
    secure=True
)
```

2. Test connection:
```python
import boto3

# Test S3 connection
s3_client = boto3.client(
    's3',
    endpoint_url=s3_config.endpoint_url,
    aws_access_key_id=s3_config.key,
    aws_secret_access_key=s3_config.secret,
    region_name=s3_config.region
)

try:
    s3_client.list_buckets()
    print("S3 connection successful")
except Exception as e:
    print(f"S3 connection failed: {e}")
```

3. For MinIO (local S3):
```python
s3_config = S3Config(
    uri="s3://test-bucket/data/",
    endpoint_url="http://localhost:9000",  # MinIO endpoint
    key="minioadmin",
    secret="minioadmin",
    secure=False  # HTTP for local development
)
```

### Permission Issues

**Symptoms:**
```python
PermissionError: [Errno 13] Permission denied
AccessDenied: Access Denied
```

**Solutions:**

1. Check file permissions:
```bash
# Check current permissions
ls -la /path/to/output

# Fix permissions
chmod 755 /path/to/output
chown $USER:$USER /path/to/output
```

2. Use appropriate S3 permissions:
```python
# For AWS S3, ensure IAM policy includes:
# - s3:PutObject
# - s3:GetObject
# - s3:ListBucket
# - s3:DeleteObject
```

## Data Issues

### Schema Validation Errors

**Symptoms:**
```python
SchemaError: Invalid column type
ValidationError: Missing required column
```

**Solutions:**

1. Check expected schema:
```python
generator = create_generator("ecommerce", seed=42)
schema = generator.get_schema()

print("Expected schema:")
for table_name, schema in schema.items():
    print(f"  {table_name}:")
    for col_name, dtype in schema.items():
        print(f"    {col_name}: {dtype}")
```

2. Validate data before writing:
```python
data = generator.generate(partition_spec)

# Validate schema matches
for table_name, df in data.items():
    expected_schema = generator.get_schema().get(table_name)
    if expected_schema:
        for col_name, dtype in expected_schema.items():
            assert col_name in df.columns, f"Missing column: {col_name}"
            assert df[col_name].dtype == dtype, f"Wrong type for {col_name}"
```

### Data Quality Issues

**Symptoms:**
- Null values in required fields
- Invalid dates or relationships
- Duplicate primary keys

**Solutions:**

1. Add data validation:
```python
def validate_data_quality(data):
    """Validate data quality rules"""
    for table_name, df in data.items():
        print(f"Validating {table_name}...")
        
        # Check for null primary keys
        if 'id' in df.columns:
            null_count = df['id'].null_count()
            if null_count > 0:
                print(f"  Warning: {null_count} null IDs found")
        
        # Check for duplicates
        if table_name == 'customers':
            customer_ids = df['customer_id']
            duplicates = len(customer_ids) - len(customer_ids.unique())
            if duplicates > 0:
                print(f"  Warning: {duplicates} duplicate customer IDs found")

# Validate before writing
validate_data_quality(data)
write_dataset(generator, writer, partition_spec)
```

2. Use constraints:
```python
generator = create_generator("ecommerce", 
    seed=42,
    constraints={
        'no_null_primary_keys': True,
        'valid_email_format': True,
        'positive_amounts': True
    }
)
```

## Writer-Specific Issues

### Parquet Writer Issues

**Symptoms:**
```python
pyarrow.lib.ArrowInvalid: Column type not supported
File size too large
```

**Solutions:**

1. Check supported types:
```python
# Polars to PyArrow type mapping
SUPPORTED_TYPES = {
    pl.Int8: "int8",
    pl.Int16: "int16", 
    pl.Int32: "int32",
    pl.Int64: "int64",
    pl.Float32: "float",
    pl.Float64: "double",
    pl.Utf8: "string",
    pl.Boolean: "bool",
    pl.Date: "date32",
    pl.Datetime: "timestamp[us]"
}
```

2. Optimize file sizes:
```python
writer_options = WriterOptions(
    file_rows_target=250_000,  # Smaller files
    compression="snappy"       # Compatible compression
)
```

### Delta Lake Writer Issues

**Symptoms:**
```python
ValueError: Delta table not found
pydelta lake transaction conflicts
```

**Solutions:**

1. Initialize Delta table:
```python
from delta.tables import DeltaTable

# Check if table exists
table_path = "./delta_data/customers"
if not DeltaTable.isDeltaTable(spark, table_path):
    # Create table schema
    spark.sql(f"""
        CREATE TABLE delta.`{table_path}` 
        USING DELTA
        (customer_id STRING, name STRING, email STRING)
    """)
```

2. Configure catalog:
```python
from dataset_generator import CatalogConfig

catalog_config = CatalogConfig(
    type="hive",
    warehouse_path="./delta_warehouse"
)

writer = create_writer("delta", "./delta_data", catalog=catalog_config)
```

### Iceberg Writer Issues

**Symptoms:**
```python
NoSuchTableException: Table not found
Catalog initialization failed
```

**Solutions:**

1. Configure Iceberg catalog:
```python
from dataset_generator import CatalogConfig

# Using SQL catalog
catalog_config = CatalogConfig(
    type="sql",
    connection="sqlite:///iceberg.db",
    warehouse_path="./iceberg_warehouse"
)

# Using REST catalog
catalog_config = CatalogConfig(
    type="rest",
    uri="http://localhost:8181",
    warehouse_path="./iceberg_warehouse"
)
```

2. Initialize table:
```python
# Iceberg tables need explicit initialization
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "local",
    **catalog_config.to_pyiceberg_kwargs()
)

# Create namespace if needed
if "my_database" not in catalog.list_namespaces():
    catalog.create_namespace("my_database")
```

## Debugging Tools

### Logging Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or specifically for dataset_generator
logger = logging.getLogger("dataset_generator")
logger.setLevel(logging.DEBUG)
```

### Progress Monitoring

```python
def progress_callback(status: str):
    """Track generation progress"""
    print(f"[{datetime.datetime.now()}] {status}")

# Use progress callback
write_dataset(generator, writer, progress_callback=progress_callback)
```

### Memory Profiling

```python
import psutil
import os

def monitor_memory():
    """Monitor memory usage"""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")

# Monitor during generation
monitor_memory()
data = generator.generate(partition_spec)
monitor_memory()
```

## Getting Help

### Check Logs

```bash
# Check Python logs
tail -f /var/log/python.log

# Check application logs
tail -f ~/.dataset_generator/logs/app.log
```

### Generate Debug Information

```python
import sys
import platform
from dataset_generator import __version__

def generate_debug_info():
    """Generate debug information"""
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "dataset_generator_version": __version__,
        "installed_packages": [
            f"{pkg.key}=={pkg.version}" 
            for pkg in pkg_resources.working_set
            if pkg.key.startswith(('dataset-generator', 'delta', 'pyarrow', 's3fs'))
        ]
    }
    
    print("Debug Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")

generate_debug_info()
```

### Report Issues

When reporting issues, include:

1. **Environment information** (Python version, OS)
2. **Package versions** (dataset-generator and dependencies)
3. **Exact error messages** and stack traces
4. **Minimal reproduction** code
5. **Configuration details** used

### Community Support

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share experiences
- **Documentation**: Check latest docs for updates

## Related Resources

- **[Getting Started](../getting-started/quick-start.md)** - Quick start guide
- **[Configuration](configuration.md)** - Configuration options
- **[API Reference](../api/core.md)** - Complete API documentation
- **[Contributing Guide](../development/contributing.md)** - Development guidelines
