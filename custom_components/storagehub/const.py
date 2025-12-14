"""Constants for the StorageHub integration."""

from typing import Final

DOMAIN: Final = "storagehub"

# Platforms
PLATFORMS: Final = ["sensor", "binary_sensor"]

# Configuration keys
CONF_HOST: Final = "host"
CONF_API_KEY: Final = "api_key"

# Defaults
DEFAULT_SCAN_INTERVAL: Final = 300  # 5 minutes
DEFAULT_TIMEOUT: Final = 10  # seconds

# API Endpoints
API_STATUS: Final = "/api/ha/status"
API_STATS: Final = "/api/ha/stats"
API_REMINDERS: Final = "/api/ha/reminders"
API_SEARCH: Final = "/api/ha/search"
API_CONTAINER_QR: Final = "/api/ha/containers/qr"

# Service names
SERVICE_SEARCH: Final = "search"
SERVICE_GET_CONTAINER: Final = "get_container"
SERVICE_REFRESH: Final = "refresh"

# Attributes
ATTR_TOTAL_LOCATIONS: Final = "total_locations"
ATTR_TOTAL_CONTAINERS: Final = "total_containers"
ATTR_TOTAL_ITEMS: Final = "total_items"
ATTR_TOTAL_PHOTOS: Final = "total_photos"
ATTR_TOTAL_TAGS: Final = "total_tags"
ATTR_ITEMS_NEEDING_REVIEW: Final = "items_needing_review"
ATTR_ITEMS_BY_CONDITION: Final = "items_by_condition"
ATTR_ITEMS_BY_SEASON: Final = "items_by_season"
ATTR_LAST_UPDATED: Final = "last_updated"

ATTR_TOTAL_REMINDERS: Final = "total_reminders"
ATTR_PENDING_REMINDERS: Final = "pending_reminders"
ATTR_OVERDUE_REMINDERS: Final = "overdue_reminders"
ATTR_DUE_TODAY: Final = "due_today"
ATTR_DUE_THIS_WEEK: Final = "due_this_week"
ATTR_REMINDERS_BY_TYPE: Final = "reminders_by_type"
