from tooluniverse import ToolUniverse

tu = ToolUniverse()

result = tu.run({
    "name": "pubmed_retriever_tool",
    "arguments": {
        "key_words": "ChatGPT[Title/Abstract]",
        "top_k_results": 3,
        "doc_content_chars_max": 2000,
        "load_all_available_meta": True
    }
})

print(result)
