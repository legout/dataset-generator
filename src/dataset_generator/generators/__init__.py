"""Register built-in dataset generators so they are discoverable by name."""

from __future__ import annotations

from dataset_generator.core.factory import register_generator
from dataset_generator.generators.ecommerce import ECommerceGenerator
from dataset_generator.generators.market_ohlcv import MarketOHLCVGenerator
from dataset_generator.generators.market_quotes import MarketQuotesGenerator
from dataset_generator.generators.sensors import SensorsGenerator
from dataset_generator.generators.weather import WeatherGenerator


register_generator("ecommerce", ECommerceGenerator)
register_generator("market_ohlcv", MarketOHLCVGenerator)
register_generator("market_quotes", MarketQuotesGenerator)
register_generator("sensors", SensorsGenerator)
register_generator("weather", WeatherGenerator)

__all__ = [
    "ECommerceGenerator",
    "MarketOHLCVGenerator",
    "MarketQuotesGenerator",
    "SensorsGenerator",
    "WeatherGenerator",
]
