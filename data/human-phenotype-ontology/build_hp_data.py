import numpy as np
from sentence_transformers import SentenceTransformer

def parse_hpo_obo(path):
    terms = []
    current = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line == "[Term]":
                if "id" in current:
                    terms.append(current)
                current = {}

            elif line.startswith("id:"):
                current["id"] = line.replace("id:", "").strip()

            elif line.startswith("name:"):
                current["name"] = line.replace("name:", "").strip()

            elif line.startswith("synonym:"):
                # synonym: "xxx" EXACT []
                try:
                    synonym = line.split('"')[1]
                    current.setdefault("synonyms", []).append(synonym)
                except IndexError:
                    pass

        if "id" in current:
            terms.append(current)

    return terms

def build_hpo_texts(hpo_terms):
    hpo_texts = []
    hpo_ids = []

    for term in hpo_terms:
        texts = [term["name"]] + term.get("synonyms", [])
        for t in texts:
            hpo_texts.append(t)
            hpo_ids.append(term["id"])

    return hpo_texts, hpo_ids

def encode_hpo_texts(
    hpo_texts,
    model_name="FremyCompany/BioLORD-2023",
    batch_size=64
):
    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        hpo_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings

if __name__ == "__main__":
    hpo_obo_path = "hp.obo" 

    print("📘 Parsing HPO...")
    hpo_terms = parse_hpo_obo(hpo_obo_path)
    print(f"✔ Parsed HPO terms: {len(hpo_terms)}")

    print("🧾 Building HPO text list (name + synonyms)...")
    hpo_texts, hpo_ids = build_hpo_texts(hpo_terms)
    print(f"✔ Total HPO texts: {len(hpo_texts)}")

    print("🧠 Encoding HPO texts with BioLORD...")
    hpo_embeddings = encode_hpo_texts(hpo_texts)

    print("💾 Saving embeddings and metadata...")
    np.save("hpo_embeddings.npy", hpo_embeddings)
    np.save("hpo_texts.npy", np.array(hpo_texts))
    np.save("hpo_ids.npy", np.array(hpo_ids))

    print("✅ All done!")
