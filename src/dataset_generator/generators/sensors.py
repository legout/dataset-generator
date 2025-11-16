from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Iterator, Sequence

import numpy as np
import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, SchemaLike


SENSOR_SCHEMA: SchemaLike = {
    "timestamp": pl.Datetime,
    "device_id": pl.Int64,
    "metric": pl.Utf8,
    "value": pl.Float64,
    "is_anomaly": pl.Boolean,
    "is_missing": pl.Boolean,
}


@dataclass
class SensorsGenerator:
    """Generate multi-metric IoT/sensor readings with noise and anomalies.

    Args:
        n_devices: Number of devices emitting readings.
        metrics: Metric names produced by every device.
        start_date: Inclusive lower bound for generated dates.
        end_date: Inclusive upper bound for generated dates.
        sampling_interval_minutes: Spacing between measurements.
        noise_sigma: Standard deviation of Gaussian measurement noise.
        drift_per_hour: Linear drift applied over the course of a day.
        missing_probability: Probability that a reading becomes missing.
        anomaly_probability: Probability that a reading becomes an anomaly.
        anomaly_scale: Magnitude of anomaly spikes.
        seed: RNG seed.
        file_rows_target: Approximate batch size.
    """
    n_devices: int = 100
    metrics: Sequence[str] = ("temperature", "vibration", "pressure")
    start_date: date = date(2023, 1, 1)
    end_date: date = date(2023, 1, 7)
    sampling_interval_minutes: int = 5
    noise_sigma: float = 0.2
    drift_per_hour: float = 0.05
    missing_probability: float = 0.01
    anomaly_probability: float = 0.002
    anomaly_scale: float = 5.0
    seed: int = 999
    file_rows_target: int = 250_000

    name: str = "sensors"

    def tables(self) -> tuple[str, ...]:
        return ("sensor_readings",)

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        if table != "sensor_readings":
            raise ValueError(f"Unknown table '{table}'")
        return self._reading_batches()

    def schema_for(self, table: str) -> SchemaLike | None:
        if table != "sensor_readings":
            return None
        schema = dict(SENSOR_SCHEMA)
        schema.update({"year": pl.Int16, "month": pl.Int8, "day": pl.Int8, "hour": pl.Int8})
        return schema

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        if table != "sensor_readings":
            return None
        return PartitionSpec(("year", "month", "day", "hour"))

    # ------------------ generation ------------------

    def _reading_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed)
        chunk: list[dict] = []
        timestamps = list(self._timestamps())
        hours = np.array([ts.hour + ts.minute / 60 for ts in timestamps], dtype=float)
        day_of_years = np.array([ts.timetuple().tm_yday for ts in timestamps], dtype=float)

        for device_id in range(1, self.n_devices + 1):
            device_seed = self.seed + device_id * 101
            device_rng = np.random.default_rng(device_seed)
            device_offset = device_rng.normal(0.0, 0.5)
            for metric in self.metrics:
                metric_hash = (hash(metric) % 997) / 997
                base_signal = (
                    10 * np.sin(2 * np.pi * day_of_years / 365 + metric_hash)
                    + self.drift_per_hour * hours
                    + device_offset
                )
                noise = rng.normal(0.0, self.noise_sigma, size=len(timestamps))
                values = base_signal + noise

                is_anomaly = rng.random(len(timestamps)) < self.anomaly_probability
                anomaly_adjustment = rng.normal(0, self.anomaly_scale, size=len(timestamps))
                values = np.where(is_anomaly, values + anomaly_adjustment, values)

                is_missing = rng.random(len(timestamps)) < self.missing_probability
                values = np.where(is_missing, np.nan, values)

                for ts, value, anomaly, missing in zip(timestamps, values, is_anomaly, is_missing):
                    row = {
                        "timestamp": ts,
                        "device_id": device_id,
                        "metric": metric,
                        "value": None if missing else float(value),
                        "is_anomaly": bool(anomaly),
                        "is_missing": bool(missing),
                    }
                    chunk.append(row)
                    if len(chunk) >= self.file_rows_target:
                        yield self._build_frame(chunk)
                        chunk = []
        if chunk:
            yield self._build_frame(chunk)

    def _build_frame(self, rows: list[dict]) -> pl.DataFrame:
        df = pl.DataFrame(rows)
        return df.with_columns(
            [
                pl.col("value").cast(pl.Float64),
                pl.col("timestamp").dt.year().cast(pl.Int16).alias("year"),
                pl.col("timestamp").dt.month().cast(pl.Int8).alias("month"),
                pl.col("timestamp").dt.day().cast(pl.Int8).alias("day"),
                pl.col("timestamp").dt.hour().cast(pl.Int8).alias("hour"),
            ]
        )

    def _timestamps(self) -> Iterable[datetime]:
        interval = timedelta(minutes=self.sampling_interval_minutes)
        current_day = self.start_date
        while current_day <= self.end_date:
            current_dt = datetime.combine(current_day, datetime.min.time())
            end_dt = current_dt + timedelta(days=1)
            while current_dt < end_dt:
                yield current_dt
                current_dt += interval
            current_day += timedelta(days=1)
