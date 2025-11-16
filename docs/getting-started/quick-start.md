# Quick Start

Get up and running with Dataset Generator in minutes. This guide will walk you through generating your first synthetic dataset.

## Your First Dataset

Let's generate an e-commerce dataset with realistic customer, product, and order data.

### Using the CLI

The fastest way to get started is with the command-line interface:

```bash
# Generate a week of e-commerce data
dataset-generator generate ecommerce \
  --format parquet \
  --output ./my-data \
  --start 2024-01-01 \
  --end 2024-01-07 \
  --n-customers 1000 \
  --orders-per-day 500 \
  --seed 42
```

This creates:
- **1,000 customers** with realistic profiles
- **3,500 orders** (500 per day for 7 days)
- **Partitioned Parquet files** in `./my-data/`
- **Reproducible data** using seed 42

### Using Python

For more control, use the Python API:

```python
from datetime import date
from dataset_generator import create_generator, create_writer, write_dataset

# Create an e-commerce data generator
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=1000,
    n_products=500,
    orders_per_day=500,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 7),
    file_rows_target=250_000,
)

# Create a Parquet writer
writer = create_writer(
    "parquet",
    output_uri="./my-data",
)

# Generate and write the dataset
write_dataset(generator, writer)
```

## Exploring the Output

The generated data is organized into tables with clear relationships:

```
my-data/
├── customers/
│   └── customers.parquet
├── products/
│   └── products.parquet
├── orders/
│   ├── year=2024/month=01/day=01/part-00000.parquet
│   ├── year=2024/month=01/day=02/part-00000.parquet
│   └── ...
└── order_items/
    ├── year=2024/month=01/day=01/part-00000.parquet
    └── ...
```

### Data Schema

**Customers**: customer_id, name, email, signup_date, country, is_vip  
**Products**: product_id, sku, category, price, discount, active  
**Orders**: order_id, customer_id, order_date, status, total_amount  
**Order Items**: order_item_id, order_id, product_id, quantity, unit_price

## Next Steps

### Try Different Formats

Experiment with different table formats:

```bash
# Delta Lake
dataset-generator generate ecommerce --format delta --output ./delta-data

# Apache Iceberg (requires catalog)
dataset-generator generate ecommerce \
  --format iceberg \
  --output ./iceberg-data \
  --catalog-kind sql \
  --catalog-uri sqlite:///iceberg_catalog.db

# DuckLake
dataset-generator generate ecommerce \
  --format ducklake \
  --output ./ducklake-data \
  --catalog-kind sql \
  --catalog-uri sqlite:///ducklake_catalog.db
```

### Scale Up

Generate larger datasets:

```bash
# Large dataset (100K customers, 10K orders/day)
dataset-generator generate ecommerce \
  --n-customers 100000 \
  --orders-per-day 10000 \
  --start 2024-01-01 \
  --end 2024-12-31
```

### Explore Other Generators

Try different data domains:

```bash
# Market data (OHLCV)
dataset-generator generate market-ohlcv \
  --format parquet \
  --output ./market-data \
  --symbols AAPL,GOOGL,MSFT \
  --start 2024-01-01 \
  --end 2024-01-31

# Sensor data
dataset-generator generate sensors \
  --format parquet \
  --output ./sensor-data \
  --n-sensors 100 \
  --start 2024-01-01 \
  --end 2024-01-07

# Weather data
dataset-generator generate weather \
  --format parquet \
  --output ./weather-data \
  --locations "New York,London,Tokyo" \
  --start 2024-01-01 \
  --end 2024-01-31
```

## What's Next?

- **[User Guide](../user-guide/index.md)** - Comprehensive documentation
- **[API Reference](../api/index.md)** - Complete API documentation  
- **[Tutorials](../tutorials/index.md)** - Step-by-step examples
- **[Examples](../examples/jupyter.md)** - Interactive notebooks

## Need Help?

- Check the [Troubleshooting Guide](../user-guide/troubleshooting.md)
- Browse [Examples](../examples/jupyter.md) for working code
- Open an issue on [GitHub](https://github.com/volker-lorrmann/dataset-generator/issues)