# Installation

Dataset Generator requires Python 3.12 or higher. Installation is flexible - you can install just the base package or add optional dependencies for specific features.

## Base Installation

The base package includes core functionality for generating datasets and writing to Parquet format:

```bash
pip install dataset-generator
```

## Optional Dependencies

### CLI Support

Add the command-line interface:

```bash
pip install dataset-generator[cli]
```

### Table Format Support

Install support for specific table formats:

```bash
# Delta Lake support
pip install dataset-generator[delta]

# Apache Iceberg support  
pip install dataset-generator[iceberg]

# DuckLake support
pip install dataset-generator[ducklake]
```

### All Features

Install all optional dependencies:

```bash
pip install dataset-generator[cli,delta,iceberg,ducklake]
```

## Development Installation

For development with all dependencies:

```bash
# Clone the repository
git clone https://github.com/volker-lorrmann/dataset-generator.git
cd dataset-generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[cli,delta,iceberg,ducklake,docs]
```

## Verification

Verify your installation:

```bash
# Check CLI is available
dataset-generator --help

# List available generators
dataset-generator list-datasets

# List available formats
dataset-generator list-formats
```

## System Requirements

- **Python**: 3.12 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Storage**: Depends on dataset size (Parquet files are compressed)
- **Network**: Required only for S3/cloud storage integration

## Troubleshooting

### Common Issues

**Import Error: No module named 'dataset_generator'**
- Ensure you've activated your virtual environment
- Try reinstalling: `pip install dataset-generator`

**Permission Denied**
- Use a virtual environment or `pip install --user dataset-generator`

**S3 Dependencies Missing**
- Install S3 support: `pip install dataset-generator[s3]` (included in base)

### Getting Help

- Check the [Troubleshooting Guide](../user-guide/troubleshooting.md)
- Open an issue on [GitHub](https://github.com/volker-lorrmann/dataset-generator/issues)
- Review [Examples](../examples/jupyter.md) for working configurations