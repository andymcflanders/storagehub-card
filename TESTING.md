# StorageHub Card — manual UI test matrix

The card has no unit tests (per `PLAN.md` Locked Decisions). Walk this matrix
against a live HA instance whenever the card or its services change.

## Setup

1. Build the card and copy `dist/storagehub-card.js` into your HA at
   `/config/www/storagehub-card.js`, OR install via HACS as a frontend
   plugin.
2. Settings → Dashboards → Resources → Add Resource:
   - URL: `/local/storagehub-card.js` (or the HACS path)
   - Resource type: JavaScript Module
3. Enable the diagnostic sensor: Settings → Devices & Services → StorageHub
   → entities → toggle **Index ETag** on. Without this, the card still
   works but won't auto-refresh until the dashboard is reloaded.
4. Add to a dashboard:
   ```yaml
   type: custom:storagehub-card
   storagehub_url: http://192.168.200.13   # optional but enables click-through
   ```

## Cases

1. **Empty inventory** — fresh install with zero items.
   Expect: search input renders, "No items in inventory yet." empty state.
2. **Instant local hit** — type a single character (e.g. `j`).
   Expect: nothing yet (we require ≥2 chars). Type one more (`ja`).
   Expect: matching items appear within one frame, no network call.
3. **Local + semantic merge** — type `Sverre Buk`, pause typing for ~500ms.
   Expect: local hits render immediately. After ~400ms, "Smart matches"
   header appears below with extra hits (cross-language, AI matches the
   local index missed). Local IDs are de-duplicated from the smart list.
4. **Enter cancels debounce** — type `bike`, press Enter mid-typing.
   Expect: semantic call fires immediately, before the debounce expires.
5. **Click-through** — with `storagehub_url` configured, click any row.
   Expect: opens `<storagehub_url>/items/<id>` in a new tab.
6. **No `storagehub_url`** — remove the config, click a row.
   Expect: nothing happens. Cursor is default, not pointer.
7. **Live index refresh** — call `storagehub.refresh_index` from Developer
   Tools while the card is open with a query that has matches.
   Expect: the card re-fetches the lite index without a page reload. If
   you've edited an item to change its container/owner, the new value
   shows up in matches without reload.
8. **Network error during semantic** — block the backend (e.g. stop the
   container) after the local index loaded.
   Expect: local hits still render. Error banner appears above where the
   "Smart matches" section would be: "Smart search unavailable: …".
9. **Bad config** — set `semantic_debounce_ms: -1` in card YAML.
   Expect: Lovelace shows the validation error from `setConfig`.
10. **Mobile / companion app** — open the dashboard on iOS/Android.
    Expect: layout doesn't break; shadow DOM scoping holds; tap-through
    works the same as click.
11. **Large inventory** — test against an account with >1000 items.
    Expect: typing latency stays under one frame (16ms). Profile via
    Chrome DevTools → Performance if uncertain.
12. **ETag sensor disabled** — disable the **Index ETag** sensor and
    reload.
    Expect: card still works, but won't auto-refresh after
    `storagehub.refresh_index`. (Document this for users who skip step 3
    of setup.)

## Card development workflow

```bash
cd storagehub-card
npm install
npm run watch    # rebuilds dist/ on file changes
```

In your HA, reference the file via Resources as above. Hard-refresh the
dashboard (Ctrl-Shift-R / Cmd-Shift-R) after each rebuild — Lovelace caches
resource files aggressively.

For one-off changes that don't need a watch loop:

```bash
npm run build    # one-shot production build
```

The committed `dist/storagehub-card.js` is what HACS users get. Always
commit a fresh build along with source changes.
