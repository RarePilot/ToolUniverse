from typing import Dict, Any, Optional
from tooluniverse.base_tool import BaseTool
from tooluniverse.tool_registry import register_tool

@register_tool("PubMedRetrieverTool", config={
    "name": "pubmed_retriever_tool",
    "type": "PubMedRetrieverTool",
    "description": "Search PubMed using LangChain's PubMedRetriever to fetch relevant documents and metadata.",
    "parameter": {
        "type": "object",
        "properties": {
            "key_words": {
                "type": "string",
                "description": "The search query string, e.g., 'ChatGPT[Title/Abstract]'"
            },
            "top_k_results": {
                "type": "integer",
                "description": "Number of top results to retrieve",
                "default": 3
            },
            "doc_content_chars_max": {
                "type": "integer",
                "description": "Maximum number of characters for the document content",
                "default": 2000
            },
            "load_all_available_meta": {
                "type": "boolean",
                "description": "Whether to load all available metadata from PubMed",
                "default": True
            }
        },
        "required": ["key_words"]
    }
})
class PubMedRetrieverTool(BaseTool):
    """
    Tool for retrieving PubMed documents using LangChain's PubMedRetriever.
    """
    
    def run(self, arguments: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        if arguments is None:
            arguments = kwargs
            
        key_words = arguments.get('key_words')
        top_k_results = arguments.get('top_k_results', 3)
        doc_content_chars_max = arguments.get('doc_content_chars_max', 2000)
        load_all_available_meta = arguments.get('load_all_available_meta', True)
        
        if not key_words:
            return {"error": "Parameter 'key_words' is required.", "success": False}
            
        try:
            from langchain_community.retrievers import PubMedRetriever
        except ImportError:
            return {
                "error": "The 'langchain_community' package is required for this tool. Please install it using `pip install langchain_community`.",
                "success": False
            }

        try:
            # Initialize the retriever with provided parameters
            retriever = PubMedRetriever(
                top_k_results=int(top_k_results),
                load_all_available_meta=bool(load_all_available_meta),
                doc_content_chars_max=int(doc_content_chars_max)
            )
            
            # Invoke the retriever
            docs = retriever.invoke(key_words)
                
            return {
                "results": docs,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Error retrieving data from PubMed: {str(e)}",
                "success": False
            }