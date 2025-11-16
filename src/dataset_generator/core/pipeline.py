from __future__ import annotations

from typing import Iterable, Sequence

from dataset_generator.core.interfaces import GeneratorBase, TableWriter


def write_dataset(
    generator: GeneratorBase,
    writer: TableWriter,
    tables: Sequence[str] | None = None,
) -> None:
    """Generate all requested tables and stream them to the writer.

    Each table is materialized via ``generator.batches_for`` and forwarded to
    the writer together with the schema and partition specification (when
    provided). This ensures storage backends can create tables with the correct
    shape and layout.

    Args:
        generator: Dataset generator that produces batches per table.
        writer: Writer implementation that persists batches.
        tables: Optional subset of table names. When omitted, every table
            returned by ``generator.tables()`` is written.
    """
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
