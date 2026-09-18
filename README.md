# SPK Mevzuat Uyum Denetim Sistemi

**Yerel RAG mimarisiyle çalışan, tamamen çevrimdışı SPK/BIST mevzuat uyum denetim motoru.**

Pazarlama materyalleri ve fon izahnamelerini Sermaye Piyasası Kurulu tebliğlerine göre otomatik olarak denetler. Microsoft Foundry Local üzerinde çalışır; hiçbir veri kurumun dışına çıkmaz.

---

## İçindekiler

- [Proje Mimarisi](#proje-mimarisi)
- [Kurulum](#kurulum)
- [Mevzuat Veri Tabanını Oluşturma](#mevzuat-veri-tabanını-oluşturma)
- [Uygulamayı Başlatma](#uygulamayı-başlatma)
- [Kullanım](#kullanım)
- [Proje Yapısı](#proje-yapısı)
- [Teknik Detaylar](#teknik-detaylar)
- [Kapsanan Mevzuat](#kapsanan-mevzuat)

---

## Proje Mimarisi

```
Kullanıcı Metni
      │
      ▼
┌─────────────────────────────────┐
│        ComplianceRetriever      │
│  Qwen3-Embedding-0.6b (local)   │
│                                 │
│  ┌──────────┐  ┌─────────────┐  │
│  │  BM25    │  │   Vektör    │  │
│  │ (FTS5)   │  │  (Cosine)   │  │
│  └────┬─────┘  └──────┬──────┘  │
│       └───── RRF ──────┘        │
│    Reciprocal Rank Fusion       │
└──────────────┬──────────────────┘
               │ Top-K Mevzuat Maddesi
               ▼
┌─────────────────────────────────┐
│      ComplianceAuditEngine      │
│      Phi-3.5-mini (local)       │
│   temp=0.2 · max_tokens=250     │
└──────────────┬──────────────────┘
               │
               ▼
        Denetim Raporu
   UYUM DURUMU / KURAL / GEREKÇE
```

**Neden tamamen yerel?** Fon izahnameleri ve taslak pazarlama materyalleri kurumsal sır niteliğindedir. Foundry Local sayesinde embedding ve LLM işlemleri cihazda gerçekleşir, internet bağlantısı gerekmez.

---

## Kurulum

### Gereksinimler

- Python 3.10+
- [Microsoft Foundry Local](https://aka.ms/foundry-local) kurulu ve çalışır durumda
- 8 GB+ RAM (Phi-3.5-mini için)

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/kullanici-adi/spk-compliance-rag.git
cd spk-compliance-rag

# 2. Sanal ortam oluştur
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Foundry Local'in çalıştığını doğrula
foundry list models
```

### requirements.txt

```
streamlit>=1.35.0
foundry-local-sdk
numpy
pypdf
sqlite3
```

---

## Mevzuat Veri Tabanını Oluşturma

`data/regulations/` klasörüne `.txt` formatında mevzuat dosyalarını koy, ardından:

```bash
python ingestion.py
```

Bu komut şunları yapar:
1. `data/regulations/` altındaki tüm `.txt` dosyalarını okur
2. Madde bazlı (`Madde X:` kalıbı) veya paragraf bazlı parçalara böler
3. Her parça için `Qwen3-Embedding-0.6b` ile vektör üretir
4. SQLite veritabanına (`compliance_rag.db`) hem ham metin hem embedding kaydeder
5. FTS5 tam metin indeksini otomatik senkronize eder

**Mevzuat dosyası formatı:**

```
[KAYNAK: Mevzuat Adı]

Madde X: Kural metni buraya gelir...

Madde Y: Bir sonraki kural...
```

---

## Uygulamayı Başlatma

```bash
streamlit run app.py
```

Tarayıcı otomatik açılır: `http://localhost:8501`

---

## Kullanım

### Metin Denetimi

1. "Metin Denetimi" sekmesine geç
2. Denetlenecek pazarlama ifadesi veya izahname maddesini metin kutusuna yapıştır
3. **Denetle** butonuna tıkla
4. Sistem şu adımları çalıştırır:
   - Metni vektöre çevirir
   - BM25 + vektör aramasıyla en ilgili mevzuat maddelerini bulur (RRF harmanlama)
   - Phi-3.5-mini'ye bağlam + metin gönderir
   - Yapılandırılmış denetim raporu alır
5. Raporu `.md` formatında indirebilirsin

**Örnek denetim raporu çıktısı:**

```
UYUM DURUMU: UYGUN DEĞİL
İHLAL EDİLEN KURAL: Yatırım Fonları Rehberi Madde 12 — azami %3.65
GEREKÇE: Belirtilen %4.50 ücreti tavanı 85 baz puan aşmaktadır.
DÜZELTME ÖNERİSİ: Ücret %3.65 veya altına düşürülmelidir.
[RAPOR SONU]
```

### Doküman Denetimi (PDF)

PDF fon izahnamesi veya bülten yükleyerek tüm sayfaları toplu denetleyebilirsin.

### Mevzuat Kütüphanesi

Yeni mevzuat eklemek için:
- **PDF yükle:** Belgeyi yükle, kaynak adını gir, İndeksle'ye tıkla
- **Manuel giriş:** Kaynak adı ve kural metnini formu doldurarak kaydet

---

## Proje Yapısı

```
spk-compliance-rag/
│
├── app.py                    # Streamlit arayüzü
├── ingestion.py              # Mevzuat parse + embedding pipeline
├── main.py                   # CLI denetim arayüzü
│
├── src/
│   ├── database.py           # SQLite + FTS5 + hybrid search (RRF)
│   ├── retriever.py          # ComplianceRetriever sınıfı
│   ├── compliance_engine.py  # ComplianceAuditEngine sınıfı
│   └── prompts.py            # Sistem prompt şablonları
│
├── data/
│   └── regulations/          # Mevzuat .txt dosyaları
│       ├── spk_teblig_iii_37.txt
│       ├── spk_teblig_ii_5.txt
│       ├── spk_teblig_iii_39.txt
│       ├── spk_teblig_iii_55.txt
│       └── fon_yonetim_rehberi.txt
│
├── compliance_rag.db         # SQLite veri tabanı (ingestion sonrası oluşur)
├── test_embeddings.py        # Embedding testi
├── test_hybrid.py            # Hybrid search testi
├── requirements.txt
└── README.md
```

---

## Teknik Detaylar

### Hibrit Arama (Reciprocal Rank Fusion)

Sistem iki farklı arama yöntemini birleştirerek en doğru mevzuat maddelerini getirir:

| Yöntem | Güçlü Olduğu Alan |
|--------|-------------------|
| **BM25 (FTS5)** | Madde numaraları, özel terimler ("anapara", "tavan", "%3.65") |
| **Vektör (Cosine)** | Anlamsal benzerlik, farklı ifade edilmiş aynı kavramlar |
| **RRF Harmanlama** | Her iki yöntemin sıralamalarını `1/(k+rank)` formülüyle birleştirir |

### Hallucination Önleme

- **Sistem promptu:** Yalnızca bağlamdaki maddelerle yanıt ver, bağlamda yoksa `"İLGİLİ MEVZUAT BULUNAMADI"` döndür
- **Düşük sıcaklık:** `temperature=0.2` — yaratıcı yorumu bastırır
- **Token limiti:** `max_tokens=250` — tekrarlama döngüsünü önler
- **`[RAPOR SONU]` tokenı:** Model bu tokendan sonra yazdıklarını çıktıdan temizler

### Modeller

| Model | Görev | Boyut |
|-------|-------|-------|
| `qwen3-embedding-0.6b` | Metin → Vektör | ~0.6B |
| `phi-3.5-mini` | Denetim raporu üretme | ~3.8B |

---

## Kapsanan Mevzuat

| Dosya | Mevzuat | Kapsam |
|-------|---------|--------|
| `spk_teblig_iii_37.txt` | SPK Yatırım Hizmetleri Tebliği III-37.1 | Maliyet bildirimi, getiri vaadi yasağı, risk profili |
| `spk_teblig_ii_5.txt` | SPK Halka Arz Tebliği II-5.1 | İzahname içerik zorunluluğu, Kurul onayı, pazarlama materyali |
| `spk_teblig_iii_39.txt` | SPK Yatırımcı Uygunluk Tebliği III-39.1 | Uygunluk testi, yüksek riskli ürün kısıtları |
| `spk_teblig_iii_55.txt` | SPK Portföy Yönetimi Tebliği III-55.1 | Ücret tavanları, raporlama, risk değeri güncelleme |
| `fon_yonetim_rehberi.txt` | Yatırım Fonları Yönetim Esasları Rehberi | Yönetim ücreti tavanları, geçmiş getiri uyarısı |

---

## Lisans

Bu proje Microsoft Yaz Okulu 2026 kapsamında eğitim amaçlı geliştirilmiştir.
