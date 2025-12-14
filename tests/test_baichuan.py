import os

# Import the tool class to ensure it is registered
# from tooluniverse.baichuan_tool import BaiChuanTool  # noqa: F401
from tooluniverse import ToolUniverse

def main():
    # Ensure API key is set
    if not os.getenv("BAICHUAN_API_KEY"):
        raise RuntimeError(
            "Please set the BAICHUAN_API_KEY environment variable before running this example."
        )

    # Initialize ToolUniverse
    tu = ToolUniverse()
    tu.load_tools()

    # Basic usage
    prompt = "25岁健康女性种植牙，刚做完植入种植体，请问手术后是否需要服用抗生素？"
    result = tu.run({
        "name": "baichuan_tool",
        "arguments": {
            "input": prompt
        }
    })

    print(result)


if __name__ == "__main__":
    main()
