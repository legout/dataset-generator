"""Core building blocks shared by generators and writers."""

from dataset_generator.core.factory import (
    available_generators,
    available_writers,
    create_generator,
    create_writer,
    get_generator_constructor,
)
from dataset_generator.core.interfaces import (
    GeneratorBase,
    PartitionSpec,
    TableWriter,
    WriterOptions,
)
from dataset_generator.core.pipeline import write_dataset

__all__ = [
    "GeneratorBase",
    "PartitionSpec",
    "TableWriter",
    "WriterOptions",
    "available_generators",
    "available_writers",
    "create_generator",
    "create_writer",
    "get_generator_constructor",
    "write_dataset",
]
