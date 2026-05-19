import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
import streamlit.components.v1 as components

# ============================================================
# 🎨 GLOBAL DESIGN SYSTEM — Holiday Glassmorphism Theme
# ============================================================
def inject_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ─────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Poppins:wght@300;400;500;600;700&display=swap');

    /* ── CSS Variables ────────────────────────────────────── */
    :root {
        --sky:        #48CAE4;
        --ocean:      #0096C7;
        --coral:      #FF6B6B;
        --sunset:     #FF8E53;
        --lime:       #A8E063;
        --mint:       #56F9A4;
        --sand:       #FFF3E0;
        --glass-bg:   rgba(255, 255, 255, 0.18);
        --glass-border: rgba(255, 255, 255, 0.35);
        --glass-shadow: 0 8px 32px rgba(0, 100, 180, 0.18);
        --text-dark:  #1a2a3a;
        --text-mid:   #2c4a6e;
        --text-light: rgba(255,255,255,0.92);
        --radius-lg:  20px;
        --radius-md:  14px;
        --radius-sm:  10px;
        --blur:       blur(18px);
    }

    /* ── Animated Gradient Background ────────────────────── */
    .stApp {
        background: linear-gradient(
            135deg,
            #74b9ff 0%,
            #48CAE4 15%,
            #00b4d8 30%,
            #56CCF2 45%,
            #f093fb 60%,
            #FF6B6B 75%,
            #FF8E53 88%,
            #ffecd2 100%
        );
        background-size: 400% 400%;
        animation: gradientShift 18s ease infinite;
        min-height: 100vh;
    }

    @keyframes gradientShift {
        0%   { background-position: 0% 50%;   }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%;   }
    }

    /* ── Floating Orbs (ambient depth) ───────────────────── */
    .stApp::before {
        content: '';
        position: fixed;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(255,107,107,0.25) 0%, transparent 70%);
        top: -100px; right: -100px;
        border-radius: 50%;
        pointer-events: none;
        animation: orbFloat 12s ease-in-out infinite;
        z-index: 0;
    }
    .stApp::after {
        content: '';
        position: fixed;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(72,202,228,0.3) 0%, transparent 70%);
        bottom: -80px; left: -80px;
        border-radius: 50%;
        pointer-events: none;
        animation: orbFloat 15s ease-in-out infinite reverse;
        z-index: 0;
    }

    @keyframes orbFloat {
        0%, 100% { transform: translateY(0px) scale(1);   }
        50%       { transform: translateY(40px) scale(1.1); }
    }

    /* ── Main Content Area ────────────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem;
        max-width: 900px;
        position: relative;
        z-index: 1;
    }

    /* ── Page Title ───────────────────────────────────────── */
    h1 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 900 !important;
        font-size: 2.4rem !important;
        background: linear-gradient(135deg, #fff 0%, #ffecd2 60%, #FFD700 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: none !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem !important;
        animation: fadeSlideDown 0.7s ease both;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.15));
    }

    /* ── Subheaders ───────────────────────────────────────── */
    h2, h3 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 800 !important;
        color: #fff !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        letter-spacing: -0.3px;
        animation: fadeSlideDown 0.6s ease both;
    }

    /* ── Animations ───────────────────────────────────────── */
    @keyframes fadeSlideDown {
        from { opacity: 0; transform: translateY(-16px); }
        to   { opacity: 1; transform: translateY(0);     }
    }
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.92); }
        to   { opacity: 1; transform: scale(1);    }
    }

    /* ── Glass Card (universal) ───────────────────────────── */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        border: 1.5px solid var(--glass-border);
        border-radius: var(--radius-lg);
        box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,0.4);
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
        animation: fadeSlideUp 0.6s ease both;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0,80,160,0.22), inset 0 1px 0 rgba(255,255,255,0.5);
    }

    /* ── Info Box Override ────────────────────────────────── */
    div[data-testid="stAlert"] {
        background: rgba(255,255,255,0.22) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1.5px solid rgba(255,255,255,0.4) !important;
        border-radius: var(--radius-md) !important;
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
        box-shadow: 0 4px 20px rgba(0,80,160,0.12) !important;
        animation: popIn 0.5s ease both !important;
    }

    /* ── st.info / st.warning / st.success text ─────────── */
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] strong {
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    div[data-testid="stLinkButton"] > a,
    button[kind="primary"], button[kind="secondary"],
    .stButton > button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        padding: 0.55rem 1.6rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15) !important;
        border: none !important;
    }

    /* Primary / link buttons – coral-to-sunset gradient */
    div[data-testid="stLinkButton"] > a,
    .stButton > button[kind="primary"],
    button[data-testid*="primary"] {
        background: linear-gradient(135deg, var(--coral), var(--sunset)) !important;
        color: #fff !important;
    }
    div[data-testid="stLinkButton"] > a:hover,
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.06) translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(255,107,107,0.45) !important;
        filter: brightness(1.08) !important;
    }

    /* Secondary buttons – glass style */
    .stButton > button {
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(10px) !important;
        color: #fff !important;
        border: 1.5px solid rgba(255,255,255,0.5) !important;
    }
    .stButton > button:hover {
        background: rgba(255,255,255,0.4) !important;
        transform: scale(1.04) translateY(-2px) !important;
    }

    /* Form submit buttons – lime-to-mint */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #A8E063, var(--mint)) !important;
        color: var(--text-dark) !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 50px !important;
        box-shadow: 0 4px 20px rgba(86,249,164,0.35) !important;
    }
    .stFormSubmitButton > button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(86,249,164,0.5) !important;
    }

    /* ── Divider ──────────────────────────────────────────── */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent) !important;
        margin: 1.8rem 0 !important;
    }

    /* ── Input fields ─────────────────────────────────────── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,0.28) !important;
        backdrop-filter: blur(10px) !important;
        border: 1.5px solid rgba(255,255,255,0.45) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-dark) !important;
        font-family: 'Poppins', sans-serif !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(255,255,255,0.8) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.2) !important;
    }

    /* ── Form containers ──────────────────────────────────── */
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.14) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1.5px solid rgba(255,255,255,0.3) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.6rem !important;
        box-shadow: 0 8px 32px rgba(0,80,160,0.15) !important;
        animation: fadeSlideUp 0.5s ease both !important;
    }

    /* ── Tabs ─────────────────────────────────────────────── */
    div[data-testid="stTabs"] > div:first-child {
        background: rgba(255,255,255,0.15) !important;
        backdrop-filter: blur(14px) !important;
        border-radius: 50px !important;
        padding: 0.3rem !important;
        border: 1.5px solid rgba(255,255,255,0.3) !important;
        gap: 4px !important;
    }
    button[data-baseweb="tab"] {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        color: rgba(255,255,255,0.75) !important;
        border-radius: 50px !important;
        transition: all 0.22s ease !important;
        padding: 0.4rem 1.2rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--coral), var(--sunset)) !important;
        color: #fff !important;
        box-shadow: 0 4px 14px rgba(255,107,107,0.4) !important;
    }
    button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: rgba(255,255,255,0.2) !important;
        color: #fff !important;
    }

    /* ── Selectbox / Radio ────────────────────────────────── */
    div[data-testid="stRadio"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stCheckbox"] label {
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.2) !important;
    }

    /* ── Spinner ──────────────────────────────────────────── */
    div[data-testid="stSpinner"] {
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* ── Sidebar override ─────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(0,50,100,0.55) !important;
        backdrop-filter: blur(24px) !important;
        border-right: 1.5px solid rgba(255,255,255,0.15) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #fff !important;
    }

    /* ── Write / Markdown text ────────────────────────────── */
    .stMarkdown p, .stMarkdown li,
    div[data-testid="stText"] p {
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.15) !important;
    }
    .stMarkdown strong {
        color: #FFD700 !important;
    }

    /* ── Iframe map container ─────────────────────────────── */
    iframe {
        border-radius: var(--radius-md) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25) !important;
        border: 2px solid rgba(255,255,255,0.35) !important;
    }

    /* ── Checkbox ─────────────────────────────────────────── */
    div[data-testid="stCheckbox"] > label {
        background: rgba(255,255,255,0.15) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem 0.8rem !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }

    /* ── Warning alert colour tweak ───────────────────────── */
    div[data-testid="stAlert"][data-alert-type="warning"] {
        background: rgba(255,180,50,0.28) !important;
        border-color: rgba(255,200,80,0.5) !important;
    }
    div[data-testid="stAlert"][data-alert-type="error"] {
        background: rgba(255,80,80,0.28) !important;
        border-color: rgba(255,120,120,0.5) !important;
    }
    div[data-testid="stAlert"][data-alert-type="success"] {
        background: rgba(86,249,164,0.22) !important;
        border-color: rgba(86,249,164,0.45) !important;
    }

    /* ── Columns equal height glass panels ────────────────── */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(255,255,255,0.13) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1.5px solid rgba(255,255,255,0.28) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: 0 6px 24px rgba(0,80,160,0.12) !important;
        animation: fadeSlideUp 0.55s ease both;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 36px rgba(0,80,160,0.2) !important;
    }

    /* ── Badge pill helper ────────────────────────────────── */
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--coral), var(--sunset));
        color: #fff;
        font-family: 'Nunito', sans-serif;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 3px 12px;
        border-radius: 50px;
        letter-spacing: 0.5px;
        box-shadow: 0 3px 10px rgba(255,107,107,0.4);
        margin-left: 8px;
        vertical-align: middle;
    }
    .badge-mint {
        background: linear-gradient(135deg, #A8E063, var(--mint));
        color: var(--text-dark);
        box-shadow: 0 3px 10px rgba(86,249,164,0.35);
    }
    </style>
    """, unsafe_allow_html=True)


def section_header(icon: str, title: str, badge: str = "", badge_style: str = ""):
    """Render a styled section header with optional badge."""
    badge_html = f'<span class="badge {badge_style}">{badge}</span>' if badge else ""
    st.markdown(
        f"""<div style="
            display:flex; align-items:center; gap:10px;
            background: rgba(255,255,255,0.18);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1.5px solid rgba(255,255,255,0.35);
            border-radius: 16px;
            padding: 0.85rem 1.4rem;
            margin: 1.2rem 0 0.8rem;
            box-shadow: 0 4px 20px rgba(0,80,160,0.12);
            animation: fadeSlideDown 0.5s ease both;
        ">
            <span style="font-size:1.6rem;">{icon}</span>
            <span style="
                font-family:'Nunito',sans-serif;
                font-weight:800;
                font-size:1.25rem;
                color:#fff;
                text-shadow:0 2px 8px rgba(0,0,0,0.2);
                letter-spacing:-0.2px;
            ">{title}</span>
            {badge_html}
        </div>""",
        unsafe_allow_html=True,
    )


def stat_card(icon: str, label: str, value: str, gradient: str = "var(--coral), var(--sunset)"):
    """Mini glass stat card for location info."""
    st.markdown(
        f"""<div style="
            background: rgba(255,255,255,0.18);
            backdrop-filter: blur(16px);
            border: 1.5px solid rgba(255,255,255,0.38);
            border-radius: 14px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.65rem;
            display: flex; align-items: center; gap: 12px;
            box-shadow: 0 4px 18px rgba(0,80,160,0.1);
            animation: popIn 0.4s ease both;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        " onmouseover="this.style.transform='translateY(-3px)'"
           onmouseout="this.style.transform='translateY(0)'">
            <div style="
                width:44px; height:44px;
                background: linear-gradient(135deg,{gradient});
                border-radius:12px;
                display:flex; align-items:center; justify-content:center;
                font-size:1.3rem;
                box-shadow:0 4px 12px rgba(0,0,0,0.15);
                flex-shrink:0;
            ">{icon}</div>
            <div>
                <div style="
                    font-family:'Poppins',sans-serif;
                    font-size:0.7rem;
                    font-weight:500;
                    color:rgba(255,255,255,0.7);
                    text-transform:uppercase;
                    letter-spacing:0.8px;
                    margin-bottom:1px;
                ">{label}</div>
                <div style="
                    font-family:'Nunito',sans-serif;
                    font-size:0.98rem;
                    font-weight:700;
                    color:#fff;
                    text-shadow:0 1px 4px rgba(0,0,0,0.15);
                ">{value}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# 🚀 APP ENTRY
# ============================================================
inject_css()

st.title("📅 Tentatif & Maklumat Lokasi")

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)


# --- FUNGSI BANTUAN UNTUK KALENDAR ---
def parse_tarikh(tarikh_str):
    try:
        return datetime.datetime.strptime(tarikh_str, "%Y-%m-%d").date()
    except:
        return datetime.date.today()


# ============================================================
# 1. PENGURUSAN DATA INFO LOKASI & POSTER (DINAMIK)
# ============================================================
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in  = str(datetime.date.today())
default_out = str(datetime.date.today())
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem = default_lokasi
check_in   = default_in
check_out  = default_out
maps_url   = default_maps
waze_url   = default_waze
p1 = p2 = p3 = ""

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if not info_db.empty:
        if current_trip and 'ID_Trip' in info_db.columns:
            info_db['ID_Trip'] = info_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            info_semasa = info_db[info_db['ID_Trip'] == current_trip]
        else:
            info_semasa = info_db

        if not info_semasa.empty:
            lokasi_kem = str(info_semasa.iloc[0].get('Lokasi', default_lokasi)).strip()
            check_in   = str(info_semasa.iloc[0].get('Check_In', default_in)).strip()
            check_out  = str(info_semasa.iloc[0].get('Check_Out', default_out)).strip()

            raw_maps = str(info_semasa.iloc[0].get('Maps_URL', default_maps)).strip()
            raw_waze = str(info_semasa.iloc[0].get('Waze_URL', default_waze)).strip()
            maps_url = default_maps if raw_maps.lower() in ['nan', ''] else raw_maps
            waze_url = default_waze if raw_waze.lower() in ['nan', ''] else raw_waze

            p1 = str(info_semasa.iloc[0].get('Poster_Pic_1', '')).strip()
            p2 = str(info_semasa.iloc[0].get('Poster_Pic_2', '')).strip()
            p3 = str(info_semasa.iloc[0].get('Poster_Pic_3', '')).strip()
except:
    pass

lokasi_url = urllib.parse.quote(lokasi_kem)
if maps_url == default_maps and lokasi_kem != default_lokasi:
    maps_url = f"https://maps.google.com/maps?q={lokasi_url}"
    waze_url = f"https://waze.com/ul?q={lokasi_url}"
embed_map_url = f"https://maps.google.com/maps?q={lokasi_url}&output=embed"


# ============================================================
# SECTION 1 — Info Tapak
# ============================================================
section_header("📍", "Info Tapak Perkhemahan",
               badge="LIVE", badge_style="badge-mint")

col1, col2 = st.columns(2)

with col1:
    stat_card("🏕️", "Lokasi Tapak", lokasi_kem,
              gradient="#48CAE4, #0096C7")
    stat_card("📥", "Check-In", check_in,
              gradient="#A8E063, #56F9A4")
    stat_card("📤", "Check-Out", check_out,
              gradient="#FF8E53, #FF6B6B")

    st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
    st.write("🚘 **Pautan Navigasi Pantas:**")
    st.link_button("🗺️ Buka di Google Maps", maps_url)
    st.link_button("🚙 Buka di Waze", waze_url)

with col2:
    if lokasi_kem != default_lokasi:
        st.components.v1.iframe(embed_map_url, height=310)
    else:
        st.warning("Peta akan dipaparkan setelah lokasi ditetapkan.")

st.divider()


# ============================================================
# SECTION 2 — SLIDESHOW POSTER (Enhanced HTML)
# ============================================================
section_header("🖼️", "Poster & Jadual Aktiviti Kumpulan")

senarai_poster = [p for p in [p1, p2, p3] if p and p.lower() != "nan"]

if senarai_poster:
    divs_gambar = ""
    dots_html   = ""
    for i, img_url in enumerate(senarai_poster):
        divs_gambar += f"""
        <div class="mySlides fade">
            <div class="slide-number">{i+1} / {len(senarai_poster)}</div>
            <img src="{img_url}"
                 style="width:100%; max-height:580px; object-fit:contain;
                        border-radius:16px; background:rgba(0,0,0,0.3);">
        </div>"""
        dots_html += f'<span class="dot" onclick="goToSlide({i})"></span>'

    html_kod = f"""
    <!DOCTYPE html><html>
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700&display=swap');
      *{{ box-sizing:border-box; margin:0; padding:0; }}
      body{{ font-family:'Nunito',sans-serif; background:transparent; }}

      .slideshow-wrapper{{
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 2px solid rgba(255,255,255,0.35);
        border-radius: 24px;
        padding: 16px;
        box-shadow: 0 12px 40px rgba(0,80,160,0.2),
                    inset 0 1px 0 rgba(255,255,255,0.4);
      }}

      .slideshow-container{{
        position: relative;
        border-radius: 16px;
        overflow: hidden;
      }}

      .mySlides{{ display:none; position:relative; text-align:center; }}

      .slide-number{{
        position: absolute; top:14px; right:16px;
        background: rgba(0,0,0,0.45);
        backdrop-filter: blur(8px);
        color: #fff;
        font-size: 0.82rem; font-weight:700;
        padding: 4px 12px;
        border-radius: 50px;
        z-index: 10;
        letter-spacing: 0.5px;
      }}

      /* Nav arrows */
      .prev, .next{{
        cursor: pointer;
        position: absolute;
        top: 50%; transform: translateY(-50%);
        background: rgba(255,255,255,0.25);
        backdrop-filter: blur(10px);
        color: #fff;
        font-weight: 900; font-size: 1.3rem;
        width: 46px; height: 46px;
        border-radius: 50%;
        display: flex; align-items:center; justify-content:center;
        user-select: none;
        border: 1.5px solid rgba(255,255,255,0.4);
        transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1);
        z-index: 20;
      }}
      .prev{{ left: 12px; }}
      .next{{ right: 12px; }}
      .prev:hover, .next:hover{{
        background: linear-gradient(135deg,#FF6B6B,#FF8E53);
        transform: translateY(-50%) scale(1.1);
        box-shadow: 0 6px 20px rgba(255,107,107,0.45);
        border-color: transparent;
      }}

      /* Progress bar */
      .progress-bar-track{{
        height: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 2px;
        margin: 14px 4px 10px;
        overflow: hidden;
      }}
      .progress-bar-fill{{
        height: 100%;
        background: linear-gradient(90deg,#48CAE4,#FF6B6B,#FF8E53);
        border-radius: 2px;
        transition: width 0.4s ease;
      }}

      /* Dots */
      .dots-container{{
        text-align: center;
        padding: 4px 0 2px;
      }}
      .dot{{
        display: inline-block;
        width: 9px; height: 9px;
        margin: 0 4px;
        border-radius: 50%;
        background: rgba(255,255,255,0.35);
        border: 1.5px solid rgba(255,255,255,0.5);
        cursor: pointer;
        transition: all 0.25s ease;
      }}
      .dot.active{{
        background: linear-gradient(135deg,#FF6B6B,#FF8E53);
        border-color: transparent;
        transform: scale(1.3);
        box-shadow: 0 2px 8px rgba(255,107,107,0.5);
      }}
      .dot:hover{{ background: rgba(255,255,255,0.7); }}

      /* Fade animation */
      .fade{{ animation: fadeIn 0.7s ease; }}
      @keyframes fadeIn{{
        from{{ opacity:0; transform:scale(0.97); }}
        to{{   opacity:1; transform:scale(1);    }}
      }}
    </style>
    </head>
    <body>
    <div class="slideshow-wrapper">
      <div class="slideshow-container">
        {divs_gambar}
        <div class="prev" onclick="plusSlides(-1)">&#10094;</div>
        <div class="next" onclick="plusSlides(1)">&#10095;</div>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" id="progressBar"></div>
      </div>
      <div class="dots-container">{dots_html}</div>
    </div>

    <script>
    let slideIndex = 0, timer, totalSlides;
    window.addEventListener('DOMContentLoaded', function(){{
      totalSlides = document.getElementsByClassName('mySlides').length;
      updateProgressBar();
      showSlide(0);
    }});

    function plusSlides(n){{
      clearTimeout(timer);
      showSlide((slideIndex + n + totalSlides) % totalSlides);
    }}
    function goToSlide(n){{
      clearTimeout(timer);
      showSlide(n);
    }}
    function showSlide(n){{
      slideIndex = (n + totalSlides) % totalSlides;
      let slides = document.getElementsByClassName('mySlides');
      let dots   = document.getElementsByClassName('dot');
      for(let i=0; i<slides.length; i++){{ slides[i].style.display='none'; }}
      for(let i=0; i<dots.length; i++){{ dots[i].classList.remove('active'); }}
      slides[slideIndex].style.display = 'block';
      if(dots[slideIndex]) dots[slideIndex].classList.add('active');
      updateProgressBar();
      timer = setTimeout(()=>plusSlides(1), 5000);
    }}
    function updateProgressBar(){{
      let pct = ((slideIndex + 1) / totalSlides) * 100;
      let bar = document.getElementById('progressBar');
      if(bar) bar.style.width = pct + '%';
    }}
    </script>
    </body></html>
    """
    components.html(html_kod, height=660)

else:
    st.info("ℹ️ Belum ada poster jadual aktiviti untuk trip ini. Admin akan kemaskini sebentar lagi.")

st.divider()


# ============================================================
# SECTION 3 — Weather
# ============================================================
section_header("🌦️", "Ramalan Cuaca Kumpulan")

if lokasi_kem != default_lokasi:
    lokasi_cuaca     = lokasi_kem.split(",")[0].strip()
    lokasi_cuaca_url = urllib.parse.quote(lokasi_cuaca)
    yahoo_weather_url = f"https://search.yahoo.com/search?p={lokasi_cuaca_url}+weather"

    st.write(f"Sistem dikesan bersambung dengan lokasi: **{lokasi_cuaca}**.")
    st.link_button("✉️ Semak Cuaca Live di Yahoo Weather", yahoo_weather_url, type="primary")
else:
    st.info("Butang ramalan cuaca Yahoo akan diaktifkan sebaik sahaja Admin menetapkan lokasi tapak.")


# ============================================================
# SECTION 4 — ADMIN PANEL
# ============================================================
if st.session_state.get("role") == "Admin":
    st.divider()
    section_header("⚙️", "Panel Pengurusan Tentatif & Lokasi",
                   badge="ADMIN", badge_style="")

    tab_trip_baru, tab_poster, tab_urus_trip = st.tabs([
        "✨ Daftar Trip & Lokasi",
        "🖼️ Urus Poster (Slideshow)",
        "✏️ Urus & Padam Trip",
    ])

    # ── TAB 1: Daftar Trip Baru ──────────────────────────
    with tab_trip_baru:
        with st.form("form_daftar_trip_dan_lokasi"):
            st.write("### 🆕 Pendaftaran Aktiviti & Lokasi Baharu")
            st.write("Isi maklumat di bawah. Sistem akan auto-jana ID Trip, "
                     "auto-link navigasi peta, dan menyelaraskan (sync) ke "
                     "semua database berkaitan serentak.")

            new_nama_trip = st.text_input("Nama Aktiviti Baru (Contoh: Camping Janda Baik 2026)")
            new_lokasi    = st.text_input("Nama Lokasi Tapak (Contoh: Riverside Camp, Pahang)")

            col_new_in, col_new_out = st.columns(2)
            with col_new_in:
                new_in  = st.date_input("Tarikh Check-In / Bertolak",
                                        value=datetime.date.today(), key="new_in")
            with col_new_out:
                new_out = st.date_input("Tarikh Check-Out / Pulang",
                                        value=datetime.date.today(), key="new_out")

            submit_trip_baru = st.form_submit_button("🚀 Daftarkan Trip & Lokasi Serta-merta")

            if submit_trip_baru:
                if not new_nama_trip or not new_lokasi:
                    st.warning("Nama Aktiviti dan Nama Lokasi wajib diisi!")
                else:
                    try:
                        db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=600)
                        next_id = f"TRP{len(db_trip_pukal) + 1:03d}" if not db_trip_pukal.empty else "TRP001"
                    except:
                        db_trip_pukal = pd.DataFrame(columns=["ID_Trip","Nama_Trip","Tarikh","Status_Trip"])
                        next_id = "TRP001"

                    trip_row = pd.DataFrame([{
                        "ID_Trip":     next_id,
                        "Nama_Trip":   new_nama_trip.strip(),
                        "Tarikh":      new_in.strftime("%Y-%m-%d"),
                        "Status_Trip": "Aktif",
                    }])

                    lokasi_url_new = urllib.parse.quote(new_lokasi.strip())
                    info_row = pd.DataFrame([{
                        "ID_Trip":      next_id,
                        "Lokasi":       new_lokasi.strip(),
                        "Check_In":     new_in.strftime("%Y-%m-%d"),
                        "Check_Out":    new_out.strftime("%Y-%m-%d"),
                        "Maps_URL":     f"https://maps.google.com/maps?q={lokasi_url_new}",
                        "Waze_URL":     f"https://waze.com/ul?q={lokasi_url_new}",
                        "Poster_Pic_1": "",
                        "Poster_Pic_2": "",
                        "Poster_Pic_3": "",
                    }])

                    try:
                        updated_trip_db = pd.concat([db_trip_pukal, trip_row], ignore_index=True)
                    except:
                        updated_trip_db = trip_row
                    try:
                        db_info_pukal   = conn.read(worksheet="Info_Kem", ttl=600)
                        updated_info_db = pd.concat([db_info_pukal, info_row], ignore_index=True)
                    except:
                        updated_info_db = info_row

                    conn.update(worksheet="Senarai_Trip", data=updated_trip_db)
                    conn.update(worksheet="Info_Kem",     data=updated_info_db)
                    st.success(f"Mantap! Trip **{new_nama_trip}** berjaya direkodkan dengan kod **{next_id}**.")
                    st.cache_data.clear()
                    st.rerun()

    # ── TAB 2: Urus Poster ───────────────────────────────
    with tab_poster:
        with st.form("form_unggah_poster"):
            id_trip_save = current_trip if current_trip else "TRP001"
            st.write(f"🖼️ **Urus Pautan Poster (Slideshow)** untuk Trip ID Aktif: **{id_trip_save}**")
            st.markdown("💡 *Sila tampal Direct Link (berakhir .jpg/.png) ke dalam ruangan "
                        "di bawah. Anda boleh masukkan sehingga 3 keping poster.*")

            url_p1 = st.text_input("🔗 Poster Utama (Wajib)",    value=p1 if p1 != "nan" else "")
            url_p2 = st.text_input("🔗 Poster Kedua (Pilihan)", value=p2 if p2 != "nan" else "")
            url_p3 = st.text_input("🔗 Poster Ketiga (Pilihan)", value=p3 if p3 != "nan" else "")

            submit_poster = st.form_submit_button("💾 Simpan Koleksi Poster")

            if submit_poster:
                with st.spinner("Sedang menyelaraskan koleksi poster ke pangkalan data..."):
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=600)
                        if info_pukal.empty or 'ID_Trip' not in info_pukal.columns:
                            info_pukal = pd.DataFrame(columns=[
                                "ID_Trip","Lokasi","Check_In","Check_Out",
                                "Maps_URL","Waze_URL","Poster_Pic_1","Poster_Pic_2","Poster_Pic_3"])
                        else:
                            for col in info_pukal.columns:
                                info_pukal[col] = info_pukal[col].astype(str).replace('nan','').str.strip()
                        for col_name in ['Poster_Pic_1','Poster_Pic_2','Poster_Pic_3']:
                            if col_name not in info_pukal.columns:
                                info_pukal[col_name] = ""

                        if id_trip_save in info_pukal['ID_Trip'].values:
                            idx = info_pukal.index[info_pukal['ID_Trip'] == id_trip_save][0]
                            info_pukal.at[idx, 'Poster_Pic_1'] = url_p1.strip()
                            info_pukal.at[idx, 'Poster_Pic_2'] = url_p2.strip()
                            info_pukal.at[idx, 'Poster_Pic_3'] = url_p3.strip()
                        else:
                            new_row = pd.DataFrame([{
                                "ID_Trip": id_trip_save, "Lokasi": default_lokasi,
                                "Check_In": default_in,  "Check_Out": default_out,
                                "Maps_URL": default_maps, "Waze_URL": default_waze,
                                "Poster_Pic_1": url_p1.strip(),
                                "Poster_Pic_2": url_p2.strip(),
                                "Poster_Pic_3": url_p3.strip(),
                            }])
                            info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)

                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Koleksi poster (Slideshow) berjaya disimpan dan diselaraskan!")
                        # MAGIC REFRESH
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memproses pautan poster: {e}")

    # ── TAB 3: Urus & Padam Trip ─────────────────────────
    with tab_urus_trip:
        if not current_trip:
            st.info("Sila pilih aktiviti/trip di menu tepi (sidebar) terlebih dahulu "
                    "sebelum menguruskannya.")
        else:
            try:
                db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=600)
                trip_semasa_info = db_trip_pukal[db_trip_pukal['ID_Trip'] == current_trip]

                if not trip_semasa_info.empty:
                    info_trip     = trip_semasa_info.iloc[0]
                    nama_semasa   = str(info_trip.get('Nama_Trip', ''))
                    tarikh_semasa = str(info_trip.get('Tarikh', ''))
                    status_semasa = str(info_trip.get('Status_Trip', 'Aktif'))

                    st.write(f"### ⚙️ Pengurusan: **{nama_semasa}** ({current_trip})")
                    tindakan_trip = st.radio("Pilih Tindakan Pengurusan:",
                                            ["Kemaskini Maklumat Trip", "Padam Trip ❌"])

                    with st.form("form_urus_trip"):
                        if tindakan_trip == "Kemaskini Maklumat Trip":
                            edit_nama   = st.text_input("Nama Aktiviti", value=nama_semasa)
                            edit_tarikh = st.date_input("Tarikh Bertolak",
                                                        value=parse_tarikh(tarikh_semasa))
                            idx_status  = 0 if status_semasa == "Aktif" else 1
                            edit_status = st.selectbox("Status", ["Aktif","Selesai"],
                                                       index=idx_status)
                        elif tindakan_trip == "Padam Trip ❌":
                            st.warning(
                                f"⚠️ AMARAN: Adakah anda pasti mahu memadam aktiviti "
                                f"**{nama_semasa}**? Semua maklumat lokasi dan poster "
                                f"berkaitan trip ini juga akan terpadam.")
                            sahkan_padam = st.checkbox(
                                "Ya, saya pasti mahu padam trip ini sepenuhnya.")

                        submit_urus = st.form_submit_button("⚡ Laksanakan Tindakan")

                        if submit_urus:
                            if tindakan_trip == "Kemaskini Maklumat Trip":
                                if not edit_nama:
                                    st.error("Nama aktiviti tidak boleh dibiarkan kosong!")
                                else:
                                    idx = db_trip_pukal.index[db_trip_pukal['ID_Trip'] == current_trip][0]
                                    db_trip_pukal.at[idx, 'Nama_Trip']   = edit_nama.strip()
                                    db_trip_pukal.at[idx, 'Tarikh']      = edit_tarikh.strftime("%Y-%m-%d")
                                    db_trip_pukal.at[idx, 'Status_Trip'] = edit_status
                                    conn.update(worksheet="Senarai_Trip", data=db_trip_pukal)
                                    st.success("Maklumat aktiviti berjaya dikemaskini!")
                                    st.cache_data.clear()
                                    st.rerun()

                            elif tindakan_trip == "Padam Trip ❌":
                                if not sahkan_padam:
                                    st.error("Sila tanda (tick) pada kotak pengesahan sebelum memadam!")
                                else:
                                    db_trip_baru = db_trip_pukal[db_trip_pukal['ID_Trip'] != current_trip]
                                    conn.update(worksheet="Senarai_Trip", data=db_trip_baru)
                                    try:
                                        info_pukal = conn.read(worksheet="Info_Kem", ttl=600)
                                        info_baru  = info_pukal[info_pukal['ID_Trip'] != current_trip]
                                        conn.update(worksheet="Info_Kem", data=info_baru)
                                    except:
                                        pass
                                    st.session_state['current_trip_id'] = ""
                                    st.success(f"Aktiviti {nama_semasa} berjaya dipadamkan sepenuhnya.")
                                    st.cache_data.clear()
                                    st.rerun()
                else:
                    st.error("Rekod aktiviti ini tidak dijumpai di pangkalan data.")
            except Exception as e:
                st.error(f"Gagal membaca sistem pangkalan data: {e}")
