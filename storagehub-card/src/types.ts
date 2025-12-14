/**
 * Type definitions for StorageHub card.
 */

/**
 * Home Assistant instance interface.
 */
export interface HomeAssistant {
  states: Record<string, HassEntity>;
  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: { entity_id?: string | string[] },
    returnResponse?: boolean
  ): Promise<unknown>;
  connection: {
    subscribeEvents(
      callback: (event: unknown) => void,
      eventType: string
    ): Promise<() => void>;
  };
  language: string;
  themes: {
    darkMode: boolean;
  };
}

/**
 * Home Assistant entity state.
 */
export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
}

/**
 * Search result item from StorageHub API.
 */
export interface SearchResultItem {
  id: string;
  name: string;
  description: string | null;
  container_id: string;
  container_name: string;
  location_name: string;
  condition: "good" | "fair" | "damaged" | "needs_repair";
  seasonal: string | null;
  value_estimate: number | null;
  primary_image_url: string | null;
  tags: string[];
}

/**
 * Search service response.
 */
export interface SearchResponse {
  items: SearchResultItem[];
  total_count: number;
  query: string;
}

/**
 * Container lookup response.
 */
export interface ContainerResponse {
  id: string;
  name: string;
  qr_code: string;
  location_name: string;
  item_count: number;
  items: SearchResultItem[];
}

/**
 * Card configuration.
 */
export interface StorageHubCardConfig {
  type: string;
  title?: string;
  storagehub_url?: string;
  show_stats?: boolean;
  show_reminders?: boolean;
  max_results?: number;
  debounce_ms?: number;
}

/**
 * Lovelace card interface.
 */
export interface LovelaceCard extends HTMLElement {
  hass?: HomeAssistant;
  setConfig(config: StorageHubCardConfig): void;
  getCardSize?(): number;
}

/**
 * Custom cards window declaration.
 */
declare global {
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description: string;
      preview?: boolean;
    }>;
  }
}
