from tooluniverse import ToolUniverse

tu = ToolUniverse()

result = tu.run({
    "name": "wikipedia_retriever_tool",
    "arguments": {
        "query": "唇腭裂",
        "lang": "zh",
        "load_max_docs": 3,
        "load_all_available_meta": False
    }
})

print(result)
