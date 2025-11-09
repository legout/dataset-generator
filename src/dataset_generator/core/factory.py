from __future__ import annotations

from typing import Callable, Dict

from dataset_generator.catalog.configs import CatalogConfig
from dataset_generator.core.interfaces import GeneratorBase, TableWriter, WriterOptions
from dataset_generator.io.s3 import S3Config


GeneratorConstructor = Callable[..., GeneratorBase]
WriterConstructor = Callable[[str, S3Config | None, CatalogConfig | None, WriterOptions], TableWriter]


_GENERATOR_REGISTRY: Dict[str, GeneratorConstructor] = {}
_WRITER_REGISTRY: Dict[str, WriterConstructor] = {}


def register_generator(name: str, constructor: GeneratorConstructor) -> None:
    _GENERATOR_REGISTRY[name] = constructor


def register_writer(name: str, constructor: WriterConstructor) -> None:
    _WRITER_REGISTRY[name] = constructor


def create_generator(name: str, **kwargs) -> GeneratorBase:
    try:
        constructor = _GENERATOR_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_GENERATOR_REGISTRY)) or "<none>"
        raise ValueError(f"Unknown generator '{name}'. Available: {available}") from exc
    return constructor(**kwargs)


def get_generator_constructor(name: str) -> GeneratorConstructor:
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
    try:
        constructor = _WRITER_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_WRITER_REGISTRY)) or "<none>"
        raise ValueError(f"Unknown writer '{name}'. Available: {available}") from exc
    opts = options or WriterOptions()
    return constructor(output_uri, s3, catalog, opts)


def available_generators() -> tuple[str, ...]:
    return tuple(sorted(_GENERATOR_REGISTRY))


def available_writers() -> tuple[str, ...]:
    return tuple(sorted(_WRITER_REGISTRY))
