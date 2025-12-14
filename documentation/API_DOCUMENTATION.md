# StorageHub API Documentation

This document provides comprehensive documentation for the StorageHub API, with a focus on Home Assistant integration.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Home Assistant Integration API](#home-assistant-integration-api)
4. [Webhooks](#webhooks)
5. [Core API Reference](#core-api-reference)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Overview

StorageHub provides a RESTful API for managing your personal inventory. The API is designed to be easy to integrate with Home Assistant and other automation platforms.

### Base URL

```
http://your-storagehub-instance/api
```

### API Versions

- **v1.0**: Current stable version
- OpenAPI/Swagger documentation available at `/api/docs`
- ReDoc documentation available at `/api/redoc`

### Content Type

All requests and responses use JSON:
```
Content-Type: application/json
```

---

## Authentication

StorageHub supports two authentication methods:

### 1. Session-Based Authentication (Web UI)

Used by the web interface. Requires logging in and uses HTTP-only cookies.

```http
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "uuid-of-user",
  "password": "optional-password"
}
```

### 2. API Key Authentication (Recommended for Home Assistant)

API keys are the recommended method for Home Assistant and other external integrations.

#### Creating an API Key

1. Log into the StorageHub web UI
2. Navigate to Settings > API Keys
3. Click "Create API Key"
4. Select the required scopes
5. Copy the key immediately (it's only shown once!)

Or via API:
```http
POST /api/api-keys
Content-Type: application/json
Cookie: session_token=your-session

{
  "name": "Home Assistant",
  "description": "API key for Home Assistant integration",
  "scopes": ["read", "search"],
  "expires_at": null
}
```

Response:
```json
{
  "id": "uuid",
  "name": "Home Assistant",
  "key": "shub_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "key_prefix": "shub_xxxxxxx",
  "scopes": ["read", "search"],
  "is_active": true,
  "created_at": "2025-12-09T10:00:00Z"
}
```

#### Using API Keys

Include the key in your requests using either header:

**Option 1: X-API-Key header (Recommended)**
```http
GET /api/ha/stats
X-API-Key: shub_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Option 2: Authorization Bearer header**
```http
GET /api/ha/stats
Authorization: Bearer shub_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### API Key Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read-only access to inventory data |
| `write` | Create, update, and delete items/containers |
| `search` | Use the search functionality |
| `webhooks` | Manage webhooks |
| `admin` | Full administrative access |

---

## Home Assistant Integration API

The Home Assistant API is available at `/api/ha/*` and is optimized for sensor data and automations.

### Status Endpoint

Check system status (no authentication required):

```http
GET /api/ha/status
```

Response:
```json
{
  "status": "online",
  "version": "1.0.0",
  "api_version": "v1",
  "name": "StorageHub"
}
```

### Inventory Statistics

Get comprehensive inventory statistics for Home Assistant sensors:

```http
GET /api/ha/stats
X-API-Key: your-api-key
```

Response:
```json
{
  "total_locations": 5,
  "total_containers": 42,
  "total_items": 1523,
  "total_photos": 3847,
  "total_tags": 156,
  "items_needing_review": 12,
  "items_by_condition": {
    "good": 1200,
    "fair": 250,
    "damaged": 50,
    "needs_repair": 23
  },
  "items_by_season": {
    "none": 1000,
    "winter": 200,
    "summer": 150,
    "spring": 100,
    "fall": 50,
    "holiday": 23
  },
  "last_updated": "2025-12-09T10:30:00Z"
}
```

### Reminder Summary

Get reminder counts for sensors:

```http
GET /api/ha/reminders
X-API-Key: your-api-key
```

Response:
```json
{
  "total_reminders": 15,
  "pending_reminders": 10,
  "overdue_reminders": 3,
  "due_today": 2,
  "due_this_week": 5,
  "reminders_by_type": {
    "check_item": 5,
    "expiration": 3,
    "maintenance": 4,
    "restock": 2,
    "custom": 1
  }
}
```

### List Reminders

Get detailed reminder list for notifications:

```http
GET /api/ha/reminders/list?limit=20&include_completed=false
X-API-Key: your-api-key
```

Response:
```json
[
  {
    "id": "uuid",
    "title": "Check winter clothes condition",
    "reminder_type": "check_item",
    "due_date": "2025-12-15T00:00:00Z",
    "is_overdue": false,
    "item_name": "Winter Jacket",
    "container_name": "Winter Storage Box"
  }
]
```

### Locations

```http
GET /api/ha/locations
X-API-Key: your-api-key
```

Response:
```json
[
  {
    "id": "uuid",
    "name": "Garage",
    "description": "Main garage storage",
    "container_count": 15,
    "item_count": 234
  }
]
```

### Containers

```http
GET /api/ha/containers?location_id=uuid&limit=50
X-API-Key: your-api-key
```

Response:
```json
[
  {
    "id": "uuid",
    "name": "Holiday Decorations",
    "qr_code": "SH-ABC123",
    "location_name": "Garage",
    "item_count": 45,
    "child_container_count": 3
  }
]
```

### Get Container by QR Code

Useful for NFC/QR scanning automations:

```http
GET /api/ha/containers/qr/SH-ABC123
X-API-Key: your-api-key
```

### Items

```http
GET /api/ha/items?container_id=uuid&condition=good&limit=50
X-API-Key: your-api-key
```

Query parameters:
- `container_id`: Filter by container
- `condition`: Filter by condition (good, fair, damaged, needs_repair)
- `seasonal`: Filter by season (none, spring, summer, fall, winter, holiday)
- `needs_review`: Filter items needing AI review
- `limit`: Maximum results (default: 50, max: 200)
- `offset`: Pagination offset

Response:
```json
[
  {
    "id": "uuid",
    "name": "Red Winter Jacket",
    "description": "Size M, waterproof",
    "container_name": "Winter Clothes",
    "location_name": "Bedroom Closet",
    "condition": "good",
    "seasonal": "winter",
    "value_estimate": 150.00,
    "owner_name": "John",
    "primary_image_url": "/uploads/images/abc123.jpg",
    "tags": ["clothing", "winter", "jacket"]
  }
]
```

### Search

Search for items (requires `search` scope):

```http
GET /api/ha/search?q=red%20jacket&limit=20
X-API-Key: your-api-key
```

Response:
```json
{
  "items": [...],
  "total_count": 5,
  "query": "red jacket"
}
```

### Tags

```http
GET /api/ha/tags
X-API-Key: your-api-key
```

Response:
```json
[
  {
    "id": "uuid",
    "name": "electronics",
    "is_ai_generated": false,
    "item_count": 45
  }
]
```

---

## Webhooks

Webhooks allow you to receive real-time notifications when events occur in StorageHub.

### Available Events

| Event | Description |
|-------|-------------|
| `item.created` | New item added |
| `item.updated` | Item modified |
| `item.deleted` | Item removed |
| `item.moved` | Item moved to different container |
| `container.created` | New container added |
| `container.updated` | Container modified |
| `container.deleted` | Container removed |
| `location.created` | New location added |
| `location.updated` | Location modified |
| `location.deleted` | Location removed |
| `reminder.due` | Reminder becomes due |
| `reminder.overdue` | Reminder is overdue |
| `reminder.completed` | Reminder marked complete |
| `stats.updated` | Inventory statistics changed |

### Creating a Webhook

```http
POST /api/webhooks
Content-Type: application/json
Cookie: session_token=your-session

{
  "name": "Home Assistant Events",
  "url": "http://homeassistant.local:8123/api/webhook/storagehub",
  "secret": "your-webhook-secret",
  "events": ["item.created", "item.updated", "reminder.due"],
  "retry_count": 3,
  "timeout_seconds": 30
}
```

### Webhook Payload

When an event occurs, StorageHub sends a POST request to your webhook URL:

```json
{
  "event": "item.created",
  "timestamp": "2025-12-09T10:30:00Z",
  "data": {
    "item_id": "uuid",
    "name": "New Item",
    "container_id": "uuid",
    "container_name": "Storage Box"
  }
}
```

### Webhook Signature

If you configure a secret, StorageHub signs the payload with HMAC-SHA256:

```
X-StorageHub-Signature: sha256=abc123...
X-StorageHub-Event: item.created
```

Verify the signature:
```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Testing Webhooks

```http
POST /api/webhooks/{webhook_id}/test
Content-Type: application/json
Cookie: session_token=your-session

{
  "event": "stats.updated"
}
```

### Webhook Delivery History

```http
GET /api/webhooks/{webhook_id}/deliveries?limit=20
Cookie: session_token=your-session
```

---

## Core API Reference

### Locations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/locations` | List all locations |
| POST | `/api/locations` | Create location |
| GET | `/api/locations/{id}` | Get location details |
| PATCH | `/api/locations/{id}` | Update location |
| DELETE | `/api/locations/{id}` | Delete location |
| GET | `/api/locations/stats` | Get dashboard stats |

### Containers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/containers` | List containers |
| POST | `/api/containers` | Create container |
| GET | `/api/containers/{id}` | Get container |
| PATCH | `/api/containers/{id}` | Update container |
| DELETE | `/api/containers/{id}` | Delete container |
| GET | `/api/containers/{id}/qr` | Get QR code image |

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/items` | List items |
| POST | `/api/items` | Create item |
| GET | `/api/items/{id}` | Get item |
| PATCH | `/api/items/{id}` | Update item |
| DELETE | `/api/items/{id}` | Delete item |
| POST | `/api/items/{id}/images` | Upload image |
| DELETE | `/api/items/{id}/images/{image_id}` | Remove image |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search` | Full search |
| GET | `/api/search/autocomplete` | Fast autocomplete |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags` | List all tags |
| POST | `/api/tags` | Create tag |
| PATCH | `/api/tags/{id}` | Update tag |
| DELETE | `/api/tags/{id}` | Delete tag |
| POST | `/api/tags/merge` | Merge tags |

### Reminders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reminders` | List reminders |
| POST | `/api/reminders` | Create reminder |
| PATCH | `/api/reminders/{id}` | Update reminder |
| POST | `/api/reminders/{id}/complete` | Mark complete |
| DELETE | `/api/reminders/{id}` | Delete reminder |

### API Keys

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/api-keys` | List API keys |
| POST | `/api/api-keys` | Create API key |
| GET | `/api/api-keys/{id}` | Get API key |
| PATCH | `/api/api-keys/{id}` | Update API key |
| DELETE | `/api/api-keys/{id}` | Delete API key |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/webhooks` | List webhooks |
| POST | `/api/webhooks` | Create webhook |
| GET | `/api/webhooks/events` | List available events |
| GET | `/api/webhooks/{id}` | Get webhook |
| PATCH | `/api/webhooks/{id}` | Update webhook |
| DELETE | `/api/webhooks/{id}` | Delete webhook |
| POST | `/api/webhooks/{id}/test` | Test webhook |
| GET | `/api/webhooks/{id}/deliveries` | Delivery history |

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing credentials |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

Validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently, StorageHub does not enforce rate limits. However, for production deployments, consider implementing rate limiting at the reverse proxy level (nginx, Traefik, etc.).

---

## Examples

### Home Assistant Configuration

#### REST Sensor

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: StorageHub Items
    resource: http://storagehub.local/api/ha/stats
    headers:
      X-API-Key: !secret storagehub_api_key
    value_template: "{{ value_json.total_items }}"
    json_attributes:
      - total_locations
      - total_containers
      - total_photos
      - items_needing_review

  - platform: rest
    name: StorageHub Overdue Reminders
    resource: http://storagehub.local/api/ha/reminders
    headers:
      X-API-Key: !secret storagehub_api_key
    value_template: "{{ value_json.overdue_reminders }}"
    json_attributes:
      - due_today
      - due_this_week
      - pending_reminders
```

#### Webhook Automation

```yaml
# automations.yaml
automation:
  - alias: "StorageHub - New Item Notification"
    trigger:
      - platform: webhook
        webhook_id: storagehub_item_created
    action:
      - service: notify.mobile_app
        data:
          title: "New Item Added"
          message: "{{ trigger.json.data.name }} was added to {{ trigger.json.data.container_name }}"

  - alias: "StorageHub - Reminder Due"
    trigger:
      - platform: webhook
        webhook_id: storagehub_reminder
    condition:
      - condition: template
        value_template: "{{ trigger.json.event == 'reminder.due' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "StorageHub Reminder"
          message: "{{ trigger.json.data.title }}"
```

#### Template Sensor for Search

```yaml
# configuration.yaml
rest_command:
  storagehub_search:
    url: "http://storagehub.local/api/ha/search"
    method: GET
    headers:
      X-API-Key: !secret storagehub_api_key
    payload: '{"q": "{{ query }}"}'
```

### Python Example

```python
import requests

API_KEY = "shub_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "http://storagehub.local/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Get inventory stats
response = requests.get(f"{BASE_URL}/ha/stats", headers=headers)
stats = response.json()
print(f"Total items: {stats['total_items']}")

# Search for items
response = requests.get(
    f"{BASE_URL}/ha/search",
    headers=headers,
    params={"q": "winter jacket", "limit": 10}
)
results = response.json()
for item in results["items"]:
    print(f"- {item['name']} in {item['container_name']}")
```

### cURL Examples

```bash
# Get system status (no auth required)
curl http://storagehub.local/api/ha/status

# Get inventory stats
curl -H "X-API-Key: shub_xxx" http://storagehub.local/api/ha/stats

# Search for items
curl -H "X-API-Key: shub_xxx" "http://storagehub.local/api/ha/search?q=red%20jacket"

# Get container by QR code
curl -H "X-API-Key: shub_xxx" http://storagehub.local/api/ha/containers/qr/SH-ABC123

# Create a webhook
curl -X POST http://storagehub.local/api/webhooks \
  -H "Cookie: session_token=your-session" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home Assistant",
    "url": "http://homeassistant.local:8123/api/webhook/storagehub",
    "events": ["item.created", "reminder.due"]
  }'
```

---

## Changelog

### v1.0.0 (2025-12-09)

- Initial API release
- Home Assistant integration API (`/api/ha/*`)
- API key authentication
- Webhook support for real-time events
- Comprehensive inventory statistics
- QR code container lookup

---

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/your-repo/storagehub/issues)
- Documentation: Check `/api/docs` for interactive OpenAPI documentation
