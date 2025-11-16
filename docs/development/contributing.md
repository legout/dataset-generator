# Contributing

We welcome contributions to Dataset Generator! This guide will help you get started.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/dataset-generator.git
cd dataset-generator
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[cli,delta,iceberg,ducklake,docs]
```

### 3. Run Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test
python -m unittest tests.test_ecommerce_generator
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- **Code changes** - Follow existing style and patterns
- **Add tests** - Ensure test coverage for new features
- **Update docs** - Document new functionality

### 3. Test Your Changes

```bash
# Run tests
python -m unittest discover -s tests

# Test CLI
dataset-generator --help

# Build documentation
mkdocs build
```

### 4. Submit Pull Request

- Push to your fork
- Create pull request with clear description
- Link any relevant issues

## Code Style

### Python Style

- Use **ruff** for linting and formatting
- Follow **PEP 8** conventions
- Use **type hints** for all functions
- Add **docstrings** for public APIs

### Example

```python
from __future__ import annotations
from typing import Iterator
import polars as pl

def generate_data(
    n_rows: int,
    seed: int = 42,
) -> pl.DataFrame:
    """Generate sample data.
    
    Args:
        n_rows: Number of rows to generate
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with generated data
    """
    # Implementation
    pass
```

## Adding New Generators

### 1. Create Generator Class

```python
# src/dataset_generator/generators/my_generator.py
from dataset_generator.core.interfaces import GeneratorBase

class MyGenerator:
    def __init__(self, seed: int, **kwargs):
        self.seed = seed
        # Initialize generator
        
    def generate(self) -> Iterator[pl.DataFrame]:
        # Yield DataFrames
        pass
```

### 2. Register Generator

```python
# src/dataset_generator/core/factory.py
GENERATORS = {
    "ecommerce": ECommerceGenerator,
    "my-generator": MyGenerator,  # Add here
}
```

### 3. Add Tests

```python
# tests/test_my_generator.py
import unittest
from dataset_generator.generators.my_generator import MyGenerator

class MyGeneratorTest(unittest.TestCase):
    def test_generation(self):
        generator = MyGenerator(seed=42)
        # Test implementation
```

### 4. Update Documentation

- Add generator to [User Guide](../user-guide/generators/ecommerce.md)
- Update API reference
- Add examples

## Adding New Writers

### 1. Create Writer Class

```python
# src/dataset_generator/writers/my_writer.py
from dataset_generator.core.interfaces import TableWriter

class MyWriter:
    def __init__(self, output_uri: str, **kwargs):
        self.output_uri = output_uri
        # Initialize writer
        
    def write(self, table_name: str, data: pl.DataFrame) -> None:
        # Write data
        pass
```

### 2. Register Writer

```python
# src/dataset_generator/core/factory.py
WRITERS = {
    "parquet": ParquetPartitionedWriter,
    "my-writer": MyWriter,  # Add here
}
```

## Documentation

### Building Documentation

```bash
# Serve locally
mkdocs serve

# Build for deployment
mkdocs build
```

### Documentation Structure

- **`docs/`** - All documentation files
- **`docs/getting-started/`** - Installation and quick start
- **`docs/user-guide/`** - Comprehensive usage guide
- **`docs/api/`** - Auto-generated API reference

### API Navigation & Includes

- `docs/scripts/gen_ref_pages.py` runs during every MkDocs build and writes
  `api/SUMMARY.md` plus one markdown file per module. The `literate-nav`
  plugin expands the `- api/` entry in `mkdocs.yml`, so you never need to hand
  edit the navigation when new modules/packages are added—just ensure the code
  is importable and has docstrings.
- Snippet-only fragments (for example `docs/includes/mkdocs.md`) are excluded
  from the navigation via `exclude_docs`. Keep additional include files under
  `docs/includes/` so they inherit the same rule and do not trigger orphan
  warnings during `mkdocs build`.

### API Docstrings

The API reference is generated directly from docstrings through `mkdocstrings`.
Follow these guidelines so the rendered pages stay consistent:

- Start every public module, class, and function with a one-line summary, then
  include details describing behavior and edge cases.
- Use Google-style sections (`Args:`, `Returns:`, `Raises:`) so parameters and
  return types show up in the table mkdocstrings renders. Reference other APIs
  with backticks (``dataset_generator.core.write_dataset``) for automatic links.
- Prefer type-hinted function signatures and keep docstrings in sync with
  defaults. Mention units or accepted values when it is not obvious from types.
- Add short examples when they clarify usage; they are shown verbatim in the API
  docs, so make sure they can be copy/pasted.
- Run `mkdocs build` (or `mkdocs serve`) after editing docstrings to confirm new
  symbols appear under **API Reference → Modules**.

## Testing

### Test Structure

```
tests/
├── test_ecommerce_generator.py
├── test_market_generators.py
├── test_writers.py
└── test_integration.py
```

### Running Tests

```bash
# All tests
python -m unittest discover -s tests

# With coverage
coverage run -m unittest discover -s tests
coverage report
```

### Test Guidelines

- **Test public APIs** - Focus on user-facing functionality
- **Use realistic data** - Small but representative datasets
- **Test edge cases** - Empty data, invalid parameters
- **Mock external services** - S3, databases, etc.

## Release Process

### 1. Update Version

```python
# pyproject.toml
version = "0.2.0"  # Bump version
```

### 2. Update Changelog

```markdown
# CHANGELOG.md

## [0.2.0] - 2024-01-15

### Added
- New weather generator
- DuckLake writer support

### Fixed
- Memory leak in large datasets
```

### 3. Create Release

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Getting Help

- **Issues** - Report bugs or request features
- **Discussions** - Ask questions or share ideas
- **Documentation** - Check existing guides first

## Code of Conduct

Please be respectful and inclusive. Follow the [Python Code of Conduct](https://www.python.org/psf/conduct/).

Thank you for contributing! 🎉
