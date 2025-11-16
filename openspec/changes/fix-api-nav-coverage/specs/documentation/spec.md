## ADDED Requirements

### Requirement: Generated API pages present in navigation
The documentation build SHALL reference every generated API module (under `docs/api/dataset_generator/**`) through the MkDocs navigation so no orphan warnings are emitted.

#### Scenario: mkdocs build runs
- **GIVEN** the API reference pages are generated via `docs/scripts/gen_ref_pages.py`
- **WHEN** `mkdocs build` (or `mkdocs serve`) runs
- **THEN** MkDocs emits no "page exists but is not included in the nav" warnings for any `docs/api/dataset_generator/**` file

### Requirement: Snippet-only files excluded from nav validation
Documentation fragments that are auto-included (e.g., `docs/includes/mkdocs.md`) SHALL be excluded from MkDocs nav validation to avoid false orphan warnings.

#### Scenario: Snippet file referenced via pymdownx.snippets
- **GIVEN** a markdown fragment under `docs/includes/`
- **WHEN** the docs build runs
- **THEN** MkDocs does not warn about the fragment missing from navigation
