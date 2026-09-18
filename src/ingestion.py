import os
import re
import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.database import init_db, insert_chunk

def parse_regulatory_text(content: str, source_name: str):
    """Mevzuat maddelerini ve tabloları anlamsal bütünlüklerini bozmadan ayrıştırır."""
    chunks = []
    
    # Madde bazlı bölme regex'i
    pattern = r'(Madde\s+\d+:[\s\S]*?)(?=(?:Madde\s+\d+:|$))'
    matches = re.findall(pattern, content.strip())
    
    if not matches:
        # Madde formatı yoksa paragraflara göre böl
        raw_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for p in raw_paragraphs:
            chunks.append({
                "source": source_name,
                "type": "table" if "|" in p else "text",
                "text": p
            })
    else:
        for block in matches:
            block_text = block.strip()
            chunks.append({
                "source": source_name,
                "type": "table" if "|" in block_text else "text",
                "text": block_text
            })
            
    return chunks

def ingest_all_regulations(regulations_dir: str = "data/regulations"):
    """Dizindeki tüm mevzuat belgelerini okur, vektörleştirir ve SQLite'a yazar."""
    init_db()
    
    config = Configuration(app_name="compliance-rag-assistant")
    FoundryLocalManager.initialize(config)
    model = FoundryLocalManager.instance.catalog.get_model("qwen3-embedding-0.6b")
    model.load()
    client = model.get_embedding_client()
    
    all_chunks = []
    
    for filename in os.listdir(regulations_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(regulations_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
                
            chunks = parse_regulatory_text(raw_text, source_name=filename)
            all_chunks.extend(chunks)
            
    print(f"Toplam {len(all_chunks)} anlamlı mevzuat bloğu ayrıştırıldı.")
    
    # Batch (Toplu) embedding üretimi
    texts = [c["text"] for c in all_chunks]
    print("Vektörler toplu olarak hesaplanıyor...")
    embeddings_res = client.generate_embeddings(texts)
    
    for chunk, emb_obj in zip(all_chunks, embeddings_res.data):
        emb_array = np.array(emb_obj.embedding, dtype=np.float32)
        insert_chunk(
            source_name=chunk["source"],
            page_number=1,
            content_type=chunk["type"],
            content=chunk["text"],
            embedding=emb_array
        )
        
    print("Ingestion tamamlandı! Tüm kurallar ve tablolar SQLite veritabanına indekslendi.")

if __name__ == "__main__":
    ingest_all_regulations()
