"""Product Search API Tools.

This module implements MCP tools for searching the Farnell Electronics catalog.
"""

from typing import Any

from ..client import get_product_client
from ..types import Product, ProductSearchResult


async def search_products_by_keyword(
    keyword: str,
    in_stock_only: bool = False,
    rohs_compliant_only: bool = False,
    max_results: int = 10,
    offset: int = 0,
    response_detail: str = "medium",
) -> dict[str, Any]:
    """Search Farnell catalog by keyword.

    Returns product listings with pricing, availability, and specifications.

    Args:
        keyword: Search keyword (e.g., "resistor 10k", "capacitor ceramic").
        in_stock_only: Filter to only show in-stock items.
        rohs_compliant_only: Filter to only show RoHS compliant items.
        max_results: Number of results to return (1-100).
        offset: Starting offset for pagination (0-based).
        response_detail: Detail level - "small", "medium", "large", "prices", or "inventory".

    Returns:
        Dictionary containing product search results with the following structure:
        - products: List of product dictionaries with details
        - total_results: Total number of matching products
        - offset: Current offset
        - number_of_results: Number of results returned

    Example:
        >>> results = await search_products_by_keyword("LM339", in_stock_only=True)
        >>> print(f"Found {results['total_results']} products")
        >>> for product in results['products']:
        >>>     print(f"{product['displayName']}: ${product['prices'][0]['cost']}")
    """
    # Build filters list
    filters = []
    if in_stock_only:
        filters.append("inStock")
    if rohs_compliant_only:
        filters.append("rohsCompliant")

    client = get_product_client()

    # Perform search
    response = client.search_by_keyword(
        keyword=keyword,
        offset=offset,
        num_results=max_results,
        filters=filters or None,
        response_group=response_detail,
    )

    # Return raw API response (parsing can be done by caller if needed)
    return response


async def search_products_by_part_number(
    manufacturer_part_number: str,
    in_stock_only: bool = False,
    rohs_compliant_only: bool = False,
    max_results: int = 10,
    response_detail: str = "medium",
) -> dict[str, Any]:
    """Search for products by manufacturer part number.

    More precise than keyword search - searches the exact manufacturer part number field.

    Args:
        manufacturer_part_number: Exact or partial manufacturer part number (e.g., "LM339ADT").
        in_stock_only: Filter to only show in-stock items.
        rohs_compliant_only: Filter to only show RoHS compliant items.
        max_results: Number of results to return (1-100).
        response_detail: Detail level - "small", "medium", "large", "prices", or "inventory".

    Returns:
        Dictionary containing product search results.

    Example:
        >>> results = await search_products_by_part_number("LM339ADT")
        >>> if results['products']:
        >>>     product = results['products'][0]
        >>>     print(f"Found: {product['displayName']}")
        >>>     print(f"Manufacturer: {product['manufacturerName']}")
    """
    # Build filters list
    filters = []
    if in_stock_only:
        filters.append("inStock")
    if rohs_compliant_only:
        filters.append("rohsCompliant")

    client = get_product_client()

    # Perform search
    response = client.search_by_mfr_part_number(
        part_number=manufacturer_part_number,
        offset=0,
        num_results=max_results,
        filters=filters or None,
        response_group=response_detail,
    )

    return response


async def get_product_by_order_code(
    order_code: str, response_detail: str = "large"
) -> dict[str, Any]:
    """Get detailed information about a specific product using its Farnell order code.

    Args:
        order_code: Farnell/Newark/Element14 order code (e.g., "1278613").
        response_detail: Detail level - "small", "medium", or "large" (default: "large").

    Returns:
        Dictionary containing detailed product information including:
        - Product specifications
        - Pricing with volume discounts
        - Stock availability
        - Datasheet URL
        - Technical attributes
        - Package information

    Example:
        >>> product = await get_product_by_order_code("1278613")
        >>> print(f"Product: {product['products'][0]['displayName']}")
        >>> print(f"In stock: {product['products'][0]['stock']['level']}")
        >>> for price in product['products'][0]['prices']:
        >>>     print(f"  {price['quantity']}+ units: ${price['cost']}")
    """
    client = get_product_client()

    # Search by order code
    response = client.search_by_order_code(order_code=order_code, response_group=response_detail)

    return response


async def check_product_availability(order_codes: list[str]) -> dict[str, Any]:
    """Check real-time inventory and availability for multiple products.

    Args:
        order_codes: List of Farnell order codes (up to 20 recommended).

    Returns:
        Dictionary containing inventory information for each product:
        - Stock levels
        - Lead times
        - Regional availability

    Example:
        >>> availability = await check_product_availability(["1278613", "2396813"])
        >>> for product in availability['products']:
        >>>     code = product['id']
        >>>     stock = product.get('stock', {}).get('level', 0)
        >>>     print(f"Order code {code}: {stock} in stock")
    """
    client = get_product_client()

    # Build term string with all order codes
    term = " OR ".join([f"id:{code}" for code in order_codes])

    # Request with inventory response group
    response = client.search_by_keyword(
        keyword=term, num_results=len(order_codes), response_group="inventory"
    )

    return response


async def get_product_pricing(order_codes: list[str]) -> dict[str, Any]:
    """Get current pricing including volume discounts for specified products.

    Args:
        order_codes: List of Farnell order codes to get pricing for.

    Returns:
        Dictionary containing pricing information:
        - Unit prices
        - Volume discount tiers
        - Currency
        - Minimum order quantities
        - Pack sizes

    Example:
        >>> pricing = await get_product_pricing(["1278613"])
        >>> product = pricing['products'][0]
        >>> print(f"Product: {product['displayName']}")
        >>> print("Volume pricing:")
        >>> for tier in product['prices']:
        >>>     print(f"  {tier['quantity']}+: ${tier['cost']} {tier['currency']}")
    """
    client = get_product_client()

    # Build term string with all order codes
    term = " OR ".join([f"id:{code}" for code in order_codes])

    # Request with prices response group
    response = client.search_by_keyword(
        keyword=term, num_results=len(order_codes), response_group="prices"
    )

    return response
