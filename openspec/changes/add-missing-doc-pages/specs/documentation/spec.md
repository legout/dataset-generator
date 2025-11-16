## ADDED Requirements

### Requirement: Navigation targets exist
Every page referenced in `mkdocs.yml` (`tutorials/*`, `development/*`, `user-guide/troubleshooting`) SHALL exist under `docs/` so builds do not emit "not found" warnings.

#### Scenario: MkDocs resolves nav entries
- **WHEN** `mkdocs build` runs
- **THEN** no warnings mention missing files for any entries in the Tutorials, Examples, User Guide, or Development sections

### Requirement: Internal documentation links resolve
All relative links inside the documentation (e.g., from `development/contributing.md`) SHALL point to valid targets that MkDocs can resolve.

#### Scenario: Relative link check
- **WHEN** MkDocs parses `development/contributing.md` (and other docs with cross-links)
- **THEN** it finds the referenced page and does not log "unrecognized relative link" warnings

### Requirement: Referenced assets exist
Any asset referenced by the Material theme configuration (`logo`, `favicon`, etc.) SHALL exist at the configured path so runtime 404s do not occur.

#### Scenario: Logo request
- **GIVEN** Material requests `/assets/logo.png`
- **WHEN** the dev server is running
- **THEN** the asset is served successfully (HTTP 200) instead of returning 404
