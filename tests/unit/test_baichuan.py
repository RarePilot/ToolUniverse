import pytest
from tooluniverse.baichuan_tool import BaiChuanTool

class TestMyNewTool:
    def setup_method(self):
        self.tool = BaiChuanTool(tool_config={})

    def test_success(self):
        result = self.tool.run({
            "input": "25岁健康女性种植牙，刚做完植入种植体，请问手术后是否需要服用抗生素"
        })

        assert result["success"] is True
        assert isinstance(result["result"], dict)
        assert "choices" in result["result"]
        assert len(result["result"]["choices"]) > 0

    def test_validation(self):
        """Test input validation."""
        with pytest.raises(ValueError):
            self.tool.validate_input(input="")

    def test_empty_input(self):
        """Test empty input handling."""
        result = self.tool.run({"input": ""})
        assert result["success"] is False
        assert "error" in result
