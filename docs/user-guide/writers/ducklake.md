# DuckLake Writer

The DuckLake writer integrates with DuckDB's lakehouse extension for efficient analytics and querying.

## Overview

DuckLake provides:
- **DuckDB integration** for fast analytics
- **Lakehouse architecture** with metadata management
- **SQL interface** to all your data
- **Performance optimization** with statistics

## Configuration

```python
writer = create_writer(
    "ducklake",
    output_uri="./ducklake-tables",
    catalog=CatalogConfig(
        kind="sql",
        uri="sqlite:///ducklake_catalog.db",
        namespace="default",
    ),
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
  --format ducklake \
  --output ./ducklake-data \
  --catalog-kind sql \
  --catalog-uri sqlite:///ducklake.db \
  --catalog-name default
```

### Python

```python
writer = create_writer(
    "ducklake",
    output_uri="./ducklake-tables",
    catalog=CatalogConfig(
        kind="sql",
        uri="sqlite:///catalog.db",
        namespace="analytics",
    ),
)
```

## Querying with DuckDB

### Direct Table Access

```python
import duckdb

# Connect to DuckDB
conn = duckdb.connect()

# Query DuckLake tables directly
result = conn.execute("""
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        COUNT(*) as order_count,
        SUM(total_amount) as revenue
    FROM ducklake_table('orders')
    WHERE order_date >= '2024-01-01'
    GROUP BY month
    ORDER BY month
""").fetchall()
```

### Automatic Registration

```python
# Tables are automatically registered in DuckDB
conn.execute("SHOW TABLES").fetchall()
# Returns: ['customers', 'products', 'orders', 'order_items']
```

## Features

### Statistics Collection

DuckLake automatically collects:
- **Row counts** for each table
- **Column statistics** for optimization
- **Partition information** for pruning

### Query Optimization

```python
# Automatic query optimization
# Partition pruning
# Predicate pushdown
# Column pruning
```

### Integration Benefits

- **Single interface** for all data formats
- **High performance** analytics queries
- **Familiar SQL** syntax
- **No separate** catalog service needed

## Use Cases

- **Analytics dashboards** with fast queries
- **Data exploration** and ad-hoc analysis
- **Reporting** with SQL-based tools
- **Machine learning** feature engineering

## Performance Tips

### File Organization

```python
# Optimize for DuckDB queries
WriterOptions(
    file_rows_target=500_000,  # Balanced file sizes
    compression="snappy",      # Fast decompression
)
```

### Query Optimization

```sql
-- Use DuckDB's optimized functions
SELECT 
    EXTRACT(YEAR FROM order_date) as year,
    EXTRACT(MONTH FROM order_date) as month,
    COUNT(*) as orders
FROM ducklake_table('orders')
GROUP BY year, month;
```

## Next Steps

- **[Parquet Writer](parquet.md)** - Basic storage format
- **[Delta Lake Writer](delta.md)** - ACID transactions
- **[Configuration](../configuration.md)** - Advanced setup