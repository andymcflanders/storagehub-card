// Thin wrappers around HA's service-call and event-subscribe APIs.

import type {
  HassEvent,
  HomeAssistant,
  SearchLiteResponse,
  SearchResponse,
} from "./types";

export async function searchLite(
  hass: HomeAssistant,
): Promise<SearchLiteResponse> {
  const result = await hass.callService(
    "storagehub",
    "search_lite",
    {},
    undefined,
    false,
    true,
  );
  return result.response as SearchLiteResponse;
}

export async function searchSemantic(
  hass: HomeAssistant,
  query: string,
  limit: number,
): Promise<SearchResponse> {
  const result = await hass.callService(
    "storagehub",
    "semantic_search",
    { query, limit },
    undefined,
    false,
    true,
  );
  return result.response as SearchResponse;
}

// Subscribe to state-change events on the diagnostic ETag sensor. HA fires
// state_changed for every entity, so we filter client-side. Returns an
// unsubscribe callback.
export async function subscribeIndexEtag(
  hass: HomeAssistant,
  entityId: string,
  onChange: () => void,
): Promise<() => void> {
  return hass.connection.subscribeEvents<HassEvent>((event) => {
    if (event.data.entity_id === entityId) onChange();
  }, "state_changed");
}
