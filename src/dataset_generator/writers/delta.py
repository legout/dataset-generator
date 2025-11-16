from __future__ import annotations

from typing import Iterable

import polars as pl

from dataset_generator.core.interfaces import PartitionSpec, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config

try:
    from deltalake import DeltaTable, write_deltalake
except ImportError as exc:  # pragma: no cover - optional dependency
    DeltaTable = None  # type: ignore
    write_deltalake = None  # type: ignore
    OPTIONAL_ERROR = exc
else:  # pragma: no branch
    OPTIONAL_ERROR = None


class DeltaLakeWriter(TableWriter):
    """Write tables to a Delta Lake location using deltalake bindings.

    Args:
        output_uri: Target table root or directory.
        s3: Optional S3 configuration passed to the Delta client.
        catalog: Unused placeholder for interface compatibility.
        options: Writer tuning parameters.
    """

    format_name = "delta"

    def __init__(
        self,
        output_uri: str,
        s3: S3Config | None,
        catalog: object | None,
        options: WriterOptions,
    ) -> None:
        if OPTIONAL_ERROR is not None:
            raise RuntimeError(
                "deltalake is required for DeltaLakeWriter. Install with 'pip install dataset-generator[delta]'"
            ) from OPTIONAL_ERROR

        self._base_uri = output_uri.rstrip("/")
        self._s3 = s3
        self._options = options

    def write(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        *,
        schema: dict[str, pl.DataType] | None,
        partition_spec: PartitionSpec | None,
    ) -> None:
        """Append all batches to a Delta table, creating it on the first write."""
        uri = f"{self._base_uri}/{table}" if table else self._base_uri
        storage_options = self._storage_options()

        table_exists = self._table_exists(uri, storage_options)
        mode = "append" if table_exists else "overwrite"
        partition_cols = partition_spec.columns if partition_spec else None

        for batch in batches:
            write_deltalake(
                uri,
                batch.to_arrow(),
                mode=mode,
                partition_by=partition_cols,
                storage_options=storage_options,
            )
            mode = "append"

    def _storage_options(self) -> dict[str, str] | None:
        if not self._s3:
            return None
        options: dict[str, str] = {
            "AWS_ACCESS_KEY_ID": self._s3.key,
            "AWS_SECRET_ACCESS_KEY": self._s3.secret,
            "AWS_REGION": self._s3.region,
        }
        if self._s3.endpoint_url:
            options["AWS_ENDPOINT_URL"] = self._s3.endpoint_url
            if self._s3.use_ssl is False or (
                self._s3.use_ssl is None and self._s3.endpoint_url.startswith("http://")
            ):
                options["AWS_ALLOW_HTTP"] = "true"
        return options

    def _table_exists(self, uri: str, storage_options: dict[str, str] | None) -> bool:
        if DeltaTable is None:
            return False
        try:
            DeltaTable(uri, storage_options=storage_options)
            return True
        except Exception:
            return False
