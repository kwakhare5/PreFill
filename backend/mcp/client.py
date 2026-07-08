"""
PreFill MCP Client wrapper — Task 1.4
Centralizes all HTTP interactions with the PreFill MCP server.
"""

import httpx
import logging
from backend.config import settings

logger = logging.getLogger(__name__)


class PreFillMCPClient:
    def __init__(self, base_url: str = settings.MCP_BASE_URL):
        self.base_url = base_url
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def get_platform_orders(self, user_id: str, limit: int = 200) -> dict:
        """Fetch complete order history for a user."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/get_platform_orders",
                params={"user_id": user_id, "limit": limit}
            )
            response.raise_for_status()
            return response.json()

    async def search_platform_items(self, query: str) -> dict:
        """Search products matching query in the catalog."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/search_platform_items",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()

    async def update_platform_cart(self, items: list) -> dict:
        """Update or create cart with standard line items."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/update_platform_cart",
                json={"items": items}
            )
            response.raise_for_status()
            return response.json()

    async def place_platform_order(self, cart_id: str) -> dict:
        """Place the quick commerce order."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/place_platform_order",
                json={"cart_id": cart_id}
            )
            response.raise_for_status()
            return response.json()


mcp_client = PreFillMCPClient()
