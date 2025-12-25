# Farnell MCP Server

An MCP (Model Context Protocol) server for searching the Farnell Electronics catalog and managing orders. Provides access to product search, pricing, availability, and order management capabilities through the Farnell Partner API.

Supports Farnell (UK/Europe), Newark (North America), and Element14 (Asia-Pacific) stores.

## Features

- **Product Search**: Search electronic components by keyword, manufacturer part number, or Farnell order code
- **Real-time Data**: Check inventory availability and current pricing with volume discounts
- **Product Details**: Access specifications, datasheets, packaging, and compliance information
- **Shopping Cart** (Sandbox): Manage cart with add, update, delete operations
- **Order Management** (Sandbox): Complete order workflow including shipping and submission
- **Multi-Region Support**: Works with Farnell, Newark, and Element14 regional stores

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Farnell Partner API key (obtain from [partner.element14.com](https://partner.element14.com))
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Docker (optional, for containerized deployment)

### Installation

1. Clone and install dependencies:

```bash
git clone <repo-url> farnell-mcp
cd farnell-mcp
uv sync
```

2. Configure API credentials:

```bash
cp .env.example .env
# Edit .env with your Farnell API key and preferences
```

3. Run the server:

```bash
uv run farnell-mcp
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FARNELL_API_KEY` | Partner API key from partner.element14.com | Yes | - |
| `FARNELL_STORE_ID` | Regional store identifier | Yes | `www.newark.com` |
| `FARNELL_ENVIRONMENT` | `production` or `sandbox` | No | `production` |
| `FARNELL_SANDBOX_USERNAME` | Sandbox username for Order API | Sandbox only | - |
| `FARNELL_SANDBOX_PASSWORD` | Sandbox password for Order API | Sandbox only | - |
| `FARNELL_API_TIMEOUT` | Request timeout in seconds | No | `30` |
| `FARNELL_DEBUG` | Enable debug logging (`true`/`false`) | No | `false` |

### Regional Store Options

**North America:**
- `www.newark.com` - Newark (US/Canada) [DEFAULT]
- `canada.newark.com` - Newark Canada
- `mexico.newark.com` - Newark Mexico

**Europe:**
- `uk.farnell.com` - Farnell UK
- `de.farnell.com` - Farnell Germany
- `fr.farnell.com` - Farnell France
- `es.farnell.com` - Farnell Spain
- `it.farnell.com` - Farnell Italy

**Asia-Pacific:**
- `au.element14.com` - Element14 Australia
- `nz.element14.com` - Element14 New Zealand
- `sg.element14.com` - Element14 Singapore
- `hk.element14.com` - Element14 Hong Kong

### API Rate Limits

The Farnell Partner API enforces the following rate limits for the **Basic** tier:

- **2 calls per second**
- **1,000 calls per day**

**Automatic Rate Limiting:**

This MCP server automatically handles the per-second rate limit for you:
- **Per-second limit**: 2 calls/second (with small bucket to prevent bursts)
- **Per-day limit**: Monitored by Farnell API (will return errors if exceeded)
- **Behavior**: Requests are automatically delayed when per-second limit is reached (not rejected)
- **No configuration required** - works out of the box

When you exceed the 2 calls/second limit, the server will pause your request until a token becomes available. The first 2 requests can execute immediately, then subsequent requests are limited to approximately 2 per second. If you hit the 1,000 calls/day limit, the Farnell API will return an error response.

**Important Notes:**
- Contact [Farnell Partner Support](https://partner.element14.com/contact) to discuss higher tier options if you need increased limits

## Available Tools

### Product Search

| Tool | Description |
|------|-------------|
| `search_products_by_keyword` | Search catalog by keyword with filters (in-stock, RoHS) |
| `search_products_by_part_number` | Search by manufacturer part number |
| `get_product_by_order_code` | Get detailed product information by order code |
| `check_product_availability` | Check real-time inventory for multiple products |
| `get_product_pricing` | Get pricing with volume discounts |

### Order Management (Sandbox Only)

| Tool | Description |
|------|-------------|
| `sandbox_add_to_cart` | Add product to shopping cart |
| `sandbox_get_cart` | View cart contents |
| `sandbox_update_cart_item` | Update item quantity in cart |
| `sandbox_delete_cart_item` | Remove item from cart |
| `sandbox_clear_cart` | Clear entire cart |
| `sandbox_get_shipping_addresses` | Retrieve shipping addresses |
| `sandbox_confirm_shipping_address` | Select shipping address |
| `sandbox_get_shipping_methods` | Get available shipping methods |
| `sandbox_confirm_shipping_method` | Select shipping method |
| `sandbox_review_order` | Review order before submission |
| `sandbox_submit_order` | Submit order for processing |

## Usage Examples

### Search for Components

```python
# Search by keyword
results = await search_products_by_keyword(
    keyword="resistor 10k",
    in_stock_only=True,
    max_results=20
)

# Search by part number
results = await search_products_by_part_number(
    manufacturer_part_number="LM339ADT"
)

# Get specific product
product = await get_product_by_order_code(order_code="1278613")
```

### Check Availability and Pricing

```python
# Check stock levels
availability = await check_product_availability(
    order_codes=["1278613", "2396813"]
)

# Get pricing tiers
pricing = await get_product_pricing(order_codes=["1278613"])
for product in pricing['products']:
    print(f"{product['displayName']}:")
    for tier in product['prices']:
        print(f"  {tier['quantity']}+: ${tier['cost']} {tier['currency']}")
```

### Sandbox Cart Operations

```python
# Add to cart (sandbox only)
await sandbox_add_to_cart(order_code="1278613", quantity=10)

# View cart
cart = await sandbox_get_cart()
print(f"Cart total: ${cart['total']} {cart['currency']}")

# Clear cart
await sandbox_clear_cart()
```

## Docker Deployment

### Build and run with Docker Compose:

```bash
docker compose up --build
```

### For development with VS Code Dev Containers:

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted

## Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "farnell-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/path/to/your/.env",
        "farnell-mcp:latest"
      ]
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "farnell-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/farnell_mcp", "run", "farnell-mcp"]
    }
  }
}
```

## Development

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

## API Documentation

For detailed API documentation, visit:
- [Farnell Partner Portal](https://partner.element14.com)
- [Product Search API Docs](https://partner.element14.com/docs)
- [Order API Docs](https://partner.element14.com/order)

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues related to:
- **This MCP server**: Open an issue on GitHub
- **Farnell Partner API**: Contact Farnell Partner support
- **API access**: Visit [partner.element14.com](https://partner.element14.com)
