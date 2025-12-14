"""
baichuan_tool

BaiChuan LLM tool via the shared ToolUniverse client.
This follows the same pattern as CallAgent.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def baichuan_tool(
    prompt: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    BaiChuan LLM with a user prompt.

    Parameters
    ----------
    prompt : str
        User input prompt sent to BaiChuan model.
    stream_callback : Callable, optional
        Callback for streaming output.
    use_cache : bool, default False
        Enable caching.
    validate : bool, default True
        Validate parameters.

    Returns
    -------
    Any
        BaiChuan model response.
    """
    return get_shared_client().run_one_function(
        {
            "name": "baichuan_tool",
            "arguments": {
                "input": prompt
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["baichuan_tool"]
