import pickle
from sentence_transformers import SentenceTransformer
import faiss
import os

INDEX_FILE = "../data/faiss_index.pkl"
EMB_MODEL = "all-mpnet-base-v2"

class Recommender:
    def __init__(self, index_file=INDEX_FILE):
        with open(index_file, 'rb') as f:
            obj = pickle.load(f)
        self.index = obj['index']
        self.docs = obj['meta']['docs']
        self.model = SentenceTransformer(EMB_MODEL)

    def embed_query(self, text):
        emb = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(emb)
        return emb

    def search(self, query_emb, top_k=30):
        D, I = self.index.search(query_emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            docs_meta = self.docs[idx]['meta']
            results.append({'score': float(score), 'meta': docs_meta})
        return results

    def balanced_recommend(self, structured, k=10):
        skills_text = ' '.join(structured.get('skills', []))
        pers_text = ' '.join(structured.get('personality_traits', []))
        weights = structured.get('weights', {'skills':0.6, 'personality':0.4})
        composite_text = ' '.join([t for t in [skills_text, pers_text] if t])
        q_emb = self.embed_query(composite_text)
        candidates = self.search(q_emb, top_k=60)
        tech = [c for c in candidates if c['meta'].get('test_type','').lower().startswith('k') or 'skill' in c['meta'].get('category','').lower()]
        beh = [c for c in candidates if c['meta'].get('test_type','').lower().startswith('p') or 'person' in c['meta'].get('category','').lower()]
        final = []
        need = max(5, min(10, k))
        if skills_text and pers_text:
            n_tech = need // 2
            n_beh = need - n_tech
        elif skills_text:
            n_tech = need; n_beh = 0
        else:
            n_tech = 0; n_beh = need
        for c in tech[:n_tech]: final.append(c)
        for c in beh[:n_beh]: final.append(c)
        idx = 0
        while len(final) < need and idx < len(candidates):
            cand = candidates[idx]
            if cand not in final:
                final.append(cand)
            idx += 1
        final = final[:10]
        out = [{"assessment_name": f['meta'].get('name',''), "assessment_url": f['meta'].get('url',''), "score": f['score']} for f in final]
        return out
