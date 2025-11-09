# Dataset Generator

<div align="center">

Synthetic data pipelines for lakehouse tables.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/Documentation-latest-brightgreen.svg)](https://dataset-generator.readthedocs.io/)

</div>

Dataset Generator creates realistic fake datasets and streams them into lake-friendly table layouts. The first bundled generator focuses on e-commerce events and can materialize data into partitioned Parquet, Delta Lake, Apache Iceberg, or DuckLake tables on the local filesystem or S3-compatible storage.

## ✨ Features

- **Modular generators** with partition-aware batch streaming
- **Multiple formats** - Parquet, Delta Lake, Iceberg, DuckLake
- **S3 integration** with configurable connectivity
- **CLI interface** for easy dataset generation and management
- **Extensible architecture** for adding new data domains

## 🚀 Quick Start

```bash
# Install with CLI support
pip install dataset-generator[cli]

# Generate an e-commerce dataset
dataset-generator generate ecommerce \
  --format parquet \
  --output ./data \
  --start 2024-01-01 \
  --end 2024-01-07 \
  --n-customers 1000 \
  --orders-per-day 500
```

## 📖 Documentation

- **[Getting Started](getting-started/installation.md)** - Installation and basic setup
- **[User Guide](user-guide/index.md)** - Comprehensive usage guide
- **[API Reference](api/core.md)** - Complete API documentation
- **[Tutorials](tutorials/index.md)** - Step-by-step examples
- **[Examples](examples/jupyter.md)** - Jupyter notebooks and Marimo apps

## 🎯 Use Cases

- **Development testing** - Generate realistic test data for applications
- **Performance benchmarking** - Create datasets of specific sizes and characteristics
- **Learning and experimentation** - Explore lakehouse architectures without real data
- **CI/CD pipelines** - Automated data generation for testing workflows

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Generators    │───▶│     Pipeline     │───▶│     Writers     │
│                 │    │                  │    │                 │
│ • E-commerce    │    │ • Partitioning   │    │ • Parquet       │
│ • Market Data   │    │ • Streaming      │    │ • Delta Lake    │
│ • Sensors       │    │ • Validation     │    │ • Iceberg       │
│ • Weather       │    │                  │    │ • DuckLake      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](development/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/volker-lorrmann/dataset-generator/blob/main/LICENSE) file for details.