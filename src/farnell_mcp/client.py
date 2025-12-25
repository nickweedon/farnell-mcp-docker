"""Farnell API Client Module.

This module handles communication with the Farnell Partner API.
Provides two specialized clients:
- ProductSearchClient: For product search (API key authentication)
- OrderAPIClient: For cart and order management (JWT authentication, sandbox only)
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from pyrate_limiter import Duration, Limiter, Rate

# Load environment variables from multiple possible locations
_env_paths = [
    Path.cwd() / ".env",
    Path(__file__).parent.parent.parent.parent / ".env",
    Path.home() / ".env",
]

for env_path in _env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class FarnellConfig:
    """Configuration for Farnell API clients."""

    api_key: str
    store_id: str
    environment: str  # "production" or "sandbox"
    timeout: int
    debug: bool
    sandbox_username: str | None = None
    sandbox_password: str | None = None

    @property
    def product_search_base_url(self) -> str:
        """Get the base URL for Product Search API."""
        # Product Search API uses same endpoint for all environments
        return "https://api.element14.com/catalog/products"

    @property
    def order_api_base_url(self) -> str:
        """Get the base URL for Order API (sandbox only)."""
        if self.environment != "sandbox":
            raise ValueError("Order API is only available in sandbox environment")

        # Map store ID to appropriate sandbox URL
        if "newark" in self.store_id.lower():
            return "https://api-uat.newark.com"
        elif "element14" in self.store_id.lower():
            return "https://api-uat.element14.com"
        else:  # farnell and others
            return "https://api-uat.farnell.com"


def get_farnell_config() -> FarnellConfig:
    """Get Farnell configuration from environment variables.

    Returns:
        FarnellConfig object with all settings.

    Raises:
        ValueError: If required configuration is missing.
    """
    api_key = os.getenv("FARNELL_API_KEY")
    if not api_key:
        raise ValueError("FARNELL_API_KEY environment variable is required")

    store_id = os.getenv("FARNELL_STORE_ID", "www.newark.com")
    environment = os.getenv("FARNELL_ENVIRONMENT", "production")
    timeout = int(os.getenv("FARNELL_API_TIMEOUT", "30"))
    debug = os.getenv("FARNELL_DEBUG", "false").lower() == "true"
    sandbox_username = os.getenv("FARNELL_SANDBOX_USERNAME")
    sandbox_password = os.getenv("FARNELL_SANDBOX_PASSWORD")

    return FarnellConfig(
        api_key=api_key,
        store_id=store_id,
        environment=environment,
        timeout=timeout,
        debug=debug,
        sandbox_username=sandbox_username,
        sandbox_password=sandbox_password,
    )


class ProductSearchClient:
    """Client for Farnell Product Search API.

    Uses simple API key authentication via query parameters.
    Works in both production and sandbox environments.
    Implements automatic rate limiting:
    - 2 calls/second (matches API limit with small bucket to prevent bursts)
    """

    def __init__(self, config: FarnellConfig) -> None:
        """Initialize the Product Search client.

        Args:
            config: Farnell configuration object.
        """
        self.config = config
        self.base_url = config.product_search_base_url
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

        # Initialize rate limiter for per-second limit
        # API limit: 2 calls/sec (per-day limit handled by upstream API)
        # Small bucket size (2) prevents bursts while allowing 2 immediate calls
        self.rate_limiter = Limiter(
            Rate(2, Duration.SECOND),  # 2 calls per second (bucket size = 2)
            raise_when_fail=False,  # Don't raise exception when rate limit hit
            max_delay=Duration.HOUR,  # Wait up to 1 hour for a token (effectively indefinite)
        )

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("ProductSearchClient initialized with store_id=%s", config.store_id)
            logger.debug("Rate limiting enabled: 2 calls/sec (bucket=2)")

    def search_by_keyword(
        self,
        keyword: str,
        offset: int = 0,
        num_results: int = 10,
        filters: list[str] | None = None,
        response_group: str = "medium",
    ) -> dict[str, Any]:
        """Search for products by keyword.

        Args:
            keyword: Search keyword (prefix with 'any:' for broad search).
            offset: Starting offset for results (0-based).
            num_results: Number of results to return (1-100).
            filters: Optional filters like ['inStock', 'rohsCompliant'].
            response_group: Detail level ('small', 'medium', 'large', 'prices', 'inventory').

        Returns:
            API response with product results.
        """
        term = keyword if keyword.startswith(("any:", "id:", "manuPartNum:")) else f"any:{keyword}"

        params = self._build_request_params(
            term=term,
            offset=offset,
            num_results=num_results,
            filters=filters,
            response_group=response_group,
        )

        return self._make_request(params)

    def search_by_order_code(
        self, order_code: str, response_group: str = "large"
    ) -> dict[str, Any]:
        """Search for a product by Farnell/Newark/Element14 order code.

        Args:
            order_code: The order code to search for.
            response_group: Detail level ('small', 'medium', 'large').

        Returns:
            API response with product details.
        """
        params = self._build_request_params(
            term=f"id:{order_code}", offset=0, num_results=1, response_group=response_group
        )

        return self._make_request(params)

    def search_by_mfr_part_number(
        self,
        part_number: str,
        offset: int = 0,
        num_results: int = 10,
        filters: list[str] | None = None,
        response_group: str = "medium",
    ) -> dict[str, Any]:
        """Search for products by manufacturer part number.

        Args:
            part_number: Manufacturer part number.
            offset: Starting offset for results.
            num_results: Number of results to return.
            filters: Optional filters.
            response_group: Detail level.

        Returns:
            API response with product results.
        """
        params = self._build_request_params(
            term=f"manuPartNum:{part_number}",
            offset=offset,
            num_results=num_results,
            filters=filters,
            response_group=response_group,
        )

        return self._make_request(params)

    def _build_request_params(
        self,
        term: str,
        offset: int = 0,
        num_results: int = 10,
        filters: list[str] | None = None,
        response_group: str = "medium",
    ) -> dict[str, Any]:
        """Build request parameters for Product Search API.

        Args:
            term: Search term (e.g., 'any:resistor', 'id:1278613').
            offset: Results offset.
            num_results: Number of results.
            filters: Optional filter list.
            response_group: Response detail level.

        Returns:
            Dictionary of request parameters.
        """
        params = {
            "term": term,
            "storeInfo.id": self.config.store_id,
            "resultsSettings.offset": str(offset),
            "resultsSettings.numberOfResults": str(num_results),
            "resultsSettings.responseGroup": response_group,
            "callInfo.responseDataFormat": "json",
            "callInfo.apiKey": self.config.api_key,
        }

        # Add filters if provided
        if filters:
            params["resultsSettings.refinements.filters"] = ",".join(filters)

        return params

    def _make_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Make a request to the Product Search API.

        Rate limiting is applied automatically - the request will be delayed
        if necessary to stay within the 2 calls/sec limit.

        Args:
            params: Request parameters.

        Returns:
            JSON response from API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        if self.config.debug:
            logger.debug("Making request to %s with params: %s", self.base_url, params)

        # Acquire rate limit - this will block/delay if we're over the limit
        # Per-second limit only; per-day limit is enforced by upstream API
        self.rate_limiter.try_acquire("farnell_api")

        try:
            response = self.session.get(self.base_url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Product Search API request failed: %s", e)
            raise


class OrderAPIClient:
    """Client for Farnell Order API.

    Uses JWT token authentication.
    Only works in sandbox environment.
    """

    def __init__(self, config: FarnellConfig) -> None:
        """Initialize the Order API client.

        Args:
            config: Farnell configuration object.

        Raises:
            ValueError: If not in sandbox environment or credentials missing.
        """
        if config.environment != "sandbox":
            raise ValueError("Order API is only available in sandbox environment")

        if not config.sandbox_username or not config.sandbox_password:
            raise ValueError(
                "FARNELL_SANDBOX_USERNAME and FARNELL_SANDBOX_PASSWORD are required for Order API"
            )

        self.config = config
        self.base_url = config.order_api_base_url
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

        # JWT token management
        self._token: str | None = None
        self._token_expiry: datetime | None = None

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("OrderAPIClient initialized with base_url=%s", self.base_url)

    def _authenticate(self) -> str:
        """Authenticate and get JWT token.

        Returns:
            JWT token string.

        Raises:
            RuntimeError: If authentication fails.
        """
        auth_url = f"{self.base_url}/auth/token"
        payload = {
            "username": self.config.sandbox_username,
            "password": self.config.sandbox_password,
        }

        try:
            if self.config.debug:
                logger.debug("Authenticating to %s", auth_url)

            response = self.session.post(auth_url, json=payload, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()
            token = data.get("token")

            if not token:
                raise RuntimeError("No token in authentication response")

            # Cache token with expiry (assume 1 hour expiry if not specified)
            self._token = token
            self._token_expiry = datetime.now() + timedelta(hours=1)

            if self.config.debug:
                logger.debug("Authentication successful, token expires at %s", self._token_expiry)

            return token

        except requests.exceptions.RequestException as e:
            logger.error("Order API authentication failed: %s", e)
            raise RuntimeError(f"Authentication failed: {e}") from e

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid JWT token.

        Refreshes token if expired or missing.
        """
        if self._token is None or self._token_expiry is None:
            # No token, need to authenticate
            self._authenticate()
        elif datetime.now() >= self._token_expiry:
            # Token expired, refresh
            if self.config.debug:
                logger.debug("Token expired, re-authenticating")
            self._authenticate()

        # Set authorization header
        self.session.headers["Authorization"] = f"Bearer {self._token}"

    def add_to_cart(self, order_code: str, quantity: int) -> dict[str, Any]:
        """Add item to shopping cart.

        Args:
            order_code: Farnell order code.
            quantity: Quantity to add.

        Returns:
            API response with cart details.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/cart/addItem"
        payload = {"orderCode": order_code, "quantity": quantity}

        response = self.session.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def get_cart(self) -> dict[str, Any]:
        """Get current cart contents.

        Returns:
            API response with cart details.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/cart"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def update_cart_item(self, line_item_id: str, quantity: int) -> dict[str, Any]:
        """Update quantity of cart item.

        Args:
            line_item_id: Line item ID from cart.
            quantity: New quantity.

        Returns:
            API response with updated cart.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/cart/updateItem"
        payload = {"lineItemId": line_item_id, "quantity": quantity}

        response = self.session.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def delete_cart_item(self, line_item_id: str) -> dict[str, Any]:
        """Delete item from cart.

        Args:
            line_item_id: Line item ID to delete.

        Returns:
            API response.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/cart/deleteItem"
        payload = {"lineItemId": line_item_id}

        response = self.session.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def clear_cart(self) -> dict[str, Any]:
        """Clear all items from cart.

        Returns:
            API response.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/cart/clear"
        response = self.session.post(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def get_shipping_addresses(self) -> dict[str, Any]:
        """Get available shipping addresses.

        Returns:
            API response with address list.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/shipping_address"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def confirm_shipping_address(self, address_id: str) -> dict[str, Any]:
        """Confirm shipping address for order.

        Args:
            address_id: Address ID to use.

        Returns:
            API response.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/shipping_address"
        payload = {"addressId": address_id}

        response = self.session.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def get_shipping_methods(self) -> dict[str, Any]:
        """Get available shipping methods.

        Returns:
            API response with shipping methods.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/shipping_methods"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def confirm_shipping_method(self, method_id: str) -> dict[str, Any]:
        """Confirm shipping method for order.

        Args:
            method_id: Shipping method ID.

        Returns:
            API response.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/shipping_method"
        payload = {"methodId": method_id}

        response = self.session.post(url, json=payload, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def review_order(self) -> dict[str, Any]:
        """Get order review (cart + shipping details).

        Returns:
            API response with complete order details.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/order_review"
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def submit_order(self) -> dict[str, Any]:
        """Submit the order for processing.

        Returns:
            API response with order confirmation.
        """
        self._ensure_authenticated()

        url = f"{self.base_url}/order/order_submit"
        response = self.session.post(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()


# Singleton client instances
_product_client: ProductSearchClient | None = None
_order_client: OrderAPIClient | None = None


def get_product_client() -> ProductSearchClient:
    """Get the Product Search client singleton instance.

    Returns:
        ProductSearchClient instance.
    """
    global _product_client
    if _product_client is None:
        config = get_farnell_config()
        _product_client = ProductSearchClient(config)
    return _product_client


def get_order_client() -> OrderAPIClient:
    """Get the Order API client singleton instance.

    Returns:
        OrderAPIClient instance.

    Raises:
        ValueError: If not in sandbox environment or credentials missing.
    """
    global _order_client
    if _order_client is None:
        config = get_farnell_config()
        _order_client = OrderAPIClient(config)
    return _order_client
