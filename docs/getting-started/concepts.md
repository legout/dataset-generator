# Basic Concepts

Understanding the core concepts of Dataset Generator will help you use it effectively.

## Architecture Overview

Dataset Generator follows a simple but powerful architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Generators    │───▶│     Pipeline     │───▶│     Writers     │
│                 │    │                  │    │                 │
│ • Data Logic    │    │ • Streaming      │    │ • Format Logic  │
│ • Schemas       │    │ • Partitioning   │    │ • Storage       │
│ • Validation    │    │ • Progress       │    │ • Catalogs      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### Generators

Generators create synthetic data with realistic patterns and relationships. Each generator:

- **Defines schemas** for the data it produces
- **Implements business logic** for realistic data generation
- **Supports partitioning** by time and other dimensions
- **Is configurable** through parameters

Available generators:
- **E-commerce** - Customers, products, orders, and order items
- **Market Data** - OHLCV data and real-time quotes
- **Sensors** - IoT sensor readings with various patterns
- **Weather** - Weather data for multiple locations

### Writers

Writers handle the output format and storage. Each writer:

- **Manages file organization** and partitioning
- **Handles format-specific details** (compression, metadata, etc.)
- **Integrates with storage systems** (local filesystem, S3, etc.)
- **Maintains table metadata** (when applicable)

Available writers:
- **Parquet** - Columnar storage with partitioning
- **Delta Lake** - ACID transactions with time travel
- **Apache Iceberg** - Table format for huge datasets
- **DuckLake** - DuckDB extension for lakehouse queries

### Pipeline

The pipeline orchestrates the generation process:

1. **Streams data** from generators in batches
2. **Applies partitioning** based on configuration
3. **Feeds data to writers** for storage
4. **Tracks progress** and provides feedback

## Key Concepts

### Partitioning

Data is automatically partitioned for efficient querying:

```python
# Default time-based partitioning
PartitionSpec(columns=("year", "month", "day"))

# Results in paths like:
# orders/year=2024/month=01/day=15/part-00000.parquet
```

### Streaming

Generators produce data in streams, not all at once:

- **Memory efficient** - Only small batches in memory
- **Scalable** - Can generate datasets larger than RAM
- **Progress tracking** - See generation progress in real-time

### Reproducibility

Use seeds for consistent results:

```python
# Same seed = same data every time
generator = create_generator("ecommerce", seed=42)
```

### Configuration

All components use dataclasses for configuration:

```python
@dataclass(frozen=True)
class WriterOptions:
    file_rows_target: int = 250_000
    compression: str = "snappy"
```

## Data Relationships

Generators create realistic relationships between entities:

**E-commerce Example:**
- Customers have multiple orders
- Orders contain multiple order items
- Order items reference products
- All entities have consistent foreign keys

## Performance Considerations

### Memory Usage

- **Streaming design** keeps memory usage low
- **Batch processing** balances speed and memory
- **Configurable batch sizes** for different systems

### File Sizes

- **Target file rows** controls output file size
- **Compression** reduces storage requirements
- **Partitioning** improves query performance

### Parallel Processing

- **Independent partitions** can be processed in parallel
- **Multiple writers** can work simultaneously
- **S3 multipart uploads** for large files

## Best Practices

### Start Small

```python
# Test with small datasets first
generator = create_generator(
    "ecommerce",
    n_customers=100,      # Small for testing
    orders_per_day=50,    # Small for testing
)
```

### Use Appropriate Formats

- **Parquet** - Best for analytics and compatibility
- **Delta Lake** - When you need ACID transactions
- **Iceberg** - For very large datasets (>TB)
- **DuckLake** - When using DuckDB for queries

### Configure Partitions Wisely

```python
# Daily partitions for recent data
PartitionSpec(columns=("year", "month", "day"))

# Monthly partitions for historical data
PartitionSpec(columns=("year", "month"))
```

### Monitor Performance

```python
# Enable progress tracking
write_dataset(generator, writer, show_progress=True)
```

## Next Steps

Now that you understand the concepts:

1. **[Try the Quick Start](quick-start.md)** - Generate your first dataset
2. **[Explore Generators](../user-guide/generators/ecommerce.md)** - Learn about available generators
3. **[Configure Writers](../user-guide/writers/parquet.md)** - Choose the right output format
4. **[Check Examples](../examples/jupyter.md)** - See real-world usage