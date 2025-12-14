# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom integration for StorageHub, a self-hosted personal inventory management system. Search-first design focused on "where is my X?" use case.

## Project Structure

```
ha-storagehunters/
├── custom_components/storagehub/   # HA integration
│   ├── __init__.py                 # Entry setup, platform forwarding
│   ├── manifest.json               # Integration metadata
│   ├── const.py                    # Constants, API endpoints
│   ├── api.py                      # Async API client (aiohttp)
│   ├── config_flow.py              # UI configuration wizard
│   ├── coordinator.py              # DataUpdateCoordinator
│   ├── sensor.py                   # total_items, overdue_reminders
│   ├── binary_sensor.py            # connected, has_overdue_reminders
│   ├── services.py                 # search, get_container, refresh
│   ├── services.yaml               # Service definitions
│   ├── strings.json                # UI strings
│   └── translations/en.json
├── storagehub-card/                # Lovelace card (TypeScript/Lit)
│   ├── src/
│   │   ├── storagehub-card.ts      # Main card component
│   │   ├── types.ts                # TypeScript interfaces
│   │   └── styles.ts               # CSS styles
│   ├── package.json
│   ├── tsconfig.json
│   └── rollup.config.js
├── documentation/                   # StorageHub API docs
└── hacs.json                       # HACS configuration
```

## StorageHub API

Endpoints at `/api/ha/*` with `X-API-Key: shub_xxx` header:

| Endpoint | Description |
|----------|-------------|
| `GET /api/ha/status` | System status (no auth) |
| `GET /api/ha/stats` | Inventory statistics |
| `GET /api/ha/reminders` | Reminder counts |
| `GET /api/ha/search?q=query` | Semantic search |
| `GET /api/ha/containers/qr/{code}` | QR code lookup |

See `documentation/API_DOCUMENTATION.md` for full reference.

## Development Commands

```bash
# Backend - lint and type check
ruff check custom_components/storagehub
ruff format custom_components/storagehub
mypy custom_components/storagehub

# Frontend - build card
cd storagehub-card
npm install
npm run build        # Production build
npm run watch        # Development with watch

# Testing
pytest tests/
pytest tests/test_config_flow.py -v
```

## Key Patterns

- **Config Flow**: Validates `/api/ha/status` (no auth) then `/api/ha/stats` (with auth)
- **Coordinator**: Polls stats + reminders every 5 minutes (configurable)
- **Services**: Use `SupportsResponse.ONLY` for search/get_container
- **Card**: Debounced search (300ms), calls `storagehub.search` service

## Home Assistant Conventions

- All I/O uses `async`/`await` with `aiohttp`
- Entities inherit `CoordinatorEntity`
- Entity descriptions use frozen dataclasses
- Services return responses via `response_variable` in automations
