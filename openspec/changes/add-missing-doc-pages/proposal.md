# Change: Add missing documentation pages and assets

## Why
`mkdocs serve` currently emits multiple warnings because the navigation references files that do not exist:

- `tutorials/ecommerce-dataset.md`, `tutorials/s3-minio.md`, `tutorials/custom-generator.md`
- `development/architecture.md`, `development/testing.md`
- `user-guide/troubleshooting.md`

In addition, several internal links (e.g., the relative link to `../user-guide/generators/` inside `development/contributing.md`) cannot be resolved, and the configured logo (`assets/logo.png`) returns HTTP 404. These gaps make the documentation site feel incomplete, hide real regressions behind warning noise, and leave core workflows (architecture, testing, troubleshooting) undocumented.

## What changes
- Author the missing tutorial pages (can start as concise stubs with TODOs/examples) so the navigation entries resolve.
- Add `user-guide/troubleshooting.md` plus a basic troubleshooting matrix referenced throughout the docs.
- Provide real content for `development/architecture.md` and `development/testing.md` (short descriptions of current architecture/testing workflow are sufficient for now).
- Fix broken internal links (e.g., `../user-guide/generators/`) so MkDocs recognizes them.
- Restore the branded assets under `docs/assets/` (at minimum `logo.png`) so Material’s header no longer 404s.

## Impact
- Capability: `documentation`
- Files touched: tutorial/user-guide/development markdown files, `docs/assets/logo.png`, possibly shared include fragments.
- Improves docs usability and removes nav/link/asset warnings during every build.
