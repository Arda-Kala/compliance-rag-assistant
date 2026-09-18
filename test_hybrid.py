import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager
from src.database import init_db, insert_chunk, search_hybrid, search_bm25, search_vector

def run_hybrid_test():
    print("=== Hibrit Arama (BM25 + Vector) Doğrulaması ===")
    
    # 1. Veritabanını hazırla
    init_db()
    
    # 2. Embedding istemcisini başlat
    config = Configuration(app_name="compliance-rag-assistant")
    FoundryLocalManager.initialize(config)
    model = FoundryLocalManager.instance.catalog.get_model("qwen3-embedding-0.6b")
    model.load()
    client = model.get_embedding_client()
    
    # 3. SPK ve Mevzuat Bilgi Tabanını Yükle
    mevzuat_verileri = [
        {
            "source": "SPK Yatırım Hizmetleri Tebliği",
            "page": 12,
            "type": "text",
            "text": "Madde 42: Yatırımcılara yönelik tanıtım, bülten ve reklamlarda kesin getiri taahhüdünde bulunulamaz. Sermaye kaybı riskinin bulunmadığı izlenimi oluşturulamaz."
        },
        {
            "source": "Yatırım Fonları Rehberi",
            "page": 4,
            "type": "table",
            "text": "| Fon Türü | Azami Yönetim Ücreti (Yıllık) |\n|---|---|\n| Hisse Senedi Şemsiye Fonu | %3.65 |\n| Para Piyasası Fonu | %1.50 |\n| Değişken Fon | %3.00 |"
        },
        {
            "source": "Borsa İstanbul Kotasyon Yönetmeliği",
            "page": 45,
            "type": "text",
            "text": "Madde 8: Ortaklıkların paylarının Yıldız Pazar'da işlem görebilmesi için halka arz edilen payların piyasa değerinin asgari 500 milyon TL olması şarttır."
        }
    ]
    
    print(f"\n{len(mevzuat_verileri)} adet mevzuat maddesi veritabanına ekleniyor...")
    metinler = [item["text"] for item in mevzuat_verileri]
    embeddings_res = client.generate_embeddings(metinler)
    
    for item, emb_obj in zip(mevzuat_verileri, embeddings_res.data):
        emb_arr = np.array(emb_obj.embedding, dtype=np.float32)
        insert_chunk(item["source"], item["page"], item["type"], item["text"], emb_arr)
        
    print("Veritabanı başarıyla dolduruldu.\n")
    
    # 4. Finansal Terim ve Kod Odaklı Sorgu Testi
    sorgu = "Madde 42 getiri garantisi"
    print(f"Denetim Sorgusu: '{sorgu}'")
    
    q_emb_res = client.generate_embeddings([sorgu])
    q_emb = np.array(q_emb_res.data[0].embedding, dtype=np.float32)
    
    # Hibrit arama çalıştır (RRF Puanlaması)
    sonuclar = search_hybrid(query_text=sorgu, query_emb=q_emb, top_k=2)
    
    print("\n=== Hibrit Arama (RRF) Sonuçları ===")
    for rank, res in enumerate(sonuclar, start=1):
        print(f"\n[{rank}. Eşleşme - RRF Skoru: {res.get('rrf_score', 0):.4f}]")
        print(f"Kaynak: {res['source_name']} (Sayfa: {res.get('page_number', 1)})")
        print(f"İçerik: {res['content']}")

if __name__ == "__main__":
    run_hybrid_test()
