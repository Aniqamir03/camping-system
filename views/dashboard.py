import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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
        --sky:          #48CAE4;
        --ocean:        #0096C7;
        --coral:        #FF6B6B;
        --sunset:       #FF8E53;
        --lime:         #A8E063;
        --mint:         #56F9A4;
        --sand:         #FFF3E0;
        --glass-bg:     rgba(255, 255, 255, 0.18);
        --glass-border: rgba(255, 255, 255, 0.35);
        --glass-shadow: 0 8px 32px rgba(0, 100, 180, 0.18);
        --text-dark:    #1a2a3a;
        --text-mid:     #2c4a6e;
        --text-light:   rgba(255,255,255,0.92);
        --radius-lg:    20px;
        --radius-md:    14px;
        --radius-sm:    10px;
        --blur:         blur(18px);
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

    /* ── Floating Orbs ────────────────────────────────────── */
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

    /* ── Main Content ─────────────────────────────────────── */
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
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255,107,107,0.4); }
        50%       { box-shadow: 0 0 0 12px rgba(255,107,107,0); }
    }
    @keyframes countdownPop {
        0%   { transform: scale(1);    }
        50%  { transform: scale(1.04); }
        100% { transform: scale(1);    }
    }

    /* ── Alert / Info Boxes ───────────────────────────────── */
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
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] strong {
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
    }
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

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        padding: 0.55rem 1.6rem !important;
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(10px) !important;
        color: #fff !important;
        border: 1.5px solid rgba(255,255,255,0.5) !important;
        transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15) !important;
    }
    .stButton > button:hover {
        background: rgba(255,255,255,0.4) !important;
        transform: scale(1.04) translateY(-2px) !important;
    }

    /* ── Divider ──────────────────────────────────────────── */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent) !important;
        margin: 1.8rem 0 !important;
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

    /* ── Sidebar ──────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(0,50,100,0.55) !important;
        backdrop-filter: blur(24px) !important;
        border-right: 1.5px solid rgba(255,255,255,0.15) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #fff !important;
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
    .badge-sky {
        background: linear-gradient(135deg, #48CAE4, #0096C7);
        color: #fff;
        box-shadow: 0 3px 10px rgba(72,202,228,0.4);
    }
    </style>
    """, unsafe_allow_html=True)


# ── Reusable UI helpers (same as tentatif_lokasi.py) ──────
def section_header(icon: str, title: str, badge: str = "", badge_style: str = ""):
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


def welcome_banner(full_name: str, trip_name: str):
    """Animated welcome card with user name and trip."""
    st.markdown(
        f"""<div style="
            background: rgba(255,255,255,0.16);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1.5px solid rgba(255,255,255,0.38);
            border-radius: 20px;
            padding: 1.5rem 2rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 32px rgba(0,80,160,0.18),
                        inset 0 1px 0 rgba(255,255,255,0.45);
            animation: fadeSlideUp 0.6s ease both;
            display: flex; align-items: center; gap: 18px;
        ">
            <!-- Avatar orb -->
            <div style="
                width: 58px; height: 58px; flex-shrink: 0;
                background: linear-gradient(135deg, #FF6B6B, #FF8E53);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.7rem;
                box-shadow: 0 4px 16px rgba(255,107,107,0.45);
            ">👤</div>
            <div>
                <div style="
                    font-family:'Poppins',sans-serif;
                    font-size:0.75rem;
                    font-weight:500;
                    color:rgba(255,255,255,0.7);
                    text-transform:uppercase;
                    letter-spacing:1px;
                    margin-bottom:3px;
                ">Selamat Datang</div>
                <div style="
                    font-family:'Nunito',sans-serif;
                    font-weight:900;
                    font-size:1.3rem;
                    color:#fff;
                    text-shadow:0 2px 8px rgba(0,0,0,0.2);
                ">{full_name}</div>
                <div style="
                    font-family:'Poppins',sans-serif;
                    font-size:0.82rem;
                    color:rgba(255,255,255,0.75);
                    margin-top:2px;
                ">Sedang melihat: <span style="color:#FFD700;font-weight:600;">
                {trip_name}</span></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def countdown_card(baki_hari: int, trip_name: str):
    """
    Render a bold countdown card.
    baki_hari > 0  → countdown
    baki_hari == 0 → departure day
    baki_hari < 0  → memories
    """
    if baki_hari > 0:
        gradient  = "linear-gradient(135deg,#FF6B6B,#FF8E53)"
        icon      = "⏳"
        big_text  = f"{baki_hari}"
        unit      = "HARI LAGI"
        sub_text  = f"Sebelum kita bertolak ke <strong style='color:#FFD700;'>{trip_name}</strong>!<br>Sediakan mental dan fizikal. 💪"
        pulse_css = "animation: countdownPop 2s ease infinite;"
    elif baki_hari == 0:
        gradient  = "linear-gradient(135deg,#A8E063,#56F9A4)"
        icon      = "🎉"
        big_text  = "HARI"
        unit      = "INI KITA BERTOLAK!"
        sub_text  = "Semoga perjalanan kita semua dipermudahkan. Jaga diri! 🙏"
        pulse_css = "animation: pulse 1.5s ease infinite;"
    else:
        gradient  = "linear-gradient(135deg,#48CAE4,#0096C7)"
        icon      = "✨"
        big_text  = "SELESAI"
        unit      = "KENANGAN INDAH"
        sub_text  = f"Trip <strong style='color:#FFD700;'>{trip_name}</strong> telah pun berakhir dengan jayanya!"
        pulse_css = ""

    st.markdown(
        f"""<div style="
            background: {gradient};
            border-radius: 22px;
            padding: 1.8rem 2rem;
            margin: 0.5rem 0 1.2rem;
            box-shadow: 0 10px 36px rgba(0,0,0,0.2),
                        inset 0 1px 0 rgba(255,255,255,0.3);
            display: flex; align-items: center; gap: 22px;
            {pulse_css}
        ">
            <!-- Big emoji -->
            <div style="font-size:3.2rem; flex-shrink:0; filter:drop-shadow(0 4px 8px rgba(0,0,0,0.2));">
                {icon}
            </div>
            <!-- Numbers + text -->
            <div>
                <div style="
                    font-family:'Nunito',sans-serif;
                    font-weight:900;
                    font-size:3rem;
                    color:#fff;
                    line-height:1;
                    text-shadow:0 3px 12px rgba(0,0,0,0.2);
                    letter-spacing:-2px;
                ">{big_text}</div>
                <div style="
                    font-family:'Nunito',sans-serif;
                    font-weight:800;
                    font-size:0.95rem;
                    color:rgba(255,255,255,0.85);
                    letter-spacing:2px;
                    text-transform:uppercase;
                    margin-top:2px;
                ">{unit}</div>
                <div style="
                    font-family:'Poppins',sans-serif;
                    font-size:0.83rem;
                    color:rgba(255,255,255,0.82);
                    margin-top:6px;
                    line-height:1.5;
                ">{sub_text}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def announcement_card(items: list[dict]):
    """
    Glass announcement card.
    Each item: {"icon": str, "title": str, "body": str}
    """
    items_html = ""
    for item in items:
        items_html += f"""
        <div style="
            display:flex; gap:14px; align-items:flex-start;
            padding: 0.85rem 1rem;
            background: rgba(255,255,255,0.12);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.25);
            margin-bottom: 0.7rem;
            transition: transform 0.2s ease, background 0.2s ease;
        ">
            <div style="
                font-size:1.4rem; flex-shrink:0;
                margin-top:1px;
            ">{item['icon']}</div>
            <div>
                <div style="
                    font-family:'Nunito',sans-serif;
                    font-weight:800; font-size:0.95rem;
                    color:#FFD700;
                    margin-bottom:3px;
                ">{item['title']}</div>
                <div style="
                    font-family:'Poppins',sans-serif;
                    font-size:0.82rem; font-weight:400;
                    color:rgba(255,255,255,0.85);
                    line-height:1.55;
                ">{item['body']}</div>
            </div>
        </div>"""

    st.markdown(
        f"""<div style="
            background: rgba(255,255,255,0.16);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1.5px solid rgba(255,255,255,0.32);
            border-radius: 20px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 8px 30px rgba(0,80,160,0.15),
                        inset 0 1px 0 rgba(255,255,255,0.4);
            animation: fadeSlideUp 0.55s ease both;
        ">{items_html}</div>""",
        unsafe_allow_html=True,
    )


# ============================================================
# 🚀 APP ENTRY
# ============================================================
inject_css()

# ── Data fetching ──────────────────────────────────────────
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip  = trip_info.iloc[0]['Nama_Trip']
            tarikh_str = str(trip_info.iloc[0]['Tarikh'])
        else:
            nama_trip  = "Aktiviti Semasa"
            tarikh_str = ""
    else:
        nama_trip  = "Aktiviti Semasa"
        tarikh_str = ""
except:
    nama_trip  = "Sistem Perkhemahan"
    tarikh_str = ""

# ── Page title ─────────────────────────────────────────────
st.title(f"🏕️ Papan Pemuka — {nama_trip}")

# ── Welcome banner ─────────────────────────────────────────
full_name = st.session_state.get('full_name', 'Tetamu')
welcome_banner(full_name=full_name, trip_name=nama_trip)

st.divider()

# ============================================================
# SECTION 1 — Countdown
# ============================================================
section_header("⏳", "Kiraan Detik Keberangkatan", badge="LIVE", badge_style="badge-mint")

if tarikh_str and tarikh_str.lower() != 'nan':
    try:
        tarikh_kem = pd.to_datetime(tarikh_str).to_pydatetime()
        baki_hari  = (tarikh_kem - datetime.now()).days
        countdown_card(baki_hari, nama_trip)
    except:
        st.warning("⚠️ Format tarikh trip tidak sah. Pastikan format YYYY-MM-DD.")
else:
    st.info("⏳ Tarikh trip belum ditetapkan. Admin akan kemaskini sebentar lagi.")

st.divider()

# ============================================================
# SECTION 2 — Announcements
# ============================================================
section_header("📢", "Pengumuman Penting", badge="BARU", badge_style="badge-sky")

announcement_card([
    {
        "icon": "🚨",
        "title": "Peringatan Admin",
        "body":  "Sila pastikan <strong style='color:#FFD700;'>no. telefon waris</strong> "
                 "diisi lengkap di bahagian <em>Profil Saya</em> untuk tujuan kecemasan.",
    },
    {
        "icon": "ℹ️",
        "title": "Maklumat Trip",
        "body":  f"Anda sedang melihat ringkasan status bagi projek "
                 f"<strong style='color:#FFD700;'>{nama_trip}</strong>. "
                 "Semak tab lain untuk butiran lanjut.",
    },
])
