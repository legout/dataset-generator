# Sensors Generator

The sensors generator creates realistic IoT sensor data for various monitoring and testing scenarios.

## Supported Sensor Types

- **Temperature**: Environmental temperature monitoring
- **Humidity**: Relative humidity sensors
- **Pressure**: Atmospheric or industrial pressure
- **Motion**: Movement and vibration sensors
- **Energy**: Power consumption monitoring

## Configuration

```python
generator = create_generator(
    "sensors",
    seed=42,
    n_sensors=100,
    sensor_types=["temperature", "humidity", "pressure"],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    readings_per_minute=1,
    failure_rate=0.001,
    location_distribution="urban",
)
```

## Data Schema

- **sensor_id**: Unique sensor identifier (string)
- **sensor_type**: Type of sensor (string)
- **timestamp**: Reading timestamp (datetime)
- **value**: Sensor reading value (float)
- **unit**: Measurement unit (string)
- **status**: Sensor status (string)
- **location**: Sensor location (string)
- **battery_level**: Battery percentage (float, optional)

## Usage Examples

### CLI

```bash
dataset-generator generate sensors \
  --n-sensors 500 \
  --sensor-types temperature,humidity,pressure \
  --readings-per-minute 2 \
  --format parquet \
  --output ./sensor-data
```

### Python

```python
generator = create_generator(
    "sensors",
    n_sensors=1000,
    sensor_types=["temperature", "humidity"],
    readings_per_hour=60,
    failure_rate=0.01,
)

writer = create_writer("parquet", output_uri="./sensors")
write_dataset(generator, writer)
```

## Data Patterns

- **Realistic ranges**: Each sensor type has appropriate value ranges
- **Temporal patterns**: Daily/seasonal variations
- **Failures**: Random sensor failures and recovery
- **Correlations**: Related sensors show correlated values

## Use Cases

- **IoT platform testing**: Validate data ingestion pipelines
- **Monitoring systems**: Test alerting and dashboard systems
- **Analytics development**: Build time-series analytics
- **Edge computing**: Test edge processing algorithms

## Next Steps

- **[Weather Generator](weather.md)** - Meteorological data
- **[E-commerce Generator](ecommerce.md)** - Retail data
- **[Market Data](market.md)** - Financial data