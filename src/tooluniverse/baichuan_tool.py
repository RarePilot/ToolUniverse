import os
import json
import requests
from typing import Dict, Any

from tooluniverse.tool_registry import register_tool
from tooluniverse.base_tool import BaseTool


@register_tool('BaiChuanTool')
class BaiChuanTool(BaseTool):
    """BaiChuanTool for ToolUniverse."""

    API_URL = "https://api.baichuan-ai.com/v1/chat/completions"
    MODEL_NAME = "Baichuan-M2-Plus"
    API_KEY_ENV = "BAICHUAN_API_KEY"

    def __init__(self, tool_config: Dict):
        """
        ToolUniverse standard constructor
        """
        super().__init__(tool_config)

        # 允许通过 tool_config 覆盖默认配置（可选，但推荐）
        self.api_url = tool_config.get("api_url", self.API_URL)
        self.model_name = tool_config.get("model", self.MODEL_NAME)
        self.api_key_env = tool_config.get("api_key_env", self.API_KEY_ENV)

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool."""
        arguments = arguments or {}
        query = arguments.get("input", "")

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            return {
                "success": False,
                "error": f"Environment variable {self.api_key_env} is not set"
            }

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(
                self.api_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=60
            )
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

        request_id = response.headers.get("X-BC-Request-Id")

        if response.status_code != 200:
            return {
                "success": False,
                "status_code": response.status_code,
                "request_id": request_id,
                "error": response.text
            }

        try:
            result_json = response.json()
        except ValueError:
            result_json = response.text

        return {
            "success": True,
            "request_id": request_id,
            "result": result_json
        }

    def validate_input(self, **kwargs) -> None:
        """Validate input parameters."""
        if not kwargs.get("input"):
            raise ValueError("Input is required")
