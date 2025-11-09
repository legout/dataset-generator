from __future__ import annotations

import os
import unittest
from datetime import date
from tempfile import TemporaryDirectory

import polars as pl

from dataset_generator import ECommerceGenerator, WriterOptions, write_dataset
from dataset_generator.core.interfaces import PartitionSpec
from dataset_generator.writers.parquet import ParquetPartitionedWriter


class ECommerceGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = ECommerceGenerator(
            seed=123,
            n_customers=50,
            n_products=30,
            orders_per_day=20,
            order_items_mean=1.8,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 2),
            file_rows_target=10,
            orders_partitioning="ym",
            orders_mode="fixed",
        )

    def test_tables_and_schema(self) -> None:
        tables = self.generator.tables()
        self.assertIn("customers", tables)
        self.assertIn("orders", tables)

        customers_batch = list(self.generator.batches_for("customers"))[0]
        self.assertIsInstance(customers_batch, pl.DataFrame)
        self.assertEqual(len(customers_batch), 50)
        schema = self.generator.schema_for("customers")
        self.assertIn("customer_id", schema)
        self.assertEqual(schema["customer_id"], pl.Int64)

    def test_orders_partition_spec(self) -> None:
        spec = self.generator.partition_spec_for("orders")
        self.assertIsInstance(spec, PartitionSpec)
        self.assertEqual(spec.columns, ("year", "month"))

    def test_write_dataset_parquet(self) -> None:
        with TemporaryDirectory() as tmpdir:
            writer = ParquetPartitionedWriter(
                output_uri=tmpdir,
                s3=None,
                catalog=None,
                options=WriterOptions(file_rows_target=10, compression="snappy"),
            )
            write_dataset(self.generator, writer, tables=("customers", "orders"))

            customers_file = os.path.join(tmpdir, "customers")
            orders_dir = os.path.join(tmpdir, "orders")
            self.assertTrue(os.path.isdir(customers_file))
            self.assertTrue(os.path.isdir(orders_dir))
            partitions = [
                entry for entry in os.listdir(orders_dir) if entry.startswith("year=")
            ]
            self.assertTrue(partitions)

    def test_yearmonth_partition(self) -> None:
        gen = ECommerceGenerator(
            seed=10,
            orders_per_day=5,
            order_items_mean=1.2,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 3),
            orders_partitioning="yearmonth",
            file_rows_target=10,
        )
        orders_batches = list(gen.batches_for("orders"))
        self.assertTrue(orders_batches)
        for batch in orders_batches:
            self.assertIn("yearmonth", batch.columns)
            self.assertNotIn("day", batch.columns)
            self.assertTrue(batch.get_column("yearmonth").str.contains("-").all())

    def test_random_orders_range_mode(self) -> None:
        gen = ECommerceGenerator(
            seed=77,
            orders_per_day=50,
            order_items_mean=1.2,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 5),
            orders_mode="range",
            orders_min=40,
            orders_max=60,
            file_rows_target=100,
        )
        counts = [count for _, count in gen._daily_counts]
        self.assertTrue(all(40 <= c <= 60 for c in counts))
        self.assertGreater(len(set(counts)), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
