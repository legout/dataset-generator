from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Tuple

import polars as pl

from dataset_generator.catalog.configs import CatalogConfig
from dataset_generator.catalog.ducklake_catalog import DuckLakeCatalog
from dataset_generator.core.interfaces import PartitionSpec, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config, filesystem_and_root

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - optional dependency
    duckdb = None  # type: ignore
    OPTIONAL_ERROR = exc
else:
    OPTIONAL_ERROR = None

class DuckLakeWriter(TableWriter):
    format_name = "ducklake"

    def __init__(
        self,
        output_uri: str,
        s3: S3Config | None,
        catalog: CatalogConfig | None,
        options: WriterOptions,
    ) -> None:
        if catalog is None:
            raise ValueError("DuckLakeWriter requires a catalog configuration")
        if OPTIONAL_ERROR is not None:
            raise RuntimeError(
                "duckdb is required for DuckLakeWriter. Install with 'pip install dataset-generator[ducklake]'"
            ) from OPTIONAL_ERROR

        self._fs, self._root = filesystem_and_root(output_uri, s3)
        self._options = options
        self._catalog = DuckLakeCatalog(catalog)
        self._partition_counters: Dict[str, Dict[Tuple[object, ...], int]] = defaultdict(dict)
        self._dimension_counters: Dict[str, int] = defaultdict(int)

        self._conn = duckdb.connect()
        self._conn.execute("INSTALL ducklake")
        self._conn.execute("LOAD ducklake")
        if s3:
            self._configure_s3(s3)

    def write(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        *,
        schema: dict[str, pl.DataType] | None,
        partition_spec: PartitionSpec | None,
    ) -> None:
        location = f"{self._root}/{table}" if table else self._root
        self._catalog.register_table(table, location, partition_spec)
        if partition_spec:
            self._write_partitioned(table, batches, partition_spec)
        else:
            self._write_dimension(table, batches)

    def _write_dimension(self, table: str, batches: Iterable[pl.DataFrame]) -> None:
        frames = list(batches)
        if not frames:
            return
        df = pl.concat(frames)
        idx = self._dimension_counters[table]
        filename = f"{table}-{idx:05d}.parquet"
        path = f"{self._root}/{table}/{filename}"
        self._ensure_parent(path)
        with self._fs.open(path, "wb") as handle:
            df.write_parquet(handle, compression=self._options.compression)
        self._dimension_counters[table] = idx + 1

    def _write_partitioned(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        partition_spec: PartitionSpec,
    ) -> None:
        for batch in batches:
            groups = batch.group_by(list(partition_spec.columns), maintain_order=True)
            for key, subdf in groups:
                key_tuple = self._normalise_partition_key(key)
                folder = self._partition_folder(table, partition_spec, key_tuple)
                if not self._fs.exists(folder):
                    self._fs.makedirs(folder, exist_ok=True)
                idx = self._partition_counters[table].get(key_tuple, 0)
                path = f"{folder}/part-{idx:05d}.parquet"
                with self._fs.open(path, "wb") as handle:
                    subdf.write_parquet(handle, compression=self._options.compression)
                self._partition_counters[table][key_tuple] = idx + 1

    def _partition_folder(
        self, table: str, partition_spec: PartitionSpec, key_tuple: Tuple[object, ...]
    ) -> str:
        parts = []
        for col, value in zip(partition_spec.columns, key_tuple):
            if isinstance(value, (int, float)):
                int_value = int(value)
                if col in {"month", "day"}:
                    parts.append(f"{col}={int_value:02d}")
                else:
                    parts.append(f"{col}={int_value}")
            else:
                parts.append(f"{col}={value}")
        return f"{self._root}/{table}/" + "/".join(parts)

    def _configure_s3(self, s3: S3Config) -> None:
        self._conn.execute("SET s3_access_key_id = ?", [s3.key])
        self._conn.execute("SET s3_secret_access_key = ?", [s3.secret])
        self._conn.execute("SET s3_region = ?", [s3.region])
        if s3.endpoint_url:
            self._conn.execute("SET s3_endpoint = ?", [s3.endpoint_url])
        if s3.use_ssl is not None:
            self._conn.execute("SET s3_use_ssl = ?", [int(bool(s3.use_ssl))])

    def _ensure_parent(self, path: str) -> None:
        parent = path.rsplit("/", 1)[0]
        if not self._fs.exists(parent):
            self._fs.makedirs(parent, exist_ok=True)

    @staticmethod
    def _normalise_partition_key(key: object) -> Tuple[object, ...]:
        if isinstance(key, tuple):
            return key
        if isinstance(key, list):
            return tuple(key)
        return (key,)
