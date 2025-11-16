from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, Iterator, Literal, Sequence, Tuple

import numpy as np
import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, SchemaLike


OHLCV_BASE_SCHEMA: SchemaLike = {
    "timestamp": pl.Datetime,
    "symbol": pl.Utf8,
    "open": pl.Float64,
    "high": pl.Float64,
    "low": pl.Float64,
    "close": pl.Float64,
    "volume": pl.Int64,
}


@dataclass
class MarketOHLCVGenerator:
    """Generate OHLCV bars for a basket of symbols.

    Args:
        symbols: Ordered list of tickers to simulate.
        freq: Bar frequency. Supported values: ``1m``, ``5m``, ``15m``, ``1h``,
            ``1d``.
        start_date: Inclusive lower bound for generated trading days.
        end_date: Inclusive upper bound for generated trading days.
        mu: Drift term for the geometric Brownian motion.
        sigma: Volatility term for the geometric Brownian motion.
        base_price: Default starting price used when ``base_prices`` omits a
            symbol.
        base_prices: Optional per-symbol overrides for the starting price.
        volume_mean: Mean of the log-normal volume distribution.
        volume_sigma: Sigma of the log-normal volume distribution.
        trading_hours: Tuple of ``(start_hour, end_hour)`` used for intraday
            frequencies.
        seed: RNG seed.
        file_rows_target: Approximate batch size used for streaming writes.
    """
    symbols: Sequence[str]
    freq: Literal["1m", "5m", "15m", "1h", "1d"] = "1m"
    start_date: date = date(2023, 1, 1)
    end_date: date = date(2023, 1, 31)
    mu: float = 0.0
    sigma: float = 0.02
    base_price: float = 100.0
    base_prices: Dict[str, float] | None = None
    volume_mean: float = 12.0
    volume_sigma: float = 0.8
    trading_hours: Tuple[int, int] = (9, 17)
    seed: int = 123
    file_rows_target: int = 250_000

    name: str = "market_ohlcv"

    _last_close: Dict[str, float] = field(init=False, repr=False)
    _step_minutes: int = field(init=False, repr=False)
    _partition_columns: Tuple[str, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("symbols must not be empty")
        self._step_minutes = self._resolve_step_minutes(self.freq)
        self._partition_columns = self._resolve_partition_columns(self.freq)
        prices = self.base_prices or {}
        self._last_close = {sym: prices.get(sym, self.base_price) for sym in self.symbols}

    def tables(self) -> tuple[str, ...]:
        return ("ohlcv",)

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        if table != "ohlcv":
            raise ValueError(f"Unknown table '{table}'")
        return self._ohlcv_batches()

    def schema_for(self, table: str) -> SchemaLike | None:
        if table != "ohlcv":
            return None
        schema = dict(OHLCV_BASE_SCHEMA)
        for col in self._partition_columns:
            schema.update(self._partition_column_schema(col))
        return schema

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        if table != "ohlcv":
            return None
        return PartitionSpec(self._partition_columns)

    # ------------------ generation ------------------

    def _ohlcv_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed)
        chunk: list[dict] = []
        for current_date in self._date_range(self.start_date, self.end_date):
            timestamps = self._timestamps_for_day(current_date)
            if not timestamps:
                continue
            for symbol in self.symbols:
                rows = self._rows_for_symbol_day(symbol, current_date, timestamps, rng)
                if rows:
                    chunk.extend(rows)
                    if len(chunk) >= self.file_rows_target:
                        yield self._build_frame(chunk)
                        chunk = []
        if chunk:
            yield self._build_frame(chunk)

    def _rows_for_symbol_day(
        self,
        symbol: str,
        day: date,
        timestamps: Sequence[datetime],
        rng: np.random.Generator,
    ) -> list[dict]:
        rows: list[dict] = []
        prev_close = self._last_close[symbol]
        dt_fraction = (self._step_minutes or 1440) / 1440.0
        mu_dt = self.mu * dt_fraction
        sigma_dt = self.sigma * math.sqrt(dt_fraction)
        for ts in timestamps:
            open_price = prev_close
            log_return = rng.normal(mu_dt, sigma_dt)
            close_price = max(0.01, open_price * math.exp(log_return))
            high = max(open_price, close_price) * (1 + abs(rng.normal(0, 0.002)))
            low = min(open_price, close_price) * (1 - abs(rng.normal(0, 0.002)))
            volume = int(max(1, rng.lognormal(self.volume_mean, self.volume_sigma)))
            rows.append(
                {
                    "timestamp": ts,
                    "symbol": symbol,
                    "open": float(open_price),
                    "high": float(high),
                    "low": float(low),
                    "close": float(close_price),
                    "volume": volume,
                }
            )
            prev_close = close_price
        self._last_close[symbol] = prev_close
        return rows

    def _build_frame(self, rows: list[dict]) -> pl.DataFrame:
        df = pl.DataFrame(rows)
        extra_cols = []
        columns = set(self._partition_columns)
        if "year" in columns:
            extra_cols.append(pl.col("timestamp").dt.year().cast(pl.Int16).alias("year"))
        if "month" in columns:
            extra_cols.append(pl.col("timestamp").dt.month().cast(pl.Int8).alias("month"))
        if "day" in columns:
            extra_cols.append(pl.col("timestamp").dt.day().cast(pl.Int8).alias("day"))
        if "hour" in columns:
            extra_cols.append(pl.col("timestamp").dt.hour().cast(pl.Int8).alias("hour"))
        return df.with_columns(extra_cols)

    # ------------------ utilities ------------------

    @staticmethod
    def _resolve_step_minutes(freq: str) -> int:
        lookup = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "1d": 1440}
        if freq not in lookup:
            raise ValueError(f"Unsupported frequency '{freq}'")
        return lookup[freq]

    @staticmethod
    def _resolve_partition_columns(freq: str) -> Tuple[str, ...]:
        if freq == "1d":
            return ("year", "month")
        return ("year", "month", "day", "hour")

    @staticmethod
    def _partition_column_schema(column: str) -> SchemaLike:
        mapping = {
            "year": pl.Int16,
            "month": pl.Int8,
            "day": pl.Int8,
            "hour": pl.Int8,
        }
        if column not in mapping:
            raise ValueError(f"Unsupported partition column '{column}'")
        return {column: mapping[column]}

    def _timestamps_for_day(self, day: date) -> list[datetime]:
        if self.freq == "1d":
            return [datetime.combine(day, time(0, 0))]
        start_hour, end_hour = self.trading_hours
        start_dt = datetime.combine(day, time(start_hour, 0))
        end_dt = datetime.combine(day, time(end_hour, 0))
        step = timedelta(minutes=self._step_minutes)
        current = start_dt
        timestamps: list[datetime] = []
        while current < end_dt:
            timestamps.append(current)
            current += step
        return timestamps

    @staticmethod
    def _date_range(start: date, end: date) -> Iterable[date]:
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)
