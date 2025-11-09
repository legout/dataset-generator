from __future__ import annotations

from typing import Iterable

import polars as pl

from dataset_generator.catalog.configs import CatalogConfig
from dataset_generator.core.interfaces import PartitionSpec, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config

try:
    from pyiceberg.catalog.sql import SqlCatalog
    from pyiceberg.partitioning import PartitionField, PartitionSpec as IcebergPartitionSpec
    from pyiceberg.schema import NestedField, Schema
    from pyiceberg.transforms import IdentityTransform
    from pyiceberg.types import (
        BooleanType,
        DateType,
        DoubleType,
        FloatType,
        IntegerType,
        LongType,
        StringType,
    )
except ImportError as exc:  # pragma: no cover - optional dependency
    SqlCatalog = None  # type: ignore
    IcebergPartitionSpec = None  # type: ignore
    Schema = None  # type: ignore
    OPTIONAL_ERROR = exc
else:
    OPTIONAL_ERROR = None


class IcebergWriter(TableWriter):
    format_name = "iceberg"

    def __init__(
        self,
        output_uri: str,
        s3: S3Config | None,
        catalog: CatalogConfig | None,
        options: WriterOptions,
    ) -> None:
        if OPTIONAL_ERROR is not None:
            raise RuntimeError(
                "pyiceberg is required for IcebergWriter. Install with 'pip install dataset-generator[iceberg]'"
            ) from OPTIONAL_ERROR
        if catalog is None:
            raise ValueError("IcebergWriter requires a catalog configuration")

        extras = dict(catalog.extras or {})
        if s3:
            extras.setdefault("s3.access-key-id", s3.key)
            extras.setdefault("s3.secret-access-key", s3.secret)
            extras.setdefault("s3.region", s3.region)
            if s3.endpoint_url:
                extras.setdefault("s3.endpoint", s3.endpoint_url)
            if s3.use_ssl is False:
                extras.setdefault("s3.ssl-enabled", "false")

        self._catalog = SqlCatalog(
            catalog.namespace or "dataset_generator",
            uri=catalog.uri,
            warehouse=output_uri,
            **extras,
        )
        self._catalog_config = catalog
        self._warehouse = output_uri.rstrip("/")

    def write(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        *,
        schema: dict[str, pl.DataType] | None,
        partition_spec: PartitionSpec | None,
    ) -> None:
        if schema is None:
            raise ValueError("Schema is required to write Iceberg tables")

        identifier = self._identifier(table)
        if not self._catalog.table_exists(identifier):
            iceberg_schema = self._to_iceberg_schema(schema)
            spec = self._to_partition_spec(iceberg_schema, partition_spec)
            location = f"{self._warehouse}/{table}"
            self._catalog.create_table(
                identifier,
                schema=iceberg_schema,
                partition_spec=spec,
                location=location,
            )

        iceberg_table = self._catalog.load_table(identifier)
        for batch in batches:
            iceberg_table.append(batch.to_arrow())

    def _identifier(self, table: str) -> str:
        if self._catalog_config.namespace:
            return f"{self._catalog_config.namespace}.{table}"
        return table

    @staticmethod
    def _to_iceberg_schema(schema: dict[str, pl.DataType]) -> Schema:
        fields = []
        for idx, (name, dtype) in enumerate(schema.items(), start=1):
            fields.append(
                NestedField(
                    field_id=idx,
                    name=name,
                    field_type=IcebergWriter._convert_dtype(dtype),
                    is_optional=True,
                )
            )
        return Schema(*fields)

    @staticmethod
    def _convert_dtype(dtype: pl.DataType):
        if dtype == pl.Int64:
            return LongType()
        if dtype in {pl.Int32, pl.Int16, pl.Int8}:
            return IntegerType()
        if dtype == pl.Float64:
            return DoubleType()
        if dtype == pl.Float32:
            return FloatType()
        if dtype == pl.Boolean:
            return BooleanType()
        if dtype == pl.Date:
            return DateType()
        if dtype == pl.Utf8:
            return StringType()
        raise TypeError(f"Unsupported Polars dtype for Iceberg: {dtype}")

    @staticmethod
    def _to_partition_spec(
        schema: Schema, partition_spec: PartitionSpec | None
    ) -> IcebergPartitionSpec | None:
        if partition_spec is None:
            return None
        fields = []
        next_id = len(schema.fields) + 1
        for column in partition_spec.columns:
            source_field = schema.find_field(column)
            fields.append(
                PartitionField(
                    source_id=source_field.field_id,
                    field_id=next_id,
                    transform=IdentityTransform(),
                    name=column,
                )
            )
            next_id += 1
        return IcebergPartitionSpec(*fields)
