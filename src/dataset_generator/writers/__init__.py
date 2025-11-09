from __future__ import annotations

from dataset_generator.core.factory import register_writer
from dataset_generator.writers.delta import DeltaLakeWriter
from dataset_generator.writers.ducklake import DuckLakeWriter
from dataset_generator.writers.iceberg import IcebergWriter
from dataset_generator.writers.parquet import ParquetPartitionedWriter


register_writer(
    "parquet",
    lambda output, s3, catalog, options: ParquetPartitionedWriter(
        output, s3, catalog, options
    ),
)
register_writer(
    "delta",
    lambda output, s3, catalog, options: DeltaLakeWriter(output, s3, catalog, options),
)
register_writer(
    "iceberg",
    lambda output, s3, catalog, options: IcebergWriter(output, s3, catalog, options),
)
register_writer(
    "ducklake",
    lambda output, s3, catalog, options: DuckLakeWriter(output, s3, catalog, options),
)


__all__ = [
    "ParquetPartitionedWriter",
    "DeltaLakeWriter",
    "IcebergWriter",
    "DuckLakeWriter",
]
