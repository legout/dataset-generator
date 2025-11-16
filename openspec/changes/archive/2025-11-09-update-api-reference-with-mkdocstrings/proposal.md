# Change: Update API Reference to mkdocstrings-generated pages

## Why
The current API chapter mixes handcrafted pages with partially generated content and missing files in navigation. This causes inconsistencies and stale documentation. We should rely on mkdocstrings with generated navigation so the API reference stays complete and up to date with the source code.

## What Changes
- Switch the API chapter to fully auto-generated pages via `mkdocstrings` and `mkdocs-gen-files`
- Replace manual API stubs under `docs/api/` with a single landing page or remove them in favor of generated content
- Update `mkdocs.yml` to use literate navigation (`api/SUMMARY.md`) instead of static `docs/api/*.md` entries
- Ensure mkdocstrings Python handler options (merge `__init__`, show signatures, source links) are configured consistently
- Establish docstring standards for public APIs to render well in mkdocstrings
- Validate local build and navigation (packages → modules → members) and fix broken links/cross-refs

## Impact
- Affected specs: `documentation` (API Reference behavior and navigation)
- Affected files:
  - `mkdocs.yml` (navigation and mkdocstrings options)
  - `docs/scripts/gen_ref_pages.py` (ensure correct module tree + SUMMARY generation)
  - `docs/api/*` (remove stale manual stubs or reduce to a landing page)
  - `src/dataset_generator/**` (docstrings for public APIs)
- No runtime behavior changes; documentation-only change
