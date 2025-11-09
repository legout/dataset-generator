<div align="center">

# Dataset Generator

Synthetic data pipelines for lakehouse tables.

</div>

## Overview

`dataset-generator` creates realistic fake datasets and streams them into lake-friendly table layouts. The first bundled generator focuses on e-commerce events and can materialize data into partitioned Parquet, Delta Lake, Apache Iceberg, or DuckLake tables on the local filesystem or S3-compatible storage.

## Features

- Modular generators with partition-aware batch streaming.
- Writer abstraction covering Parquet, Delta Lake, Iceberg (SQL catalog), and DuckLake (DuckDB extension).
- Configurable S3 connectivity and catalog backends via dataclasses.
- Typer-powered CLI with dataset listing, metadata inspection, and end-to-end generation.
- Extensible architecture intended for future synthetic domains (market data, sensors, weather, ...).

## Installation

Python 3.12+ is required.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .          # base (Parquet)
pip install -e .[cli]     # CLI support
pip install -e .[delta]   # Delta Lake writer
pip install -e .[iceberg] # Apache Iceberg writer
pip install -e .[ducklake]# DuckLake writer
```

Optional extras can be combined (e.g. `pip install -e .[cli,delta]`).

## 📚 Documentation

For comprehensive documentation, visit **[dataset-generator.readthedocs.io](https://dataset-generator.readthedocs.io/)**

- **[Getting Started](https://dataset-generator.readthedocs.io/getting-started/installation/)** - Installation and setup
- **[User Guide](https://dataset-generator.readthedocs.io/user-guide/)** - Complete usage guide
- **[API Reference](https://dataset-generator.readthedocs.io/api/core/)** - Full API documentation
- **[Examples](https://dataset-generator.readthedocs.io/examples/jupyter/)** - Interactive notebooks

## Quick start (Python)

```python
from datetime import date

from dataset_generator import (
    S3Config,
    create_generator,
    create_writer,
    WriterOptions,
    write_dataset,
)

generator = create_generator(
    "ecommerce",
    seed=42,
    n_customers=50_000,
    n_products=10_000,
    orders_per_day=30_000,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 7),
    file_rows_target=250_000,
)

writer = create_writer(
    "parquet",
    output_uri="s3://bucket/prefix",
    s3=S3Config(uri="s3://bucket", key="...", secret="...", endpoint_url="https://..."),
    catalog=None,
    options=WriterOptions(compression="snappy"),
)

write_dataset(generator, writer)
```

## CLI usage

```
dataset-generator list-datasets
dataset-generator list-formats
dataset-generator info ecommerce

dataset-generator generate \
  ecommerce \
  --format delta \
  --output ./warehouse \
  --seed 777 \
  --start 2023-01-01 \
  --end 2023-01-31 \
  --n-customers 200000 \
  --orders-per-day 80000 \
  --file-rows-target 250000
```

S3 credentials can be passed via options (`--s3-uri`, `--s3-key`, `--s3-secret`, `--s3-endpoint`) or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.). Catalog parameters (`--catalog-kind`, `--catalog-uri`, `--catalog-namespace`) are required for Iceberg and DuckLake writers.

## Examples

Interactive notebooks live under [`examples/`](examples/):

- Jupyter: partitioned Parquet and Delta Lake tutorials.
- Marimo: adjustable control panel to regenerate data and inspect order summaries.

Follow the [examples README](examples/README.md) for environment setup and launch commands.

## Testing

```bash
. .venv/bin/activate
python -m unittest discover -s tests
```

## Roadmap

- Additional data domains (market data, IoT sensors, weather feeds).
- Extended CLI commands (profiling, schema export, validation).
- Optional connectors for cloud-native catalogs.

Contributions and ideas are welcome.
