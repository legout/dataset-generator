# Change: Fix API navigation coverage warnings

## Why
`mkdocs serve` reports that every generated API page (e.g., `api/dataset_generator/core/factory.md`) exists on disk but is missing from `nav`. Today we point the nav entry at `api/SUMMARY.md`, yet MkDocs still treats the generated module files as orphaned, spamming warnings and making it hard to spot real problems. The warning list keeps growing as new modules land, so the build output is noisy and reviewers miss regressions. We need a predictable way to surface the generated hierarchy in navigation (or explicitly exclude it) so the build is clean.

The same warning also appears for `includes/mkdocs.md`, which is intentionally auto-included via `pymdownx.snippets`. Those fragments should be excluded from nav scans to avoid false alarms.

## What changes
- Update the MkDocs configuration to consume the generated API tree without triggering orphan warnings (either by wiring `literate-nav` to `api/SUMMARY.md` properly or by converting the nav entry into an `include` that enumerates the tree).
- Explicitly exclude auto-generated or snippet-only files (e.g., `docs/includes/mkdocs.md`) from the `nav` scan via `exclude_docs` / `not_in_nav` so MkDocs ignores them.
- Ensure future generated API modules continue to appear in the navigation tree without manual edits.
- Document the pattern in the contributor guide so new API packages automatically land in navigation with zero warnings.

## Impact
- Capability: `documentation`
- Files expected to change:
  - `mkdocs.yml` (nav + exclude configuration)
  - `docs/scripts/gen_ref_pages.py` (if the SUMMARY format needs tweaks for literate navigation)
  - `docs/development/contributing.md` (brief note about auto-generated nav expectations)
- No runtime/library code changes; documentation build quality only.
