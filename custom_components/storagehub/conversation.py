"""Voice/Assist trigger for StorageHub.

Wires HA Assist to the search backend through the conversation
component's `register_trigger` API. Sentences and response templates
both live in this module — HA's translation helper is for UI strings
shown by the framework, not runtime templates an integration renders
itself.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from hassil.recognize import RecognizeResult
from homeassistant.components.conversation import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.conversation.const import DATA_DEFAULT_ENTITY
from homeassistant.components.conversation.models import ConversationInput
from homeassistant.core import HomeAssistant, callback
from homeassistant.setup import async_setup_component

from .api import CannotConnect, InvalidAuth, SearchResult, StorageHubError
from .const import DOMAIN

if TYPE_CHECKING:
    from . import StorageHubData

_LOGGER = logging.getLogger(__name__)

# hassil patterns. `{item}` becomes a wildcard slot automatically
# (default_agent.py:_collect_list_references). Bracketed words are
# optional. Both languages live in one list — hassil's recognize_all
# tries every sentence regardless of HA's configured language.
_TRIGGER_SENTENCES: list[str] = [
    # English
    "where is [the] {item}",
    "where's [the] {item}",
    "find [the|my] {item}",
    "locate [the] {item}",
    "show me [the] {item}",
    # Norwegian
    "hvor er [den|det] {item}",
    "hvor ligger [den|det] {item}",
    "finn [min|mitt] {item}",
]

_TEMPLATES_EN: dict[str, str] = {
    "found_with_owner": "{owner}'s {name} is in the {container} box in the {location}.",
    "found": "The {name} is in the {container} box in the {location}.",
    "found_no_container": "The {name} is in the {location}.",
    "found_multi": "I found {count} matches: {first} and {second}{more}.",
    "found_multi_more": ", and {n} more",
    "no_results": "I couldn't find a {item} in your inventory.",
    "error_cannot_connect": "I couldn't reach StorageHub.",
    "error_auth": "StorageHub rejected my API key. Please reconfigure the integration.",
    "error_generic": "StorageHub returned an error.",
    "not_configured": "StorageHub isn't configured yet.",
}

_TEMPLATES_NO: dict[str, str] = {
    "found_with_owner": "{owner}s {name} ligger i boksen {container} på {location}.",
    "found": "{name} ligger i boksen {container} på {location}.",
    "found_no_container": "{name} ligger på {location}.",
    "found_multi": "Jeg fant {count} treff: {first} og {second}{more}.",
    "found_multi_more": ", og {n} til",
    "no_results": "Jeg fant ingen {item} i inventaret.",
    "error_cannot_connect": "Jeg når ikke StorageHub.",
    "error_auth": "StorageHub avviste API-nøkkelen. Rekonfigurer integrasjonen.",
    "error_generic": "StorageHub returnerte en feil.",
    "not_configured": "StorageHub er ikke konfigurert ennå.",
}


def _templates_for(language: str | None) -> dict[str, str]:
    """Pick the template bundle for a language (norm: prefix match on 'no')."""
    if language and language.lower().startswith("no"):
        return _TEMPLATES_NO
    return _TEMPLATES_EN


def _query_mentions_owner(query: str, owner_name: str) -> bool:
    """Return True if any token of `query` looks like `owner_name`.

    Catches English `Sverre's` and Norwegian `Sverres` via prefix matching
    on the lowercased owner name. Light-touch — keeps us out of NLP land.
    """
    if not owner_name:
        return False
    owner_lc = owner_name.lower()
    for token in query.lower().split():
        token = token.rstrip("'s").rstrip("s")
        if token == owner_lc or owner_lc.startswith(token) and len(token) >= 3:
            return True
        if token.startswith(owner_lc):
            return True
    return False


def _format_response(
    result: SearchResult,
    item_text: str,
    language: str | None,
) -> str:
    templates = _templates_for(language)
    if result.total_count == 0:
        return templates["no_results"].format(item=item_text)

    items = result.items
    top = items[0]

    # Multi-result summary triggers if matches diverge on container, or
    # if there are too many to make a confident pick. Otherwise the top
    # result is good enough — same-container matches all answer the
    # "where is X" question identically.
    summarize = result.total_count > 5 or (
        len(items) >= 2 and items[0].container_name != items[1].container_name
    )

    if summarize and len(items) >= 2:
        more_count = result.total_count - 2
        more = (
            templates["found_multi_more"].format(n=more_count) if more_count > 0 else ""
        )
        return templates["found_multi"].format(
            count=result.total_count,
            first=items[0].name,
            second=items[1].name,
            more=more,
        )

    container = top.container_name
    location = top.location_name or "an unknown location"
    if not container:
        return templates["found_no_container"].format(name=top.name, location=location)

    if top.owner_name and _query_mentions_owner(item_text, top.owner_name):
        return templates["found_with_owner"].format(
            owner=top.owner_name,
            name=top.name,
            container=container,
            location=location,
        )

    return templates["found"].format(
        name=top.name, container=container, location=location
    )


async def async_register_conversation(hass: HomeAssistant) -> None:
    """Register our voice trigger on the default conversation agent."""
    if hass.data.get(_REGISTERED_KEY):
        return

    if DATA_DEFAULT_ENTITY not in hass.data:
        # `conversation` is in our manifest dependencies, but be defensive
        # in case async_setup runs before HA finishes wiring the agent.
        await async_setup_component(hass, CONVERSATION_DOMAIN, {})

    agent = hass.data[DATA_DEFAULT_ENTITY]
    agent.register_trigger(_TRIGGER_SENTENCES, _build_handler(hass))
    hass.data[_REGISTERED_KEY] = True


_REGISTERED_KEY = f"{DOMAIN}_conversation_registered"


def _build_handler(hass: HomeAssistant):
    @callback
    async def _handle(
        user_input: ConversationInput, result: RecognizeResult
    ) -> str | None:
        item_text = result.entities["item"].text.strip()
        templates = _templates_for(user_input.language)

        entries = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            return templates["not_configured"]

        data: StorageHubData = entries[0].runtime_data
        try:
            search_result = await data.client.async_search(item_text, limit=5)
        except InvalidAuth:
            return templates["error_auth"]
        except CannotConnect:
            return templates["error_cannot_connect"]
        except StorageHubError:
            _LOGGER.exception("StorageHub search failed for voice query %r", item_text)
            return templates["error_generic"]

        return _format_response(search_result, item_text, user_input.language)

    return _handle
