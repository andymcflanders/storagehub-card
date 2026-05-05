// StorageHub Lovelace card.
//
// On connect: pulls the lite item index via storagehub.search_lite, builds an
// in-memory matcher, subscribes to the diagnostic ETag sensor for cache
// invalidation. Local hits render synchronously per keystroke; semantic hits
// fire after a debounce or on Enter and merge below local results under a
// "Smart matches" separator.

import { LitElement, html, nothing, type TemplateResult } from "lit";
import { customElement, property, state } from "lit/decorators.js";

import { searchLite, searchSemantic, subscribeIndexEtag } from "./api";
import { Index, type ScoredEntry } from "./search-index";
import { cardStyles } from "./styles";
import type {
  HomeAssistant,
  SearchResultItem,
  StorageHubCardConfig,
} from "./types";

const CARD_VERSION = "2.0.0";
const ETAG_SENSOR = "sensor.storagehub_index_etag";

const DEFAULTS = {
  max_local_results: 10,
  max_semantic_results: 10,
  semantic_debounce_ms: 400,
};

const enum LimitRange {
  LocalMin = 1,
  LocalMax = 100,
  SemanticMin = 1,
  SemanticMax = 50,
  DebounceMin = 0,
  DebounceMax = 5000,
}

// eslint-disable-next-line no-console
console.info(
  `%c STORAGEHUB-CARD %c v${CARD_VERSION} `,
  "color: white; background: #03a9f4; font-weight: 700",
  "color: #03a9f4; background: white; font-weight: 700",
);

interface CustomCardEntry {
  type: string;
  name: string;
  description?: string;
  preview?: boolean;
  documentationURL?: string;
}
declare global {
  interface Window {
    customCards?: CustomCardEntry[];
  }
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "storagehub-card",
  name: "StorageHub Search",
  description: "Search your StorageHub inventory with instant local matches and a semantic fallback.",
});

@customElement("storagehub-card")
export class StorageHubCard extends LitElement {
  static styles = cardStyles;

  @property({ attribute: false }) hass?: HomeAssistant;

  @state() private _query = "";
  @state() private _localResults: ScoredEntry[] = [];
  @state() private _semanticResults: SearchResultItem[] = [];
  @state() private _loadingIndex = true;
  @state() private _loadingSemantic = false;
  @state() private _error: string | null = null;
  @state() private _semanticError: string | null = null;

  private _config!: Required<Omit<StorageHubCardConfig, "type" | "storagehub_url">> & {
    type: "custom:storagehub-card";
    storagehub_url?: string;
  };
  private _index: Index | null = null;
  private _debounceHandle: number | null = null;
  private _unsubEtag: (() => void) | null = null;
  // Stale-response guard: each semantic call increments this; when the call
  // resolves, we only commit results if the gen still matches.
  private _semanticGen = 0;

  setConfig(config: StorageHubCardConfig): void {
    if (!config || config.type !== "custom:storagehub-card") {
      throw new Error("Invalid configuration: type must be custom:storagehub-card");
    }
    const max_local_results = config.max_local_results ?? DEFAULTS.max_local_results;
    const max_semantic_results = config.max_semantic_results ?? DEFAULTS.max_semantic_results;
    const semantic_debounce_ms = config.semantic_debounce_ms ?? DEFAULTS.semantic_debounce_ms;

    if (max_local_results < LimitRange.LocalMin || max_local_results > LimitRange.LocalMax) {
      throw new Error(`max_local_results must be ${LimitRange.LocalMin}–${LimitRange.LocalMax}`);
    }
    if (max_semantic_results < LimitRange.SemanticMin || max_semantic_results > LimitRange.SemanticMax) {
      throw new Error(
        `max_semantic_results must be ${LimitRange.SemanticMin}–${LimitRange.SemanticMax}`,
      );
    }
    if (semantic_debounce_ms < LimitRange.DebounceMin || semantic_debounce_ms > LimitRange.DebounceMax) {
      throw new Error(
        `semantic_debounce_ms must be ${LimitRange.DebounceMin}–${LimitRange.DebounceMax}`,
      );
    }

    this._config = {
      type: "custom:storagehub-card",
      storagehub_url: config.storagehub_url,
      max_local_results,
      max_semantic_results,
      semantic_debounce_ms,
    };
  }

  static getStubConfig(): Partial<StorageHubCardConfig> {
    return { type: "custom:storagehub-card" };
  }

  getCardSize(): number {
    return 4;
  }

  connectedCallback(): void {
    super.connectedCallback();
    void this._loadIndex();
    void this._subscribeUpdates();
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this._debounceHandle !== null) {
      window.clearTimeout(this._debounceHandle);
      this._debounceHandle = null;
    }
    this._unsubEtag?.();
    this._unsubEtag = null;
  }

  private async _loadIndex(): Promise<void> {
    if (!this.hass) return;
    this._loadingIndex = true;
    this._error = null;
    try {
      const resp = await searchLite(this.hass);
      this._index = new Index(resp.items);
      if (this._query) this._recomputeLocal();
    } catch (err) {
      this._error = `Could not load inventory index: ${(err as Error).message ?? err}`;
    } finally {
      this._loadingIndex = false;
    }
  }

  private async _subscribeUpdates(): Promise<void> {
    if (!this.hass || this._unsubEtag) return;
    try {
      this._unsubEtag = await subscribeIndexEtag(this.hass, ETAG_SENSOR, () => {
        void this._loadIndex();
      });
    } catch {
      // If the diagnostic sensor isn't enabled, subscribeEvents still works
      // — events for that entity just never fire. No-op here is fine.
    }
  }

  private _onInput(e: InputEvent): void {
    const value = (e.target as HTMLInputElement).value;
    this._query = value;
    this._recomputeLocal();
    this._scheduleSemantic();
  }

  private _onKeydown(e: KeyboardEvent): void {
    if (e.key === "Enter") {
      if (this._debounceHandle !== null) {
        window.clearTimeout(this._debounceHandle);
        this._debounceHandle = null;
      }
      void this._runSemantic();
    }
  }

  private _recomputeLocal(): void {
    if (!this._index || this._query.trim().length < 2) {
      this._localResults = [];
      return;
    }
    this._localResults = this._index.search(this._query, this._config.max_local_results);
  }

  private _scheduleSemantic(): void {
    if (this._debounceHandle !== null) {
      window.clearTimeout(this._debounceHandle);
    }
    if (this._query.trim().length < 2) {
      this._semanticResults = [];
      this._semanticError = null;
      this._debounceHandle = null;
      return;
    }
    this._debounceHandle = window.setTimeout(() => {
      this._debounceHandle = null;
      void this._runSemantic();
    }, this._config.semantic_debounce_ms);
  }

  private async _runSemantic(): Promise<void> {
    if (!this.hass || this._query.trim().length < 2) return;
    const gen = ++this._semanticGen;
    this._loadingSemantic = true;
    this._semanticError = null;
    try {
      const resp = await searchSemantic(
        this.hass,
        this._query,
        this._config.max_semantic_results,
      );
      if (gen !== this._semanticGen) return; // a newer call is in flight
      const localIds = new Set(this._localResults.map((r) => r.entry.id));
      this._semanticResults = resp.items.filter((it) => !localIds.has(it.id));
    } catch (err) {
      if (gen !== this._semanticGen) return;
      this._semanticError = `Smart search unavailable: ${(err as Error).message ?? err}`;
      this._semanticResults = [];
    } finally {
      if (gen === this._semanticGen) this._loadingSemantic = false;
    }
  }

  private _openItem(id: string): void {
    if (!this._config.storagehub_url) return;
    const base = this._config.storagehub_url.replace(/\/+$/, "");
    window.open(`${base}/items/${id}`, "_blank", "noopener");
  }

  private _absoluteImageUrl(path: string | null): string | null {
    if (!path) return null;
    // Already absolute? Pass through.
    if (/^https?:\/\//i.test(path)) return path;
    // Relative path from the backend; needs the configured host to load.
    if (!this._config.storagehub_url) return null;
    const base = this._config.storagehub_url.replace(/\/+$/, "");
    return `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  }

  private _onThumbError(e: Event): void {
    // Hide broken thumbs rather than showing the browser's default icon.
    const target = e.target as HTMLImageElement;
    target.classList.add("thumb-broken");
  }

  private _renderRow(
    id: string,
    name: string,
    container: string | null,
    location: string | null,
    owner: string | null,
    imageUrl: string | null,
  ): TemplateResult {
    const where = [container ? `${container}` : null, location ? `in ${location}` : null]
      .filter((p) => p !== null)
      .join(" ");
    const clickable = !!this._config.storagehub_url;
    const absUrl = this._absoluteImageUrl(imageUrl);
    return html`
      <div
        class="row ${clickable ? "clickable" : ""}"
        @click=${clickable ? () => this._openItem(id) : undefined}
      >
        <div class="thumb">
          ${absUrl
            ? html`<img
                src=${absUrl}
                alt=""
                loading="lazy"
                @error=${this._onThumbError}
              />`
            : nothing}
        </div>
        <div class="row-main">
          <div class="row-name">${name}</div>
          <div class="row-location">${where || "—"}</div>
        </div>
        ${owner ? html`<span class="owner-pill">${owner}</span>` : nothing}
      </div>
    `;
  }

  protected render(): TemplateResult {
    const showEmpty =
      !this._loadingIndex &&
      !this._error &&
      this._index?.size === 0;
    const queryReady = this._query.trim().length >= 2;
    return html`
      <ha-card>
        <input
          class="search-input"
          type="text"
          placeholder="Search inventory…"
          .value=${this._query}
          @input=${this._onInput}
          @keydown=${this._onKeydown}
          autocomplete="off"
          spellcheck="false"
        />
        ${this._error
          ? html`<div class="error">${this._error}</div>`
          : nothing}
        ${this._loadingIndex
          ? html`<div class="loading">Loading inventory…</div>`
          : nothing}
        ${showEmpty
          ? html`<div class="empty">No items in inventory yet.</div>`
          : nothing}
        ${queryReady && this._localResults.length === 0 && !this._loadingSemantic && this._semanticResults.length === 0
          ? html`<div class="empty">No matches.</div>`
          : nothing}
        <div class="results">
          ${this._localResults.map((r) =>
            this._renderRow(
              r.entry.id,
              r.entry.name,
              r.entry.container_name,
              r.entry.location_name,
              r.entry.owner_name,
              r.entry.primary_image_url,
            ),
          )}
        </div>
        ${this._semanticError
          ? html`<div class="error">${this._semanticError}</div>`
          : nothing}
        ${this._semanticResults.length > 0
          ? html`<div class="smart-matches-header">Smart matches</div>
              <div class="results">
                ${this._semanticResults.map((it) =>
                  this._renderRow(
                    it.id,
                    it.name,
                    it.container_name,
                    it.location_name,
                    it.owner_name,
                    it.primary_image_url,
                  ),
                )}
              </div>`
          : nothing}
        ${this._loadingSemantic && this._semanticResults.length === 0
          ? html`<div class="semantic-loading">Looking deeper…</div>`
          : nothing}
      </ha-card>
    `;
  }
}
