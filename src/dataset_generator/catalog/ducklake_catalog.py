from __future__ import annotations

import json
from typing import Optional

from dataset_generator.catalog.configs import CatalogConfig
from dataset_generator.core.interfaces import PartitionSpec

try:
    from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select, update
    from sqlalchemy.engine import Engine
    from sqlalchemy.sql import Insert
except ImportError as exc:  # pragma: no cover - optional dependency
    Engine = None  # type: ignore
    OPTIONAL_ERROR = exc
else:
    OPTIONAL_ERROR = None


class DuckLakeCatalog:
    def __init__(self, config: CatalogConfig) -> None:
        if OPTIONAL_ERROR is not None:
            raise RuntimeError(
                "sqlalchemy is required for DuckLakeWriter. Install with 'pip install dataset-generator[ducklake]'"
            ) from OPTIONAL_ERROR
        self._engine: Engine = create_engine(config.uri, future=True)
        self._metadata = MetaData()
        self._tables = Table(
            "ducklake_tables",
            self._metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("table_name", String, unique=True, nullable=False),
            Column("location", String, nullable=False),
            Column("partition_spec", String, nullable=True),
        )
        self._metadata.create_all(self._engine)

    def register_table(
        self, table_name: str, location: str, partition_spec: PartitionSpec | None
    ) -> None:
        serialized = json.dumps(partition_spec.columns) if partition_spec else None
        with self._engine.begin() as conn:
            result = conn.execute(
                select(self._tables.c.id).where(self._tables.c.table_name == table_name)
            ).first()
            if result is None:
                insert_stmt: Insert = self._tables.insert().values(
                    table_name=table_name,
                    location=location,
                    partition_spec=serialized,
                )
                conn.execute(insert_stmt)
            else:
                conn.execute(
                    update(self._tables)
                    .where(self._tables.c.table_name == table_name)
                    .values(location=location, partition_spec=serialized)
                )

    def location_for(self, table_name: str) -> Optional[str]:
        with self._engine.begin() as conn:
            result = conn.execute(
                select(self._tables.c.location).where(
                    self._tables.c.table_name == table_name
                )
            ).first()
            if result is None:
                return None
            return result[0]
