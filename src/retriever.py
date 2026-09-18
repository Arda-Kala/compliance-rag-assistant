import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.database import search_hybrid

class ComplianceRetriever:
    def __init__(self):
        config = Configuration(app_name="compliance-rag-assistant")
        try:
            FoundryLocalManager.initialize(config)
        except Exception:
            pass
            
        self.model = FoundryLocalManager.instance.catalog.get_model("qwen3-embedding-0.6b")
        self.model.load()
        self.client = self.model.get_embedding_client()

    def get_top_chunks(self, query: str, top_k: int = 3):
        q_res = self.client.generate_embeddings([query])
        q_emb = np.array(q_res.data[0].embedding, dtype=np.float32)
        raw_matches = search_hybrid(query_text=query, query_emb=q_emb, top_k=top_k * 2)
        
        unique_results = []
        seen_texts = set()
        for m in raw_matches:
            content_clean = m["content"].strip()
            if content_clean not in seen_texts:
                seen_texts.add(content_clean)
                unique_results.append(m)
            if len(unique_results) == top_k:
                break
                
        return unique_results
