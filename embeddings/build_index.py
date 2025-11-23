import json, pickle, os
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from tqdm import tqdm

DATA_PATH = "../data/shl_catalog.json"
INDEX_OUT = "../data/faiss_index.pkl"
EMB_MODEL = "all-mpnet-base-v2"

def build_documents():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)
    docs = []
    for it in items:
        text = f"{it.get('name','')}. {it.get('category','')}. {it.get('test_type','')}. {it.get('description','')}. Skills: {', '.join(it.get('skills',[]))}"
        docs.append({"text": text, "meta": it})
    return docs

def main():
    docs = build_documents()
    model = SentenceTransformer(EMB_MODEL)
    texts = [d['text'] for d in docs]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, batch_size=32)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    meta = {"docs": docs, "embeddings_shape": embeddings.shape, "dim": dim}
    with open(INDEX_OUT, "wb") as f:
        pickle.dump({"index": index, "meta": meta}, f)
    print("Saved FAISS index to", INDEX_OUT)

if __name__ == '__main__':
    main()
