"""
EU Health Information Portal runtime utilities: topic search and deep dive.

Exports
-------
- TOPICS : Dict[str, dict]
    Topic specs with seed terms and (optional) theme URI prefixes for filtering.
- euhealthinfo_search_* functions
    One per topic; run keyword/embedding/hybrid search over the local "euhealth" collection
    and return normalized dataset summaries (uuid/title/landing_page/license/keywords/themes/language/spatial/snippet).
- euhealthinfo_deepdive(uuids=None, topic=None, links_per=3, method="hybrid", limit=10, ...)
    For explicit UUIDs or the top-N seeds from a topic, fetch landing pages and classify outgoing links:
    direct_file | html_portal | login_or_error | error | unknown (with status/type when available).

Assumptions
-----------
- The "euhealth" collection exists locally as <user_cache_dir>/embeddings/euhealth.db and euhealth.faiss.
- Themes are compared case-insensitively (specs may use uppercase ontology prefixes; data is lowercased URIs).

Notes
-----
- De-duplicates results by dataset UUID when merging hits.
- Network access is required only for deep dive.
"""

from typing import Dict, Any, List, Optional
from tooluniverse.base_tool import BaseTool
from tooluniverse.tool_registry import register_tool

# Import the runtime surface (topic functions + deep dive).
from tooluniverse.euhealth import tools_runtime as rt


@register_tool("EuHealthTopicSearchTool")
class EuHealthTopicSearchTool(BaseTool):
    """
    Generic wrapper for all EU Health 'topic search' tools.

    - 20 topic tools are defined in euhealth_tools.json.
    - Each JSON entry sets fields.topic = the function name (e.g., "euhealthinfo_search_cancer").
    - At runtime, this class dispatches the call to that function in tools_runtime.

    Arguments supported:
      - limit: int (default 25)
      - country: Optional[str]
      - language: Optional[str]
      - term_override: Optional[str]

    Returns:
      List[Dict[str, Any]] shaped by _topic_search, including
      {uuid, title, landing_page, license, keywords[], themes[], language[], spatial, snippet}.
    """

    def run(self, arguments: Dict[str, Any]) -> Any:
        """Dispatch to the configured topic function in tools_runtime.

        Expects the tool config to include fields.topic with the function name.
        Returns a shaped list of dataset summaries or an error dict.
        """

        topic = (self.tool_config.get("fields") or {}).get("topic")
        if not topic:
            return {
                "error": "EuHealthTopicSearchTool misconfigured: missing fields.topic in tool config"
            }

        fn = getattr(rt, topic, None)
        if fn is None or not callable(fn):
            return {"error": f"Topic function '{topic}' not found in tools_runtime"}

        limit: int = int(arguments.get("limit", 25))
        country: Optional[str] = arguments.get("country")
        language: Optional[str] = arguments.get("language")
        term_override: Optional[str] = arguments.get("term_override")

        try:
            return fn(
                limit=limit,
                country=country,
                language=language,
                term_override=term_override,
            )
        except Exception as e:
            return {"error": f"euhealth topic search failed: {e}", "topic": topic}


@register_tool("EuHealthDeepDiveTool")
class EuHealthDeepDiveTool(BaseTool):
    """
    Adapter for the EU Health deep dive function.

    Usage:
      - Provide uuids=[...] to dive specific datasets.
      - Or provide topic="euhealthinfo_search_cancer" to auto-select top-N datasets and dive them.

    Arguments supported:
      - uuids: Optional[List[str]]
      - topic: Optional[str]
      - limit: int (default 10, topic mode only)
      - links_per: int (default 3)
      - country: Optional[str] (topic mode only)
      - language: Optional[str] (topic mode only)
      - term_override: Optional[str] (topic mode only)

    Returns:
      List[Dict[str, Any]] with
        { uuid, title, landing_page,
          candidates: [ {url, classification, http_status?, content_type?, notes?}, ... ]
        }
    """

    def run(self, arguments: Dict[str, Any]) -> Any:
        """Run euhealth deep dive by explicit `uuids` or by a topic seed list.

        Returns a list of {uuid, title, landing_page, candidates:[...]} or an error dict.
        """

        uuids: Optional[List[str]] = arguments.get("uuids")
        topic: Optional[str] = arguments.get("topic")
        limit: int = int(arguments.get("limit", 10))
        links_per: int = int(arguments.get("links_per", 3))
        country: Optional[str] = arguments.get("country")
        language: Optional[str] = arguments.get("language")
        term_override: Optional[str] = arguments.get("term_override")

        if not uuids and not topic:
            return {
                "error": "Provide either 'uuids' (preferred) or 'topic' to run deep dive"
            }

        try:
            if uuids:
                return rt.euhealthinfo_deepdive(
                    uuids=uuids,
                    limit=limit,
                    links_per=links_per,
                    country=country,
                    language=language,
                    term_override=term_override,
                )
            else:
                if not hasattr(rt, topic):
                    return {"error": f"Unknown topic '{topic}' for deep dive"}
                return rt.euhealthinfo_deepdive(
                    topic=topic,
                    limit=limit,
                    links_per=links_per,
                    country=country,
                    language=language,
                    term_override=term_override,
                )
        except Exception as e:
            return {"error": f"euhealth deep dive failed: {e}"}
