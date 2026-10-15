# SOLVEN Engineering Conventions

This file defines permanent repository conventions for the SOLVEN project. All contributors (and Jules AI agents) must obey these instructions.

## 1. Architecture and Dependency Direction
- **Data Layer:** `src/solven/data/` handles external I/O (e.g., HTTP requests). It must never perform financial normalization.
- **Models Layer:** `src/solven/models/` contains core business objects (dataclasses). It must not depend on `data` or `processing`.
- **Processing Layer:** `src/solven/processing/` contains pure functions for standardization and validation. It relies only on models and Python standard libraries.

## 2. Naming Standards
- Functions, variables, and modules: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## 3. Formatting and Static Analysis
- **Ruff:** Used for linting and formatting. Line length is 88 characters.
- **MyPy:** Used for static type analysis. Strict mode is enabled. All public APIs must have type annotations.

## 4. Testing Requirements
- Use `pytest` for all testing.
- HTTP operations must be mocked (e.g., using `respx` or `unittest.mock`).
- All code changes that alter behavior must include updated or new deterministic tests.

## 5. Financial Data Integrity
- Keep source data strictly separate from standardized data.
- **Never silently replace missing financial data with zero.** Use `None`.
- **Never invent financial values.**
- **Never silently change units or reporting periods.**
- Every derived standard figure must record the origin (SEC Provenance) of its observation.

## 6. Error-Handling Rules
- Raise explicit custom exceptions (e.g., `SECAPIError`, `ValidationError`).
- Handle API rate limits and connection issues gracefully.

## 7. Documentation Conventions
- Use explicit docstrings for all public modules, functions, and classes.
- Brand palette (Warm Espresso: `#F6F3ED`, `#302820`, `#A79B8D`, `#B57B57`) should guide design documentation.

## 8. Security Practices
- Do not commit or embed any private credentials.
- Ensure all API calls use secure configuration (e.g., environment variables for user agents).

## 9. Branch and Change-Review Workflow
- Create a reviewable branch for feature work.
- Run all static checks (`ruff format`, `ruff check`, `mypy`) and tests before finalizing the branch.
- Clearly summarize changes and document remaining limitations in the PR/submission.
