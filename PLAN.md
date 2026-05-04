# HA Integration Reboot Plan

Search-first rebuild of the StorageHub Home Assistant integration. The
product surface is two things:

1. A Lovelace card with as-you-type search and a semantic fallback.
2. HA Assist voice queries answered with structured natural-language
   responses.

Everything else (reminders, triage, outgrown, owner-suggestion review,
per-location dashboards) is out of scope for the reboot.

## Architecture

**Two-tier search.** Card pre-loads a lite index from the backend
(`/api/ha/items/index`, backend issue 2) and substring-filters in JS
on every keystroke. After ~400ms of no typing, or on Enter, the card
fires `storagehub.search` against the backend's semantic search
(backend issue 1) and merges those hits below the local matches under
a "smart matches" header.

**Voice.** HA Assist routes utterances to a custom intent handler
shipped by the integration. The handler calls the same semantic
search service, picks the top result, and renders a natural-language
response template. Custom sentences are registered for English and
Norwegian.

**Connection heartbeat.** A single sensor (`total_items`) and a binary
sensor (`connected`) are populated from `/api/ha/stats` and
`/api/ha/status` on a 5-minute coordinator. They exist solely so users
can verify the integration is healthy from the UI.

## File structure

```
custom_components/storagehub/
├── __init__.py              # Setup, entry.runtime_data, platform forwarding
├── manifest.json            # Real URLs, codeowners, version 2.0.0
├── const.py                 # Domain, defaults, scopes
├── api.py                   # Async API client (status, stats, search, index)
├── coordinator.py           # Heartbeat + index coordinators
├── config_flow.py           # User + reauth + reconfigure
├── sensor.py                # total_items only
├── binary_sensor.py         # connected only
├── services.py              # search, search_lite, get_container
├── services.yaml
├── conversation.py          # IntentHandler for HA Assist
├── strings.json
└── translations/
    ├── en.json
    └── no.json

storagehub-card/
├── src/
│   ├── storagehub-card.ts   # Card component (Lit)
│   ├── search-index.ts      # Local index + ranked matcher
│   ├── api.ts               # Thin service-call wrapper
│   ├── types.ts
│   └── styles.ts
├── package.json
├── tsconfig.json
└── rollup.config.js

tests/
├── conftest.py              # HA test fixtures, aiohttp mock
├── test_api.py              # API client unit tests
├── test_config_flow.py      # User / reauth / reconfigure flows
├── test_coordinator.py      # Heartbeat + ETag handling
├── test_search_service.py   # Service call shapes
└── test_conversation.py     # Intent handler responses

PLAN.md                       # this file
BACKEND_REQUIREMENTS.md       # backend-side spec
README.md                     # rewritten near end of phase 4
CLAUDE.md                     # rewritten in phase 0
hacs.json                     # validated/refreshed in phase 4
```

## Phased rollout

The backend is shipping in order **1 → 3 → 2**. The HA side can be
built largely in parallel: phases 0–2 depend only on what already
exists or what backend issue 1 unblocks; phase 3 needs backend issue 2.

### Phase 0 — Skeleton (no backend dependency)

Build the modern HA-pattern skeleton so everything else has a place
to land.

- `manifest.json`: real URLs, `codeowners: ["@andersjh"]` (TBC),
  version `2.0.0`, `iot_class: local_polling`.
- `const.py`: `DOMAIN`, `DEFAULT_HEARTBEAT_INTERVAL = 300`,
  `DEFAULT_INDEX_INTERVAL = 1800`, scope constants.
- `api.py`: `StorageHubApiClient` with `async_get_status`,
  `async_get_stats`. ETag-aware `async_get_index` stub returning
  `None` until phase 3.
- `coordinator.py`: `HeartbeatCoordinator` polling status+stats every
  5 min. Stores `total_items: int`, `instance_id: str | None`,
  `connected: bool`.
- `__init__.py`: uses `entry.runtime_data` (no `hass.data[DOMAIN]`).
  Forwards `sensor` and `binary_sensor` platforms.
- `config_flow.py`: user step (host + API key, validates `/status`
  then `/stats`). Sets `unique_id` from `instance_id` if backend
  issue 3 has shipped, else from host. Reauth and reconfigure steps
  scaffolded but minimal.
- `sensor.py`: `total_items` (`mdi:package-variant`, measurement,
  unit "items").
- `binary_sensor.py`: `connected` (`CONNECTIVITY` device class).
- `tests/`: scaffolding, one happy-path test for the API client and
  one for the user config flow.

**Acceptance:** Integration installable via Settings → Integrations.
After config, `sensor.storagehub_total_items` populates with the
correct count and `binary_sensor.storagehub_connected` is `on`.

### Phase 1 — Semantic search service (depends on backend issue 1)

- Add `async_search` to `api.py`.
- Register `storagehub.search` service in `services.py`,
  `SupportsResponse.ONLY`, schema validates `query` (≥2 chars) and
  `limit` (1–50, default 20).
- `services.yaml` with field descriptions for the UI.
- Service dispatches to **a specific** config entry (via
  `entry_id` field, optional, defaults to first). Multi-instance
  ready.
- Translates API errors into `HomeAssistantError` /
  `ServiceValidationError` with `translation_key` references.

**Acceptance:** Developer Tools → Services → `storagehub.search`
with `{query: "jakke"}` returns a structured response with `items`,
`total_count`, `query`. Calling with `{query: "Sverre jakke"}` after
backend issue 1 ships returns owner-filtered results.

### Phase 2 — Voice / Conversation intent (depends on phase 1)

Wire HA Assist to the search service.

- `conversation.py`: implement `IntentHandler` subclass
  `FindItemIntentHandler`. Slot: `item` (open string). The handler
  calls the search service, formats top result as natural language,
  and falls back to a multi-result summary if scores are close.
- Register the intent in `__init__.py:async_setup_entry` via
  `intent.async_register(hass, FindItemIntentHandler())`.
- Custom sentences shipped under
  `translations/<lang>.json → conversation` (HA's preferred location
  for integration-bundled sentences). Initial coverage:
  - English: `"where is {item}"`, `"find {item}"`, `"show me {item}"`,
    `"locate {item}"`
  - Norwegian: `"hvor er {item}"`, `"finn {item}"`, `"hvor ligger
    {item}"`
- Response templates render structured data — *"{name} is in **{
  container}** in the **{location}**"*. Owner is appended only if
  present and the query mentioned a person.
- No-result and error paths have their own templates.

**Acceptance:** From HA Assist debug, *"Where is the yellow jacket?"*
→ *"The yellow rain jacket is in the Winter box in the Attic."*
*"Hvor er Sverres ullgenser?"* → *"Sverres rød ullgenser ligger i
boksen Vinter på loftet."* Failure path: *"I couldn't find a Foo in
your inventory."*

### Phase 3 — Lite index + card rebuild (depends on backend issue 2)

The big one. Everything search-as-you-type lands here.

**Integration side:**
- `IndexCoordinator`: separate coordinator with 30-min cadence, calls
  `/api/ha/items/index` with `If-None-Match`. Stores last ETag and
  the deserialized list. On 304, no-op.
- `async_get_index` on the API client returns
  `(etag, list[IndexEntry] | None)` — `None` payload on 304.
- `storagehub.search_lite` service: returns the current cached index
  to the caller. Includes `etag` so callers can short-circuit. No
  scoring on the integration side — the card scores client-side.
- `storagehub.refresh_index` service: forces a coordinator refresh
  (debug aid).

**Card side (full rewrite):**
- `search-index.ts`: builds an in-memory index from the lite payload.
  Per-token substring matching with field weights:
  `name=10, owner_name=6, container_name=4, location_name=3,
  ai_names=8`. Starts-with bonus 1.5×, word-boundary bonus 1.2×.
- `storagehub-card.ts`: on connect, calls `storagehub.search_lite`,
  feeds index. Subscribes to coordinator updates via the websocket
  API to refresh when ETag changes. Renders results as the user types
  (no debounce on local hits). After 400ms of no typing OR on Enter,
  fires `storagehub.search` and merges semantic results below local
  hits under a separator.
- Result rendering: per row, *"{name} → {container} in {location}"*
  with optional owner pill. Click opens the StorageHub web UI to the
  item detail page (configurable base URL).
- Card config schema: `storagehub_url` (string, optional),
  `entry_id` (string, optional, for multi-instance),
  `max_local_results` (int, default 10),
  `max_semantic_results` (int, default 10),
  `semantic_debounce_ms` (int, default 400).

**Acceptance:**
- Card loads, index downloads (one-time, gzipped), filters appear
  within one frame of each keystroke.
- After typing pauses, smart matches section populates with extra
  hits (e.g. cross-language matches the local substring index missed).
- Navigating away and back reuses the cached index until ETag changes.
- Card works on a fresh install with zero YAML configuration.

### Phase 4 — Polish & ship

- Reauth flow exercised end-to-end (rotate API key on backend, HA
  prompts for new key).
- Reconfigure flow lets users change host without re-adding the
  integration (relies on backend issue 3's `instance_id`).
- HACS validation passes; `hacs.json` updated; `info.md` written.
- README rewritten: install via HACS, screenshots, voice examples.
- Tests fleshed out — target is ≥80% coverage on `api.py`,
  `coordinator.py`, `config_flow.py`, `conversation.py`. Card tested
  manually; no unit tests on the Lit component.
- `CLAUDE.md` updated to reflect the new structure.

## Sequencing & critical path

```
Backend:    [Issue 1]──────[Issue 3]────────────────[Issue 2]──────────
                  │             │                        │
HA:    [Phase 0]──┴─[Phase 1]──┴─[Phase 2]              [Phase 3]──[Phase 4]
              │           │            │                     │
              │           │            └── Phase 2 needs Phase 1 only
              │           └── Phase 1 callable as soon as Issue 1 ships
              └── Phase 0 has no backend dependency
```

Phases 0, 1, 2 can land before backend issue 2 is done. Phase 3 is
the long pole; phase 4 follows directly.

## Locked decisions

1. **Codeowner.** `@andersjh`.
2. **Voice languages.** English + Norwegian at launch. Sentences
   live in `translations/<lang>.json` so adding a language later is
   data, not code.
3. **Card distribution.** Pre-built `dist/storagehub-card.js`
   committed to the repo.
4. **Multi-instance.** Out of scope. Single config entry only —
   services and card assume one StorageHub per HA.
5. **Test framework.** `pytest-homeassistant-custom-component`.
   Standard for HA custom integrations; the heavy dependencies are
   dev-time only and the `hass`/`MockConfigEntry` fixtures save us
   from rebuilding HA's testing scaffolding ourselves.
6. **Release.** One bundled v2.0 — phases 0–4 ship together, no
   alpha cut.

## Risks / unknowns

- **HA voice intent registration API has churned.** I'll verify the
  current pattern (likely `intent.async_register` + sentences in
  `translations/<lang>.json` under a `conversation` key) before
  starting phase 2. If the API has moved further, the phase 2 design
  may shift; the user-facing behavior stays the same.
- **ETag with HA's `async_get_clientsession`.** Need to confirm the
  shared session doesn't strip conditional-request headers. Likely
  fine; will verify with a smoke test in phase 3.
- **Card cache across devices.** Each browser/companion app pulls its
  own copy. For inventories under ~5k items the per-load gzip cost is
  trivial; if it ever grows, we add IndexedDB caching. Not designing
  for that now.
- **Owner pill rendering when many household members exist.** UX
  decision deferred to phase 3 implementation; will mock and ask.
