"""Farnell MCP Server.

This is the main entry point for the Farnell MCP server. It provides access to
Farnell Electronics product search and ordering capabilities through MCP tools.

Features:
- Product search by keyword, part number, or order code
- Real-time inventory and pricing information
- Shopping cart management (sandbox)
- Order placement workflow (sandbox)
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastmcp import FastMCP

from .client import get_farnell_config
from .api import products, orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP(
    name="Farnell MCP Server",
    instructions="""
    This MCP server provides access to the Farnell Electronics Partner API.

    **Product Search Tools:**
    - Search by keyword, manufacturer part number, or Farnell order code
    - Check real-time inventory and availability
    - Get pricing information with volume discounts

    **Order Management Tools (Sandbox Only):**
    - Shopping cart management
    - Shipping address and method selection
    - Order review and submission

    **Configuration:**
    - Default store: Newark (www.newark.com)
    - Supports Farnell UK, Element14 APAC, and other regional stores
    - Environment: Production for product search, Sandbox for orders

    Start by using health_check to verify your API key is configured.
    """,
)


def timing_middleware(func: Callable) -> Callable:
    """Middleware to log execution time for tools."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise

    return wrapper


# =============================================================================
# TOOLS
# =============================================================================


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Check the health status of the Farnell MCP server.

    Returns:
        Dictionary with server status, configuration, and API connectivity info.
    """
    try:
        config = get_farnell_config()
        return {
            "status": "healthy",
            "server": "Farnell MCP Server",
            "version": "0.1.0",
            "api_key_configured": bool(config.api_key),
            "store_id": config.store_id,
            "environment": config.environment,
            "product_search_available": True,
            "order_api_available": config.environment == "sandbox"
            and config.sandbox_username is not None,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Failed to load configuration. Check environment variables.",
        }


# =============================================================================
# Product Search Tools
# =============================================================================

mcp.tool()(products.search_products_by_keyword)
mcp.tool()(products.search_products_by_part_number)
mcp.tool()(products.get_product_by_order_code)
mcp.tool()(products.check_product_availability)
mcp.tool()(products.get_product_pricing)


# =============================================================================
# Order Management Tools (Sandbox Only)
# =============================================================================

# Cart Management
mcp.tool()(orders.sandbox_add_to_cart)
mcp.tool()(orders.sandbox_get_cart)
mcp.tool()(orders.sandbox_update_cart_item)
mcp.tool()(orders.sandbox_delete_cart_item)
mcp.tool()(orders.sandbox_clear_cart)

# Shipping and Order Submission
mcp.tool()(orders.sandbox_get_shipping_addresses)
mcp.tool()(orders.sandbox_confirm_shipping_address)
mcp.tool()(orders.sandbox_get_shipping_methods)
mcp.tool()(orders.sandbox_confirm_shipping_method)
mcp.tool()(orders.sandbox_review_order)
mcp.tool()(orders.sandbox_submit_order)


# =============================================================================
# RESOURCES
# =============================================================================


@mcp.resource("farnell://status")
async def get_status() -> str:
    """Get the current server status."""
    return "Farnell MCP Server is running"


@mcp.resource("farnell://stores")
async def get_available_stores() -> str:
    """Get list of available Farnell regional stores."""
    stores = """
    Available Farnell Regional Stores:

    **North America:**
    - www.newark.com (Newark - US/Canada)
    - canada.newark.com (Newark Canada)
    - mexico.newark.com (Newark Mexico)

    **Europe:**
    - uk.farnell.com (Farnell UK)
    - de.farnell.com (Farnell Germany)
    - fr.farnell.com (Farnell France)
    - es.farnell.com (Farnell Spain)
    - it.farnell.com (Farnell Italy)
    - export.farnell.com (Farnell Export)

    **Asia Pacific:**
    - au.element14.com (Element14 Australia)
    - nz.element14.com (Element14 New Zealand)
    - sg.element14.com (Element14 Singapore)
    - hk.element14.com (Element14 Hong Kong)
    - cn.element14.com (Element14 China)

    Configure your store using the FARNELL_STORE_ID environment variable.
    """
    return stores


# =============================================================================
# PROMPTS
# =============================================================================


@mcp.prompt()
def getting_started() -> str:
    """A prompt to help users get started with the Farnell MCP server."""
    return """
    Welcome to the Farnell MCP Server!

    This server provides access to Farnell Electronics product search and ordering.

    **Available Tools:**

    *Product Search:*
    1. search_products_by_keyword - Search catalog by keyword
    2. search_products_by_part_number - Search by manufacturer part number
    3. get_product_by_order_code - Get detailed product info
    4. check_product_availability - Check inventory for products
    5. get_product_pricing - Get pricing with volume discounts

    *Order Management (Sandbox Only):*
    6. sandbox_add_to_cart - Add product to cart
    7. sandbox_get_cart - View cart contents
    8. sandbox_clear_cart - Clear cart
    9. sandbox_submit_order - Place order (full workflow available)

    **Getting Started:**

    1. First, check your configuration:
       - Call health_check to verify API key and settings

    2. Try searching for a product:
       - search_products_by_keyword("resistor 10k", in_stock_only=True)

    3. Get detailed product information:
       - get_product_by_order_code("1278613")

    4. Check pricing:
       - get_product_pricing(["1278613"])

    **Configuration:**
    Set these environment variables in your .env file:
    - FARNELL_API_KEY: Your Partner API key
    - FARNELL_STORE_ID: Regional store (default: www.newark.com)
    - FARNELL_ENVIRONMENT: "production" or "sandbox"
    """


@mcp.prompt()
def search_workflow() -> str:
    """Guide for searching and researching electronic components."""
    return """
    **Farnell Component Search Workflow:**

    1. **Broad Search:**
       - Start with keyword search: search_products_by_keyword("capacitor ceramic")
       - Add filters: in_stock_only=True, rohs_compliant_only=True

    2. **Narrow Down:**
       - Search by specific part number: search_products_by_part_number("LM339ADT")
       - Review results and identify exact order codes

    3. **Get Details:**
       - Look up specific product: get_product_by_order_code("1278613")
       - Review specifications, datasheet, packaging

    4. **Check Availability & Pricing:**
       - check_product_availability(["1278613", "2396813"])
       - get_product_pricing(["1278613"])
       - Compare volume pricing tiers

    5. **Make Decision:**
       - Based on specs, availability, and pricing
       - Ready to order? Use sandbox_add_to_cart (if in sandbox mode)
    """


@mcp.prompt()
def ordering_workflow() -> str:
    """Guide for placing orders through the sandbox Order API."""
    return """
    **Farnell Order Placement Workflow (Sandbox):**

    Prerequisites:
    - FARNELL_ENVIRONMENT=sandbox
    - FARNELL_SANDBOX_USERNAME and FARNELL_SANDBOX_PASSWORD configured

    **Steps:**

    1. **Build Your Cart:**
       - sandbox_add_to_cart("1278613", 10)
       - sandbox_add_to_cart("2396813", 5)
       - sandbox_get_cart() to review

    2. **Select Shipping Address:**
       - sandbox_get_shipping_addresses()
       - sandbox_confirm_shipping_address(address_id)

    3. **Choose Shipping Method:**
       - sandbox_get_shipping_methods()
       - sandbox_confirm_shipping_method(method_id)

    4. **Review Order:**
       - sandbox_review_order()
       - Check totals, shipping, tax

    5. **Submit Order:**
       - sandbox_submit_order()
       - Receive order confirmation

    **Cart Management:**
    - Update quantity: sandbox_update_cart_item(line_item_id, new_quantity)
    - Remove item: sandbox_delete_cart_item(line_item_id)
    - Start over: sandbox_clear_cart()
    """


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    """Run the Farnell MCP server."""
    logger.info("Starting Farnell MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
