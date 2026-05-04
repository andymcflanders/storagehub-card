"""Async API client for the StorageHub /api/ha/* surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

import aiohttp

from .const import API_INDEX, API_SEARCH, API_STATS, API_STATUS, DEFAULT_TIMEOUT

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


@dataclass(frozen=True, slots=True)
class SearchResultItem:
    """One match returned by /api/ha/search."""

    id: str
    name: str
    description: str | None
    container_name: str | None
    location_name: str | None
    condition: str | None
    seasonal: str | None
    value_estimate: float | None
    owner_name: str | None
    primary_image_url: str | None
    tags: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchResultItem:
        value = data.get("value_estimate")
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or ""),
            description=data.get("description"),
            container_name=data.get("container_name"),
            location_name=data.get("location_name"),
            condition=data.get("condition"),
            seasonal=data.get("seasonal"),
            value_estimate=float(value) if value is not None else None,
            owner_name=data.get("owner_name"),
            primary_image_url=data.get("primary_image_url"),
            tags=tuple(data.get("tags") or ()),
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Wrapper around /api/ha/search's response envelope."""

    items: tuple[SearchResultItem, ...]
    total_count: int
    query: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchResult:
        raw_items = data.get("items") or ()
        return cls(
            items=tuple(SearchResultItem.from_dict(item) for item in raw_items),
            total_count=int(data.get("total_count") or 0),
            query=str(data.get("query") or ""),
        )


@dataclass(frozen=True, slots=True)
class IndexEntry:
    """One row of the lite item index used by the Lovelace card."""

    id: str
    name: str
    owner_name: str | None
    container_name: str | None
    location_name: str | None
    ai_names: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IndexEntry:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or ""),
            owner_name=data.get("owner_name"),
            container_name=data.get("container_name"),
            location_name=data.get("location_name"),
            ai_names=tuple(data.get("ai_names") or ()),
        )


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

    async def async_search(self, query: str, limit: int = 20) -> SearchResult:
        data = await self._request(
            "GET", API_SEARCH, params={"q": query, "limit": limit}
        )
        return SearchResult.from_dict(data)

    async def async_get_index(
        self, etag: str | None = None
    ) -> tuple[str | None, list[IndexEntry] | None]:
        """Fetch the lite item index, conditionally on `etag`.

        Bypasses `_request` because 304 isn't an error and carries no body.
        Returns `(new_etag, entries)`; on 304 the new_etag mirrors the
        request etag and entries is None — caller keeps the prior payload.
        ETag string includes its surrounding quotes; pass through verbatim.
        """
        url = f"{self._host}{API_INDEX}"
        headers: dict[str, str] = {
            "Accept": "application/json",
            "X-API-Key": self._api_key,
        }
        if etag is not None:
            headers["If-None-Match"] = etag

        try:
            async with self._session.request(
                "GET",
                url,
                headers=headers,
                timeout=self._timeout,
            ) as response:
                if response.status == 304:
                    return etag, None
                if response.status in (401, 403):
                    raise InvalidAuth(
                        f"API key rejected ({response.status}) for {API_INDEX}"
                    )
                if response.status >= 400:
                    body = await response.text()
                    raise StorageHubError(
                        f"GET {API_INDEX} -> {response.status}: {body[:200]}"
                    )
                new_etag = response.headers.get("ETag")
                payload = await response.json()
                entries = [IndexEntry.from_dict(item) for item in payload]
                return new_etag, entries
        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout contacting {url}") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Cannot reach {url}: {err}") from err

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
