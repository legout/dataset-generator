# User Guide

Welcome to the comprehensive user guide for Dataset Generator. This section covers everything you need to know to generate synthetic data effectively.

## Overview

Dataset Generator provides a flexible, extensible system for creating realistic synthetic datasets. Whether you need test data for development, datasets for performance testing, or examples for learning, this guide will help you get the most out of the library.

## What You'll Learn

- **[Generators](generators/ecommerce.md)** - Available data generators and their configurations
- **[Writers](writers/parquet.md)** - Output formats and storage options  
- **[Configuration](configuration.md)** - Advanced configuration options
- **[S3 Integration](s3.md)** - Working with cloud storage

## Key Features

### 🎯 Realistic Data
- Business logic that mimics real-world patterns
- Proper relationships between entities
- Realistic distributions and correlations

### 📊 Multiple Formats
- Parquet for analytics workloads
- Delta Lake for ACID transactions
- Apache Iceberg for massive datasets
- DuckLake for DuckDB integration

### ☁️ Cloud Native
- S3-compatible storage support
- Partitioned data organization
- Catalog integration for table formats

### 🔧 Highly Configurable
- Adjustable data volumes and characteristics
- Custom partitioning strategies
- Extensible architecture

## Common Use Cases

### Development Testing
Generate realistic test data for your applications:

```python
# Small dataset for development
generator = create_generator(
    "ecommerce",
    n_customers=100,
    orders_per_day=50,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 7),
)
```

### Performance Benchmarking
Create large datasets for testing performance:

```python
# Large dataset for benchmarking
generator = create_generator(
    "ecommerce", 
    n_customers=1_000_000,
    orders_per_day=100_000,
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
)
```

### Learning and Education
Generate data for learning data engineering concepts:

```python
# Educational dataset with clear patterns
generator = create_generator(
    "ecommerce",
    seed=42,  # Reproducible for teaching
    n_customers=1000,
    orders_per_day=100,
)
```

## Getting Help

If you need help beyond what's covered in this guide:

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Examples](../examples/jupyter.md)** - Working code examples
- **[API Reference](../api/core.md)** - Complete API documentation
- **[GitHub Issues](https://github.com/volker-lorrmann/dataset-generator/issues)** - Report bugs or request features

## Next Steps

1. **Choose a Generator** - Start with [E-commerce](generators/ecommerce.md) or explore other options
2. **Select a Writer** - [Parquet](writers/parquet.md) is great for getting started
3. **Configure Your Dataset** - Use the [Configuration Guide](configuration.md)
4. **Run Your Generation** - Follow the examples in each section

Let's dive into the specific components!