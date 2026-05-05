import { css } from "lit";

export const cardStyles = css`
  :host {
    display: block;
  }

  ha-card {
    padding: 12px 16px;
  }

  .search-input {
    width: 100%;
    padding: 10px 12px;
    font-size: 16px;
    border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: var(--ha-card-border-radius, 8px);
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color, #212121);
    box-sizing: border-box;
    outline: none;
    transition: border-color 120ms ease;
  }
  .search-input:focus {
    border-color: var(--primary-color, #03a9f4);
  }

  .empty,
  .loading,
  .error {
    padding: 16px 4px;
    color: var(--secondary-text-color, #727272);
    font-size: 14px;
    text-align: center;
  }
  .error {
    color: var(--error-color, #db4437);
  }

  .results {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-top: 8px;
  }

  .row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 4px;
    border-radius: 6px;
    cursor: default;
  }
  .row.clickable {
    cursor: pointer;
  }
  .row.clickable:hover {
    background: var(--secondary-background-color, #f5f5f5);
  }

  .row-main {
    flex: 1 1 auto;
    min-width: 0;
  }
  .row-name {
    font-size: 14px;
    color: var(--primary-text-color);
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .row-location {
    font-size: 12px;
    color: var(--secondary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .owner-pill {
    flex: 0 0 auto;
    padding: 2px 8px;
    font-size: 11px;
    border-radius: 999px;
    background: var(--primary-color, #03a9f4);
    color: var(--text-primary-color, #fff);
    white-space: nowrap;
  }

  .smart-matches-header {
    margin-top: 12px;
    padding: 4px 4px 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--secondary-text-color);
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }

  .semantic-loading {
    padding: 4px 4px;
    font-size: 12px;
    color: var(--secondary-text-color);
    font-style: italic;
  }
`;
