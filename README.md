# StorageHub Card

A Lovelace card for the [StorageHub Home Assistant
integration](https://github.com/andymcflanders/ha-storagehunter).
Search your inventory as you type, with smart matches that bridge
synonyms and Norwegian/English translations.

## What it does

- **Instant local filter.** The card pre-loads a lite item index on
  connect and filters in JavaScript on every keystroke. No network
  round-trip per character.
- **Smart matches.** After a short pause, fires the integration's
  `semantic_search` service to catch synonym/translation matches the
  local substring filter missed (e.g. *"genser"* finds items literally
  named *"cardigan"*).
- **Thumbnails + owner pills.** Each row shows the item's primary
  photo (when available) and an owner pill if the item has one.
- **Click-through.** Configurable: clicking a row opens the StorageHub
  web UI to that item's detail page.
- **Live updates.** Subscribes to a diagnostic ETag sensor, so when
  inventory changes on the backend the card refreshes without a page
  reload.

## Requirements

1. A running [StorageHub](https://github.com/andymcflanders/storagehunters)
   backend.
2. The [ha-storagehunter integration](https://github.com/andymcflanders/ha-storagehunter)
   installed and configured in Home Assistant. The card calls
   services that the integration registers — it can't work
   standalone.

## Install via HACS (recommended)

1. **HACS** → ⋮ → **Custom repositories**
2. Add `andymcflanders/storagehub-card` as type **Dashboard**
3. Install **StorageHub Card** from the HACS list
4. **Restart Home Assistant** (or do a hard browser refresh — Lovelace
   caches resource files aggressively)

HACS usually registers the Lovelace resource for you. If it doesn't:

- **Settings** → **Dashboards** → **Resources** → **Add Resource**
- URL: `/hacsfiles/storagehub-card/storagehub-card.js`
- Type: **JavaScript Module**

## Install manually

1. Download `dist/storagehub-card.js` from the latest release
2. Copy it to `<config>/www/storagehub-card.js`
3. Add it as a Lovelace resource (URL `/local/storagehub-card.js`,
   type **JavaScript Module**)
4. Hard-refresh your dashboard

## Add it to a dashboard

```yaml
type: custom:storagehub-card
storagehub_url: http://storagehub.local
```

`storagehub_url` is optional but recommended — without it, click-through
is disabled and thumbnails won't load (image URLs are relative to your
StorageHub host, not Home Assistant). Use the same URL you configured
for the integration.

## Card configuration

| Option | Default | Description |
|---|---|---|
| `type` | — | Must be `custom:storagehub-card` |
| `storagehub_url` | — | StorageHub web UI base URL. Enables thumbnails and click-through. |
| `max_local_results` | `10` | Max instant-filter results (1–100) |
| `max_semantic_results` | `10` | Max smart-match results (1–50) |
| `semantic_debounce_ms` | `400` | Pause before the smart-match query fires (0–5000) |

## Enable live updates

The card refreshes automatically when inventory changes — but only if
the integration's diagnostic **Index ETag** sensor is enabled.

1. **Settings** → **Devices & Services** → **StorageHub**
2. Open the device, scroll to entities
3. Enable **Index ETag** (it's disabled by default)

Without this, the card still works but won't pick up new items until
you reload the dashboard.

## Login + click-through

Clicking a result opens the StorageHub web UI for that item. If you
aren't logged in, StorageHub redirects to its profile-select / login
page. Stay logged in to StorageHub in the same browser you use for
Home Assistant and click-through lands directly on the item.

## Troubleshooting

**Card shows "Could not load inventory index"** — the integration's
`storagehub.search_lite` service didn't return data. Usually means
the integration isn't configured, the entry isn't loaded, or
StorageHub is unreachable. Check **Settings** → **Devices & Services**
for the StorageHub integration's state.

**Thumbnails are missing** — set `storagehub_url` in the card config.
Image URLs from the backend are relative paths; they need a host to
load.

**Card doesn't auto-refresh after editing items** — enable the
**Index ETag** sensor (see above).

**Smart matches are empty for queries the StorageHub web UI matches**
— the backend's semantic search is synonym-based, not embedding-based.
If a query class consistently misses, file a follow-up against the
backend; extending the synonym dictionary is a small change.

## Development

```bash
git clone git@github.com:andymcflanders/storagehub-card.git
cd storagehub-card
npm install
npm run watch    # rebuilds dist/ on file changes
```

In your HA, point a Lovelace resource at the rebuilt file (via
`/local/` after copying, or symlink the dist file into your HA config's
`www/`). Hard-refresh after each rebuild.

For one-off production builds: `npm run build`. The committed
`dist/storagehub-card.js` is what HACS users get — always rebuild
before committing source changes.

There are no card unit tests; manual UI testing checklist lives in
[`TESTING.md`](TESTING.md).

## License

MIT.
