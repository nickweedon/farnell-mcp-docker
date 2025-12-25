# Claude Context for Farnell MCP Server

This document provides context and guidelines for Claude when working with the Farnell MCP server project.

## ⚠️ CRITICAL: Research Approach

**ALWAYS use the Playwright MCP server for web research when working on this project.**

When you need to research ANY topic related to implementing or customizing this MCP server:

- ✅ **DO**: Use Playwright MCP browser tools (`browser_navigate`, `browser_snapshot`, `browser_click`, etc.) for all web research
- ❌ **DON'T**: Use the Task tool with `claude-code-guide` subagent (that's ONLY for Claude Code documentation)
- ❌ **DON'T**: Use WebSearch or WebFetch as your first choice
- ⚠️ **FALLBACK**: Only use WebSearch, WebFetch, or similar tools when Playwright cannot work due to:
  - CAPTCHAs blocking access
  - Login walls or paywalls
  - Other technical barriers that prevent browser automation

The Playwright MCP server offers more sophisticated methods for searching the web, including the ability to operate single-page web applications, interact with dynamic content, and navigate complex websites.

**Example workflow**: When researching an API like Nexar:
1. Navigate to Google: `browser_navigate` to https://www.google.com
2. Search for the topic: `browser_type` to enter search terms
3. Click on results: `browser_click` on relevant links
4. Read documentation: `browser_snapshot` to capture page content
5. Navigate through docs: Continue using browser tools to explore

**When to fall back to WebSearch/WebFetch**:
- If you encounter "Access Denied" or CAPTCHA messages
- If authentication is required and cannot be bypassed
- If the site explicitly blocks automated browsers
- Only after attempting with Playwright first

## Project Overview

This is an MCP (Model Context Protocol) server that provides access to the Farnell Electronics Partner API. It enables product search, pricing lookups, inventory checks, and order management for electronic components from Farnell, Newark, and Element14 stores worldwide.

## Technology Stack

- **Language**: Python 3.10+
- **Framework**: FastMCP
- **HTTP Client**: requests
- **Package Manager**: uv
- **Testing**: pytest, pytest-asyncio
- **Linting**: ruff
- **Containerization**: Docker

## Project Structure

```
src/farnell_mcp/
├── server.py     # Main entry point, tool registration
├── client.py     # Farnell API clients (ProductSearchClient, OrderAPIClient)
├── types.py      # TypedDict definitions for products, carts, orders
├── api/          # Domain-specific API modules
│   ├── products.py  # Product search tools
│   └── orders.py    # Order management tools (sandbox)
└── utils/        # Utility functions
```

## Farnell API Integration

This server integrates with two Farnell Partner APIs:

### Product Search API
- **Base URL**: `https://api.element14.com/catalog/products`
- **Authentication**: API key in query parameters
- **Environment**: Production (default)
- **Tools**: 5 product search and pricing tools

### Order API
- **Base URLs**: Regional sandbox URLs (e.g., `https://api-uat.newark.com`)
- **Authentication**: JWT tokens
- **Environment**: Sandbox only
- **Tools**: 11 cart and order management tools

## API Key Management

Your Farnell API key should be kept secure:
- Store in `.env` file (gitignored)
- Never commit to version control
- For production deployment, use environment variables or secrets management
- Get your API key from [partner.element14.com](https://partner.element14.com)

## Store Selection

The server supports multiple regional stores via `FARNELL_STORE_ID`:
- **North America**: `www.newark.com` (default)
- **UK/Europe**: `uk.farnell.com`
- **Asia-Pacific**: `au.element14.com`, `sg.element14.com`, etc.

Different stores may have different inventory, pricing, and availability.

## Development Workflow

When implementing new features:

1. Start with Product Search API (simpler, no auth complexity)
2. Test with real API using small queries to understand response format
3. Create mock responses in test fixtures based on real API responses
4. Implement Order API features in sandbox environment only
5. Never test Order API against production without explicit approval from Farnell

## Key Patterns

### Tool Registration

Tools are registered in `server.py` using the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def my_tool(param: str) -> dict:
    """Tool description shown to clients."""
    return {"result": "value"}
```

Or by importing from API modules:

```python
from .api import my_module
mcp.tool()(my_module.my_function)
```

### API Module Structure

Each API module in `src/skeleton_mcp/api/` should:

1. Define async functions that perform specific operations
2. Include comprehensive docstrings (these become tool descriptions)
3. Use type hints for all parameters and return values
4. Handle errors gracefully with informative messages

Example:

```python
async def get_resource(resource_id: str) -> dict:
    """
    Get a resource by its ID.

    Args:
        resource_id: The unique identifier of the resource

    Returns:
        The resource data

    Raises:
        ValueError: If the resource is not found
    """
    # Implementation here
```

### Type Definitions

Use TypedDict classes in `types.py` for structured data:

```python
class ResourceData(TypedDict):
    id: str
    name: str
    description: str | None
```

### Error Handling

- Raise `ValueError` for invalid input or not found errors
- Raise `RuntimeError` for server/API errors
- Include descriptive error messages

## Development Workflow

### Running the Server

```bash
uv run skeleton-mcp
```

### Running Tests

```bash
uv run pytest -v
```

### Linting

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Building

```bash
uv build
```

## Coding Standards

1. **Async by default**: All tool functions should be async
2. **Type everything**: Use type hints for parameters, returns, and variables
3. **Document thoroughly**: Docstrings are exposed to MCP clients
4. **Test comprehensively**: Each API function should have tests
5. **Handle errors gracefully**: Provide informative error messages

## Adding New Features

When adding new functionality:

1. Create a new module in `src/skeleton_mcp/api/`
2. Define async functions with proper docstrings
3. Add TypedDict definitions in `types.py` if needed
4. Register tools in `server.py`
5. Write tests in `tests/`
6. Update this documentation if patterns change

## Handling Large Files and Binary Data

### Using mcp-mapped-resource-lib

For MCP servers that need to handle large file uploads/downloads or binary blob storage, use the **mcp-mapped-resource-lib** library instead of implementing custom blob storage:

**Installation:**
```bash
pip install mcp-mapped-resource-lib
```

**Key Features:**
- Blob management with unique identifiers (`blob://TIMESTAMP-HASH.EXT`)
- Metadata storage alongside blobs
- Automatic TTL-based expiration and cleanup
- Content deduplication via SHA256
- Security features (path traversal prevention, MIME validation, size limits)
- Docker volume integration for shared storage across containers

**Basic Usage:**
```python
from mcp_mapped_resource_lib import BlobStorage

# Initialize storage
storage = BlobStorage(
    storage_root="/mnt/blob-storage",
    max_size_mb=100
)

# Upload a blob
result = storage.upload_blob(
    data=b"file content",
    filename="document.pdf"
)

# Retrieve metadata
metadata = storage.get_metadata(result['blob_id'])

# Delete when done
storage.delete_blob(result['blob_id'])
```

**Docker Setup:**
When using with Docker, mount a shared volume for blob storage:

```yaml
volumes:
  - blob-storage:/mnt/blob-storage
```

**Important:** This library requires `libmagic` for MIME detection:
- Ubuntu/Debian: `apt-get install libmagic1`
- macOS: Install via Homebrew

For more details, see: https://github.com/nickweedon/mcp_mapped_resource_lib

## Common Tasks

### Add a new API endpoint/tool

1. Create function in appropriate `api/` module
2. Add types in `types.py`
3. Register in `server.py`: `mcp.tool()(module.function)`
4. Write tests

### Add a new resource

Resources provide read-only data access:

```python
@mcp.resource("myserver://resource-name")
async def get_resource() -> str:
    """Resource description."""
    return "resource content"
```

### Add a new prompt

Prompts are templates for common operations:

```python
@mcp.prompt()
def my_prompt() -> str:
    """Prompt description."""
    return "Prompt template text..."
```

## Environment Variables

Configure in `.env`:

- `API_KEY`: Authentication key for backend API
- `API_BASE_URL`: Base URL for API requests
- `API_TIMEOUT`: Request timeout in seconds
- `DEBUG`: Enable debug logging

## Troubleshooting

### Server won't start

1. Check that all dependencies are installed: `uv sync`
2. Verify `.env` file exists and has required variables
3. Check for syntax errors: `uv run python -m py_compile src/skeleton_mcp/server.py`

### Tests failing

1. Ensure test dependencies are installed: `uv sync`
2. Run with verbose output: `uv run pytest -v --tb=long`

### Docker issues

1. Rebuild image: `docker compose build --no-cache`
2. Check logs: `docker compose logs -f`
