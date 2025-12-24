import os
import numpy as np
from collections import defaultdict
from typing import Dict, Any, Optional, List
from tooluniverse.base_tool import BaseTool
from tooluniverse.tool_registry import register_tool

@register_tool("HPONormalizationTool", config={
    "name": "hpo_normalization_tool",
    "type": "HPONormalizationTool",
    "description": "Normalize phenotype mentions to Human Phenotype Ontology (HPO) concepts using BioLORD semantic embeddings.",
    "parameter": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of phenotype mentions to normalize"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of nearest neighbors to retrieve",
                "default": 5
            },
            "model_name": {
                "type": "string",
                "description": "HuggingFace model name or path",
                "default": "FremyCompany/BioLORD-2023"
            },
            "emb_path": {
                "type": "string",
                "description": "Path to HPO embeddings file (.npy)",
                "default": "hpo_embeddings.npy"
            },
            "text_path": {
                "type": "string",
                "description": "Path to HPO texts file (.npy)",
                "default": "hpo_texts.npy"
            },
            "id_path": {
                "type": "string",
                "description": "Path to HPO IDs file (.npy)",
                "default": "hpo_ids.npy"
            }
        },
        "required": ["queries"]
    }
})
class HPONormalizationTool(BaseTool):
    """
    Tool for normalizing phenotype mentions to HPO terms using BioLORD embeddings.
    """
    
    _model = None
    _hpo_embeddings = None
    _hpo_texts = None
    _hpo_ids = None
    
    def __init__(self, tool_config):
        super().__init__(tool_config)
        # Defaults
        self.default_model_name = "FremyCompany/BioLORD-2023"
        self.default_emb_file = "hpo_embeddings.npy"
        self.default_text_file = "hpo_texts.npy"
        self.default_id_file = "hpo_ids.npy"
        
    def _get_default_data_path(self):
        """
        Resolve the default path to the HPO data directory.
        """
        # Strategy 1: Look in the current working directory (development mode)
        cwd_data = os.path.join(os.getcwd(), 'data', 'human-phenotype-ontology')
        if os.path.exists(cwd_data):
            return cwd_data
            
        # Strategy 2: Look relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check ../../../data (development structure)
        dev_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'data', 'human-phenotype-ontology'))
        if os.path.exists(dev_path):
            return dev_path
            
        # Check package data
        pkg_path = os.path.join(current_dir, '..', 'data', 'human-phenotype-ontology')
        if os.path.exists(pkg_path):
            return pkg_path
            
        return None

    def _resolve_path(self, path_arg, default_filename):
        """
        Resolve a file path. If it's just a filename, look in default data dir.
        If it's an absolute path or exists relative to CWD, use it.
        """
        # If absolute path or exists relative to CWD, return it
        if os.path.exists(path_arg):
            return path_arg
            
        # If it looks like just a filename, check default data directory
        default_dir = self._get_default_data_path()
        if default_dir:
            joined_path = os.path.join(default_dir, path_arg)
            if os.path.exists(joined_path):
                return joined_path
                
        # If default filename provided and matches arg, check default dir
        if path_arg == default_filename and default_dir:
             joined_path = os.path.join(default_dir, default_filename)
             if os.path.exists(joined_path):
                 return joined_path
                 
        return path_arg # Return as is, it might be a user error but let loader fail

    def _load_resources(self, model_name, emb_path, text_path, id_path):
        """Lazy load model and data resources."""
        # Only reload if model changed or data not loaded
        # Note: simplistic caching, assumes if model name is same, it's the same model
        if (self.__class__._model is not None and 
            getattr(self.__class__, '_loaded_model_name', None) == model_name):
            # Check if paths are same? For simplicity assume static data for same model session
            pass
        
        # Resolve paths
        full_emb_path = self._resolve_path(emb_path, self.default_emb_file)
        full_text_path = self._resolve_path(text_path, self.default_text_file)
        full_id_path = self._resolve_path(id_path, self.default_id_file)

        # Check existence
        if not all(os.path.exists(p) for p in [full_emb_path, full_text_path, full_id_path]):
             raise FileNotFoundError(f"One or more HPO data files not found:\n{full_emb_path}\n{full_text_path}\n{full_id_path}")

        # Set tokenizers parallelism to false to avoid segfaults/deadlocks
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("The 'sentence_transformers' package is required. Please install it with `pip install sentence-transformers`.")

        # Load model if needed
        if (self.__class__._model is None or 
            getattr(self.__class__, '_loaded_model_name', None) != model_name):
            self.__class__._model = SentenceTransformer(model_name)
            self.__class__._loaded_model_name = model_name

        # Load data (we reload data if we are re-initializing, or we could verify paths)
        # For safety/simplicity in this tool context, we'll reload numpy arrays if paths differ 
        # from what we might store. But sticking to simple lazy load for now.
        self.__class__._hpo_embeddings = np.load(full_emb_path)
        self.__class__._hpo_texts = np.load(full_text_path, allow_pickle=True)
        self.__class__._hpo_ids = np.load(full_id_path, allow_pickle=True)

    def run(self, arguments: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        if arguments is None:
            arguments = kwargs
            
        queries = arguments.get('queries')
        top_k = int(arguments.get('top_k', 5))
        
        model_name = arguments.get('model_name', self.default_model_name)
        emb_path = arguments.get('emb_path', self.default_emb_file)
        text_path = arguments.get('text_path', self.default_text_file)
        id_path = arguments.get('id_path', self.default_id_file)
        
        if not queries:
            return {"error": "Parameter 'queries' is required and must be a non-empty list.", "success": False}
        
        if isinstance(queries, str):
            queries = [queries]
            
        try:
            self._load_resources(model_name, emb_path, text_path, id_path)
            
            from sentence_transformers import util
            
            model = self.__class__._model
            hpo_embeddings = self.__class__._hpo_embeddings
            hpo_texts = self.__class__._hpo_texts
            hpo_ids = self.__class__._hpo_ids
            
            # Encode all queries at once
            query_embeddings = model.encode(queries, normalize_embeddings=True)

            # Cosine similarity
            scores = util.cos_sim(query_embeddings, hpo_embeddings)

            outputs = []

            for i, query in enumerate(queries):
                # Ensure we don't request more top_k than available embeddings
                k = min(top_k, len(hpo_embeddings))
                top_scores, top_indices = scores[i].topk(k)

                # Collect synonym-level matches
                raw_results = []
                for score, idx in zip(top_scores, top_indices):
                    raw_results.append({
                        "hpo_id": hpo_ids[idx],
                        "matched_text": hpo_texts[idx],
                        "score": float(score)
                    })

                # Merge by HPO ID
                merged = defaultdict(float)
                # Keep track of the best matched text for each ID
                best_match_text = {}
                
                for r in raw_results:
                    if r["score"] > merged[r["hpo_id"]]:
                        merged[r["hpo_id"]] = r["score"]
                        best_match_text[r["hpo_id"]] = r["matched_text"]
                    # If scores are equal, we could prefer one, but max is fine

                final_results = sorted(
                    [{"hpo_id": k, "score": v, "matched_text": best_match_text[k]} for k, v in merged.items()],
                    key=lambda x: x["score"],
                    reverse=True
                )

                outputs.append({
                    "query": query,
                    "results": final_results
                })
                
            return {
                "results": outputs,
                "count": len(outputs),
                "success": True
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "error": f"Error normalizing to HPO: {str(e)}",
                "success": False
            }