# Customization Guide

This guide explains how to customize the skeleton MCP server for your specific use case.

## Step 1: Rename the Project

1. **Rename the package directory**:
   ```bash
   mv src/skeleton_mcp src/your_project_name
   ```

2. **Update pyproject.toml**:
   - Change `name = "skeleton-mcp"` to your project name
   - Update the description, authors, and keywords
   - Update the script entry point:
     ```toml
     [project.scripts]
     your-project = "your_project_name.server:main"
     ```
   - Update the wheel packages:
     ```toml
     [tool.hatch.build.targets.wheel]
     packages = ["src/your_project_name"]
     ```

3. **Update imports in all Python files**:
   - `server.py`: Update imports from `skeleton_mcp` to `your_project_name`
   - `api/__init__.py`: Update imports
   - Test files: Update imports

## Step 2: Configure Your API Client

Edit `src/your_project_name/client.py`:

1. **Update environment variable names**:
   ```python
   def get_client_config() -> dict[str, Any]:
       return {
           "api_key": os.getenv("YOUR_API_KEY"),
           "api_base_url": os.getenv("YOUR_API_BASE_URL", "https://api.yourservice.com/v1"),
           # ...
       }
   ```

2. **Customize authentication**:
   ```python
   # For Bearer token auth:
   self.session.headers["Authorization"] = f"Bearer {self.api_key}"

   # For API key header:
   self.session.headers["X-API-Key"] = self.api_key

   # For Basic auth:
   self.session.auth = (self.username, self.password)
   ```

3. **Add custom methods** for your API's patterns:
   ```python
   def paginated_get(self, endpoint: str, page: int = 1) -> dict:
       """Get with pagination support."""
       return self.get(endpoint, params={"page": page, "per_page": 100})
   ```

## Step 3: Define Your Data Types

Edit `src/your_project_name/types.py`:

```python
class ProductData(TypedDict):
    id: str
    sku: str
    name: str
    price: float
    quantity: int
    category: str | None

class OrderData(TypedDict):
    id: str
    customer_id: str
    items: list[OrderItemData]
    total: float
    status: str
```

## Step 4: Create Your API Modules

Create new files in `src/your_project_name/api/`:

```python
# src/your_project_name/api/products.py

from typing import Any
from ..client import get_client
from ..types import ProductData

async def list_products(
    category: str | None = None,
    in_stock: bool | None = None,
) -> list[ProductData]:
    """
    List products with optional filtering.

    Args:
        category: Filter by category
        in_stock: Filter by stock availability

    Returns:
        List of products matching the criteria
    """
    client = get_client()
    params = {}
    if category:
        params["category"] = category
    if in_stock is not None:
        params["in_stock"] = in_stock

    return client.get("products", params=params)
```

## Step 5: Register Your Tools

Update `src/your_project_name/server.py`:

```python
from .api import products, orders, inventory

# Register all tools
mcp.tool()(products.list_products)
mcp.tool()(products.get_product)
mcp.tool()(products.create_product)

mcp.tool()(orders.list_orders)
mcp.tool()(orders.create_order)
mcp.tool()(orders.update_order_status)

mcp.tool()(inventory.check_stock)
mcp.tool()(inventory.adjust_stock)
```

## Step 6: Add Resources (Optional)

Resources provide read-only data access:

```python
@mcp.resource("yourserver://categories")
async def list_categories() -> str:
    """Get all product categories."""
    client = get_client()
    categories = client.get("categories")
    return "\n".join(c["name"] for c in categories)

@mcp.resource("yourserver://product/{product_id}")
async def get_product_resource(product_id: str) -> str:
    """Get product details as a resource."""
    client = get_client()
    product = client.get(f"products/{product_id}")
    return json.dumps(product, indent=2)
```

## Step 7: Add Prompts (Optional)

Prompts are templates for common operations:

```python
@mcp.prompt()
def inventory_report() -> str:
    """Generate an inventory status report."""
    return """
    Please generate an inventory report that includes:
    1. Total number of products
    2. Products low on stock (< 10 units)
    3. Out of stock products
    4. Categories with the most items

    Use the list_products and check_stock tools to gather this information.
    """
```

## Step 8: Write Tests

Create test files in `tests/`:

```python
# tests/test_products_api.py

import pytest
from your_project_name.api import products

class TestListProducts:
    @pytest.mark.asyncio
    async def test_list_all_products(self):
        result = await products.list_products()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_filter_by_category(self):
        result = await products.list_products(category="electronics")
        for product in result:
            assert product["category"] == "electronics"
```

## Step 9: Update Documentation

1. **README.md**: Update with your project's specific information
2. **CLAUDE.md**: Update patterns and guidelines for your project
3. **.env.example**: Add your required environment variables

## Step 10: Configure Deployment

Update Docker and deployment files:

1. **Dockerfile**: Add any system dependencies your API needs
2. **docker-compose.yml**: Update service name and configuration
3. **.devcontainer/devcontainer.json**: Update container name

## Best Practices

### Tool Design

- **One tool per operation**: Keep tools focused on a single action
- **Clear naming**: Use verb_noun format (list_products, get_order)
- **Comprehensive docstrings**: These are shown to MCP clients
- **Sensible defaults**: Optional parameters should have reasonable defaults

### Error Handling

- Raise `ValueError` for validation errors and not found
- Raise `RuntimeError` for API/server errors
- Include enough context to help debug issues

### Type Safety

- Use TypedDict for all structured data
- Use `| None` for optional fields
- Keep types in sync with your actual API responses

### Testing

- Test happy paths and error cases
- Use fixtures for common test data
- Mock external API calls in unit tests
