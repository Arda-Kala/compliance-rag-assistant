from foundry_local_sdk import Configuration, FoundryLocalManager
from src.retriever import ComplianceRetriever

SYSTEM_PROMPT = """Sen SPK ve Borsa mevzuatına uygunluk denetimi yapan profesyonel bir Finansal Uyum Denetçisisin.
GÖREVİN: Taslak metni verilen mevzuata göre denetlemek.
KURALLAR:
- Sadece ve sadece aşağıdaki 4 başlığı doldur.
- Rapor bittikten sonra ASLA ek yorum, basitleştirme veya tekrarlayan kelimeler yazma.
- [RAPOR SONU] yaz ve dur.

ÇIKTI FORMATI:
UYUM DURUMU: [UYGUN / UYGUN DEĞİL / MEVZUAT YETERSİZ]
İHLAL EDİLEN KURAL: [Varsa madde no ve mevzuat adı, yoksa 'Yok']
GEREKÇE: [Kısa ve net açıklama]
DÜZELTME ÖNERİSİ: [Pazarlama ekibine somut öneri]
[RAPOR SONU]"""

class ComplianceAuditEngine:
    def __init__(self, model_alias: str = "phi-3.5-mini"):
        config = Configuration(app_name="compliance-rag-assistant")
        try:
            FoundryLocalManager.initialize(config)
        except Exception:
            pass
            
        self.catalog = FoundryLocalManager.instance.catalog
        self.model = self.catalog.get_model(model_alias)
        self.model.load()
        
        self.chat_client = self.model.get_chat_client()
        
        # Token ve sıcaklık ayarları (Tekrarlama döngüsünü keser)
        self.chat_client.settings.temperature = 0.2
        if hasattr(self.chat_client.settings, "max_tokens"):
            self.chat_client.settings.max_tokens = 250
        elif hasattr(self.chat_client.settings, "max_output_tokens"):
            self.chat_client.settings.max_output_tokens = 250
            
        self.retriever = ComplianceRetriever()

    def audit_text(self, draft_text: str, top_k: int = 2):
        print(" -> [1/3] Mevzuat taranıyor (BM25 + Vektör Arama)...")
        matched_chunks = self.retriever.get_top_chunks(draft_text, top_k=top_k)
        print(f" -> [2/3] {len(matched_chunks)} adet mevzuat maddesi bağlama alındı.")
        
        context_parts = []
        for i, c in enumerate(matched_chunks, 1):
            context_parts.append(f"MEVZUAT KAYNAĞI {i} ({c['source_name']}):\n{c['content']}")
            
        context_str = "\n\n".join(context_parts)
        
        user_prompt = f"""YASAL BAĞLAM:
{context_str}

DENETLENECEK TASLAK METİN:
"{draft_text}"

Lütfen belirlenen 4 başlık altında kısa denetim raporunu yaz ve [RAPOR SONU] ile bitir:"""

        print(" -> [3/3] Phi-3.5-mini modeli denetim raporunu üretiyor...")
        response = self.chat_client.complete_chat([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])
        
        raw_text = response.choices[0].message.content
        
        # Eğer model [RAPOR SONU] sonrasına bir şeyler eklemeye çalışırsa temizle
        if "[RAPOR SONU]" in raw_text:
            cleaned_verdict = raw_text.split("[RAPOR SONU]")[0].strip()
        else:
            cleaned_verdict = raw_text.strip()
            
        return {
            "verdict": cleaned_verdict,
            "references": matched_chunks
        }
