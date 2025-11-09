# Market Data Generators

Dataset Generator includes two market data generators for financial applications: OHLCV (candlestick) data and real-time quotes.

## OHLCV Generator

Creates realistic Open-High-Low-Close-Volume data for financial instruments.

### Configuration

```python
generator = create_generator(
    "market-ohlcv",
    seed=42,
    symbols=["AAPL", "GOOGL", "MSFT", "AMZN"],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    frequency="1d",              # 1m, 5m, 15m, 1h, 1d
    initial_price_range=(50, 500),
    volatility_range=(0.1, 0.4),
    trend_probability=0.55,
)
```

### Data Schema

- **symbol**: Stock symbol (string)
- **timestamp**: Trading timestamp (datetime)
- **open**: Opening price (float)
- **high**: Highest price (float)
- **low**: Lowest price (float)
- **close**: Closing price (float)
- **volume**: Trading volume (int64)

### CLI Usage

```bash
dataset-generator generate market-ohlcv \
  --symbols AAPL,GOOGL,MSFT \
  --start 2024-01-01 \
  --end 2024-12-31 \
  --frequency 1d \
  --format parquet \
  --output ./market-data
```

## Market Quotes Generator

Generates real-time market quotes with bid/ask spreads.

### Configuration

```python
generator = create_generator(
    "market-quotes",
    seed=42,
    symbols=["BTC-USD", "ETH-USD", "EUR-USD"],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    quotes_per_second=10,
    spread_percentage=0.001,
)
```

### Data Schema

- **symbol**: Trading symbol (string)
- **timestamp**: Quote timestamp (datetime)
- **bid_price**: Bid price (float)
- **ask_price**: Ask price (float)
- **bid_size**: Bid size (int64)
- **ask_size**: Ask size (int64)

## Use Cases

- **Backtesting**: Historical data for trading strategies
- **System Testing**: Real-time data for trading platforms
- **Analytics**: Market data analysis and visualization
- **Education**: Learning about financial data patterns

## Next Steps

- **[E-commerce Generator](ecommerce.md)** - Retail data generation
- **[Sensors Generator](sensors.md)** - IoT sensor data
- **[Weather Generator](weather.md)** - Meteorological data