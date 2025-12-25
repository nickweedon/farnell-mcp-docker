"""Type definitions for Farnell MCP server."""

from typing import NotRequired, TypedDict

# ============================================================================
# Product Search Types
# ============================================================================


class Price(TypedDict):
    """Single price point for a product."""

    cost: float
    quantity: int
    currency: str  # e.g., "GBP", "USD"


class Stock(TypedDict):
    """Stock information."""

    level: int  # Quantity available
    regional_availability: NotRequired[dict[str, int]]  # Stock by warehouse


class ProductAttribute(TypedDict):
    """Product attribute/specification."""

    attribute_label: str
    attribute_value: str
    attribute_unit: NotRequired[str]


class Product(TypedDict):
    """Core product information."""

    id: str  # Farnell order code
    sku: str  # Same as id
    manufacturer_part_number: str
    manufacturer_name: str
    display_name: str
    product_description: NotRequired[str]
    pack_size: NotRequired[int]
    unit_of_measure: NotRequired[str]  # e.g., "EACH", "REEL"
    stock: NotRequired[Stock]
    prices: NotRequired[list[Price]]
    datasheet_url: NotRequired[str]
    product_image_url: NotRequired[str]
    rohs_status_code: NotRequired[str]  # "Compliant", "Non-Compliant", etc.
    attributes: NotRequired[list[ProductAttribute]]


class ProductSearchResult(TypedDict):
    """Response from product search."""

    products: list[Product]
    total_results: int
    offset: int
    number_of_results: int
    keyword: NotRequired[str]


class ProductDetail(TypedDict):
    """Detailed product information (large response)."""

    product: Product
    technical_specifications: NotRequired[list[ProductAttribute]]
    related_products: NotRequired[list[str]]  # Order codes
    compliance_documents: NotRequired[list[dict]]


# ============================================================================
# Inventory and Pricing Types
# ============================================================================


class ProductInventory(TypedDict):
    """Inventory status for a product."""

    order_code: str
    in_stock: bool
    quantity_available: int
    lead_time_days: NotRequired[int]
    next_arrival_date: NotRequired[str]
    regional_stock: NotRequired[dict[str, int]]


class ProductPricing(TypedDict):
    """Pricing information for a product."""

    order_code: str
    currency: str
    price_breaks: list[Price]  # Volume pricing tiers
    minimum_order_quantity: int
    pack_size: int
    unit_of_measure: str


# ============================================================================
# Cart and Order Types
# ============================================================================


class CartLineItem(TypedDict):
    """Single line item in shopping cart."""

    line_item_id: str
    order_code: str
    manufacturer_part_number: str
    description: str
    quantity: int
    unit_price: float
    line_total: float
    currency: str


class CartDetails(TypedDict):
    """Shopping cart contents."""

    cart_id: str
    line_items: list[CartLineItem]
    subtotal: float
    tax: NotRequired[float]
    shipping: NotRequired[float]
    total: NotRequired[float]
    currency: str


class CartResponse(TypedDict):
    """Response from cart modification operations."""

    success: bool
    message: str
    cart: CartDetails


class ShippingAddress(TypedDict):
    """Shipping address information."""

    address_id: str
    name: str
    company: NotRequired[str]
    street1: str
    street2: NotRequired[str]
    city: str
    state_province: NotRequired[str]
    postal_code: str
    country: str
    is_default: bool


class ShippingMethod(TypedDict):
    """Available shipping method."""

    method_id: str
    name: str
    description: NotRequired[str]
    cost: float
    currency: str
    estimated_delivery_days: NotRequired[int]


class OrderReview(TypedDict):
    """Order review before submission."""

    cart: CartDetails
    shipping_address: ShippingAddress
    shipping_method: ShippingMethod
    subtotal: float
    tax: float
    shipping_cost: float
    total: float
    currency: str


class OrderSubmitResponse(TypedDict):
    """Response from order submission."""

    success: bool
    order_id: NotRequired[str]
    order_number: NotRequired[str]
    message: str
    errors: NotRequired[list[str]]


# ============================================================================
# Error Types
# ============================================================================


class FarnellAPIError(TypedDict):
    """Standard error response from Farnell API."""

    error: str
    message: str
    status_code: int
    details: NotRequired[dict]


# ============================================================================
# Configuration Types
# ============================================================================


class FarnellConfigDict(TypedDict):
    """Configuration for Farnell API client."""

    api_key: str
    store_id: str  # e.g., "uk.farnell.com", "www.newark.com"
    environment: str  # "production" or "sandbox"
    timeout: int
    debug: bool
    sandbox_username: NotRequired[str]
    sandbox_password: NotRequired[str]
