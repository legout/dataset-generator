from __future__ import annotations

from typing import Iterable, Sequence

from dataset_generator.core.interfaces import GeneratorBase, TableWriter


def write_dataset(
    generator: GeneratorBase,
    writer: TableWriter,
    tables: Sequence[str] | None = None,
) -> None:
    selected: Iterable[str] = tables or generator.tables()
    for table in selected:
        batches = generator.batches_for(table)
        schema = generator.schema_for(table)
        partition_spec = generator.partition_spec_for(table)
        writer.write(
            table,
            batches,
            schema=schema,
            partition_spec=partition_spec,
        )
