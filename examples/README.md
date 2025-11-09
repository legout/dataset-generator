# Examples

This directory contains interactive walkthroughs for the synthetic dataset generators.

## 1. Environment setup

```bash
uv sync --all-extras
# activates .venv/. For one-shot commands use `uv run ...`
```

All notebooks default to local filesystem outputs under `examples/demo_output/`.

## 2. Jupyter notebooks

Launch Jupyter Lab or Notebook after activating the environment:

```bash
uv run jupyter lab examples/jupyter
```

Available notebooks:

| Notebook                  | Summary                                                                                                  | Extras                        |
| ------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `ecommerce_parquet.ipynb` | Generate a compact e-commerce dataset, write partitioned Parquet locally, and inspect sample partitions. | base                          |
| `ecommerce_delta.ipynb`   | Stores the same dataset as Delta Lake and inspects the transaction log.                                  | `dataset-generator[delta]`    |
| `s3_ducklake_minio.ipynb` | Uses DuckLake to write into a MinIO bucket (or RustFS) and query via DuckDB.                             | `dataset-generator[ducklake]` |
| `s3_iceberg_minio.ipynb`  | Writes Iceberg tables to MinIO using a SQLite catalog.                                                   | `dataset-generator[iceberg]`  |

## 3. Marimo app

The marimo notebook can be launched with:

```bash
uv run marimo run examples/marimo/ecommerce_overview.py
```

The UI lets you adjust core generator parameters, re-materialize the dataset, and inspect order summaries.

## 4. Cleanup

Output folders are created under `examples/demo_output/`. Remove them when you no longer need the generated data:

```bash
rm -rf examples/demo_output
```

## 5. Local S3 services (MinIO / RustFS / SeaweedFS)

All services share the same credentials: `access_key=demo`, `secret_key=demo123`.

### Start the stack

```bash
cd examples/services/object-storage
docker compose up -d
```

### Management consoles & S3 endpoints

| Service   | S3 endpoint           | Console / UI                                                        |
| --------- | --------------------- | ------------------------------------------------------------------- |
| MinIO     | http://localhost:9000 | http://localhost:9001 (console)                                     |
| RustFS    | http://localhost:9002 | http://localhost:9900 (console)                                     |
| SeaweedFS | http://localhost:9003 | http://localhost:8888 (filer UI), http://localhost:9333 (master UI) |

After starting, create a bucket named `demo` (or adjust notebooks accordingly) using one of the consoles. SeaweedFS filer UI exposes bucket/directory management; MinIO and RustFS consoles provide similar options.

### Configure notebooks

- DuckLake notebook: update the `endpoint` value to point at MinIO, RustFS, or SeaweedFS; credentials remain `demo/demo123`.
- Iceberg notebook: same endpoint rules plus ensure the local SQLite catalog path under `examples/demo_output/iceberg/` is writable.

### Stop the stack

```bash
docker compose down
```
