# StorageHub Home Assistant Integration

A Home Assistant custom integration for [StorageHub](https://github.com/yourusername/storagehub), a self-hosted personal inventory management system.

## Features

- **Search-first design**: Quickly find items with "where is my X?" searches
- **Minimal sensors**: Essential stats without entity clutter
- **Custom Lovelace card**: Search interface with live results
- **Services for automations**: Voice assistants, NFC tags, scripts

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add this repository URL and select **Integration** as the category
4. Click **Add**
5. Search for "StorageHub" and install
6. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/storagehub` to your `config/custom_components/` directory
2. Restart Home Assistant

### Frontend Card

The card is included in `storagehub-card/dist/storagehub-card.js`. Add it as a Lovelace resource:

1. Go to **Settings** → **Dashboards** → **Resources**
2. Add resource: `/local/storagehub-card.js` (copy the file to `config/www/`)
3. Or use HACS Frontend to install the card separately

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "StorageHub"
4. Enter your StorageHub URL and API key

### Creating an API Key

1. Log into your StorageHub web UI
2. Navigate to **Settings** → **API Keys**
3. Create a new key with `read` and `search` scopes
4. Copy the key (starts with `shub_`)

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| URL | — | StorageHub server URL (e.g., `http://storagehub.local`) |
| API Key | — | API key with `read` and `search` scopes |
| Scan Interval | 300 | Polling interval in seconds (60-3600) |

## Entities

The integration creates minimal entities to avoid clutter:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.storagehub_total_items` | Sensor | Total inventory count |
| `sensor.storagehub_overdue_reminders` | Sensor | Overdue reminder count |
| `binary_sensor.storagehub_connected` | Binary Sensor | API connectivity status |
| `binary_sensor.storagehub_has_overdue_reminders` | Binary Sensor | True if any reminders overdue |

### Sensor Attributes

The sensors include detailed attributes for dashboards:

**Total Items Sensor:**
- `total_locations` - Number of storage locations
- `total_containers` - Number of containers
- `total_photos` - Total photos uploaded
- `total_tags` - Number of tags
- `items_needing_review` - Items flagged for review
- `items_by_condition` - Breakdown by condition (good, fair, damaged, needs_repair)
- `items_by_season` - Breakdown by season (winter, summer, etc.)

**Overdue Reminders Sensor:**
- `total_reminders` - Total reminder count
- `pending_reminders` - Pending reminder count
- `due_today` - Reminders due today
- `due_this_week` - Reminders due this week
- `reminders_by_type` - Breakdown by type

## Services

### storagehub.search

Search for items in your inventory. Returns results that can be used in automations.

```yaml
service: storagehub.search
data:
  query: "winter jacket"
  limit: 10
response_variable: search_results
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Red Winter Jacket",
      "description": "Size M, waterproof",
      "container_name": "Winter Clothes Box",
      "location_name": "Garage",
      "condition": "good",
      "tags": ["clothing", "winter"]
    }
  ],
  "total_count": 1,
  "query": "winter jacket"
}
```

### storagehub.get_container

Look up a container by QR code. Useful for NFC tag automations.

```yaml
service: storagehub.get_container
data:
  qr_code: "SH-ABC123"
response_variable: container
```

### storagehub.refresh

Force an immediate data refresh.

```yaml
service: storagehub.refresh
```

## Lovelace Card

### Basic Configuration

```yaml
type: custom:storagehub-card
title: StorageHub
storagehub_url: http://storagehub.local
```

### Full Configuration

```yaml
type: custom:storagehub-card
title: My Inventory
storagehub_url: http://storagehub.local
show_stats: true
show_reminders: true
max_results: 15
debounce_ms: 300
```

| Option | Default | Description |
|--------|---------|-------------|
| `title` | StorageHub | Card title |
| `storagehub_url` | — | URL for deep links (click to open items) |
| `show_stats` | true | Show item/reminder counts |
| `show_reminders` | true | Show overdue reminder count |
| `max_results` | 10 | Maximum search results |
| `debounce_ms` | 300 | Search debounce delay |

## Automation Examples

### Voice Assistant - Find Item

```yaml
automation:
  - alias: "Find Item Voice Command"
    trigger:
      - platform: conversation
        command: "where is my {item}"
    action:
      - service: storagehub.search
        data:
          query: "{{ trigger.slots.item }}"
          limit: 1
        response_variable: results
      - service: tts.speak
        target:
          entity_id: media_player.living_room
        data:
          message: >
            {% if results.items | length > 0 %}
              Found {{ results.items[0].name }} in
              {{ results.items[0].container_name }} at
              {{ results.items[0].location_name }}.
            {% else %}
              Sorry, I couldn't find that item.
            {% endif %}
```

### NFC Tag - Container Contents

```yaml
automation:
  - alias: "Storage Box NFC Scan"
    trigger:
      - platform: tag
        tag_id: garage-box-01
    action:
      - service: storagehub.get_container
        data:
          qr_code: "SH-GARAGE01"
        response_variable: container
      - service: notify.mobile_app
        data:
          title: "{{ container.name }}"
          message: "{{ container.item_count }} items at {{ container.location_name }}"
          data:
            url: "http://storagehub.local/containers/{{ container.id }}"
```

### Daily Reminder Notification

```yaml
automation:
  - alias: "StorageHub Daily Reminder"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.storagehub_overdue_reminders
        above: 0
    action:
      - service: notify.mobile_app
        data:
          title: "StorageHub Reminders"
          message: >
            You have {{ states('sensor.storagehub_overdue_reminders') }} overdue
            and {{ state_attr('sensor.storagehub_overdue_reminders', 'due_today') }} due today.
```

### Seasonal Alert

```yaml
automation:
  - alias: "Winter Clothes Reminder"
    trigger:
      - platform: template
        value_template: "{{ now().month == 10 and now().day == 1 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Time for Winter Clothes!"
          message: >
            You have {{ state_attr('sensor.storagehub_total_items', 'items_by_season').winter | default(0) }}
            winter items in storage.
```

## Troubleshooting

### Cannot Connect

- Verify StorageHub URL is accessible from Home Assistant
- Check firewall rules if running in Docker
- Try accessing `http://storagehub.local/api/ha/status` directly

### Invalid Auth

- Verify API key is correct and active
- Ensure key has `read` and `search` scopes
- Check key hasn't expired

### Sensors Not Updating

- Check the scan interval in integration options
- Use `storagehub.refresh` service to force update
- Check Home Assistant logs for errors

### Card Not Loading

- Verify `storagehub-card.js` is in the correct location
- Clear browser cache
- Check browser console for JavaScript errors

## Development

### Building the Card

```bash
cd storagehub-card
npm install
npm run build
```

### Running Tests

```bash
# Integration tests (requires Home Assistant dev environment)
pytest tests/
```

## License

MIT License - see LICENSE file for details.
