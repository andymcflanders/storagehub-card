// Pure-TS search index used by the StorageHub Lovelace card.
//
// Per-token substring matcher with field weights and starts-with /
// word-boundary bonuses. AND-across-query-tokens (every token must hit
// some field), OR-across-fields-per-token (best field wins).
//
// No DOM, no Lit. Test by importing the file from a node REPL if needed.

import type { IndexEntry } from "./types";

export interface ScoredEntry {
  entry: IndexEntry;
  score: number;
}

const WEIGHT_NAME = 10;
const WEIGHT_AI_NAMES = 8;
const WEIGHT_OWNER = 6;
const WEIGHT_CONTAINER = 4;
const WEIGHT_LOCATION = 3;

const BONUS_STARTS_WITH = 1.5;
const BONUS_WORD_BOUNDARY = 1.2;

// Strip punctuation before tokenizing. Keep letters and numbers from any
// alphabet (Norwegian å/ø/æ, etc.).
const PUNCT = /[^\p{L}\p{N}\s]/gu;

function tokenize(s: string): string[] {
  return s
    .toLowerCase()
    .replace(PUNCT, " ")
    .split(/\s+/)
    .filter((t) => t.length > 0);
}

interface Indexed {
  entry: IndexEntry;
  nameLc: string;
  nameTokens: string[];
  ownerLc: string;
  ownerTokens: string[];
  containerLc: string;
  containerTokens: string[];
  locationLc: string;
  locationTokens: string[];
  aiNames: { lc: string; tokens: string[] }[];
}

function buildIndexed(entry: IndexEntry): Indexed {
  const nameLc = entry.name.toLowerCase();
  const ownerLc = (entry.owner_name ?? "").toLowerCase();
  const containerLc = (entry.container_name ?? "").toLowerCase();
  const locationLc = (entry.location_name ?? "").toLowerCase();
  return {
    entry,
    nameLc,
    nameTokens: tokenize(entry.name),
    ownerLc,
    ownerTokens: tokenize(entry.owner_name ?? ""),
    containerLc,
    containerTokens: tokenize(entry.container_name ?? ""),
    locationLc,
    locationTokens: tokenize(entry.location_name ?? ""),
    aiNames: entry.ai_names.map((n) => ({
      lc: n.toLowerCase(),
      tokens: tokenize(n),
    })),
  };
}

// Score one query token against one field. Returns 0 if the token doesn't
// appear in the field at all.
function scoreField(
  token: string,
  fieldLc: string,
  fieldTokens: string[],
  weight: number,
): number {
  if (fieldLc.length === 0 || !fieldLc.includes(token)) return 0;
  let bonus = 1.0;
  if (fieldLc.startsWith(token) || fieldTokens.some((t) => t.startsWith(token))) {
    bonus = BONUS_STARTS_WITH;
  } else if (fieldTokens.some((t) => t.includes(token) && t !== fieldLc)) {
    // Token sits at the start of a sub-token (word boundary) but isn't the
    // overall field prefix.
    bonus = BONUS_WORD_BOUNDARY;
  }
  return weight * bonus;
}

function scoreAiNames(token: string, aiNames: Indexed["aiNames"]): number {
  let best = 0;
  for (const { lc, tokens } of aiNames) {
    const s = scoreField(token, lc, tokens, WEIGHT_AI_NAMES);
    if (s > best) best = s;
  }
  return best;
}

function scoreEntry(idx: Indexed, queryTokens: string[]): number {
  let total = 0;
  for (const token of queryTokens) {
    const best = Math.max(
      scoreField(token, idx.nameLc, idx.nameTokens, WEIGHT_NAME),
      scoreField(token, idx.ownerLc, idx.ownerTokens, WEIGHT_OWNER),
      scoreField(token, idx.containerLc, idx.containerTokens, WEIGHT_CONTAINER),
      scoreField(token, idx.locationLc, idx.locationTokens, WEIGHT_LOCATION),
      scoreAiNames(token, idx.aiNames),
    );
    if (best === 0) return 0; // AND across tokens — every token must hit
    total += best;
  }
  return total;
}

export class Index {
  private readonly entries: Indexed[];

  constructor(entries: IndexEntry[]) {
    this.entries = entries.map(buildIndexed);
  }

  get size(): number {
    return this.entries.length;
  }

  search(query: string, limit: number): ScoredEntry[] {
    const tokens = tokenize(query);
    if (tokens.length === 0) return [];
    if (tokens.every((t) => t.length < 2)) return [];

    const scored: ScoredEntry[] = [];
    for (const idx of this.entries) {
      const score = scoreEntry(idx, tokens);
      if (score > 0) scored.push({ entry: idx.entry, score });
    }

    // Stable: descending score, then alphabetical name as tiebreak.
    scored.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return a.entry.name.localeCompare(b.entry.name);
    });

    return scored.slice(0, limit);
  }
}
