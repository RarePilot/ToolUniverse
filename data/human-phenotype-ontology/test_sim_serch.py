import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util

def load_hpo_index(
    model_name="FremyCompany/BioLORD-2023",
    emb_path="hpo_embeddings.npy",
    text_path="hpo_texts.npy",
    id_path="hpo_ids.npy"
):
    model = SentenceTransformer(model_name)

    hpo_embeddings = np.load(emb_path)
    hpo_texts = np.load(text_path, allow_pickle=True)
    hpo_ids = np.load(id_path, allow_pickle=True)

    return model, hpo_embeddings, hpo_texts, hpo_ids

def normalize_batch_to_hpo(
    queries,
    model,
    hpo_embeddings,
    hpo_texts,
    hpo_ids,
    top_k: int = 5
):
    """
    Normalize phenotype mentions to HPO concepts (batch version).

    Parameters
    ----------
    queries : List[str]
        Input phenotype mentions (batch).
    top_k : int
        Number of nearest neighbors to retrieve.

    Returns
    -------
    List[dict]
        Each item contains:
        {
          "query": str,
          "results": [
              {"hpo_id": str, "score": float},
              ...
          ]
        }
    """

    # Encode all queries at once
    query_embeddings = model.encode(queries, normalize_embeddings=True)

    # Cosine similarity
    scores = util.cos_sim(query_embeddings, hpo_embeddings)

    outputs = []

    for i, query in enumerate(queries):
        top_scores, top_indices = scores[i].topk(top_k)

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
        for r in raw_results:
            merged[r["hpo_id"]] = max(merged[r["hpo_id"]], r["score"])

        final_results = sorted(
            [{"hpo_id": k, "score": v} for k, v in merged.items()],
            key=lambda x: x["score"],
            reverse=True
        )

        outputs.append({
            "query": query,
            "results": final_results
        })

    return outputs

if __name__ == "__main__":
    model, hpo_embeddings, hpo_texts, hpo_ids = load_hpo_index()

    queries = [
        "Bartonellosis",
        "Swollen lymph nodes",
        "Fever"
    ]

    # queries = [
    #     "Bartonellosis"
    # ]

    results = normalize_batch_to_hpo(
        queries,
        model,
        hpo_embeddings,
        hpo_texts,
        hpo_ids,
        top_k=3
    )

    for r in results:
        print(r)
