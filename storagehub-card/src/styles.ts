/**
 * Styles for StorageHub card.
 */

import { css } from "lit";

export const styles = css`
  :host {
    --storagehub-primary: var(--primary-color, #03a9f4);
    --storagehub-warning: var(--warning-color, #ff9800);
    --storagehub-error: var(--error-color, #f44336);
    --storagehub-success: var(--success-color, #4caf50);
    --storagehub-text-primary: var(--primary-text-color, #212121);
    --storagehub-text-secondary: var(--secondary-text-color, #727272);
    --storagehub-divider: var(--divider-color, rgba(0, 0, 0, 0.12));
    --storagehub-surface: var(--card-background-color, #fff);
    --storagehub-surface-variant: var(--secondary-background-color, #fafafa);
  }

  ha-card {
    overflow: hidden;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 16px 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .title {
    font-size: 1.2em;
    font-weight: 500;
    color: var(--storagehub-text-primary);
  }

  .status-icon {
    --mdc-icon-size: 20px;
  }

  .status-icon.offline {
    color: var(--storagehub-error);
  }

  .status-icon.online {
    color: var(--storagehub-success);
  }

  .card-content {
    padding: 16px;
  }

  /* Search input */
  .search-container {
    position: relative;
  }

  .search-input-wrapper {
    display: flex;
    align-items: center;
    background: var(--storagehub-surface-variant);
    border-radius: 28px;
    padding: 8px 16px;
    gap: 12px;
    border: 2px solid transparent;
    transition: border-color 0.2s, background-color 0.2s;
  }

  .search-input-wrapper:focus-within {
    border-color: var(--storagehub-primary);
    background: var(--storagehub-surface);
  }

  .search-input-wrapper ha-icon {
    color: var(--storagehub-text-secondary);
    --mdc-icon-size: 24px;
    flex-shrink: 0;
  }

  .search-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 16px;
    color: var(--storagehub-text-primary);
    outline: none;
    min-width: 0;
  }

  .search-input::placeholder {
    color: var(--storagehub-text-secondary);
  }

  .search-spinner {
    --mdc-circular-progress-bar-color: var(--storagehub-primary);
  }

  .clear-button {
    background: none;
    border: none;
    padding: 4px;
    cursor: pointer;
    color: var(--storagehub-text-secondary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .clear-button:hover {
    background: var(--storagehub-divider);
  }

  .clear-button ha-icon {
    --mdc-icon-size: 18px;
  }

  /* Search results */
  .search-results {
    margin-top: 12px;
    border: 1px solid var(--storagehub-divider);
    border-radius: 12px;
    overflow: hidden;
    max-height: 350px;
    overflow-y: auto;
  }

  .result-item {
    display: flex;
    align-items: center;
    padding: 12px;
    gap: 12px;
    cursor: pointer;
    border-bottom: 1px solid var(--storagehub-divider);
    transition: background-color 0.15s;
  }

  .result-item:last-child {
    border-bottom: none;
  }

  .result-item:hover {
    background: var(--storagehub-surface-variant);
  }

  .item-image {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
  }

  .item-image-placeholder {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    background: var(--storagehub-surface-variant);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .item-image-placeholder ha-icon {
    color: var(--storagehub-text-secondary);
    --mdc-icon-size: 24px;
  }

  .item-details {
    flex: 1;
    min-width: 0;
  }

  .item-name {
    font-weight: 500;
    color: var(--storagehub-text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-location {
    font-size: 0.85em;
    color: var(--storagehub-text-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
    flex-wrap: wrap;
  }

  .item-location ha-icon {
    --mdc-icon-size: 14px;
  }

  .location-separator {
    opacity: 0.5;
  }

  .item-condition {
    font-size: 0.7em;
    padding: 2px 8px;
    border-radius: 12px;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 4px;
    display: inline-block;
  }

  .condition-fair {
    background: var(--storagehub-warning);
    color: white;
  }

  .condition-damaged,
  .condition-needs_repair {
    background: var(--storagehub-error);
    color: white;
  }

  /* No results / Error states */
  .no-results,
  .error-message {
    padding: 24px;
    text-align: center;
    color: var(--storagehub-text-secondary);
  }

  .error-message {
    color: var(--storagehub-error);
  }

  .search-hint {
    font-size: 0.9em;
    color: var(--storagehub-text-secondary);
    text-align: center;
    padding: 8px;
    margin-top: 8px;
  }

  /* Stats section */
  .stats-section {
    display: flex;
    justify-content: space-around;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--storagehub-divider);
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 8px;
    cursor: pointer;
    border-radius: 8px;
    transition: background-color 0.15s;
  }

  .stat-item:hover {
    background: var(--storagehub-surface-variant);
  }

  .stat-item ha-icon {
    --mdc-icon-size: 24px;
    color: var(--storagehub-text-secondary);
  }

  .stat-item.warning ha-icon {
    color: var(--storagehub-warning);
  }

  .stat-value {
    font-size: 1.5em;
    font-weight: 600;
    color: var(--storagehub-text-primary);
  }

  .stat-item.warning .stat-value {
    color: var(--storagehub-warning);
  }

  .stat-label {
    font-size: 0.8em;
    color: var(--storagehub-text-secondary);
  }

  /* External link */
  .storagehub-link {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 16px;
    padding: 10px;
    color: var(--storagehub-primary);
    text-decoration: none;
    border-radius: 8px;
    font-size: 0.9em;
    transition: background-color 0.15s;
  }

  .storagehub-link:hover {
    background: var(--storagehub-surface-variant);
  }

  .storagehub-link ha-icon {
    --mdc-icon-size: 18px;
  }

  /* Scrollbar styling */
  .search-results::-webkit-scrollbar {
    width: 8px;
  }

  .search-results::-webkit-scrollbar-track {
    background: transparent;
  }

  .search-results::-webkit-scrollbar-thumb {
    background: var(--storagehub-divider);
    border-radius: 4px;
  }

  .search-results::-webkit-scrollbar-thumb:hover {
    background: var(--storagehub-text-secondary);
  }
`;
