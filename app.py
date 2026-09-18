import streamlit as st
import datetime
import re

st.set_page_config(
    page_title="SPK Uyum Denetim Paneli",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    font-size: 14px;
}

/* ── TÜM STREAMLIT CHROME'U GİZLE ── */
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"]       { display: none !important; }
[data-testid="collapsedControl"]{ display: none !important; }

/* ── ZEMIN ── */
.stApp { background: #ECEEF2 !important; }

/* ── BLOCK CONTAINER SIFIRLA ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}
section[data-testid="stMain"] > div:first-child { padding: 0 !important; }

/* ── ÜST BAR ── */
.topbar {
    background: #0D1520;
    height: 56px;
    padding: 0 36px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: sticky; top: 0; z-index: 200;
    width: 100%;
}
.topbar-left  { display: flex; align-items: center; gap: 12px; }
.topbar-logo  {
    width: 32px; height: 32px; border-radius: 6px;
    background: #1A6FD4;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; font-weight: 600; color: #fff;
}
.topbar-title { font-size: 14px; font-weight: 600; color: #E4EAF0; }
.topbar-sub   { font-size: 11px; color: #3D5166; margin-top: 1px; }
.topbar-right { display: flex; align-items: center; gap: 20px; }
.t-chip {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: #3D5166;
    display: flex; align-items: center; gap: 5px;
}
.dot { width: 6px; height: 6px; border-radius: 50%; background: #22C55E; }

/* ── SAYFA İÇERİĞİ ── */
.page {
    padding: 28px 36px 48px;
    width: 100%;
}

/* ── STAT KARTLARI ── */
.stat-row { display: flex; gap: 14px; margin-bottom: 24px; }
.stat-card {
    background: #fff; border: 1px solid #D8DDE5;
    border-radius: 8px; padding: 16px 20px;
    flex: 1;
}
.stat-lbl {
    font-size: 10px; font-weight: 600; color: #8A96A6;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 6px;
}
.stat-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px; font-weight: 600; color: #0D1520; line-height: 1;
    margin-bottom: 3px;
}
.stat-val-sm {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px; font-weight: 600; color: #0D1520; line-height: 1.3;
    margin-bottom: 3px;
}
.stat-sub { font-size: 11px; color: #A8B2BC; }

/* ── HIZLI SENARYOLAR ── */
.scenario-row {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-bottom: 20px;
}
.scenario-chip {
    background: #fff; border: 1px solid #D8DDE5;
    border-radius: 20px; padding: 6px 14px;
    font-size: 12px; color: #4A5568; cursor: pointer;
    transition: all 0.12s; white-space: nowrap;
    font-weight: 500;
}
.scenario-chip:hover {
    background: #EEF4FF; border-color: #93C5FD; color: #1D4ED8;
}

/* ── SEKMELER ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0 !important; background: transparent !important;
    border-bottom: 2px solid #D8DDE5 !important;
    padding: 0 !important; border-radius: 0 !important;
    width: 100% !important; margin-bottom: 24px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 0 !important; padding: 10px 24px !important;
    border: none !important; background: transparent !important;
    border-bottom: 2px solid transparent !important; margin-bottom: -2px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] * {
    color: #7A8999 !important; font-size: 13px !important; font-weight: 500 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #1A6FD4 !important; background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] * {
    color: #1A6FD4 !important; font-weight: 600 !important;
}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display:none !important; }

/* ── GİRİŞ ALANLARI ── */
label, [data-testid="stWidgetLabel"] * {
    color: #2D3748 !important; font-weight: 500 !important; font-size: 13px !important;
}
.stTextArea textarea {
    background: #fff !important; border: 1px solid #C8D0DA !important;
    border-radius: 6px !important; color: #1A202C !important;
    font-size: 13px !important; font-family: 'IBM Plex Sans', sans-serif !important;
    line-height: 1.65 !important;
}
.stTextArea textarea:focus {
    border-color: #1A6FD4 !important;
    box-shadow: 0 0 0 3px rgba(26,111,212,0.09) !important;
    outline: none !important;
}

/* ── BUTONLAR ── */
.stButton > button {
    border-radius: 6px !important; font-size: 13px !important;
    font-weight: 500 !important; padding: 9px 20px !important;
    border: 1px solid transparent !important; transition: all 0.15s !important;
    height: auto !important;
}
.stButton > button[kind="primary"] {
    background: #1A6FD4 !important; color: #fff !important;
    border-color: #1A6FD4 !important;
}
.stButton > button[kind="primary"]:hover { background: #1457AA !important; }
.stButton > button[kind="secondary"] {
    background: #fff !important; border-color: #C8D0DA !important; color: #4A5568 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #9BA8B5 !important; background: #F7F9FB !important;
}

/* ── SONUÇ PANELİ ── */
.result-panel {
    background: #fff; border: 1px solid #D8DDE5;
    border-radius: 8px; margin-top: 20px; overflow: hidden;
}
.result-header {
    padding: 14px 20px; border-bottom: 1px solid #EEF1F5;
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    background: #F8FAFB;
}
.result-quote { font-size: 13px; color: #4A5568; font-style: italic; line-height: 1.5; flex: 1; }
.result-body { padding: 0; }
.result-row {
    display: grid; grid-template-columns: 150px 1fr;
    border-bottom: 1px solid #EEF1F5;
}
.result-row:last-child { border-bottom: none; }
.result-key {
    font-size: 10px; font-weight: 700; color: #8A96A6;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 14px 20px; background: #F8FAFB;
    border-right: 1px solid #EEF1F5;
    display: flex; align-items: flex-start; padding-top: 17px;
}
.result-val { font-size: 13px; color: #1A202C; line-height: 1.65; padding: 14px 20px; }
.result-val code {
    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    background: #EEF1F5; padding: 2px 6px; border-radius: 3px; color: #2D3748;
}
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 4px;
    font-size: 11px; font-weight: 700;
    font-family: 'IBM Plex Mono', monospace; white-space: nowrap; flex-shrink: 0;
}
.badge-ok   { background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; }
.badge-err  { background:#FEF2F2; color:#B91C1C; border:1px solid #FECACA; }
.badge-warn { background:#FFFBEB; color:#B45309; border:1px solid #FDE68A; }

/* ── REFERANS ── */
.ref-block {
    background:#F8FAFB; border:1px solid #D8DDE5;
    border-left:3px solid #1A6FD4;
    border-radius:0 6px 6px 0; padding:10px 14px; margin-bottom:8px;
}
.ref-src { font-size:11px; font-weight:600; color:#1A6FD4; font-family:'IBM Plex Mono',monospace; margin-bottom:4px; }
.ref-txt { font-size:12px; color:#4A5568; line-height:1.6; }

[data-testid="stExpander"] {
    border:1px solid #D8DDE5 !important; border-radius:6px !important;
    background:#fff !important; margin-top:10px !important;
}
[data-testid="stDataFrame"] {
    border:1px solid #D8DDE5 !important; border-radius:8px !important; overflow:hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ── TOPBAR ──
st.markdown("""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">RAG</div>
    <div>
      <div class="topbar-title">SPK Uyum Denetim Paneli</div>
      <div class="topbar-sub">Mevzuat ve Pazarlama Materyali Kontrol Sistemi</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="t-chip"><span class="dot"></span>Çevrimdışı</div>
    <div class="t-chip">Phi-3.5-mini · Qwen3-0.6b</div>
    <div class="t-chip">Microsoft Foundry Local</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SAYFA ──
st.markdown('<div class="page">', unsafe_allow_html=True)

# STAT KARTLARI
st.markdown("""
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-lbl">Mevzuat Parçacığı</div>
    <div class="stat-val">27</div>
    <div class="stat-sub">5 kaynak belge</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">Arama Motoru</div>
    <div class="stat-val-sm">BM25 + Vektör</div>
    <div class="stat-sub">Reciprocal Rank Fusion</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">Çalışma Modu</div>
    <div class="stat-val-sm">On-Premises</div>
    <div class="stat-sub">Sıfır ağ bağlantısı</div>
  </div>
  <div class="stat-card">
    <div class="stat-lbl">LLM Modeli</div>
    <div class="stat-val-sm">Phi-3.5-mini</div>
    <div class="stat-sub">temp 0.2 · max 250 token</div>
  </div>
</div>
""", unsafe_allow_html=True)

# SEKMELER
tab1, tab2, tab3 = st.tabs(["Metin Denetimi", "Doküman Denetimi (PDF)", "Mevzuat Kütüphanesi"])

def parse_verdict(raw):
    r = {"durum":"BELİRSİZ","kural":"—","gerekce":"—","oneri":"—"}
    u = raw.upper()
    if any(k in u for k in ["UYUMSUZ","UYGUN DEĞİL","İHLAL"]): r["durum"]="UYUMSUZ"
    elif "UYGUN" in u and "DEĞİL" not in u: r["durum"]="UYGUN"
    elif "YETERSİZ" in u: r["durum"]="MEVZUAT YETERSİZ"
    for key, pat in [("kural", r'İHLAL EDİLEN KURAL[:\s]+(.*?)(?=GEREKÇE|DÜZELTME|$)'),
                     ("gerekce", r'GEREKÇE[:\s]+(.*?)(?=DÜZELTME|UYUM DURUMU|$)'),
                     ("oneri",   r'DÜZELTME ÖNERİSİ[:\s]+(.*?)(?=\[RAPOR SONU\]|$)')]:
        m = re.search(pat, raw, re.I|re.S)
        if m: r[key] = m.group(1).strip()
    return r

# TAB 1 ──────────────────────────────────────────
with tab1:
    # Hızlı senaryo butonları
    st.markdown("**Hazır Test Senaryoları:**")
    scenarios = {
        "Yönetim ücreti aşımı":    "Yeni Hisse Senedi Yoğun Fonumuzda yönetim ücreti yıllık %4.50 olarak belirlenmiştir.",
        "Getiri vaadi":            "Fonumuz son 1 yılda %80 kazandırdı! Siz de aynı yüksek kazancı elde edin.",
        "Anapara garantisi":       "Fonumuzda anapara kaybı riski sıfırdır, %100 devlet güvencesindedir.",
        "Sözleşme öncesi bildirim":"İşlem masrafları hakkında bilgi müşteri temsilcimizce bildirilecektir.",
    }
    cols = st.columns(len(scenarios))
    for col, (label, val) in zip(cols, scenarios.items()):
        with col:
            if st.button(label, use_container_width=True, type="secondary"):
                st.session_state["draft"] = val

    st.markdown("---")
    draft = st.text_area(
        "Denetlenecek pazarlama metni veya izahname maddesi:",
        value=st.session_state.get("draft", ""),
        height=110,
        placeholder="Denetlenmesini istediğiniz metni buraya yapıştırın..."
    )
    c1, c2, _ = st.columns([1.1, 1, 7])
    with c1:
        run = st.button("Denetle", type="primary", use_container_width=True)
    with c2:
        if st.button("Temizle", type="secondary", use_container_width=True):
            st.session_state["draft"] = ""
            st.rerun()

    if run and draft.strip():
        with st.spinner("Mevzuat taranıyor (BM25 + Vektör)..."):
            # GERÇEK PROJEDE: result = engine.audit_text(draft.strip())
            demo = """UYUM DURUMU: UYGUN DEĞİL
İHLAL EDİLEN KURAL: Yatırım Fonları Rehberi Madde 12 — Hisse Senedi Yoğun Fon azami yönetim ücreti %3.65
GEREKÇE: Belirtilen %4.50 yönetim ücreti, Madde 12'de belirlenen %3.65 tavanını 85 baz puan aşmaktadır.
DÜZELTME ÖNERİSİ: Yönetim ücreti %3.65 veya altına düşürülmeli; izahname ve pazarlama materyalleri güncellenmelidir.
[RAPOR SONU]"""
            p = parse_verdict(demo)

        badges = {
            "UYGUN":            '<span class="badge badge-ok">✓ Mevzuata Uygun</span>',
            "UYUMSUZ":          '<span class="badge badge-err">✕ Mevzuat İhlali</span>',
            "MEVZUAT YETERSİZ": '<span class="badge badge-warn">⚠ Mevzuat Yetersiz</span>',
        }
        badge = badges.get(p["durum"], '<span class="badge badge-warn">— Belirsiz</span>')
        q = draft.strip()
        q_short = (q[:145] + "…") if len(q) > 145 else q

        st.markdown(f"""
        <div class="result-panel">
          <div class="result-header">
            <div class="result-quote">"{q_short}"</div>
            {badge}
          </div>
          <div class="result-body">
            <div class="result-row">
              <div class="result-key">Dayanak Kural</div>
              <div class="result-val"><code>{p["kural"]}</code></div>
            </div>
            <div class="result-row">
              <div class="result-key">Gerekçe</div>
              <div class="result-val">{p["gerekce"]}</div>
            </div>
            <div class="result-row">
              <div class="result-key">Düzeltme Önerisi</div>
              <div class="result-val">{p["oneri"]}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Dayanak alınan mevzuat hükümleri"):
            st.markdown("""
            <div class="ref-block">
              <div class="ref-src">fon_yonetim_rehberi.txt — Madde 12</div>
              <div class="ref-txt">Hisse Senedi Yoğun Fon için azami yıllık yönetim ücreti %3.65 olarak belirlenmiştir.</div>
            </div>
            <div class="ref-block">
              <div class="ref-src">spk_teblig_iii_37.txt — Madde 42</div>
              <div class="ref-txt">Tanıtım materyallerinde kesin getiri vaadinde bulunulamaz ve piyasa koşullarından bağımsız algı oluşturulamaz.</div>
            </div>
            """, unsafe_allow_html=True)

        st.download_button("↓ Raporu İndir (.md)",
            data=f"# SPK Uyum Raporu\nTarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\nMetin: \"{draft.strip()}\"\n\nDurum: {p['durum']}\nKural: {p['kural']}\nGerekçe: {p['gerekce']}\nÖneri: {p['oneri']}\n",
            file_name=f"uyum_raporu_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown")

# TAB 2 ──────────────────────────────────────────
with tab2:
    st.markdown("##### Fon İzahnamesi veya Bülten Denetimi")
    st.caption("PDF belgesini yükleyerek tüm sayfaları otomatik olarak tarayabilirsiniz.")
    uploaded = st.file_uploader("PDF dosyası seç", type=["pdf"])
    if uploaded:
        st.info(f"Yüklendi: **{uploaded.name}**")
        if st.button("Belgeyi Baştan Sona Denetle", type="primary"):
            st.warning("Demo mod — Gerçek projede engine.audit_text() her paragraf için çağrılır.")

# TAB 3 ──────────────────────────────────────────
with tab3:
    st.markdown("##### Mevzuat Bilgi Tabanı")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("###### PDF ile Yükle")
        pdf_f = st.file_uploader("Mevzuat PDF", type=["pdf"], key="reg")
        if pdf_f:
            src = st.text_input("Kaynak adı:", value=pdf_f.name.replace(".pdf",""))
            if st.button("İndeksle", type="primary"):
                st.success(f"{src} indekslendi.")
    with col_r:
        st.markdown("###### Manuel Kural Girişi")
        with st.form("mf"):
            ms = st.text_input("Kaynak:")
            mt = st.text_area("Kural metni:", height=80)
            if st.form_submit_button("Kaydet"):
                st.success("Kaydedildi.")

    st.markdown("---")
    st.markdown("###### Kayıtlı Mevzuat")
    st.dataframe([
        {"Kaynak":"spk_teblig_iii_37.txt", "Tür":"text",  "İçerik":"Madde 24: Maliyet bildirimi · Madde 42: Getiri vaadi · Madde 55: Risk profili"},
        {"Kaynak":"fon_yonetim_rehberi.txt","Tür":"table","İçerik":"Madde 12: Yönetim ücreti tavanları · Madde 18: Geçmiş getiri uyarısı"},
        {"Kaynak":"spk_teblig_ii_5.txt",   "Tür":"text",  "İçerik":"Madde 6: İzahname içerik · Madde 22: Kayıt şartı · Madde 38: Pazarlama"},
        {"Kaynak":"spk_teblig_iii_39.txt", "Tür":"text",  "İçerik":"Madde 5: Uygunluk testi · Madde 12: Yüksek riskli ürünler"},
        {"Kaynak":"spk_teblig_iii_55.txt", "Tür":"table", "İçerik":"Madde 41: Portföy ücret tavanları · Madde 35: Risk değeri güncelleme"},
    ], use_container_width=True, height=220)

st.markdown('</div>', unsafe_allow_html=True)