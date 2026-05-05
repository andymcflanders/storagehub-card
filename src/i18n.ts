// Card chrome strings. The voice surface lives in the integration's
// conversation.py and has its own templates; nothing in here is ever
// spoken. Keep the dicts flat and synchronized.

export interface CardStrings {
  searchPlaceholder: string;
  searchAriaLabel: string;
  emptyInventory: string;
  noMatches: string;
  loadingInventory: string;
  lookingDeeper: string;
  smartMatchesHeader: string;
  errorIndexLoad: string;
  errorSemantic: string;
}

export const STRINGS_EN: CardStrings = {
  searchPlaceholder: "Search inventory…",
  searchAriaLabel: "Search inventory",
  emptyInventory: "No items in inventory yet.",
  noMatches: "No matches.",
  loadingInventory: "Loading inventory…",
  lookingDeeper: "Looking deeper…",
  smartMatchesHeader: "Smart matches",
  errorIndexLoad: "Could not load inventory index",
  errorSemantic: "Smart search unavailable",
};

export const STRINGS_NO: CardStrings = {
  searchPlaceholder: "Søk i inventar…",
  searchAriaLabel: "Søk i inventar",
  emptyInventory: "Ingen ting i inventaret ennå.",
  noMatches: "Ingen treff.",
  loadingInventory: "Laster inventar…",
  lookingDeeper: "Leter dypere…",
  smartMatchesHeader: "Smarte treff",
  errorIndexLoad: "Klarte ikke å laste inventarindeksen",
  errorSemantic: "Smart søk er utilgjengelig",
};

// Match HA's BCP-47 language codes. "no", "nb", "nn", "nb-NO" all
// resolve to Norwegian; everything else falls through to English.
export function pickStrings(language: string | null | undefined): CardStrings {
  if (!language) return STRINGS_EN;
  const lc = language.toLowerCase();
  if (lc.startsWith("no") || lc.startsWith("nb") || lc.startsWith("nn")) {
    return STRINGS_NO;
  }
  return STRINGS_EN;
}
