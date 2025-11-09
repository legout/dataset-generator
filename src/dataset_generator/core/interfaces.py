from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol

import polars as pl


SchemaLike = Mapping[str, pl.DataType]


@dataclass(frozen=True)
class PartitionSpec:
    columns: tuple[str, ...] = ("year", "month", "day")

    def as_tuple(self) -> tuple[str, ...]:
        return self.columns


@dataclass(frozen=True)
class WriterOptions:
    file_rows_target: int = 250_000
    compression: str = "snappy"


class GeneratorBase(Protocol):
    """Protocol that all dataset generators must satisfy."""

    name: str

    def tables(self) -> tuple[str, ...]:
        ...

    def batches_for(self, table: str) -> Iterable[pl.DataFrame]:
        ...

    def schema_for(self, table: str) -> SchemaLike | None:
        ...

    def partition_spec_for(self, table: str) -> PartitionSpec | None:
        ...


class TableWriter(Protocol):
    """Common interface for all table writers."""

    format_name: str

    def write(
        self,
        table: str,
        batches: Iterable[pl.DataFrame],
        *,
        schema: SchemaLike | None,
        partition_spec: PartitionSpec | None,
    ) -> None:
        ...
