from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Iterable, Iterator, Literal, Sequence, Tuple

import numpy as np
import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, SchemaLike


CUSTOMERS_SCHEMA: SchemaLike = {
    "customer_id": pl.Int64,
    "name": pl.Utf8,
    "email": pl.Utf8,
    "signup_date": pl.Date,
    "country": pl.Utf8,
    "is_vip": pl.Boolean,
}

PRODUCTS_SCHEMA: SchemaLike = {
    "product_id": pl.Int64,
    "sku": pl.Utf8,
    "category": pl.Utf8,
    "price": pl.Float64,
    "discount": pl.Float64,
    "active": pl.Boolean,
}

ORDERS_BASE_SCHEMA: SchemaLike = {
    "order_id": pl.Int64,
    "customer_id": pl.Int64,
    "order_date": pl.Date,
    "hour_of_day": pl.Int16,
    "status": pl.Utf8,
    "amount": pl.Float64,
}

ORDER_ITEMS_BASE_SCHEMA: SchemaLike = {
    "order_item_id": pl.Int64,
    "order_id": pl.Int64,
    "product_id": pl.Int64,
    "qty": pl.Int16,
}


@dataclass
class ECommerceGenerator:
    """Generate a synthetic multi-table transactional e-commerce dataset.

    The generator emits customers, products, orders, and order_items tables with
    controllable volumes, batching behavior, and partition columns. Batches are
    sized so downstream writers can stream data without loading everything into
    memory.

    Args:
        seed: Base RNG seed used to derive deterministic sub-seeds.
        n_customers: Number of unique synthetic customers.
        n_products: Number of unique synthetic products.
        orders_per_day: Baseline number of orders sampled per day.
        order_items_mean: Average number of line items per order.
        start_date: Inclusive lower bound for generated orders.
        end_date: Inclusive upper bound for generated orders.
        file_rows_target: Approximate number of rows placed into each batch.
        orders_partitioning: Partitioning strategy for orders/order_items
            tables (``"ymd"``, ``"ym"``, or ``"yearmonth"``).
        orders_mode: Strategy for sampling daily order counts
            (``"fixed"``, ``"range"``, or ``"normal"``).
        orders_min: Lower bound when ``orders_mode="range"``.
        orders_max: Upper bound when ``orders_mode="range"``.
        orders_mean: Mean used when ``orders_mode="normal"``.
        orders_std: Standard deviation when ``orders_mode="normal"``.
        orders_floor: Minimum number of orders enforced after sampling.
    """
    seed: int = 42
    n_customers: int = 1_000_000
    n_products: int = 50_000
    orders_per_day: int = 200_000
    order_items_mean: float = 2.6
    start_date: date = date(2023, 1, 1)
    end_date: date = date(2023, 3, 31)
    file_rows_target: int = 250_000
    orders_partitioning: Literal["ymd", "ym", "yearmonth"] = "ym"
    orders_mode: Literal["fixed", "range", "normal"] = "fixed"
    orders_min: int | None = None
    orders_max: int | None = None
    orders_mean: float | None = None
    orders_std: float | None = None
    orders_floor: int = 0

    name: str = "ecommerce"

    def __post_init__(self) -> None:
        self._categories = np.array(
            [
                "apparel",
                "electronics",
                "home",
                "beauty",
                "sports",
                "toys",
                "books",
                "groceries",
                "pet",
                "auto",
            ]
        )
        self._validate_configuration()
        self._partition_columns_cache = self._resolve_partition_columns()
        self._daily_counts: Tuple[Tuple[date, int], ...] = tuple(self._compute_daily_counts())

    def tables(self) -> tuple[str, ...]:
        return ("customers", "products", "orders", "order_items")

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        if table == "customers":
            return (self._generate_customers(),)
        if table == "products":
            return (self._generate_products(),)
        if table == "orders":
            return self._order_batches()
        if table == "order_items":
            return self._order_item_batches()
        raise ValueError(f"Unknown table '{table}'")

    def schema_for(self, table: str) -> SchemaLike | None:
        if table == "customers":
            return CUSTOMERS_SCHEMA
        if table == "products":
            return PRODUCTS_SCHEMA
        if table == "orders":
            schema = dict(ORDERS_BASE_SCHEMA)
            for col in self._partition_columns_cache:
                schema.update(self._partition_column_schema(col))
            return schema
        if table == "order_items":
            schema = dict(ORDER_ITEMS_BASE_SCHEMA)
            for col in self._partition_columns_cache:
                schema.update(self._partition_column_schema(col))
            return schema
        return None

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        if table in {"orders", "order_items"}:
            return PartitionSpec(self._partition_columns_cache)
        return None

    # ------------------ helpers ------------------

    def _partition_column_schema(self, column: str) -> SchemaLike:
        if column == "year":
            return {"year": pl.Int16}
        if column == "month":
            return {"month": pl.Int8}
        if column == "day":
            return {"day": pl.Int8}
        if column == "yearmonth":
            return {"yearmonth": pl.Utf8}
        raise ValueError(f"Unsupported partition column '{column}'")

    def _resolve_partition_columns(self) -> Tuple[str, ...]:
        if self.orders_partitioning == "ymd":
            return ("year", "month", "day")
        if self.orders_partitioning == "yearmonth":
            return ("yearmonth",)
        return ("year", "month")

    def _validate_configuration(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")

        if self.orders_mode == "fixed":
            if self.orders_per_day < 0:
                raise ValueError("orders_per_day must be non-negative")
        elif self.orders_mode == "range":
            if self.orders_min is None:
                self.orders_min = max(self.orders_floor, int(self.orders_per_day * 0.7))
            if self.orders_max is None:
                candidate = int(self.orders_per_day * 1.3)
                self.orders_max = max(self.orders_min, candidate)
            if self.orders_min < 0 or self.orders_max < 0:
                raise ValueError("orders_min/orders_max must be non-negative")
            if self.orders_min > self.orders_max:
                raise ValueError("orders_min must be <= orders_max")
        elif self.orders_mode == "normal":
            if self.orders_mean is None:
                self.orders_mean = float(self.orders_per_day)
            if self.orders_std is None:
                self.orders_std = max(1.0, self.orders_per_day * 0.1)
            if self.orders_std < 0:
                raise ValueError("orders_std must be non-negative")
        else:
            raise ValueError(f"Unsupported orders_mode '{self.orders_mode}'")

        if self.orders_floor < 0:
            raise ValueError("orders_floor must be >= 0")

    def _compute_daily_counts(self) -> Iterable[Tuple[date, int]]:
        rng = np.random.default_rng(self.seed + 505)
        for day in self._date_range(self.start_date, self.end_date):
            yield day, self._sample_orders_for_day(rng)

    def _sample_orders_for_day(self, rng: np.random.Generator) -> int:
        if self.orders_mode == "fixed":
            return max(self.orders_floor, self.orders_per_day)
        if self.orders_mode == "range":
            assert self.orders_min is not None and self.orders_max is not None
            value = int(rng.integers(self.orders_min, self.orders_max + 1))
            return max(self.orders_floor, value)
        if self.orders_mode == "normal":
            assert self.orders_mean is not None and self.orders_std is not None
            value = int(round(rng.normal(self.orders_mean, self.orders_std)))
            return max(self.orders_floor, value)
        raise ValueError(f"Unsupported orders_mode '{self.orders_mode}'")

    # ------------------ generators ------------------

    def _generate_customers(self) -> pl.DataFrame:
        rng = np.random.default_rng(self.seed + 101)
        n = self.n_customers
        signup_offsets = rng.integers(0, 365 * 4, size=n, dtype=np.int32)
        signup_dates = np.array(
            date(2020, 1, 1).toordinal() + signup_offsets, dtype=np.int32
        )

        df = pl.DataFrame(
            {
                "customer_id": np.arange(1, n + 1, dtype=np.int64),
                "signup_date": signup_dates,
                "country": rng.choice(
                    np.array(
                        [
                            "DE",
                            "AT",
                            "CH",
                            "FR",
                            "NL",
                            "BE",
                            "IT",
                            "ES",
                            "PL",
                            "SE",
                        ]
                    ),
                    size=n,
                    replace=True,
                ),
                "is_vip": rng.random(n) < 0.05,
            }
        )

        df = df.with_columns(
            [
                (pl.lit("cust_") + pl.col("customer_id").cast(pl.Utf8)).alias("name"),
                (
                    pl.lit("user")
                    + pl.col("customer_id").cast(pl.Utf8)
                    + pl.lit("@example.com")
                ).alias("email"),
                pl.from_epoch(
                    pl.col("signup_date").cast(pl.Int64) * 24 * 3600, time_unit="s"
                )
                .dt.date()
                .alias("signup_date"),
            ]
        )
        return df

    def _generate_products(self) -> pl.DataFrame:
        rng = np.random.default_rng(self.seed + 202)
        p = self.n_products
        base_price = rng.lognormal(mean=3.0, sigma=0.5, size=p)
        discounts = np.clip(rng.normal(0.05, 0.08, size=p), 0.0, 0.6)

        return pl.DataFrame(
            {
                "product_id": np.arange(1, p + 1, dtype=np.int64),
                "sku": np.array([f"SKU-{i:08d}" for i in range(1, p + 1)], dtype=object),
                "category": rng.choice(self._categories, size=p, replace=True),
                "price": base_price.round(2),
                "discount": discounts.round(2),
                "active": rng.random(p) > 0.02,
            }
        )

    def _order_batches(self) -> Iterator[pl.DataFrame]:
        rng = np.random.default_rng(self.seed + 303)
        current_order_id = 1
        for day, total in self._daily_counts:
            remaining = total
            while remaining > 0:
                batch = min(remaining, self.file_rows_target)
                orders_df = self._order_batch(rng, day, current_order_id, batch)
                current_order_id += batch
                remaining -= batch
                yield orders_df

    def _order_item_batches(self) -> Iterator[pl.DataFrame]:
        order_rng = np.random.default_rng(self.seed + 303)
        item_rng = np.random.default_rng(self.seed + 404)
        current_order_id = 1
        for day, total in self._daily_counts:
            remaining = total
            while remaining > 0:
                batch = min(remaining, self.file_rows_target)
                orders_df = self._order_batch(order_rng, day, current_order_id, batch)
                current_order_id += batch
                remaining -= batch
                yield self._order_items_for_orders(item_rng, orders_df)

    def _order_batch(
        self,
        rng: np.random.Generator,
        day: date,
        start_id: int,
        n_orders: int,
    ) -> pl.DataFrame:
        hour_weights = np.array(
            [
                0.02,
                0.01,
                0.01,
                0.01,
                0.02,
                0.03,
                0.04,
                0.05,
                0.06,
                0.06,
                0.05,
                0.05,
                0.04,
                0.04,
                0.05,
                0.06,
                0.07,
                0.08,
                0.09,
                0.08,
                0.05,
                0.04,
                0.03,
                0.02,
            ],
            dtype=float,
        )
        hour_weights /= hour_weights.sum()

        order_ids = np.arange(start_id, start_id + n_orders, dtype=np.int64)
        cust_ids = rng.integers(1, self.n_customers + 1, size=n_orders, dtype=np.int64)
        hours = rng.choice(np.arange(24), size=n_orders, p=hour_weights)
        statuses = rng.choice(
            np.array(["completed", "returned", "cancelled"], dtype=object),
            size=n_orders,
            p=[0.90, 0.06, 0.04],
        )
        amounts = np.clip(rng.gamma(shape=3.0, scale=20.0, size=n_orders), 5.0, None)

        order_dates = pl.Series("order_date", [day] * n_orders, dtype=pl.Date)

        df = pl.DataFrame(
            {
                "order_id": order_ids,
                "customer_id": cust_ids,
                "order_date": order_dates,
                "hour_of_day": hours.astype(np.int16),
                "status": statuses,
                "amount": np.round(amounts, 2),
            }
        )
        extra_cols = []
        columns = set(self._partition_columns_cache)
        if "year" in columns:
            extra_cols.append(pl.col("order_date").dt.year().cast(pl.Int16).alias("year"))
        if "month" in columns:
            extra_cols.append(pl.col("order_date").dt.month().cast(pl.Int8).alias("month"))
        if "day" in columns:
            extra_cols.append(pl.col("order_date").dt.day().cast(pl.Int8).alias("day"))
        if "yearmonth" in columns:
            extra_cols.append(pl.col("order_date").dt.strftime("%Y-%m").alias("yearmonth"))

        return df.with_columns(extra_cols)

    def _order_items_for_orders(
        self, rng: np.random.Generator, orders_df: pl.DataFrame
    ) -> pl.DataFrame:
        n_orders = orders_df.height
        items_per_order = rng.poisson(self.order_items_mean, size=n_orders).astype(np.int32)
        items_per_order = np.where(items_per_order < 1, 1, items_per_order)
        total_items = int(items_per_order.sum())

        order_ids = np.repeat(orders_df.get_column("order_id").to_numpy(), items_per_order)
        product_ids = rng.integers(1, self.n_products + 1, size=total_items, dtype=np.int64)
        qty = rng.integers(1, 6, size=total_items, dtype=np.int16)

        items_df = pl.DataFrame(
            {
                "order_item_id": np.arange(1, total_items + 1, dtype=np.int64),
                "order_id": order_ids,
                "product_id": product_ids,
                "qty": qty,
            }
        )

        partition_cols = list(self._partition_columns_cache)
        if partition_cols:
            order_meta = orders_df.select(["order_id", *partition_cols])
            items_df = items_df.join(order_meta, on="order_id", how="left")
        return items_df

    @staticmethod
    def _date_range(start: date, end: date) -> Iterable[date]:
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)
