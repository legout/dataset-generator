# E-commerce Dataset Tutorial

Learn how to generate realistic e-commerce datasets using the Dataset Generator.

## Overview

The e-commerce generator creates synthetic data that mimics real-world online retail transactions, including customers, products, orders, and order items.

## Prerequisites

- Python 3.12+
- Dataset Generator installed with e-commerce support
- Basic understanding of e-commerce data structures

## Basic Usage

### 1. Simple E-commerce Dataset

```python
from dataset_generator import create_generator, create_writer, write_dataset
from datetime import date

# Create e-commerce generator
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=1000,
    n_products=500,
    orders_per_day=100,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
)

# Create writer for Parquet format
writer = create_writer("parquet", output_uri="./ecommerce_data")

# Generate the dataset
write_dataset(generator, writer)
```

### 2. Advanced Configuration

```python
# Configure realistic business parameters
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=10000,
    n_products=5000,
    orders_per_day=1000,
    order_items_mean=2.1,  # Average items per order
    order_items_std=0.8,    # Variation in order size
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    # Custom product categories distribution
    categories={
        "Electronics": 0.3,
        "Clothing": 0.25, 
        "Home": 0.2,
        "Books": 0.15,
        "Sports": 0.1
    }
)
```

## Generated Data Structure

### Customers Table
```python
# Customer demographics and attributes
- customer_id (string): Unique customer identifier
- name (string): Customer full name
- email (string): Email address
- phone (string): Phone number
- address (string): Street address
- city (string): City
- state (string): State/Province
- zip_code (string): Postal code
- country (string): Country
- created_at (datetime): Account creation date
- last_active (datetime): Last activity timestamp
- segment (string): Customer segment (Premium/Standard/Basic)
- lifetime_value (float): Estimated customer lifetime value
```

### Products Table
```python
# Product catalog information
- product_id (string): Unique product identifier
- name (string): Product name
- description (string): Product description
- category (string): Product category
- brand (string): Brand name
- price (float): Regular price
- sale_price (float): Discount price (if applicable)
- sku (string): Stock keeping unit
- weight (float): Product weight in kg
- dimensions (string): Product dimensions
- color (string): Product color
- size (string): Product size
- in_stock (boolean): Availability status
- created_at (datetime): Product addition date
```

### Orders Table
```python
# Order transaction records
- order_id (string): Unique order identifier
- customer_id (string): Reference to customer
- order_date (date): Order date
- order_time (datetime): Order timestamp
- status (string): Order status
- amount (float): Total order amount
- tax_amount (float): Tax charged
- shipping_amount (float): Shipping cost
- discount_amount (float): Applied discounts
- payment_method (string): Payment type
- shipping_address (string): Delivery address
- tracking_number (string): Shipment tracking
- created_at (datetime): Order creation time
- updated_at (datetime): Last update timestamp
```

### Order Items Table
```python
# Individual product line items
- order_item_id (string): Unique line item identifier
- order_id (string): Reference to order
- product_id (string): Reference to product
- quantity (integer): Number of units
- unit_price (float): Price per unit
- total_price (float): Line item total
- discount_percentage (float): Applied discount
- created_at (datetime): Line item creation
```

## Data Relationships

### Entity Relationship Model
```
Customers (1) ----< (n) Orders (1) ----< (n) Order Items
                       |                    |
                       |                    |
                       +                    +
Products (1) --------< (n) Order Items (n) >----- (1) Orders
```

### Join Examples
```python
import polars as pl

# Load generated data
customers = pl.read_parquet("ecommerce_data/customers/*.parquet")
orders = pl.read_parquet("ecommerce_data/orders/**/*.parquet")
order_items = pl.read_parquet("ecommerce_data/order_items/**/*.parquet")
products = pl.read_parquet("ecommerce_data/products/*.parquet")

# Customer order analysis
customer_orders = (
    orders
    .join(customers, on="customer_id")
    .group_by("customer_id", "name", "email")
    .agg([
        pl.count("order_id").alias("total_orders"),
        pl.sum("amount").alias("total_spent"),
        pl.mean("amount").alias("avg_order_value")
    ])
    .sort("total_spent", descending=True)
)

# Product sales analysis
product_sales = (
    order_items
    .join(orders, on="order_id")
    .join(products, on="product_id")
    .group_by("product_id", "name", "category")
    .agg([
        pl.sum("quantity").alias("total_sold"),
        pl.sum("total_price").alias("revenue"),
        pl.count("order_id").alias("unique_orders")
    ])
    .sort("revenue", descending=True)
)
```

## Customization Examples

### 1. Seasonal Demand Patterns
```python
# Create seasonal variation in order volume
import numpy as np
from datetime import date, timedelta

def seasonal_orders_per_day(current_date):
    """Simulate seasonal demand patterns"""
    # Peak seasons: Nov-Dec (holidays), Jun-Aug (summer)
    if current_date.month in [11, 12]:
        return int(np.random.normal(1500, 200))  # Holiday season
    elif current_date.month in [6, 7, 8]:
        return int(np.random.normal(1200, 150))  # Summer season
    else:
        return int(np.random.normal(800, 100))   # Regular season

# Apply seasonal pattern
generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=50000,
    orders_per_day_function=seasonal_orders_per_day,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
)
```

### 2. Customer Segmentation
```python
# Define customer segments with different behaviors
segments = {
    "premium": {
        "probability": 0.1,  # 10% of customers
        "order_frequency": 5.0,  # 5x average frequency
        "avg_order_value": 150.0,  # Higher spend
        "retention_rate": 0.9
    },
    "regular": {
        "probability": 0.7,  # 70% of customers
        "order_frequency": 1.0,  # Baseline frequency
        "avg_order_value": 75.0,
        "retention_rate": 0.7
    },
    "occasional": {
        "probability": 0.2,  # 20% of customers
        "order_frequency": 0.3,  # Infrequent shoppers
        "avg_order_value": 50.0,
        "retention_rate": 0.4
    }
}

generator = create_generator(
    "ecommerce",
    seed=42,
    customer_segments=segments,
    # ... other parameters
)
```

## Output Formats

### 1. Parquet (Default)
```python
writer = create_writer("parquet", "./ecommerce_data")
write_dataset(generator, writer)

# Results in:
# ecommerce_data/
# ├── customers/
# │   └── customers.parquet
# ├── orders/
# │   ├── year=2023/
# │   │   ├── month=01/
# │   │   │   └── day=01/
# │   │   │       └── part-0.parquet
# │   │   └── ...
# ├── order_items/
# │   └── year=2023/month=01/...
# └── products/
#     └── products.parquet
```

### 2. Delta Lake
```python
writer = create_writer("delta", "./ecommerce_data", s3=None, catalog=None)
write_dataset(generator, writer)

# Benefits: ACID transactions, time travel, schema evolution
```

### 3. Apache Iceberg
```python
writer = create_writer("iceberg", "./ecommerce_data", s3=None, catalog=None)
write_dataset(generator, writer)

# Benefits: Advanced partitioning, schema evolution, performance optimization
```

## Performance Tips

### 1. Memory Management
```python
# Use file targeting to control memory usage
writer_options = WriterOptions(
    file_rows_target=250_000,  # Balance between performance and memory
    compression="snappy"        # Fast compression
)

writer = create_writer("parquet", "./data", options=writer_options)
```

### 2. Parallel Processing
```python
# Use uvicorn for parallel generation
import multiprocessing

# Dataset Generator automatically uses available cores
# Monitor with: htop or Activity Monitor
```

### 3. Disk Space Planning
```python
# Rough estimates for 1 year of data:
# - 10K customers, 1K orders/day = ~2-5GB (Parquet)
# - 50K customers, 5K orders/day = ~10-25GB (Parquet)
# - Scale linearly with data volume
```

## Next Steps

- **[S3 with MinIO](s3-minio.md)** - Store datasets in cloud storage
- **[Custom Generator](custom-generator.md)** - Create domain-specific generators
- **[Examples](../examples/jupyter.md)** - Interactive notebook examples
- **[API Reference](../api/core.md)** - Complete API documentation

## Common Questions

### Q: How do I control data quality?
A: Use the `seed` parameter for reproducibility and adjust the randomness parameters to match your desired data characteristics.

### Q: Can I add custom fields?
A: Yes, you can extend the generator or post-process the generated data to add custom fields and business logic.

### Q: How realistic is the generated data?
A: The generator uses realistic distributions and business rules derived from e-commerce patterns, but should be validated against your specific use case.
