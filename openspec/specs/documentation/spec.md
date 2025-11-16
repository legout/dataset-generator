# documentation Specification

## Purpose
TBD - created by archiving change add-mkdocs-documentation. Update Purpose after archive.
## Requirements
### Requirement: Documentation Site
The system SHALL provide a comprehensive documentation site built with MkDocs and Material theme.

#### Scenario: User accesses documentation
- **WHEN** a user visits the documentation site
- **THEN** they see a modern, responsive interface with clear navigation

#### Scenario: User searches for information
- **WHEN** a user uses the search functionality
- **THEN** they find relevant documentation pages and API references

### Requirement: Getting Started Guide
The documentation SHALL include a comprehensive getting started guide.

#### Scenario: New user onboarding
- **WHEN** a new user reads the getting started guide
- **THEN** they can install the package and generate their first dataset

#### Scenario: Installation instructions
- **WHEN** a user follows installation instructions
- **THEN** they can successfully install all required dependencies

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

### Requirement: Generator Documentation
The documentation SHALL provide detailed documentation for all dataset generators.

#### Scenario: User explores available generators
- **WHEN** a user browses the generators section
- **THEN** they see documentation for ecommerce, market, sensors, and weather generators

#### Scenario: Generator configuration
- **WHEN** a user reads generator documentation
- **THEN** they understand all configuration options and parameters

### Requirement: Writer Documentation
The documentation SHALL provide comprehensive documentation for all table format writers.

#### Scenario: User chooses output format
- **WHEN** a user reviews writer options
- **THEN** they see documentation for parquet, delta, iceberg, and ducklake writers

#### Scenario: S3 configuration
- **WHEN** a user needs S3 integration
- **THEN** they find clear configuration examples and troubleshooting guides

### Requirement: Tutorial Content
The documentation SHALL include interactive tutorials and examples.

#### Scenario: User follows tutorial
- **WHEN** a user completes a tutorial
- **THEN** they understand how to use specific features end-to-end

#### Scenario: Example code execution
- **WHEN** a user copies example code
- **THEN** the code runs successfully and produces expected results

### Requirement: Documentation Build System
The project SHALL include a build system for generating and serving documentation.

#### Scenario: Developer builds documentation locally
- **WHEN** a developer runs the documentation build command
- **THEN** the site builds successfully without errors

#### Scenario: Documentation validation
- **WHEN** documentation is built
- **THEN** all links are validated and references are correct

### Requirement: Marimo Documentation
The project SHALL provide comprehensive documentation for marimo notebooks to help users understand and use marimo examples effectively.

#### Scenario: User discovers marimo examples
- **WHEN** user navigates to Examples section in documentation
- **THEN** they find a "Marimo Apps" entry with clear documentation
- **AND** the documentation explains setup and usage of marimo notebooks

#### Scenario: User wants to run marimo examples
- **WHEN** user reads marimo documentation
- **THEN** they find installation instructions for marimo
- **AND** they can successfully run the provided example files
- **AND** they understand the differences between marimo and Jupyter notebooks

#### Scenario: User explores marimo examples
- **WHEN** user examines examples/marimo/ directory
- **THEN** documentation explains each example file (ecommerce_overview.py, ecommerce_overview_dl.py)
- **AND** code snippets demonstrate how to use the examples
- **AND** best practices for marimo development are provided

#### Scenario: User compares notebook options
- **WHEN** user evaluates notebook solutions
- **THEN** documentation clearly compares marimo vs Jupyter notebooks
- **AND** advantages of marimo are highlighted (reactive UI, app deployment)
- **AND** use cases for each option are clearly explained

### Requirement: API Navigation Generation
The API navigation SHALL be auto-generated using `mkdocs-gen-files` and `mkdocs-literate-nav`, producing `api/SUMMARY.md` consumed by MkDocs navigation.

#### Scenario: Generated navigation is in sync
- **WHEN** modules are added, removed, or renamed under `src/dataset_generator`
- **THEN** the API navigation updates automatically on the next documentation build

#### Scenario: Stable ordering and correct links
- **WHEN** a user browses the API navigation
- **THEN** packages and modules are listed in a stable, alphabetical order and links open the corresponding generated API pages

