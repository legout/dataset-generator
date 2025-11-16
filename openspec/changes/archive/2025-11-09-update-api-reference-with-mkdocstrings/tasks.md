## 1. Analysis & Alignment
- [x] 1.1 Review current API nav in `mkdocs.yml` and remove static `docs/api/*.md` entries
- [x] 1.2 Confirm `mkdocstrings`, `mkdocs-gen-files`, and `mkdocs-literate-nav` plugins are configured

## 2. MkDocs Configuration
- [x] 2.1 Update `mkdocs.yml` to use generated `api/SUMMARY.md` for the API section
- [x] 2.2 Ensure mkdocstrings Python handler options: merge `__init__`, show signatures, types, and source links
- [x] 2.3 Keep `gen-files` script `docs/scripts/gen_ref_pages.py` wired in `plugins.gen-files`

## 3. Content & Cleanup
- [x] 3.1 Replace/remove manual API stubs in `docs/api/` (e.g., `core.md`, `generators.md`, `writers.md`, `cli.md`)
- [x] 3.2 Add a minimal landing page (optional) that points to the generated API index
- [x] 3.3 Update contributing docs to mention docstring standards for mkdocstrings

## 4. Docstrings Quality Pass
- [x] 4.1 Ensure public APIs in `core/`, `generators/`, `writers/`, and `cli/` have informative docstrings
- [x] 4.2 Verify parameter and return types are documented where helpful
- [x] 4.3 Add cross-references where appropriate

## 5. Build & Validate
- [x] 5.1 Run `mkdocs build` and verify `site/api/` structure and links
- [x] 5.2 Spot-check core pages (pipeline, factory, interfaces, writers, generators, CLI)
- [x] 5.3 Fix broken links or rendering issues
- [x] 5.4 Run `openspec validate update-api-reference-with-mkdocstrings --strict`

## 6. Rollout
- [x] 6.1 Update `README.md` references if needed
- [x] 6.2 Share preview and request review/approval
- [x] 6.3 Merge after approval
