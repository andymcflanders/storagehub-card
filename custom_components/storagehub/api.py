"""Async API client for the StorageHub /api/ha/* surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

import aiohttp

from .const import API_STATS, API_STATUS, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class StorageHubError(Exception):
    """Base error for the StorageHub client."""


class CannotConnect(StorageHubError):
    """The StorageHub host could not be reached."""


class InvalidAuth(StorageHubError):
    """The API key was rejected or lacks the required scope."""


@dataclass(frozen=True, slots=True)
class SystemStatus:
    """Subset of /api/ha/status used by the integration."""

    name: str
    version: str
    api_version: str
    instance_id: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SystemStatus:
        return cls(
            name=str(data.get("name") or "StorageHub"),
            version=str(data.get("version") or "unknown"),
            api_version=str(data.get("api_version") or "v1"),
            instance_id=data.get("instance_id"),
        )


@dataclass(frozen=True, slots=True)
class InventoryStats:
    """Slim view of /api/ha/stats — just the heartbeat sensor."""

    total_items: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InventoryStats:
        return cls(total_items=int(data.get("total_items") or 0))


class StorageHubApiClient:
    """Thin async client around StorageHub's HA-facing endpoints."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._host = host.rstrip("/")
        self._api_key = api_key
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def host(self) -> str:
        return self._host

    async def async_get_status(self) -> SystemStatus:
        data = await self._request("GET", API_STATUS, authenticated=False)
        return SystemStatus.from_dict(data)

    async def async_get_stats(self) -> InventoryStats:
        data = await self._request("GET", API_STATS)
        return InventoryStats.from_dict(data)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        url = f"{self._host}{path}"
        headers: dict[str, str] = {"Accept": "application/json"}
        if authenticated:
            headers["X-API-Key"] = self._api_key

        try:
            async with self._session.request(
                method,
                url,
                params=params,
                headers=headers,
                timeout=self._timeout,
            ) as response:
                if response.status in (401, 403):
                    raise InvalidAuth(
                        f"API key rejected ({response.status}) for {path}"
                    )
                if response.status >= 400:
                    body = await response.text()
                    raise StorageHubError(
                        f"{method} {path} -> {response.status}: {body[:200]}"
                    )
                return await response.json()
        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout contacting {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Cannot reach {url}: {err}") from err
