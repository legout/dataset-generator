# Weather Generator

The weather generator creates realistic meteorological data for multiple locations with proper weather patterns and correlations.

## Weather Variables

- **Temperature**: Air temperature in Celsius
- **Humidity**: Relative humidity percentage
- **Pressure**: Atmospheric pressure in hPa
- **Wind Speed**: Wind speed in km/h
- **Wind Direction**: Wind direction in degrees
- **Precipitation**: Precipitation amount in mm
- **Cloud Cover**: Cloud coverage percentage

## Configuration

```python
from dataset_generator.generators.weather import WeatherLocation

generator = create_generator(
    "weather",
    seed=42,
    locations=[
        WeatherLocation("New York", 40.7128, -74.0060, "urban"),
        WeatherLocation("London", 51.5074, -0.1278, "urban"),
        WeatherLocation("Tokyo", 35.6762, 139.6503, "urban"),
    ],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    readings_per_hour=1,
    climate_model="realistic",
)
```

## Data Schema

- **location**: Location name (string)
- **latitude**: Latitude coordinate (float)
- **longitude**: Longitude coordinate (float)
- **timestamp**: Reading timestamp (datetime)
- **temperature**: Temperature in Celsius (float)
- **humidity**: Relative humidity % (float)
- **pressure**: Atmospheric pressure hPa (float)
- **wind_speed**: Wind speed km/h (float)
- **wind_direction**: Wind direction degrees (float)
- **precipitation**: Precipitation mm (float)
- **cloud_cover**: Cloud coverage % (float)

## Usage Examples

### CLI

```bash
dataset-generator generate weather \
  --locations "New York,London,Tokyo" \
  --start 2024-01-01 \
  --end 2024-12-31 \
  --readings-per-hour 4 \
  --format parquet \
  --output ./weather-data
```

### Python

```python
locations = [
    WeatherLocation("New York", 40.7128, -74.0060),
    WeatherLocation("Los Angeles", 34.0522, -118.2437),
    WeatherLocation("Chicago", 41.8781, -87.6298),
]

generator = create_generator(
    "weather",
    locations=locations,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    readings_per_day=24,
)

writer = create_writer("parquet", output_uri="./weather")
write_dataset(generator, writer)
```

## Weather Patterns

### Seasonal Variations
- **Temperature**: Follows seasonal patterns by latitude
- **Humidity**: Varies with climate and season
- **Pressure**: Weather front patterns
- **Precipitation**: Seasonal rainfall patterns

### Daily Cycles
- **Temperature**: Daily heating/cooling cycles
- **Wind**: Diurnal wind pattern changes
- **Humidity**: Daily humidity variations

### Correlations
- **Temperature & Humidity**: Inverse relationship
- **Pressure & Weather**: Low pressure = storms
- **Wind & Temperature**: Wind patterns affect temperature

## Climate Models

### Realistic Model
- Based on historical weather patterns
- Proper seasonal variations
- Realistic extreme weather events

### Simplified Model
- Basic weather patterns
- Faster generation
- Good for testing

## Use Cases

- **Energy forecasting**: Weather-dependent energy consumption
- **Agriculture planning**: Crop and weather correlation
- **Transportation**: Weather impact on logistics
- **Insurance**: Weather risk modeling

## Next Steps

- **[Sensors Generator](sensors.md)** - IoT sensor data
- **[Market Data](market.md)** - Financial data
- **[E-commerce Generator](ecommerce.md)** - Retail data