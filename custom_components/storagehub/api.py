"""API client for StorageHub."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import (
    API_CONTAINER_QR,
    API_REMINDERS,
    API_SEARCH,
    API_STATS,
    API_STATUS,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class StorageHubApiError(Exception):
    """Base exception for StorageHub API errors."""


class CannotConnect(StorageHubApiError):
    """Exception for connection errors."""


class InvalidAuth(StorageHubApiError):
    """Exception for authentication errors."""


class StorageHubApiClient:
    """API client for StorageHub."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client.

        Args:
            session: aiohttp client session
            host: StorageHub host URL (e.g., http://storagehub.local)
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self._session = session
        self._host = host.rstrip("/")
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def host(self) -> str:
        """Return the host URL."""
        return self._host

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Make an API request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            authenticated: Whether to include auth headers

        Returns:
            Response JSON data

        Raises:
            CannotConnect: If connection fails
            InvalidAuth: If authentication fails
            StorageHubApiError: For other API errors
        """
        url = f"{self._host}{endpoint}"
        headers = self._get_headers() if authenticated else {}

        try:
            async with asyncio.timeout(self._timeout.total):
                async with self._session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth("Invalid API key")
                    if response.status == 403:
                        raise InvalidAuth("Insufficient API key permissions")
                    if response.status >= 400:
                        text = await response.text()
                        raise StorageHubApiError(
                            f"API error {response.status}: {text}"
                        )
                    return await response.json()

        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout connecting to {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Error connecting to {url}: {err}") from err

    async def async_get_status(self) -> dict[str, Any]:
        """Get system status (no authentication required).

        Returns:
            Status data with keys: status, version, api_version, name
        """
        return await self._request("GET", API_STATUS, authenticated=False)

    async def async_get_stats(self) -> dict[str, Any]:
        """Get inventory statistics.

        Returns:
            Stats data with keys: total_locations, total_containers,
            total_items, total_photos, total_tags, items_needing_review,
            items_by_condition, items_by_season, last_updated
        """
        return await self._request("GET", API_STATS)

    async def async_get_reminders(self) -> dict[str, Any]:
        """Get reminder summary.

        Returns:
            Reminders data with keys: total_reminders, pending_reminders,
            overdue_reminders, due_today, due_this_week, reminders_by_type
        """
        return await self._request("GET", API_REMINDERS)

    async def async_search(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search for items.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            Search results with keys: items, total_count, query
        """
        return await self._request(
            "GET",
            API_SEARCH,
            params={"q": query, "limit": limit},
        )

    async def async_get_container_by_qr(
        self,
        qr_code: str,
    ) -> dict[str, Any]:
        """Get container by QR code.

        Args:
            qr_code: QR code value (e.g., SH-ABC123)

        Returns:
            Container data with keys: id, name, qr_code, location_name,
            item_count, items
        """
        return await self._request(
            "GET",
            f"{API_CONTAINER_QR}/{qr_code}",
        )

    async def async_test_connection(self) -> bool:
        """Test the connection to StorageHub.

        Returns:
            True if connection and authentication are successful

        Raises:
            CannotConnect: If connection fails
            InvalidAuth: If authentication fails
        """
        # First test basic connectivity (no auth)
        await self.async_get_status()
        # Then test authentication
        await self.async_get_stats()
        return True
