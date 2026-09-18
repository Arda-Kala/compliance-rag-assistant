import sys
from src.compliance_engine import ComplianceAuditEngine

def run_interactive_audit():
    print("==========================================================")
    print(" SPK & BORSA MEVZUAT UYUM (COMPLIANCE) DENETİM MOTORU ")
    print("           (Microsoft Foundry Local - Offline)            ")
    print("==========================================================")
    print("Modeller yükleniyor, lütfen bekleyin...\n")
    
    engine = ComplianceAuditEngine()
    print("Sistem hazır. Denetlemek istediğiniz metni girin (Çıkış için 'q').\n")
    
    # Hazır örnek test senaryoları
    hazir_ornekler = [
        "Yeni Hisse Senedi Yoğun Fonumuzda yönetim ücreti yıllık %4.50 olarak belirlenmiştir.",
        "Fonumuz son 1 yılda %80 kazandırdı! Hemen katılın, siz de gelecekte aynı yüksek kazancı elde edin.",
        "İşlem masraflarınız hakkında detaylı bilgi müşteri temsilcimizce sözleşme öncesinde bildirilecektir."
    ]
    
    print("--- Hızlı Test İçin Örnek Senaryolar ---")
    for idx, ornek in enumerate(hazir_ornekler, 1):
        print(f"[{idx}] {ornek}")
    print("----------------------------------------\n")
    
    while True:
        try:
            user_input = input("Denetlenecek Metin [veya 1-3 no / q]: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() == 'q':
                print("Denetim motoru kapatıldı.")
                break
                
            # Hazır senaryo seçimi kontrolü
            if user_input in ["1", "2", "3"]:
                draft = hazir_ornekler[int(user_input) - 1]
                print(f"\nSeçilen Taslak: '{draft}'")
            else:
                draft = user_input
                
            print("\n>> Mevzuat taranıyor ve yerel AI denetimi yapılıyor...")
            audit_result = engine.audit_text(draft)
            
            print("\n" + "="*50)
            print("DENETİM RAPORU:")
            print("="*50)
            print(audit_result["verdict"])
            print("="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\nÇıkış yapıldı.")
            break
        except Exception as e:
            print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    run_interactive_audit()
