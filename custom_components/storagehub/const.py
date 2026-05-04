"""Constants for the StorageHub integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "storagehub"

HEARTBEAT_INTERVAL: Final = 300
DEFAULT_TIMEOUT: Final = 10

API_STATUS: Final = "/api/ha/status"
API_STATS: Final = "/api/ha/stats"
API_SEARCH: Final = "/api/ha/search"
