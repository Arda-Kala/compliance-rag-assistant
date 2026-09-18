import sqlite3
import re
import numpy as np

DB_PATH = "compliance_rag.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Tabloları ve FTS5 tam metin arama indeksini oluşturur."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Ham Metin ve Embedding Saklama Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                page_number INTEGER DEFAULT 1,
                content_type TEXT DEFAULT 'text',
                content TEXT NOT NULL,
                embedding BLOB NOT NULL
            );
        """)
        
        # 2. Finansal Terimler ve Madde Numaraları İçin BM25 FTS5 Tablosu
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
                content,
                source_name,
                content=document_chunks,
                content_rowid=id
            );
        """)
        
        # 3. Senkronizasyon Tetikleyicileri (Triggers)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_chunks_ai AFTER INSERT ON document_chunks BEGIN
                INSERT INTO document_fts(rowid, content, source_name)
                VALUES (new.id, new.content, new.source_name);
            END;
        """)
        conn.commit()

def insert_chunk(source_name: str, page_number: int, content_type: str, content: str, embedding: np.ndarray):
    """Metin parçasını ve float32 formatındaki embedding vektörünü kaydeder."""
    emb_bytes = embedding.astype(np.float32).tobytes()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO document_chunks (source_name, page_number, content_type, content, embedding)
            VALUES (?, ?, ?, ?, ?)
        """, (source_name, page_number, content_type, content, emb_bytes))
        conn.commit()

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    return float(dot / norm) if norm > 0 else 0.0

def search_vector(query_emb: np.ndarray, top_k: int = 3):
    """Cosine similarity kullanarak en yakın metinleri getirir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, source_name, page_number, content_type, content, embedding FROM document_chunks")
        rows = cursor.fetchall()
        
    results = []
    for r in rows:
        doc_emb = np.frombuffer(r["embedding"], dtype=np.float32)
        score = cosine_similarity(query_emb, doc_emb)
        results.append({
            "id": r["id"],
            "source_name": r["source_name"],
            "page_number": r["page_number"],
            "content_type": r["content_type"],
            "content": r["content"],
            "score": score,
            "method": "Vector"
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def clean_fts_query(raw_query: str) -> str:
    """FTS5 için zararlı karakterleri (? * : vb.) temizler ve terimleri OR ile birleştirir."""
    tokens = re.findall(r'\w+', raw_query)
    if not tokens:
        return ""
    return " OR ".join(f'"{t}"' for t in tokens)

def search_bm25(keyword_query: str, top_k: int = 3):
    """SQLite FTS5 motoru üzerinden temizlenmiş kelime araması yapar."""
    cleaned = clean_fts_query(keyword_query)
    if not cleaned:
        return []
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rowid as id, source_name, content, rank
                FROM document_fts
                WHERE document_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (cleaned, top_k))
            rows = cursor.fetchall()
            
        return [{
            "id": r["id"],
            "source_name": r["source_name"],
            "content": r["content"],
            "score": abs(r["rank"]),
            "method": "BM25"
        } for r in rows]
    except sqlite3.OperationalError:
        return []

def search_hybrid(query_text: str, query_emb: np.ndarray, top_k: int = 3):
    """Reciprocal Rank Fusion (RRF) ile BM25 ve Vektör aramalarını harmanlar."""
    vector_results = search_vector(query_emb, top_k=top_k * 2)
    bm25_results = search_bm25(query_text, top_k=top_k * 2)
    
    rrf_scores = {}
    content_map = {}
    k_constant = 60
    
    for rank, item in enumerate(vector_results, start=1):
        c_id = item["id"]
        rrf_scores[c_id] = rrf_scores.get(c_id, 0.0) + (1.0 / (k_constant + rank))
        content_map[c_id] = item
        
    for rank, item in enumerate(bm25_results, start=1):
        c_id = item["id"]
        rrf_scores[c_id] = rrf_scores.get(c_id, 0.0) + (1.0 / (k_constant + rank))
        if c_id not in content_map:
            content_map[c_id] = item

    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    final_results = []
    for c_id in sorted_ids[:top_k]:
        res = content_map[c_id]
        res["rrf_score"] = rrf_scores[c_id]
        final_results.append(res)
        
    return final_results
