// Shapes mirroring the integration's Python dataclasses.

export interface IndexEntry {
  id: string;
  name: string;
  owner_name: string | null;
  container_name: string | null;
  location_name: string | null;
  ai_names: string[];
}

export interface SearchLiteResponse {
  etag: string | null;
  items: IndexEntry[];
  count: number;
}

export interface SearchResultItem {
  id: string;
  name: string;
  description: string | null;
  container_name: string | null;
  location_name: string | null;
  condition: string | null;
  seasonal: string | null;
  value_estimate: number | null;
  owner_name: string | null;
  primary_image_url: string | null;
  tags: string[];
}

export interface SearchResponse {
  items: SearchResultItem[];
  total_count: number;
  query: string;
}

// Lovelace card config. No `entry_id` — the integration is single-instance.
export interface StorageHubCardConfig {
  type: "custom:storagehub-card";
  storagehub_url?: string;
  max_local_results?: number;
  max_semantic_results?: number;
  semantic_debounce_ms?: number;
}

// Minimal shape of HA's HomeAssistant object surfaced to cards. The full type
// from `home-assistant-js-websocket` brings in too much for what we need.
export interface HomeAssistant {
  states: Record<string, { state: string; attributes: Record<string, unknown> }>;
  callService: (
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: unknown,
    notifyOnError?: boolean,
    returnResponse?: boolean,
  ) => Promise<{ response?: unknown }>;
  connection: {
    subscribeEvents: <T>(
      callback: (event: T) => void,
      eventType: string,
    ) => Promise<() => void>;
  };
}

export interface HassEvent {
  event_type: string;
  data: { entity_id?: string; new_state?: { state: string } | null };
}
