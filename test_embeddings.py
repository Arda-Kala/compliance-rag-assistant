import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_product / (norm_v1 * norm_v2))

def test_embedding_and_similarity():
    print("=== 2. Hafta: Yerel Vektör Arama ve Benzerlik Testi ===")
    
    # 1. SDK ve Modeli Başlat
    config = Configuration(app_name="compliance-rag-assistant")
    FoundryLocalManager.initialize(config)
    catalog = FoundryLocalManager.instance.catalog
    
    model = catalog.get_model("qwen3-embedding-0.6b")
    model.load()
    client = model.get_embedding_client()
    
    # 2. Veritabanına girecek örnek mevzuat ve kural metinleri
    belgeler = [
        "SPK Yatırım Hizmetleri Tebliği: Tanıtım ve reklamlarda kesin getiri taahhüdünde bulunulamaz, anapara garantisi izlenimi verilemez.",
        "Yatırım Fonları Yönetim Ücreti Esasları: Fon toplam değerinden karşılanan yönetim ücreti tavanı yıllık %3.65'i geçemez.",
        "Hava durumu raporu: Marmara bölgesinde yarın parçalı bulutlu bir gökyüzü beklenmektedir."
    ]
    
    print(f"\n{len(belgeler)} adet metin vektörleştiriliyor...")
    doc_response = client.generate_embeddings(belgeler)
    doc_embeddings = [np.array(item.embedding) for item in doc_response.data]
    
    print(f"Vektör boyutu (Embedding Dimension): {len(doc_embeddings[0])}")
    
    # 3. Denetim Sorgusu
    sorgu = "Yatırımcılara reklamda garanti kazanç vaat edilebilir mi?"
    print(f"\nSorgu: '{sorgu}'")
    
    query_response = client.generate_embeddings([sorgu])
    query_emb = np.array(query_response.data[0].embedding)
    
    # 4. Kosinüs Benzerliği Hesaplama ve Sıralama
    skorlar = []
    for idx, (belge, emb) in enumerate(zip(belgeler, doc_embeddings)):
        skor = cosine_similarity(query_emb, emb)
        skorlar.append((idx, belge, skor))
    
    skorlar.sort(key=lambda x: x[2], reverse=True)
    
    print("\n=== Anlamsal Benzerlik Sıralaması (Vector Search Çıktısı) ===")
    for rank, (idx, belge, skor) in enumerate(skorlar, start=1):
        print(f"\n[{rank}. Sıra - Benzerlik Skoru: %{skor*100:.2f}]")
        print(f"Metin: {belge}")

if __name__ == "__main__":
    test_embedding_and_similarity()
