"""Order Management API Tools (Sandbox Only).

This module implements MCP tools for cart and order management via the Farnell Order API.
All tools in this module require sandbox environment and credentials.
"""

from typing import Any

from ..client import get_order_client


# ============================================================================
# Cart Management Tools
# ============================================================================


async def sandbox_add_to_cart(order_code: str, quantity: int) -> dict[str, Any]:
    """Add a product to the shopping cart (sandbox environment only).

    Args:
        order_code: Farnell order code of the product to add.
        quantity: Quantity to add to cart.

    Returns:
        Dictionary containing:
        - success: Boolean indicating if operation succeeded
        - message: Status message
        - cart: Updated cart details with line items

    Raises:
        ValueError: If not in sandbox environment or credentials missing.
        RuntimeError: If API request fails.

    Example:
        >>> result = await sandbox_add_to_cart("1278613", 10)
        >>> print(f"Added to cart: {result['message']}")
        >>> print(f"Cart total: ${result['cart']['total']}")
    """
    client = get_order_client()
    response = client.add_to_cart(order_code=order_code, quantity=quantity)
    return response


async def sandbox_get_cart() -> dict[str, Any]:
    """Retrieve current shopping cart contents (sandbox environment only).

    Returns:
        Dictionary containing cart details:
        - cart_id: Unique cart identifier
        - line_items: List of items in cart with quantities and prices
        - subtotal: Subtotal before tax and shipping
        - tax: Tax amount (if calculated)
        - shipping: Shipping cost (if calculated)
        - total: Total order amount
        - currency: Currency code

    Example:
        >>> cart = await sandbox_get_cart()
        >>> print(f"Cart has {len(cart['line_items'])} items")
        >>> for item in cart['line_items']:
        >>>     print(f"  {item['description']}: {item['quantity']} @ ${item['unit_price']}")
        >>> print(f"Total: ${cart['total']} {cart['currency']}")
    """
    client = get_order_client()
    response = client.get_cart()
    return response


async def sandbox_update_cart_item(line_item_id: str, quantity: int) -> dict[str, Any]:
    """Update the quantity of an item in the shopping cart (sandbox environment only).

    Args:
        line_item_id: Line item ID from the cart (obtained from sandbox_get_cart).
        quantity: New quantity (use 0 to remove item, or use sandbox_delete_cart_item).

    Returns:
        Dictionary containing updated cart details.

    Example:
        >>> cart = await sandbox_get_cart()
        >>> line_item = cart['line_items'][0]
        >>> result = await sandbox_update_cart_item(line_item['line_item_id'], 20)
        >>> print(f"Updated quantity to 20")
    """
    client = get_order_client()
    response = client.update_cart_item(line_item_id=line_item_id, quantity=quantity)
    return response


async def sandbox_delete_cart_item(line_item_id: str) -> dict[str, Any]:
    """Remove an item from the shopping cart (sandbox environment only).

    Args:
        line_item_id: Line item ID to remove from cart.

    Returns:
        Dictionary containing updated cart details.

    Example:
        >>> cart = await sandbox_get_cart()
        >>> line_item = cart['line_items'][0]
        >>> result = await sandbox_delete_cart_item(line_item['line_item_id'])
        >>> print("Item removed from cart")
    """
    client = get_order_client()
    response = client.delete_cart_item(line_item_id=line_item_id)
    return response


async def sandbox_clear_cart() -> dict[str, Any]:
    """Clear all items from the shopping cart (sandbox environment only).

    Useful for testing or starting fresh with a new order.

    Returns:
        Dictionary with success status and message.

    Example:
        >>> result = await sandbox_clear_cart()
        >>> print(result['message'])
    """
    client = get_order_client()
    response = client.clear_cart()
    return response


# ============================================================================
# Shipping and Order Submission Tools
# ============================================================================


async def sandbox_get_shipping_addresses() -> dict[str, Any]:
    """Retrieve available shipping addresses (sandbox environment only).

    Returns:
        Dictionary containing list of shipping addresses:
        - Each address includes: address_id, name, street, city, country, etc.
        - Indicates which address is the default

    Example:
        >>> addresses = await sandbox_get_shipping_addresses()
        >>> for addr in addresses['addresses']:
        >>>     print(f"{addr['name']}: {addr['street1']}, {addr['city']}")
        >>>     if addr['is_default']:
        >>>         print("  (Default)")
    """
    client = get_order_client()
    response = client.get_shipping_addresses()
    return response


async def sandbox_confirm_shipping_address(address_id: str) -> dict[str, Any]:
    """Confirm shipping address for the current order (sandbox environment only).

    Args:
        address_id: Address ID to use (from sandbox_get_shipping_addresses).

    Returns:
        Dictionary with confirmation status.

    Example:
        >>> addresses = await sandbox_get_shipping_addresses()
        >>> address_id = addresses['addresses'][0]['address_id']
        >>> result = await sandbox_confirm_shipping_address(address_id)
        >>> print("Shipping address confirmed")
    """
    client = get_order_client()
    response = client.confirm_shipping_address(address_id=address_id)
    return response


async def sandbox_get_shipping_methods() -> dict[str, Any]:
    """Get available shipping methods for the current cart (sandbox environment only).

    Returns:
        Dictionary containing available shipping methods:
        - method_id: Unique identifier
        - name: Shipping method name (e.g., "Standard", "Express")
        - cost: Shipping cost
        - estimated_delivery_days: Estimated delivery time

    Example:
        >>> methods = await sandbox_get_shipping_methods()
        >>> print("Available shipping methods:")
        >>> for method in methods['methods']:
        >>>     print(f"  {method['name']}: ${method['cost']} ({method['estimated_delivery_days']} days)")
    """
    client = get_order_client()
    response = client.get_shipping_methods()
    return response


async def sandbox_confirm_shipping_method(method_id: str) -> dict[str, Any]:
    """Confirm shipping method for the current order (sandbox environment only).

    Args:
        method_id: Shipping method ID (from sandbox_get_shipping_methods).

    Returns:
        Dictionary with confirmation status.

    Example:
        >>> methods = await sandbox_get_shipping_methods()
        >>> method_id = methods['methods'][0]['method_id']
        >>> result = await sandbox_confirm_shipping_method(method_id)
        >>> print("Shipping method confirmed")
    """
    client = get_order_client()
    response = client.confirm_shipping_method(method_id=method_id)
    return response


async def sandbox_review_order() -> dict[str, Any]:
    """Review order before submission (sandbox environment only).

    Returns complete order details including cart, shipping address, shipping method,
    and all costs for final review before placing the order.

    Returns:
        Dictionary containing complete order review:
        - cart: Cart details with all line items
        - shipping_address: Selected shipping address
        - shipping_method: Selected shipping method
        - subtotal: Items subtotal
        - tax: Tax amount
        - shipping_cost: Shipping cost
        - total: Grand total
        - currency: Currency code

    Example:
        >>> review = await sandbox_review_order()
        >>> print(f"Order Review:")
        >>> print(f"  Items: ${review['subtotal']}")
        >>> print(f"  Shipping: ${review['shipping_cost']}")
        >>> print(f"  Tax: ${review['tax']}")
        >>> print(f"  Total: ${review['total']} {review['currency']}")
        >>> print(f"Shipping to: {review['shipping_address']['city']}, {review['shipping_address']['country']}")
    """
    client = get_order_client()
    response = client.review_order()
    return response


async def sandbox_submit_order() -> dict[str, Any]:
    """Submit the order for processing (sandbox environment only).

    This is the final step in the order workflow. Submits the order with the confirmed
    cart, shipping address, and shipping method.

    Returns:
        Dictionary containing order submission result:
        - success: Boolean indicating if order was placed
        - order_id: Unique order identifier (if successful)
        - order_number: Human-readable order number (if successful)
        - message: Status or confirmation message
        - errors: List of errors (if any)

    Example:
        >>> result = await sandbox_submit_order()
        >>> if result['success']:
        >>>     print(f"Order placed successfully!")
        >>>     print(f"Order ID: {result['order_id']}")
        >>>     print(f"Order Number: {result['order_number']}")
        >>> else:
        >>>     print(f"Order failed: {result['message']}")
        >>>     for error in result.get('errors', []):
        >>>         print(f"  - {error}")
    """
    client = get_order_client()
    response = client.submit_order()
    return response
