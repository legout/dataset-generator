# API Reference

The API reference provides detailed documentation for all Dataset Generator classes and functions.

## Core API

The core API is automatically generated from the source code. See the [generated API documentation](../api/) for complete details.

## Main Functions

### create_generator()

Creates a data generator instance.

```python
from dataset_generator import create_generator

generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=1000,
    orders_per_day=500,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
)
```

### create_writer()

Creates a writer instance for outputting data.

```python
from dataset_generator import create_writer

writer = create_writer(
    "parquet",
    output_uri="./data",
    options=WriterOptions(
        file_rows_target=250_000,
        compression="snappy",
    ),
)
```

### write_dataset()

Executes the data generation pipeline.

```python
from dataset_generator import write_dataset

write_dataset(generator, writer, show_progress=True)
```

## Available Generators

- **ECommerceGenerator** - E-commerce data generation
- **MarketOHLCVGenerator** - Market OHLCV data
- **MarketQuotesGenerator** - Real-time market quotes
- **SensorsGenerator** - IoT sensor data
- **WeatherGenerator** - Weather station data

## Available Writers

- **ParquetPartitionedWriter** - Parquet format output
- **DeltaLakeWriter** - Delta Lake format output
- **IcebergWriter** - Apache Iceberg format output
- **DuckLakeWriter** - DuckLake format output

## Configuration Classes

- **S3Config** - S3 storage configuration
- **CatalogConfig** - Catalog configuration
- **WriterOptions** - Writer options
- **PartitionSpec** - Partition specification

For complete API documentation, see the [generated reference](../api/).