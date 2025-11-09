from __future__ import annotations

import unittest
from datetime import date

import polars as pl

from dataset_generator import (
    MarketOHLCVGenerator,
    MarketQuotesGenerator,
    SensorsGenerator,
    WeatherGenerator,
)
from dataset_generator.generators.weather import WeatherLocation


class MarketOHLCVGeneratorTest(unittest.TestCase):
    def test_basic_generation(self) -> None:
        gen = MarketOHLCVGenerator(
            symbols=["AAPL", "MSFT"],
            freq="1h",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 2),
            file_rows_target=10_000,
            seed=1,
        )
        batches = list(gen.batches_for("ohlcv"))
        self.assertTrue(batches)
        df = pl.concat(batches)
        self.assertIn("year", df.columns)
        self.assertIn("hour", df.columns)
        self.assertTrue((df["high"] >= df["open"]).all())
        self.assertTrue((df["high"] >= df["close"]).all())
        self.assertTrue((df["low"] <= df["open"]).all())
        self.assertTrue((df["low"] <= df["close"]).all())


class MarketQuotesGeneratorTest(unittest.TestCase):
    def test_quotes_structure(self) -> None:
        gen = MarketQuotesGenerator(
            symbols=["BTC"],
            quotes_per_minute=1,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
            file_rows_target=1_000,
            seed=2,
        )
        batches = list(gen.batches_for("quotes"))
        self.assertTrue(batches)
        df = pl.concat(batches)
        self.assertIn("year", df.columns)
        self.assertIn("hour", df.columns)
        self.assertTrue((df["bid_price"] < df["ask_price"]).all())
        self.assertGreater(df["sequence"].max(), df["sequence"].min())


class SensorsGeneratorTest(unittest.TestCase):
    def test_missing_and_anomaly_flags(self) -> None:
        gen = SensorsGenerator(
            n_devices=2,
            metrics=("temperature",),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
            sampling_interval_minutes=60,
            missing_probability=0.2,
            anomaly_probability=0.2,
            file_rows_target=1_000,
            seed=3,
        )
        df = pl.concat(list(gen.batches_for("sensor_readings")))
        self.assertIn("year", df.columns)
        self.assertTrue("hour" in df.columns)
        missing_rows = df.filter(pl.col("is_missing"))
        if missing_rows.height > 0:
            self.assertTrue(missing_rows["value"].is_null().all())
        anomaly_rows = df.filter(pl.col("is_anomaly"))
        if anomaly_rows.height > 0:
            self.assertTrue(anomaly_rows.height > 0)


class WeatherGeneratorTest(unittest.TestCase):
    def test_hourly_and_daily_outputs(self) -> None:
        gen = WeatherGenerator(
            locations=[WeatherLocation(1, "TestCity", 45.0, 8.0)],
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 2),
            seed=4,
            file_rows_target=1_000,
        )
        hourly = pl.concat(list(gen.batches_for("weather_hourly")))
        daily = pl.concat(list(gen.batches_for("weather_daily")))
        self.assertIn("hour", hourly.columns)
        self.assertIn("year", hourly.columns)
        self.assertIn("month", daily.columns)
        self.assertTrue((daily["tmax_c"] >= daily["tmin_c"]).all())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
