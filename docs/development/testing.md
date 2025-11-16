# Testing Guide

Testing strategies and practices for the Dataset Generator project.

## Testing Philosophy

The Dataset Generator follows a comprehensive testing approach focused on:

- **Data correctness** - Ensuring generated data is realistic and valid
- **Integration reliability** - Verifying end-to-end workflows
- **Performance validation** - Maintaining efficient generation and writing
- **Regression prevention** - Catching breaking changes early

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_generators/     # Generator-specific tests
│   ├── test_writers/        # Writer-specific tests
│   └── test_core/           # Core functionality tests
├── integration/             # Integration tests across components
│   ├── test_end_to_end.py   # Full pipeline tests
│   ├── test_s3_integration.py # S3 storage tests
│   └── test_catalog_integration.py # Catalog tests
├── performance/             # Performance and load tests
├── fixtures/               # Test data and configurations
└── conftest.py            # Shared test utilities
```

## Unit Testing

### 1. Generator Testing

```python
# tests/unit/test_generators/test_ecommerce.py

import unittest
from datetime import date, timedelta
import polars as pl
from dataset_generator.generators.ecommerce import EcommerceGenerator
from dataset_generator.core.interfaces import PartitionSpec

class TestEcommerceGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'seed': 42,
            'n_customers': 100,
            'n_products': 50,
            'orders_per_day': 10
        }
        self.generator = EcommerceGenerator(**self.config)
    
    def test_customer_generation(self):
        """Test customer data generation"""
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        data = self.generator.generate(partition_spec)
        customers = data['customers']
        
        # Verify data structure
        self.assertEqual(len(customers), self.config['n_customers'])
        self.assertIn('customer_id', customers.columns)
        self.assertIn('email', customers.columns)
        
        # Verify data quality
        self.assertTrue(all(customers['email'].str.contains('@')))
        self.assertTrue(all(customers['customer_id'].str.startswith('CUST-')))
    
    def test_order_generation(self):
        """Test order data generation"""
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7)
        )
        
        data = self.generator.generate(partition_spec)
        orders = data['orders']
        customers = data['customers']
        
        # Verify order count
        expected_orders = self.config['orders_per_day'] * 7
        self.assertLessEqual(abs(len(orders) - expected_orders), expected_orders * 0.2)
        
        # Verify referential integrity
        customer_ids = set(customers['customer_id'])
        order_customer_ids = set(orders['customer_id'])
        self.assertTrue(order_customer_ids.issubset(customer_ids))
    
    def test_schema_validation(self):
        """Test schema generation"""
        schema = self.generator.get_schema()
        
        expected_tables = ['customers', 'products', 'orders', 'order_items']
        for table in expected_tables:
            self.assertIn(table, schema)
            self.assertIsInstance(schema[table], pl.Schema)
    
    def test_reproducibility(self):
        """Test data generation reproducibility with same seed"""
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        # Generate data twice with same seed
        data1 = self.generator.generate(partition_spec)
        
        # Reset generator with same seed
        self.generator = EcommerceGenerator(**self.config)
        data2 = self.generator.generate(partition_spec)
        
        # Compare results
        self.assertTrue(data1['customers'].equals(data2['customers']))
```

### 2. Writer Testing

```python
# tests/unit/test_writers/test_parquet.py

import unittest
import tempfile
import shutil
from pathlib import Path
import polars as pl
from dataset_generator.writers.parquet import ParquetWriter

class TestParquetWriter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.writer = ParquetWriter(str(self.temp_dir))
        
        # Sample test data
        self.test_data = {
            'customers': pl.DataFrame({
                'customer_id': ['CUST-001', 'CUST-002'],
                'name': ['John Doe', 'Jane Smith'],
                'email': ['john@example.com', 'jane@example.com']
            }),
            'orders': pl.DataFrame({
                'order_id': ['ORDER-001', 'ORDER-002'],
                'customer_id': ['CUST-001', 'CUST-002'],
                'amount': [100.0, 200.0],
                'order_date': [date(2024, 1, 1), date(2024, 1, 2)]
            })
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_write_master_tables(self):
        """Test writing master tables without partitioning"""
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        self.writer.write(self.test_data, partition_spec)
        
        # Verify master tables are written correctly
        customers_path = self.temp_dir / "customers" / "customers.parquet"
        self.assertTrue(customers_path.exists())
        
        loaded_customers = pl.read_parquet(customers_path)
        self.assertTrue(self.test_data['customers'].equals(loaded_customers))
    
    def test_write_partitioned_tables(self):
        """Test writing transactional tables with partitioning"""
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2)
        )
        
        self.writer.write(self.test_data, partition_spec)
        
        # Verify partitioned structure
        orders_path = self.temp_dir / "orders" / "year=2024" / "month=01"
        self.assertTrue(orders_path.exists())
        
        # Check for both day partitions
        day_01_path = orders_path / "day=01"
        day_02_path = orders_path / "day=02"
        self.assertTrue(day_01_path.exists())
        self.assertTrue(day_02_path.exists())
        
        # Verify data can be read back
        loaded_orders = pl.read_parquet(str(orders_path / "**" / "*.parquet"))
        self.assertEqual(len(loaded_orders), 2)
```

### 3. Core Component Testing

```python
# tests/unit/test_core/test_factory.py

import unittest
from dataset_generator.core.factory import create_generator, create_writer

class TestFactory(unittest.TestCase):
    
    def test_create_generator_valid_types(self):
        """Test creating generators with valid types"""
        valid_types = ['ecommerce', 'market_ohlcv', 'market_quotes', 'sensors', 'weather']
        
        for generator_type in valid_types:
            with self.subTest(generator_type=generator_type):
                generator = create_generator(generator_type, seed=42)
                self.assertIsNotNone(generator)
    
    def test_create_generator_invalid_type(self):
        """Test creating generator with invalid type"""
        with self.assertRaises(ValueError):
            create_generator('invalid_type', seed=42)
    
    def test_create_writer_valid_types(self):
        """Test creating writers with valid types"""
        valid_types = ['parquet', 'delta', 'iceberg', 'ducklake']
        
        for writer_type in valid_types:
            with self.subTest(writer_type=writer_type):
                writer = create_writer(writer_type, '/tmp/test')
                self.assertIsNotNone(writer)
    
    def test_create_writer_invalid_type(self):
        """Test creating writer with invalid type"""
        with self.assertRaises(ValueError):
            create_writer('invalid_type', '/tmp/test')
```

## Integration Testing

### 1. End-to-End Testing

```python
# tests/integration/test_end_to_end.py

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import date, timedelta
from dataset_generator import create_generator, create_writer, write_dataset

class TestEndToEnd(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_ecommerce_parquet_pipeline(self):
        """Test complete e-commerce to parquet pipeline"""
        # Create generator
        generator = create_generator(
            'ecommerce',
            seed=42,
            n_customers=100,
            n_products=50,
            orders_per_day=10
        )
        
        # Create writer
        writer = create_writer('parquet', str(self.temp_dir / 'ecommerce'))
        
        # Generate data
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7)
        )
        
        write_dataset(generator, writer, partition_spec)
        
        # Verify output
        self.assertTrue((self.temp_dir / 'ecommerce' / 'customers' / 'customers.parquet').exists())
        self.assertTrue((self.temp_dir / 'ecommerce' / 'orders' / 'year=2024').exists())
        
        # Verify data integrity
        customers = pl.read_parquet(str(self.temp_dir / 'ecommerce' / 'customers' / '*.parquet'))
        self.assertEqual(len(customers), 100)
        
        orders = pl.read_parquet(str(self.temp_dir / 'ecommerce' / 'orders' / '**' / '*.parquet'))
        self.assertGreater(len(orders), 0)
    
    def test_multiple_generator_writer_combinations(self):
        """Test various generator/writer combinations"""
        combinations = [
            ('ecommerce', 'parquet'),
            ('sensors', 'parquet'),
            ('weather', 'parquet'),
        ]
        
        for generator_type, writer_type in combinations:
            with self.subTest(generator=generator_type, writer=writer_type):
                self._test_combination(generator_type, writer_type)
    
    def _test_combination(self, generator_type: str, writer_type: str):
        """Test a specific generator/writer combination"""
        output_path = self.temp_dir / f"{generator_type}_{writer_type}"
        
        # Create components
        generator = create_generator(generator_type, seed=42, n_customers=10)
        writer = create_writer(writer_type, str(output_path))
        
        # Generate data
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2)
        )
        
        write_dataset(generator, writer, partition_spec)
        
        # Basic verification
        self.assertTrue(output_path.exists())
```

### 2. S3 Integration Testing

```python
# tests/integration/test_s3_integration.py

import unittest
import os
from moto import mock_s3
import boto3
from dataset_generator import S3Config, create_writer, create_generator, write_dataset

class TestS3Integration(unittest.TestCase):
    
    @mock_s3
    def test_s3_parquet_writer(self):
        """Test writing to S3-compatible storage"""
        # Create mock S3
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        # Configure S3
        s3_config = S3Config(
            uri="s3://test-bucket/test-data/",
            key="test-key",
            secret="test-secret",
            endpoint_url="http://localhost:9000",
            secure=False
        )
        
        # Create generator and writer
        generator = create_generator('ecommerce', seed=42, n_customers=10)
        writer = create_writer('parquet', "s3://test-bucket/test-data/", s3=s3_config)
        
        # Generate data
        write_dataset(generator, writer)
        
        # Verify files exist in S3
        objects = s3_client.list_objects_v2(Bucket='test-bucket', Prefix='test-data/')
        self.assertGreater(len(objects.get('Contents', [])), 0)
```

## Performance Testing

### 1. Load Testing

```python
# tests/performance/test_load.py

import unittest
import time
import psutil
import os
from dataset_generator import create_generator, create_writer, write_dataset

class TestPerformance(unittest.TestCase):
    
    def test_large_dataset_generation(self):
        """Test performance with large datasets"""
        sizes = [
            {'n_customers': 1000, 'orders_per_day': 100},
            {'n_customers': 10000, 'orders_per_day': 1000},
            {'n_customers': 100000, 'orders_per_day': 10000},
        ]
        
        for config in sizes:
            with self.subTest(config=config):
                self._benchmark_generation(config)
    
    def _benchmark_generation(self, config):
        """Benchmark generation performance"""
        process = psutil.Process(os.getpid())
        
        # Record initial state
        initial_memory = process.memory_info().rss
        
        # Generate data
        generator = create_generator('ecommerce', seed=42, **config)
        
        start_time = time.time()
        data = generator.generate(PartitionSpec.default())
        generation_time = time.time() - start_time
        
        # Record final state
        final_memory = process.memory_info().rss
        memory_used = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Performance assertions
        self.assertLess(generation_time, 300)  # Should complete in 5 minutes
        self.assertLess(memory_used, 2000)     # Should use less than 2GB RAM
        
        print(f"Config: {config}")
        print(f"Generation time: {generation_time:.2f} seconds")
        print(f"Memory used: {memory_used:.2f} MB")
        print(f"Records generated: {len(data['orders'])}")
```

### 2. Memory Testing

```python
# tests/performance/test_memory.py

import unittest
import tracemalloc
from dataset_generator import create_generator, create_writer

class TestMemoryUsage(unittest.TestCase):
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations"""
        tracemalloc.start()
        
        generator = create_generator('ecommerce', seed=42, n_customers=100)
        
        # Generate data multiple times
        for i in range(10):
            data = generator.generate(PartitionSpec.default())
            
            # Force garbage collection
            del data
            
            # Check memory usage
            if i > 0:
                current, peak = tracemalloc.get_traced_memory()
                self.assertLess(current, peak * 1.1)  # Allow 10% growth
        
        tracemalloc.stop()
```

## Test Fixtures and Utilities

### 1. Common Fixtures

```python
# tests/conftest.py

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import date
from dataset_generator import create_generator, create_writer
from dataset_generator.core.interfaces import PartitionSpec

@pytest.fixture
def temp_output_dir():
    """Temporary directory for test outputs"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_ecommerce_generator():
    """Sample e-commerce generator for testing"""
    return create_generator(
        'ecommerce',
        seed=42,
        n_customers=100,
        n_products=50,
        orders_per_day=10
    )

@pytest.fixture
def sample_partition_spec():
    """Sample partition specification"""
    return PartitionSpec(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 7)
    )

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing"""
    return pl.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [10.0, 20.0, 30.0]
    })
```

### 2. Test Utilities

```python
# tests/utils.py

import polars as pl
from typing import Dict, Any
from dataset_generator.core.interfaces import PartitionSpec

def assert_dataframes_equal(df1: pl.DataFrame, df2: pl.DataFrame, tolerance: float = 0.0):
    """Assert two DataFrames are equal with optional tolerance"""
    assert df1.columns == df2.columns, "Column names differ"
    assert len(df1) == len(df2), "Row counts differ"
    
    for col in df1.columns:
        if df1[col].dtype in [pl.Float32, pl.Float64]:
            # Use tolerance for floating point comparisons
            diff = (df1[col] - df2[col]).abs().max()
            assert diff <= tolerance, f"Column {col} differs by more than {tolerance}"
        else:
            # Exact comparison for other types
            assert df1[col].equals(df2[col]), f"Column {col} values differ"

def validate_schema_compliance(data: Dict[str, pl.DataFrame], schema: Dict[str, pl.Schema]):
    """Validate data matches expected schema"""
    for table_name, df in data.items():
        if table_name in schema:
            expected_schema = schema[table_name]
            actual_schema = df.schema
            
            for col_name, dtype in expected_schema.items():
                assert col_name in actual_schema, f"Missing column {col_name} in {table_name}"
                assert actual_schema[col_name] == dtype, f"Type mismatch for {table_name}.{col_name}"

def count_partitions(output_path: Path) -> int:
    """Count number of partition directories"""
    count = 0
    for path in output_path.rglob("*"):
        if path.is_dir() and any(part in path.name for part in ['year=', 'month=', 'day=']):
            count += 1
    return count
```

## Running Tests

### 1. Local Development

```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.unit.test_generators.test_ecommerce

# Run with coverage
coverage run -m unittest discover -s tests
coverage report
coverage html  # Generate HTML report
```

### 2. CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[cli,delta,iceberg,ducklake,docs,test]
    
    - name: Run tests
      run: |
        python -m unittest discover -s tests
    
    - name: Generate coverage report
      run: |
        coverage run -m unittest discover -s tests
        coverage xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Data Management

### 1. Test Data Generation

```python
# tests/fixtures/data_generator.py

from dataset_generator import create_generator
from datetime import date

def create_test_dataset(generator_type: str, size: str = 'small'):
    """Create test datasets of different sizes"""
    sizes = {
        'small': {'n_customers': 10, 'orders_per_day': 5},
        'medium': {'n_customers': 100, 'orders_per_day': 50},
        'large': {'n_customers': 1000, 'orders_per_day': 500}
    }
    
    config = sizes.get(size, sizes['small'])
    generator = create_generator(generator_type, seed=42, **config)
    
    return generator.generate(PartitionSpec(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 7)
    ))
```

### 2. Expected Results

```python
# tests/fixtures/expected_results.py

import polars as pl

EXPECTED_CUSTOMERS_SCHEMA = pl.Schema({
    'customer_id': pl.Utf8,
    'name': pl.Utf8,
    'email': pl.Utf8,
    'phone': pl.Utf8,
    'address': pl.Utf8,
    'city': pl.Utf8,
    'state': pl.Utf8,
    'zip_code': pl.Utf8,
    'country': pl.Utf8,
    'created_at': pl.Datetime
})

def validate_customers_schema(df: pl.DataFrame):
    """Validate customers DataFrame schema"""
    for col, dtype in EXPECTED_CUSTOMERS_SCHEMA.items():
        assert col in df.columns, f"Missing column: {col}"
        assert df[col].dtype == dtype, f"Wrong type for {col}: got {df[col].dtype}, expected {dtype}"
```

## Best Practices

### 1. Test Organization

- **One test per concern** - Focus on specific functionality
- **Descriptive test names** - Make it clear what's being tested
- **Arrange-Act-Assert pattern** - Structure tests clearly
- **Independent tests** - Tests should not depend on each other

### 2. Data Quality Testing

```python
def test_data_quality_rules(self):
    """Test data quality rules"""
    data = self.generator.generate(self.partition_spec)
    
    # Test null constraints
    self.assertEqual(data['customers']['customer_id'].null_count(), 0)
    
    # Test uniqueness constraints
    customer_ids = data['customers']['customer_id']
    self.assertEqual(len(customer_ids.unique()), len(customer_ids))
    
    # Test business rules
    self.assertTrue((data['orders']['amount'] > 0).all())
    self.assertTrue((data['order_items']['quantity'] > 0).all())
```

### 3. Error Handling Testing

```python
def test_error_conditions(self):
    """Test error handling and edge cases"""
    # Test invalid configurations
    with self.assertRaises(ValueError):
        create_generator('ecommerce', n_customers=-1)
    
    # Test invalid dates
    with self.assertRaises(ValueError):
        partition_spec = PartitionSpec(
            start_date=date(2024, 1, 1),
            end_date=date(2023, 12, 31)  # End before start
        )
        self.generator.generate(partition_spec)
```

## Related Documentation

- **[Architecture Guide](architecture.md)** - System architecture overview
- **[Contributing Guide](contributing.md)** - Development guidelines
- **[API Reference](../api/core.md)** - Detailed API documentation
