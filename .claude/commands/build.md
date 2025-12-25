# Build Command

Build the MCP server package and run all quality checks.

## Steps

1. Run linting with ruff: `uv run ruff check src/ tests/`
2. Run tests: `uv run pytest`
3. Build the package: `uv build`

Report any errors found during the build process.
