from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable, Iterator, Sequence

import numpy as np
import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, SchemaLike


@dataclass(frozen=True)
class WeatherLocation:
    id: int
    name: str
    latitude: float
    longitude: float


HOURLY_BASE_SCHEMA: SchemaLike = {
    "timestamp": pl.Datetime,
    "location_id": pl.Int64,
    "temperature_c": pl.Float64,
    "humidity_pct": pl.Float64,
    "wind_kph": pl.Float64,
    "pressure_hpa": pl.Float64,
    "precip_mm": pl.Float64,
    "condition": pl.Utf8,
}


DAILY_BASE_SCHEMA: SchemaLike = {
    "date": pl.Date,
    "location_id": pl.Int64,
    "tmin_c": pl.Float64,
    "tmax_c": pl.Float64,
    "precip_mm": pl.Float64,
    "snow_mm": pl.Float64,
    "condition": pl.Utf8,
}


@dataclass
class WeatherGenerator:
    locations: Sequence[WeatherLocation] = field(
        default_factory=lambda: (
            WeatherLocation(1, "Berlin", 52.52, 13.40),
            WeatherLocation(2, "Madrid", 40.42, -3.70),
            WeatherLocation(3, "Helsinki", 60.17, 24.94),
        )
    )
    start_date: date = date(2023, 1, 1)
    end_date: date = date(2023, 1, 31)
    seasonal_amplitude: float = 12.0
    diurnal_amplitude: float = 3.0
    storm_rate: float = 0.1
    seed: int = 2024
    file_rows_target: int = 250_000

    name: str = "weather"

    def tables(self) -> tuple[str, ...]:
        return ("weather_hourly", "weather_daily")

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        if table == "weather_hourly":
            return self._hourly_batches()
        if table == "weather_daily":
            return self._daily_batches()
        raise ValueError(f"Unknown table '{table}'")

    def schema_for(self, table: str) -> SchemaLike | None:
        if table == "weather_hourly":
            schema = dict(HOURLY_BASE_SCHEMA)
            schema.update({"year": pl.Int16, "month": pl.Int8, "day": pl.Int8, "hour": pl.Int8})
            return schema
        if table == "weather_daily":
            schema = dict(DAILY_BASE_SCHEMA)
            schema.update({"year": pl.Int16, "month": pl.Int8})
            return schema
        return None

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        if table == "weather_hourly":
            return PartitionSpec(("year", "month", "day", "hour"))
        if table == "weather_daily":
            return PartitionSpec(("year", "month"))
        return None

    # ------------------ hourly generation ------------------

    def _hourly_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed)
        chunk: list[dict] = []
        for current_date in self._date_range(self.start_date, self.end_date):
            day_of_year = current_date.timetuple().tm_yday
            for hour in range(24):
                ts = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour)
                for location in self.locations:
                    row = self._hourly_row(location, ts, day_of_year, hour, rng)
                    chunk.append(row)
                    if len(chunk) >= self.file_rows_target:
                        yield self._build_hourly_frame(chunk)
                        chunk = []
        if chunk:
            yield self._build_hourly_frame(chunk)

    def _hourly_row(
        self,
        location: WeatherLocation,
        ts: datetime,
        day_of_year: int,
        hour: int,
        rng: np.random.Generator,
    ) -> dict:
        lat_factor = math.cos(math.radians(location.latitude))
        seasonal = self.seasonal_amplitude * math.sin(2 * math.pi * day_of_year / 365.0 + lat_factor)
        diurnal = self.diurnal_amplitude * math.sin(2 * math.pi * hour / 24.0)
        base_temp = 15 - location.latitude * 0.1
        temperature = base_temp + seasonal + diurnal + rng.normal(0, 1.0)

        humidity = np.clip(70 - 0.6 * (temperature - 20) + rng.normal(0, 3), 20, 100)
        wind = abs(rng.normal(15, 5))
        pressure = 1013 + rng.normal(0, 6)
        precip_chance = self.storm_rate + max(0, 0.02 * (humidity - 70))
        precip = rng.gamma(shape=1.5, scale=1.0) if rng.random() < precip_chance else 0.0

        if precip > 3:
            condition = "rain"
        elif temperature < 0 and precip > 0.2:
            condition = "snow"
        elif temperature > 25 and humidity < 40:
            condition = "sunny"
        else:
            condition = "cloudy"

        return {
            "timestamp": ts,
            "location_id": location.id,
            "temperature_c": float(temperature),
            "humidity_pct": float(humidity),
            "wind_kph": float(wind),
            "pressure_hpa": float(pressure),
            "precip_mm": float(precip),
            "condition": condition,
        }

    def _build_hourly_frame(self, rows: list[dict]) -> pl.DataFrame:
        df = pl.DataFrame(rows)
        return df.with_columns(
            [
                pl.col("timestamp").dt.year().cast(pl.Int16).alias("year"),
                pl.col("timestamp").dt.month().cast(pl.Int8).alias("month"),
                pl.col("timestamp").dt.day().cast(pl.Int8).alias("day"),
                pl.col("timestamp").dt.hour().cast(pl.Int8).alias("hour"),
            ]
        )

    # ------------------ daily generation ------------------

    def _daily_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed + 10_000)
        chunk: list[dict] = []
        for current_date in self._date_range(self.start_date, self.end_date):
            day_of_year = current_date.timetuple().tm_yday
            for location in self.locations:
                row = self._daily_row(location, current_date, day_of_year, rng)
                chunk.append(row)
                if len(chunk) >= self.file_rows_target:
                    yield self._build_daily_frame(chunk)
                    chunk = []
        if chunk:
            yield self._build_daily_frame(chunk)

    def _daily_row(
        self,
        location: WeatherLocation,
        day: date,
        day_of_year: int,
        rng: np.random.Generator,
    ) -> dict:
        lat_factor = math.cos(math.radians(location.latitude))
        seasonal = self.seasonal_amplitude * math.sin(2 * math.pi * day_of_year / 365.0 + lat_factor)
        base_temp = 15 - location.latitude * 0.1
        avg_temp = base_temp + seasonal + rng.normal(0, 1.5)
        spread = abs(rng.normal(8, 2))
        tmax = avg_temp + spread / 2
        tmin = avg_temp - spread / 2
        precip = max(0.0, rng.gamma(1.2, 1.5) - 0.5)
        snow = 0.0
        if tmax < 0:
            snow = precip * rng.uniform(0.3, 0.8)

        if precip > 5:
            condition = "storm"
        elif snow > 1:
            condition = "snow"
        elif tmax > 27:
            condition = "hot"
        elif tmin < -5:
            condition = "freezing"
        else:
            condition = "mild"

        return {
            "date": day,
            "location_id": location.id,
            "tmin_c": float(tmin),
            "tmax_c": float(tmax),
            "precip_mm": float(precip),
            "snow_mm": float(snow),
            "condition": condition,
        }

    def _build_daily_frame(self, rows: list[dict]) -> pl.DataFrame:
        df = pl.DataFrame(rows)
        return df.with_columns(
            [
                pl.col("date").dt.year().cast(pl.Int16).alias("year"),
                pl.col("date").dt.month().cast(pl.Int8).alias("month"),
            ]
        )

    # ------------------ utilities ------------------

    @staticmethod
    def _date_range(start: date, end: date) -> Iterable[date]:
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)
