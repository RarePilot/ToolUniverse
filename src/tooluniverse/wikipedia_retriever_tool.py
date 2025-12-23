from typing import Dict, Any, Optional
from tooluniverse.base_tool import BaseTool
from tooluniverse.tool_registry import register_tool

@register_tool("WikipediaRetrieverTool", config={
    "name": "wikipedia_retriever_tool",
    "type": "WikipediaRetrieverTool",
    "description": "Search Wikipedia using LangChain's WikipediaRetriever to fetch relevant documents and metadata.",
    "parameter": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string, e.g., '唇腭裂'"
            },
            "lang": {
                "type": "string",
                "description": "Language code for Wikipedia (e.g., 'zh', 'en')",
                "default": "zh"
            },
            "load_max_docs": {
                "type": "integer",
                "description": "Maximum number of documents to load",
                "default": 300
            },
            "load_all_available_meta": {
                "type": "boolean",
                "description": "Whether to load all available metadata",
                "default": False
            }
        },
        "required": ["query"]
    }
})
class WikipediaRetrieverTool(BaseTool):
    """
    Tool for retrieving Wikipedia documents using LangChain's WikipediaRetriever.
    """
    
    def run(self, arguments: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        if arguments is None:
            arguments = kwargs
            
        query = arguments.get('query')
        lang = arguments.get('lang', 'zh')
        load_max_docs = arguments.get('load_max_docs', 300)
        load_all_available_meta = arguments.get('load_all_available_meta', False)
        
        if not query:
            return {"error": "Parameter 'query' is required.", "success": False}
            
        try:
            from langchain_community.retrievers import WikipediaRetriever
        except ImportError:
            return {
                "error": "The 'langchain_community' package is required for this tool. Please install it using `pip install langchain_community`.",
                "success": False
            }

        try:
            # Initialize the retriever with provided parameters
            retriever = WikipediaRetriever(
                lang=lang,
                load_max_docs=int(load_max_docs),
                load_all_available_meta=bool(load_all_available_meta)
            )
            
            # Invoke the retriever
            docs = retriever.invoke(query)

            return {
                "results": docs,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Error retrieving data from Wikipedia: {str(e)}",
                "success": False
            }