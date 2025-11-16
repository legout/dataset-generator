## MODIFIED Requirements

### Requirement: API Reference
The documentation SHALL provide a complete API reference generated from code docstrings using `mkdocstrings` for all public packages, modules, classes, and functions under `src/dataset_generator`.

#### Scenario: Navigate API packages and modules
- **WHEN** a user opens the "API Reference" section
- **THEN** they see a package → module navigation tree that reflects the code in `src/dataset_generator`

#### Scenario: View class and function details
- **WHEN** a user opens a class or function
- **THEN** the page shows its docstring, parameters with types, return type, and signature rendered by mkdocstrings

#### Scenario: Source links available
- **WHEN** a user views an API object
- **THEN** a link to the source file and line is displayed when available

#### Scenario: Private members hidden by default
- **WHEN** mkdocs is built
- **THEN** private members (underscore-prefixed) are hidden unless explicitly documented

#### Scenario: Successful build
- **WHEN** running `mkdocs build`
- **THEN** the build completes successfully and generates API pages under `site/api/` without missing references

## ADDED Requirements

### Requirement: API Navigation Generation
The API navigation SHALL be auto-generated using `mkdocs-gen-files` and `mkdocs-literate-nav`, producing `api/SUMMARY.md` consumed by MkDocs navigation.

#### Scenario: Generated navigation is in sync
- **WHEN** modules are added, removed, or renamed under `src/dataset_generator`
- **THEN** the API navigation updates automatically on the next documentation build

#### Scenario: Stable ordering and correct links
- **WHEN** a user browses the API navigation
- **THEN** packages and modules are listed in a stable, alphabetical order and links open the corresponding generated API pages
