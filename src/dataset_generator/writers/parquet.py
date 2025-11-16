from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Tuple

import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config, filesystem_and_root


class ParquetPartitionedWriter(TableWriter):
    """Write tables as partitioned Parquet datasets to the local FS or S3."""

    format_name = "parquet"

    def __init__(
        self,
        output_uri: str,
        s3: S3Config | None,
        catalog: object | None,
        options: WriterOptions,
    ) -> None:
        self._fs, self._root = filesystem_and_root(output_uri, s3)
        self._options = options
        self._partition_counters: Dict[str, Dict[Tuple[str, ...], int]] = defaultdict(dict)

    def write(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        *,
        schema: dict[str, pl.DataType] | None,
        partition_spec: PartitionSpec | None,
    ) -> None:
        """Write the provided batches either as a single file or partitioned tree."""
        if partition_spec:
            self._write_partitioned(table, batches, partition_spec)
        else:
            self._write_single(table, batches)

    def _write_single(self, table: str, batches: Iterable[pl.DataFrame]) -> None:
        frames = list(batches)
        if not frames:
            return
        df = pl.concat(frames)
        path = f"{self._root}/{table}/{table}.parquet"
        self._ensure_parent(path)
        with self._fs.open(path, "wb") as handle:
            df.write_parquet(handle, compression=self._options.compression)

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
                folder = f"{self._root}/{table}/" + "/".join(parts)
                if not self._fs.exists(folder):
                    self._fs.makedirs(folder, exist_ok=True)
                idx = self._partition_counters[table].get(key_tuple, 0)
                path = f"{folder}/part-{idx:05d}.parquet"
                with self._fs.open(path, "wb") as handle:
                    subdf.write_parquet(handle, compression=self._options.compression)
                self._partition_counters[table][key_tuple] = idx + 1

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
