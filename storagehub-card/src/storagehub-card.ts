/**
 * StorageHub Card - Search-first Lovelace card for StorageHub inventory.
 */

import { LitElement, html, nothing, PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  HomeAssistant,
  StorageHubCardConfig,
  SearchResultItem,
  SearchResponse,
} from "./types";
import { styles } from "./styles";

const CARD_VERSION = "1.0.0";

// Log card info for debugging
console.info(
  `%c STORAGEHUB-CARD %c ${CARD_VERSION} `,
  "color: white; background: #03a9f4; font-weight: bold;",
  "color: #03a9f4; background: white; font-weight: bold;"
);

@customElement("storagehub-card")
export class StorageHubCard extends LitElement {
  // Home Assistant instance
  @property({ attribute: false }) public hass!: HomeAssistant;

  // Card configuration
  @state() private _config!: StorageHubCardConfig;

  // Search state
  @state() private _searchQuery = "";
  @state() private _searchResults: SearchResultItem[] = [];
  @state() private _isSearching = false;
  @state() private _searchError: string | null = null;
  @state() private _hasSearched = false;

  // Debounce timer
  private _debounceTimer?: ReturnType<typeof setTimeout>;

  static styles = styles;

  /**
   * Set card configuration.
   */
  public setConfig(config: StorageHubCardConfig): void {
    if (!config) {
      throw new Error("Invalid configuration");
    }

    this._config = {
      title: "StorageHub",
      show_stats: true,
      show_reminders: true,
      max_results: 10,
      debounce_ms: 300,
      ...config,
    };
  }

  /**
   * Return card size for masonry layout.
   */
  public getCardSize(): number {
    return 3;
  }

  /**
   * Get stub configuration for card picker.
   */
  public static getStubConfig(): StorageHubCardConfig {
    return {
      type: "custom:storagehub-card",
      title: "StorageHub",
      show_stats: true,
      show_reminders: true,
    };
  }

  /**
   * Render the card.
   */
  protected render() {
    if (!this.hass || !this._config) {
      return html``;
    }

    const totalItemsEntity = this.hass.states["sensor.storagehub_total_items"];
    const overdueEntity =
      this.hass.states["sensor.storagehub_overdue_reminders"];
    const connectedEntity =
      this.hass.states["binary_sensor.storagehub_connected"];

    const isConnected = connectedEntity?.state === "on";
    const totalItems = totalItemsEntity?.state ?? "—";
    const overdueCount = parseInt(overdueEntity?.state ?? "0", 10);

    return html`
      <ha-card>
        <div class="card-header">
          <div class="header-left">
            <span class="title">${this._config.title}</span>
          </div>
          ${connectedEntity
            ? html`
                <ha-icon
                  class="status-icon ${isConnected ? "online" : "offline"}"
                  icon="${isConnected ? "mdi:cloud-check" : "mdi:cloud-off-outline"}"
                  title="${isConnected ? "Connected" : "Disconnected"}"
                ></ha-icon>
              `
            : nothing}
        </div>

        <div class="card-content">
          <!-- Search Input -->
          ${this._renderSearchInput()}

          <!-- Search Results -->
          ${this._hasSearched ? this._renderSearchResults() : nothing}

          <!-- Stats Section (hidden when showing results) -->
          ${!this._hasSearched && this._config.show_stats
            ? this._renderStats(totalItems, overdueCount)
            : nothing}

          <!-- Link to StorageHub -->
          ${this._config.storagehub_url
            ? html`
                <a
                  href="${this._config.storagehub_url}"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="storagehub-link"
                >
                  <ha-icon icon="mdi:open-in-new"></ha-icon>
                  Open StorageHub
                </a>
              `
            : nothing}
        </div>
      </ha-card>
    `;
  }

  /**
   * Render search input.
   */
  private _renderSearchInput() {
    return html`
      <div class="search-container">
        <div class="search-input-wrapper">
          <ha-icon icon="mdi:magnify"></ha-icon>
          <input
            type="text"
            class="search-input"
            placeholder="Search inventory..."
            .value=${this._searchQuery}
            @input=${this._handleSearchInput}
            @keydown=${this._handleKeyDown}
          />
          ${this._isSearching
            ? html`
                <ha-circular-progress
                  class="search-spinner"
                  indeterminate
                  size="small"
                ></ha-circular-progress>
              `
            : nothing}
          ${this._searchQuery && !this._isSearching
            ? html`
                <button
                  class="clear-button"
                  @click=${this._clearSearch}
                  title="Clear search"
                >
                  <ha-icon icon="mdi:close"></ha-icon>
                </button>
              `
            : nothing}
        </div>
        ${!this._hasSearched
          ? html`<div class="search-hint">
              Type at least 2 characters to search
            </div>`
          : nothing}
      </div>
    `;
  }

  /**
   * Render search results.
   */
  private _renderSearchResults() {
    if (this._searchError) {
      return html`
        <div class="error-message">
          <ha-icon icon="mdi:alert-circle"></ha-icon>
          ${this._searchError}
        </div>
      `;
    }

    if (this._searchResults.length === 0 && !this._isSearching) {
      return html`
        <div class="no-results">
          <ha-icon icon="mdi:magnify-close"></ha-icon>
          <div>No items found for "${this._searchQuery}"</div>
        </div>
      `;
    }

    return html`
      <div class="search-results">
        ${this._searchResults.map((item) => this._renderResultItem(item))}
      </div>
    `;
  }

  /**
   * Render a single search result item.
   */
  private _renderResultItem(item: SearchResultItem) {
    const imageUrl = item.primary_image_url
      ? this._config.storagehub_url
        ? `${this._config.storagehub_url}${item.primary_image_url}`
        : item.primary_image_url
      : null;

    return html`
      <div class="result-item" @click=${() => this._handleResultClick(item)}>
        ${imageUrl
          ? html`<img class="item-image" src="${imageUrl}" alt="" />`
          : html`
              <div class="item-image-placeholder">
                <ha-icon icon="mdi:package-variant-closed"></ha-icon>
              </div>
            `}
        <div class="item-details">
          <div class="item-name">${item.name}</div>
          <div class="item-location">
            <ha-icon icon="mdi:archive"></ha-icon>
            ${item.container_name}
            <span class="location-separator">•</span>
            <ha-icon icon="mdi:map-marker"></ha-icon>
            ${item.location_name}
          </div>
          ${item.condition !== "good"
            ? html`
                <span class="item-condition condition-${item.condition}">
                  ${item.condition.replace("_", " ")}
                </span>
              `
            : nothing}
        </div>
      </div>
    `;
  }

  /**
   * Render stats section.
   */
  private _renderStats(totalItems: string, overdueCount: number) {
    return html`
      <div class="stats-section">
        <div
          class="stat-item"
          @click=${() => this._openStorageHub("/items")}
          title="View all items"
        >
          <ha-icon icon="mdi:package-variant"></ha-icon>
          <span class="stat-value">${totalItems}</span>
          <span class="stat-label">Items</span>
        </div>
        ${this._config.show_reminders
          ? html`
              <div
                class="stat-item ${overdueCount > 0 ? "warning" : ""}"
                @click=${() => this._openStorageHub("/reminders")}
                title="View reminders"
              >
                <ha-icon
                  icon="${overdueCount > 0 ? "mdi:bell-alert" : "mdi:bell-outline"}"
                ></ha-icon>
                <span class="stat-value">${overdueCount}</span>
                <span class="stat-label">Overdue</span>
              </div>
            `
          : nothing}
      </div>
    `;
  }

  /**
   * Handle search input changes.
   */
  private _handleSearchInput(e: Event): void {
    const input = e.target as HTMLInputElement;
    this._searchQuery = input.value;
    this._searchError = null;

    // Clear previous debounce timer
    if (this._debounceTimer) {
      clearTimeout(this._debounceTimer);
    }

    if (this._searchQuery.length >= 2) {
      this._debounceTimer = setTimeout(() => {
        this._performSearch();
      }, this._config.debounce_ms);
    } else {
      this._searchResults = [];
      this._hasSearched = false;
    }
  }

  /**
   * Handle keyboard events.
   */
  private _handleKeyDown(e: KeyboardEvent): void {
    if (e.key === "Escape") {
      this._clearSearch();
    } else if (e.key === "Enter" && this._searchQuery.length >= 2) {
      // Immediate search on Enter
      if (this._debounceTimer) {
        clearTimeout(this._debounceTimer);
      }
      this._performSearch();
    }
  }

  /**
   * Clear search and reset state.
   */
  private _clearSearch(): void {
    this._searchQuery = "";
    this._searchResults = [];
    this._searchError = null;
    this._hasSearched = false;

    if (this._debounceTimer) {
      clearTimeout(this._debounceTimer);
    }
  }

  /**
   * Perform search via Home Assistant service.
   */
  private async _performSearch(): Promise<void> {
    if (!this._searchQuery || this._searchQuery.length < 2) {
      return;
    }

    this._isSearching = true;
    this._searchError = null;
    this._hasSearched = true;

    try {
      const response = (await this.hass.callService(
        "storagehub",
        "search",
        {
          query: this._searchQuery,
          limit: this._config.max_results,
        },
        undefined,
        true // return_response
      )) as SearchResponse;

      this._searchResults = response?.items ?? [];
    } catch (error) {
      console.error("StorageHub search error:", error);
      this._searchError = "Search failed. Check connection.";
      this._searchResults = [];
    } finally {
      this._isSearching = false;
    }
  }

  /**
   * Handle click on search result.
   */
  private _handleResultClick(item: SearchResultItem): void {
    if (this._config.storagehub_url) {
      window.open(
        `${this._config.storagehub_url}/items/${item.id}`,
        "_blank",
        "noopener,noreferrer"
      );
    }
  }

  /**
   * Open StorageHub web UI to a specific path.
   */
  private _openStorageHub(path: string): void {
    if (this._config.storagehub_url) {
      window.open(
        `${this._config.storagehub_url}${path}`,
        "_blank",
        "noopener,noreferrer"
      );
    }
  }
}

// Register card for picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "storagehub-card",
  name: "StorageHub Card",
  description: "Search your StorageHub inventory",
  preview: true,
});

// TypeScript declaration for custom element
declare global {
  interface HTMLElementTagNameMap {
    "storagehub-card": StorageHubCard;
  }
}
