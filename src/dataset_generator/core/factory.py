"""Factory helpers for registering and instantiating generators and writers."""

from __future__ import annotations

from typing import Any, Callable, Dict

from dataset_generator.catalog.configs import CatalogConfig
from dataset_generator.core.interfaces import GeneratorBase, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config


GeneratorConstructor = Callable[..., GeneratorBase]
WriterConstructor = Callable[[str, S3Config | None, CatalogConfig | None, WriterOptions], TableWriter]


_GENERATOR_REGISTRY: Dict[str, GeneratorConstructor] = {}
_WRITER_REGISTRY: Dict[str, WriterConstructor] = {}


def register_generator(name: str, constructor: GeneratorConstructor) -> None:
    """Register a dataset generator constructor under ``name``."""
    _GENERATOR_REGISTRY[name] = constructor


def register_writer(name: str, constructor: WriterConstructor) -> None:
    """Register a table writer constructor under ``name``."""
    _WRITER_REGISTRY[name] = constructor


def create_generator(name: str, **kwargs: Any) -> GeneratorBase:
    """Instantiate the registered generator.

    Args:
        name: Identifier passed to :func:`register_generator`.
        **kwargs: Parameters forwarded to the generator constructor.

    Returns:
        GeneratorBase: A configured generator instance.

    Raises:
        ValueError: If ``name`` is unknown.
    """
    try:
        constructor = _GENERATOR_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_GENERATOR_REGISTRY)) or "<none>"
        raise ValueError(f"Unknown generator '{name}'. Available: {available}") from exc
    return constructor(**kwargs)


def get_generator_constructor(name: str) -> GeneratorConstructor:
    """Look up the raw constructor for ``name`` without instantiating it.

    Raises:
        ValueError: If ``name`` is unknown.
    """
    try:
        return _GENERATOR_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_GENERATOR_REGISTRY)) or "<none>"
        raise ValueError(f"Unknown generator '{name}'. Available: {available}") from exc


def create_writer(
    name: str,
    output_uri: str,
    s3: S3Config | None,
    catalog: CatalogConfig | None,
    options: WriterOptions | None = None,
) -> TableWriter:
    """Instantiate a writer.

    Args:
        name: Identifier passed to :func:`register_writer`.
        output_uri: Base location (filesystem path, S3 URI, warehouse path).
        s3: Optional S3 configuration for remote writes.
        catalog: Optional catalog configuration (Delta/Iceberg/DuckLake).
        options: Writer tuning parameters.

    Raises:
        ValueError: If ``name`` is unknown.
    """
    try:
        constructor = _WRITER_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_WRITER_REGISTRY)) or "<none>"
        raise ValueError(f"Unknown writer '{name}'. Available: {available}") from exc
    opts = options or WriterOptions()
    return constructor(output_uri, s3, catalog, opts)


def available_generators() -> tuple[str, ...]:
    """Return the alphabetically sorted generator names."""
    return tuple(sorted(_GENERATOR_REGISTRY))


def available_writers() -> tuple[str, ...]:
    """Return the alphabetically sorted writer names."""
    return tuple(sorted(_WRITER_REGISTRY))
