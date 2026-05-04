# Backend Requirements for HA Integration Reboot

Hand this to the StorageHub backend agent. These are the changes the
Home Assistant integration needs in order to deliver a search-first UX:

- A Lovelace card with as-you-type filtering (sub-50ms per keystroke)
- A semantic fallback when the user pauses typing or hits Enter
- Voice queries via HA Assist (e.g. *"Where is Sverre's yellow winter
  jacket?"* → *"In the Winter box in the Attic"*)

All three issues touch `backend/app/api/homeassistant.py`. None of them
should require a database migration.

## Summary

| # | Title | Priority | Blocker for |
|---|-------|----------|-------------|
| 1 | Add owner to `/api/ha/search` matching | High | Voice queries with possessive ("Sverre's …") |
| 2 | New `GET /api/ha/items/index` lite endpoint | High | Card's instant as-you-type filter |
| 3 | Add `instance_id` to `/api/ha/status` | Low | HA `unique_id` stability across host changes |

---

## Issue 1 — Add owner to semantic search

**Where:** `backend/app/api/homeassistant.py`, `search_items` function
(around line 603).

**Problem:** The current WHERE clause matches the query against
`Item.name`, `Item.description`, `Item.ai_names`, and `Item.ai_descriptions`,
but **not the owner's name**. A voice query like *"Where is Sverre's
jakke?"* therefore returns every jacket in the system, not just
Sverre's.

```python
# current (homeassistant.py:624)
where = (
    func.lower(Item.name).like(search_term)
    | func.lower(Item.description).like(search_term)
    | func.lower(func.cast(Item.ai_names, Text)).like(search_term)
    | func.lower(func.cast(Item.ai_descriptions, Text)).like(search_term)
)
```

**Suggested change:** Tokenize the query, strip possessive `'s` /
Norwegian `s` from each token, and require **all tokens** to match
**any field** (the owner name being one of them). This naturally lets
"Sverre jakke" find Sverre's jackets without a special owner param.

```python
# rough sketch — adapt to your style
tokens = [t.rstrip("'s").rstrip("s") for t in q.lower().split() if len(t) >= 2]
# join Item.owner so owner.name is searchable
query = select(Item).join(Item.owner, isouter=True)...
for token in tokens:
    pat = f"%{token}%"
    query = query.where(
        func.lower(Item.name).like(pat)
        | func.lower(Item.description).like(pat)
        | func.lower(func.cast(Item.ai_names, Text)).like(pat)
        | func.lower(func.cast(Item.ai_descriptions, Text)).like(pat)
        | func.lower(User.name).like(pat)
    )
```

**Acceptance criteria:**
- `GET /api/ha/search?q=Sverre+jakke` returns only items where owner
  name contains "Sverre" AND name/description/ai\_\* contains "jakke".
- `GET /api/ha/search?q=Sverres+jakke` (possessive) behaves the same.
- Existing single-token queries (`?q=jakke`) still match all jackets.
- Watch out for the AI multi-language fields — the current cast-to-Text
  approach should keep working.

---

## Issue 2 — New `GET /api/ha/items/index` lite endpoint

**Why:** The HA Lovelace card needs to filter items as the user types,
with no per-keystroke network round-trip. The plan is to pre-load a
minimal index once on card load (and refresh occasionally), then
substring-filter in JavaScript. Calling `/api/ha/search` per keystroke
is too slow; pre-loading `/api/ha/items` is too heavy (it includes
images, tags, descriptions, owner objects, etc.).

**Suggested API:**

```
GET /api/ha/items/index
Headers:
  X-API-Key: shub_...
  If-None-Match: "<etag>"   (optional)

Response 200 OK:
Content-Type: application/json
ETag: "abc123"
Cache-Control: private, max-age=900

[
  {
    "id": "uuid",
    "name": "Red wool cardigan",
    "owner_name": "Sverre",            // null if no owner
    "container_name": "Winter Box",    // null if uncontained
    "location_name": "Attic",          // null if container has no location
    "ai_names": ["Rød ullgenser"]      // values only, all languages flattened
  },
  ...
]

Response 304 Not Modified:
(empty body, when If-None-Match matches current ETag)
```

**Required scope:** `read`.

**Implementation notes:**
- One SQL query, three LEFT JOINs (item → container → location, item →
  user). No `selectinload` of images, tags, or full container objects.
- `ai_names` is the JSONB dict's *values* concatenated into a list —
  the card doesn't care which language each name is in, it just wants
  searchable strings.
- ETag can be the `MAX(updated_at)` across `items`, `containers`,
  `locations`, `users` (whichever invalidates the cached index), hashed
  to keep it short. Simpler alternative: a monotonic counter bumped by
  any mutation.
- Enable gzip via the existing FastAPI middleware. Target wire size
  under 200 KB for a 10k-item inventory.

**Acceptance criteria:**
- Returns minimal item data for *all* items the API key can see.
- Returns `ETag`; returns 304 when client sends matching `If-None-Match`.
- Response under 1 MB ungzipped for 10k items; under 200 KB gzipped.
- No image URLs, no tag arrays, no descriptions — keep it tight.
- 4xx if API key lacks `read` scope.

---

## Issue 3 — Add `instance_id` to `/api/ha/status`

**Why:** The HA integration currently uses the host URL as its
`unique_id`. If a user reconfigures from `http://storagehub.local` to
`https://storagehub.example.com`, HA forks a new config entry instead
of updating the existing one (orphaning all entities, history, and
automations referencing the old entry). A stable instance UUID fixes
this — HA can detect "same instance, new URL" and migrate.

**Suggested change:** Add `instance_id: UUID` to the `SystemStatus`
response model (`homeassistant.py:34`). Generate once on first boot,
persist in the DB.

```python
class SystemStatus(BaseModel):
    status: str = "online"
    version: str = "1.0.0"
    api_version: str = "v1"
    name: str = "StorageHub"
    instance_id: str  # NEW — stable UUID, persisted in DB
```

**Storage:** A one-row `instance` table, or a row in an existing
settings/config table — whatever fits the existing pattern. Generate
on first boot, never rotate.

**Acceptance criteria:**
- `GET /api/ha/status` (still no auth) returns `instance_id` as a UUID
  string.
- The same UUID survives container restarts, image rebuilds, and HTTPS
  reconfiguration.
- The UUID changes only when the database is wiped.

---

## What's intentionally NOT on this list

- **Triage / outgrown / owner-suggestion endpoints in `/api/ha/*`.**
  Out of scope for the search-first reboot. Revisit later.
- **Webhooks / push events.** The integration will keep polling for
  the lightweight `total_items` heartbeat; real-time push isn't worth
  the complexity until search works well.
- **A "format the answer as natural language" flag on
  `/api/ha/search`.** HA templates can render *"in the Winter box in
  the Attic"* from the existing structured response.

---

## Testing the integration end-to-end

Once issues 1 and 2 ship, the HA agent will pull data with these calls.
A working setup means:

```bash
# Issue 3
curl http://storagehub.local/api/ha/status
# → {"status":"online", ..., "instance_id":"<uuid>"}

# Issue 2
curl -H "X-API-Key: shub_..." http://storagehub.local/api/ha/items/index
# → [{"id":"...","name":"...","owner_name":"...","container_name":"...","location_name":"...","ai_names":[...]}, ...]

curl -H "X-API-Key: shub_..." -H 'If-None-Match: "<etag>"' \
     http://storagehub.local/api/ha/items/index
# → 304 (when nothing changed)

# Issue 1
curl -H "X-API-Key: shub_..." \
     "http://storagehub.local/api/ha/search?q=Sverre+jakke"
# → only Sverre's jackets, not the household's
```
