# Change: Add comprehensive MkDocs documentation with Material theme

## Why
The project currently has limited documentation (only README.md and examples) making it difficult for users to discover and understand the full capabilities of the dataset generator. Comprehensive documentation will improve adoption, provide clear API references, and offer better learning resources.

## What Changes
- Add MkDocs with Material theme for modern, responsive documentation
- Create comprehensive documentation structure covering all generators, writers, and configuration options
- Add API reference documentation from code docstrings
- Include interactive examples and tutorials
- Add search functionality and navigation
- **BREAKING**: Will add new documentation dependencies to the project

## Impact
- Affected specs: New `documentation` capability
- Affected code: Adding `mkdocs.yml`, `docs/` directory, new optional dependencies in pyproject.toml
- New documentation site will serve as the primary user resource