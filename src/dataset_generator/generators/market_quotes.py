from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, Iterator, Sequence, Tuple

import numpy as np
import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, SchemaLike


QUOTES_BASE_SCHEMA: SchemaLike = {
    "timestamp": pl.Datetime,
    "symbol": pl.Utf8,
    "bid_price": pl.Float64,
    "ask_price": pl.Float64,
    "bid_size": pl.Int32,
    "ask_size": pl.Int32,
    "spread_bps": pl.Float32,
    "sequence": pl.Int64,
}


@dataclass
class MarketQuotesGenerator:
    """Generate a high-frequency quote stream with microstructure noise.

    Args:
        symbols: Symbols that receive quotes.
        quotes_per_minute: Number of quote events per minute per symbol.
        start_date: Inclusive lower bound for generated trading days.
        end_date: Inclusive upper bound for generated trading days.
        mu: Drift term for the geometric Brownian motion applied to the
            mid-price.
        sigma: Volatility term for the mid-price process.
        base_price: Default starting mid-price used when ``base_prices`` does
            not contain an entry.
        base_prices: Optional per-symbol overrides for the starting price.
        spread_bps_mean: Mean (in basis points) for spreads.
        spread_bps_sigma: Standard deviation (in basis points) for spreads.
        size_mean: Mean shares/contracts shown on each side of the book.
        size_sigma: Standard deviation for order sizes.
        trading_hours: Tuple of ``(start_hour, end_hour)`` describing the
            session.
        seed: RNG seed.
        file_rows_target: Approximate batch size.
    """
    symbols: Sequence[str]
    quotes_per_minute: int = 5
    start_date: date = date(2023, 1, 1)
    end_date: date = date(2023, 1, 31)
    mu: float = 0.0
    sigma: float = 0.03
    base_price: float = 100.0
    base_prices: Dict[str, float] | None = None
    spread_bps_mean: float = 1.0
    spread_bps_sigma: float = 0.3
    size_mean: float = 200.0
    size_sigma: float = 60.0
    trading_hours: Tuple[int, int] = (9, 17)
    seed: int = 321
    file_rows_target: int = 250_000

    name: str = "market_quotes"

    _last_mid: Dict[str, float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("symbols must not be empty")
        if self.quotes_per_minute <= 0:
            raise ValueError("quotes_per_minute must be > 0")
        prices = self.base_prices or {}
        self._last_mid = {sym: prices.get(sym, self.base_price) for sym in self.symbols}

    def tables(self) -> tuple[str, ...]:
        return ("quotes",)

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        if table != "quotes":
            raise ValueError(f"Unknown table '{table}'")
        return self._quote_batches()

    def schema_for(self, table: str) -> SchemaLike | None:
        if table != "quotes":
            return None
        schema = dict(QUOTES_BASE_SCHEMA)
        for col in ("year", "month", "day", "hour"):
            schema[col] = self._partition_column_schema(col)
        return schema

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        if table != "quotes":
            return None
        return PartitionSpec(("year", "month", "day", "hour"))

    # ------------------ generation ------------------

    def _quote_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed)
        chunk: list[dict] = []
        sequence = 1
        for current_date in self._date_range(self.start_date, self.end_date):
            minute_timestamps = self._minute_timestamps(current_date)
            if not minute_timestamps:
                continue
            for symbol in self.symbols:
                rows, sequence = self._rows_for_symbol_day(
                    symbol, minute_timestamps, rng, sequence
                )
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
        minute_timestamps: Sequence[datetime],
        rng: np.random.Generator,
        sequence_start: int,
    ) -> Tuple[list[dict], int]:
        rows: list[dict] = []
        sequence = sequence_start
        prev_mid = self._last_mid[symbol]
        dt_fraction = 1 / (6.5 * 60)  # approximate US trading day minutes
        mu_dt = self.mu * dt_fraction
        sigma_dt = self.sigma * math.sqrt(dt_fraction)

        for minute_ts in minute_timestamps:
            for _ in range(self.quotes_per_minute):
                mid_log_return = rng.normal(mu_dt, sigma_dt)
                mid_price = max(0.01, prev_mid * math.exp(mid_log_return))
                spread_bps = max(0.1, rng.lognormal(self.spread_bps_mean, self.spread_bps_sigma))
                spread = mid_price * spread_bps / 10_000.0
                bid = max(0.01, mid_price - spread / 2)
                ask = bid + spread
                bid_size = max(1, int(rng.normal(self.size_mean, self.size_sigma)))
                ask_size = max(1, int(rng.normal(self.size_mean, self.size_sigma)))
                second_offset = rng.integers(0, 60)
                ts = minute_ts + timedelta(seconds=int(second_offset))
                rows.append(
                    {
                        "timestamp": ts,
                        "symbol": symbol,
                        "bid_price": float(bid),
                        "ask_price": float(ask),
                        "bid_size": int(bid_size),
                        "ask_size": int(ask_size),
                        "spread_bps": float(spread_bps),
                        "sequence": sequence,
                    }
                )
                prev_mid = mid_price
                sequence += 1
        self._last_mid[symbol] = prev_mid
        return rows, sequence

    def _build_frame(self, rows: list[dict]) -> pl.DataFrame:
        df = pl.DataFrame(rows)
        return df.with_columns(
            [
                pl.col("timestamp").dt.year().cast(pl.Int16).alias("year"),
                pl.col("timestamp").dt.month().cast(pl.Int8).alias("month"),
                pl.col("timestamp").dt.day().cast(pl.Int8).alias("day"),
                pl.col("timestamp").dt.hour().cast(pl.Int8).alias("hour"),
            ]
        )

    @staticmethod
    def _partition_column_schema(column: str) -> pl.DataType:
        mapping = {
            "year": pl.Int16,
            "month": pl.Int8,
            "day": pl.Int8,
            "hour": pl.Int8,
        }
        return mapping[column]

    # ------------------ utilities ------------------

    def _minute_timestamps(self, day: date) -> list[datetime]:
        start_hour, end_hour = self.trading_hours
        start_dt = datetime.combine(day, time(start_hour, 0))
        end_dt = datetime.combine(day, time(end_hour, 0))
        current = start_dt
        step = timedelta(minutes=1)
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
