# Project Context

## Purpose
Dataset Generator creates realistic synthetic data pipelines for lakehouse tables. It generates fake datasets and streams them into partitioned table formats (Parquet, Delta Lake, Apache Iceberg, DuckLake) with support for local filesystem and S3-compatible storage. The project focuses on e-commerce events initially but is designed to be extensible to other domains like market data, IoT sensors, and weather feeds.

## Tech Stack
- **Python 3.12+** - Core language
- **Polars** - High-performance data manipulation
- **NumPy** - Numerical computations
- **fsspec/s3fs** - Filesystem abstraction and S3 connectivity
- **Typer** - CLI framework
- **Delta Lake** - Optional Delta table format support
- **Apache Iceberg** - Optional Iceberg table format support  
- **DuckDB** - Optional DuckLake format support
- **PyArrow** - Arrow format support for Delta/Iceberg
- **uv** - Package management and build system

## Project Conventions

### Code Style
- Use `ruff` for linting and formatting
- Type hints required (uses `py.typed` for package typing)
- `from __future__ import annotations` in test files
- Dataclasses for configuration objects
- Factory pattern for generator/writer creation
- Interface-based architecture with abstract base classes

### Architecture Patterns
- **Generator Pattern**: Domain-specific data generators inheriting from `GeneratorBase`
- **Writer Pattern**: Format-specific writers implementing `TableWriter` interface
- **Factory Pattern**: Centralized creation of generators and writers via `create_generator()` and `create_writer()`
- **Pipeline Pattern**: `write_dataset()` orchestrates generation and writing
- **Configuration Pattern**: Dataclasses for S3, catalog, and writer options
- **Partition-aware**: All generators support `PartitionSpec` for time-based partitioning

### Testing Strategy
- Standard `unittest` framework
- Tests in `tests/` directory
- Use `TemporaryDirectory` for file system tests
- Test data generation with small datasets (50 customers, 30 products, etc.)
- Verify output schemas and partition structures
- Run with `python -m unittest discover -s tests`

### Git Workflow
- No specific branching strategy documented
- Standard gitignore for Python projects
- Uses semantic versioning (currently 0.1.0)

## Domain Context
- **E-commerce domain**: Customers, products, orders, order_items with realistic relationships
- **Lakehouse architecture**: Partitioned tables optimized for analytics
- **Time-series data**: Daily partitioning by year/month/day
- **Synthetic data**: Realistic but fake data for testing and development
- **Multi-format support**: Same data can be written to different table formats

## Important Constraints
- Python 3.12+ required
- Optional dependencies must be installed separately (delta, iceberg, ducklake, cli)
- S3 credentials required for cloud storage
- Catalog configuration required for Iceberg and DuckLake formats
- File size targets for partitioning (default 250k rows per file)

## External Dependencies
- **S3-compatible storage**: AWS S3, MinIO, etc. via s3fs
- **SQL catalogs**: For Iceberg and DuckLake table management
- **Object storage services**: Configurable endpoint URLs for non-AWS storage
- **No external APIs**: All data is generated synthetically
