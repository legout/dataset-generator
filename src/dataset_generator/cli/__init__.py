from __future__ import annotations

import inspect
from datetime import date
from typing import Optional

try:
    import typer
except ImportError as exc:  # pragma: no cover - optional dependency
    typer = None  # type: ignore
    OPTIONAL_ERROR = exc
else:
    OPTIONAL_ERROR = None

from dataset_generator import (
    CatalogConfig,
    S3Config,
    WriterOptions,
    available_generators,
    available_writers,
    create_generator,
    create_writer,
    get_generator_constructor,
    write_dataset,
)


if OPTIONAL_ERROR is not None:  # pragma: no cover - runtime guard
    raise RuntimeError(
        "typer is required for the CLI. Install with 'pip install dataset-generator[cli]'"
    ) from OPTIONAL_ERROR


app = typer.Typer(help="Synthetic dataset generator CLI")


@app.command("list-datasets")
def list_datasets() -> None:
    """List available dataset generators."""
    for name in available_generators():
        typer.echo(name)


@app.command("list-formats")
def list_formats() -> None:
    """List supported output formats."""
    for name in available_writers():
        typer.echo(name)


@app.command("info")
def dataset_info(dataset: str) -> None:
    """Print the schema and partitioning metadata for a dataset.

    Args:
        dataset: Generator name registered via ``register_generator``.
    """
    gen = create_generator(dataset)
    typer.echo(f"Dataset: {dataset}")
    typer.echo("Tables:")
    for table in gen.tables():
        typer.echo(f"  - {table}")
        schema = gen.schema_for(table)
        if schema:
            typer.echo("    columns:")
            for name, dtype in schema.items():
                typer.echo(f"      {name}: {dtype}")
        spec = gen.partition_spec_for(table)
        if spec:
            typer.echo(f"    partition_by: {spec.columns}")


@app.command("generate")
def generate(
    dataset: str = typer.Argument(..., help="Dataset generator name"),
    format: str = typer.Option("parquet", "--format", help="Output format"),
    output: str = typer.Option(..., "--output", help="Target path or URI"),
    seed: int = typer.Option(42, help="Random seed"),
    n_customers: int = typer.Option(1_000_000, help="Number of customers"),
    n_products: int = typer.Option(50_000, help="Number of products"),
    orders_per_day: int = typer.Option(200_000, help="Orders per day"),
    order_items_mean: float = typer.Option(2.6, help="Average items per order"),
    start_date: date = typer.Option(date(2023, 1, 1), help="Start date"),
    end_date: date = typer.Option(date(2023, 3, 31), help="End date"),
    file_rows_target: int = typer.Option(250_000, help="Rows per output file"),
    compression: str = typer.Option("snappy", help="Compression codec"),
    orders_partitioning: str = typer.Option(
        "ym",
        help="Orders partitioning for ecommerce (choices: ymd, ym, yearmonth)",
        case_sensitive=False,
    ),
    orders_mode: str = typer.Option(
        "fixed",
        help="Daily order mode for ecommerce (choices: fixed, range, normal)",
        case_sensitive=False,
    ),
    orders_min: Optional[int] = typer.Option(None, help="Minimum orders per day when mode=range"),
    orders_max: Optional[int] = typer.Option(None, help="Maximum orders per day when mode=range"),
    orders_mean: Optional[float] = typer.Option(None, help="Mean orders per day when mode=normal"),
    orders_std: Optional[float] = typer.Option(None, help="Std dev for orders per day when mode=normal"),
    orders_floor: int = typer.Option(0, help="Minimum floor after sampling orders per day"),
    s3_uri: Optional[str] = typer.Option(None, help="Base S3 URI"),
    s3_key: Optional[str] = typer.Option(None, help="S3 access key"),
    s3_secret: Optional[str] = typer.Option(None, help="S3 secret key"),
    s3_endpoint: Optional[str] = typer.Option(None, help="S3 endpoint URL"),
    s3_region: str = typer.Option("us-east-1", help="S3 region"),
    s3_use_ssl: Optional[bool] = typer.Option(None, help="Force SSL for S3"),
    catalog_kind: Optional[str] = typer.Option(None, help="Catalog kind: sqlite or postgres"),
    catalog_uri: Optional[str] = typer.Option(None, help="Catalog connection URI"),
    catalog_namespace: Optional[str] = typer.Option(None, help="Catalog namespace"),
) -> None:
    """Generate a dataset using the requested writer and configuration."""
    opts = WriterOptions(file_rows_target=file_rows_target, compression=compression)

    orders_partitioning = orders_partitioning.lower()
    orders_mode = orders_mode.lower()

    gen_kwargs = dict(
        seed=seed,
        n_customers=n_customers,
        n_products=n_products,
        orders_per_day=orders_per_day,
        order_items_mean=order_items_mean,
        start_date=start_date,
        end_date=end_date,
        file_rows_target=file_rows_target,
        orders_partitioning=orders_partitioning,
        orders_mode=orders_mode,
        orders_min=orders_min,
        orders_max=orders_max,
        orders_mean=orders_mean,
        orders_std=orders_std,
        orders_floor=orders_floor,
    )
    constructor = get_generator_constructor(dataset)
    valid_params = set(inspect.signature(constructor).parameters.keys())
    filtered_kwargs = {k: v for k, v in gen_kwargs.items() if k in valid_params and v is not None}
    generator = create_generator(dataset, **filtered_kwargs)

    s3_config = _build_s3_config(s3_uri, s3_key, s3_secret, s3_endpoint, s3_region, s3_use_ssl)
    catalog_config = _build_catalog_config(catalog_kind, catalog_uri, catalog_namespace)

    writer = create_writer(format, output, s3_config, catalog_config, opts)
    write_dataset(generator, writer)
    typer.echo("Generation complete")


def _build_s3_config(
    uri: Optional[str],
    key: Optional[str],
    secret: Optional[str],
    endpoint: Optional[str],
    region: str,
    use_ssl: Optional[bool],
) -> Optional[S3Config]:
    """Build an optional S3Config from CLI options.

    Args:
        uri: Base S3 URI (e.g. ``s3://bucket/prefix``).
        key: Access key ID.
        secret: Secret access key.
        endpoint: Optional custom endpoint.
        region: AWS region, defaults to ``us-east-1``.
        use_ssl: Force TLS on/off. ``None`` keeps the backend default.

    Raises:
        typer.BadParameter: If incomplete credentials are provided.
    """
    if not uri:
        return None
    if not key or not secret:
        raise typer.BadParameter("S3 key and secret are required when s3-uri is provided")
    return S3Config(
        uri=uri,
        key=key,
        secret=secret,
        endpoint_url=endpoint,
        region=region,
        use_ssl=use_ssl,
    )


def _build_catalog_config(
    kind: Optional[str], uri: Optional[str], namespace: Optional[str]
) -> Optional[CatalogConfig]:
    """Build an optional CatalogConfig from CLI options.

    Args:
        kind: Catalog implementation name (``sqlite`` or ``postgres``).
        uri: Connection URI.
        namespace: Optional logical namespace.

    Raises:
        typer.BadParameter: If only one of ``catalog-kind``/``catalog-uri`` is supplied.
    """
    if not kind and not uri:
        return None
    if not kind or not uri:
        raise typer.BadParameter("catalog-kind and catalog-uri must be provided together")
    return CatalogConfig(kind=kind, uri=uri, namespace=namespace)


def main() -> None:  # pragma: no cover - CLI entrypoint
    """CLI entry point used by ``python -m dataset_generator.cli``."""
    app()


__all__ = ["app", "main"]
