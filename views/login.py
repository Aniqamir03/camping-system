import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo


def clean_text(value, default=""):
    try:
        if value is None or pd.isna(value):
            return default
    except Exception:
        pass

    value = str(value).replace("nan", "").replace("NaN", "").strip()
    return value if value else default


def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
    color-scheme: dark;
}

.stApp {
    background:
        radial-gradient(circle at 16% 10%, rgba(10,191,138,0.22), transparent 30%),
        radial-gradient(circle at 82% 84%, rgba(0,119,182,0.26), transparent 34%),
        linear-gradient(135deg, #06131f 0%, #082539 48%, #063b48 100%) !important;
    background-attachment: fixed !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,0.024) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.024) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
    z-index: 0;
    animation: bgFloat 18s ease-in-out infinite alternate;
}

.main .block-container {
    max-width: 620px !important;
    padding: 2.5rem 1.2rem 3rem !important;
    position: relative;
    z-index: 1;
}

h1 {
    font-size: clamp(1.75rem, 5vw, 2.65rem) !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    text-align: center !important;
    background: linear-gradient(135deg, #ffffff 0%, #9fffe0 45%, #39c9ff 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: 0 !important;
    animation: fadeDown 0.7s ease both !important;
}

p, .stMarkdown p, .stText p {
    color: rgba(255,255,255,0.78) !important;
}

[data-testid="stAlert"],
[data-testid="stForm"] {
    background: rgba(255,255,255,0.075) !important;
    backdrop-filter: blur(20px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(145%) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 20px !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.28),
        inset 0 1px 0 rgba(255,255,255,0.10) !important;
    animation: fadeUp 0.65s ease both !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] strong {
    color: rgba(255,255,255,0.94) !important;
}

div[data-testid="stSuccess"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.20), rgba(255,255,255,0.06)) !important;
    border: 1px solid rgba(10,191,138,0.42) !important;
}

div[data-testid="stWarning"] {
    background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(255,255,255,0.055)) !important;
    border: 1px solid rgba(245,158,11,0.35) !important;
}

div[data-testid="stError"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(255,255,255,0.055)) !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
}

[data-testid="stForm"] {
    padding: 1.35rem !important;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-height: 48px !important;
    border: 0 !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.35rem !important;
    background: linear-gradient(135deg, #0abf8a 0%, #00a6c8 52%, #0077b6 100%) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    box-shadow: 0 12px 30px rgba(10,191,138,0.28) !important;
    transition: transform 0.28s ease, box-shadow 0.28s ease, filter 0.28s ease !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-3px) scale(1.015) !important;
    filter: brightness(1.08) saturate(1.08) !important;
    box-shadow: 0 18px 42px rgba(10,191,138,0.42) !important;
}

.stTextInput input {
    background: rgba(248,250,252,0.96) !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: #0f172a !important;
    border: 1px solid rgba(255,255,255,0.26) !important;
    border-radius: 14px !important;
    min-height: 46px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.80), 0 10px 24px rgba(0,0,0,0.12) !important;
}

.stTextInput input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

.stTextInput input:focus {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border-color: rgba(10,191,138,0.82) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.18), 0 12px 28px rgba(0,0,0,0.16) !important;
}

.stTextInput label {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

.login-hero {
    margin: 0.2rem 0 1rem;
    padding: 1rem 1.05rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.62s ease both;
    text-align: center;
}

.login-hero-icon {
    width: 58px;
    height: 58px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 18px;
    margin-bottom: 0.72rem;
    background: linear-gradient(135deg, rgba(10,191,138,0.30), rgba(0,119,182,0.30));
    border: 1px solid rgba(255,255,255,0.14);
    font-size: 1.7rem;
    box-shadow: 0 14px 34px rgba(0,0,0,0.24);
}

.login-hero-title {
    color: rgba(255,255,255,0.96);
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.login-hero-sub {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    line-height: 1.45;
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-14px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes bgFloat {
    from { transform: translate3d(0,0,0); opacity: 0.7; }
    to { transform: translate3d(-16px,10px,0); opacity: 1; }
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1.4rem 0.75rem 2.4rem !important;
    }

    h1 {
        font-size: 1.65rem !important;
    }

    [data-testid="stForm"] {
        padding: 1rem !important;
        border-radius: 18px !important;
    }

    .login-hero {
        border-radius: 18px;
    }
}
</style>
""", unsafe_allow_html=True)


inject_css()

st.title("🔐 Log Masuk Sistem")

st.markdown(
    """
<div class="login-hero">
    <div class="login-hero-icon">🏕️</div>
    <div class="login-hero-title">Selamat datang semula</div>
    <div class="login-hero-sub">Masukkan username dan kata laluan untuk mengakses sistem perkhemahan kumpulan.</div>
</div>
""",
    unsafe_allow_html=True
)

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    users_db = conn.read(worksheet="Users", ttl=0)
except Exception:
    st.error("⚠️ Ralat Pangkalan Data: Tab 'Users' tidak dijumpai di dalam Google Sheets. Sila hubungi Admin.")
    st.stop()

with st.form("login_form"):
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log Masuk")

    if submit:
        if not input_user or not input_pass:
            st.warning("⚠️ Sila isi Username dan Password terlebih dahulu!")
        else:
            db_user = users_db["Username"].astype(str).str.strip().str.lower()
            db_pass = users_db["Password"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

            in_user = str(input_user).strip().lower()
            in_pass = str(input_pass).strip()

            match = users_db[(db_user == in_user) & (db_pass == in_pass)]

            if not match.empty:
                user_terpilih = match.iloc[0]

                username_log = clean_text(user_terpilih.get("Username", ""))
                nama_log = clean_text(user_terpilih.get("Full_Name", ""))
                role_log = clean_text(user_terpilih.get("Role", "Member"), "Member")

                masa_sekarang = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%Y-%m-%d %H:%M:%S")

                log_baru = pd.DataFrame([{
                    "Username": username_log,
                    "Nama_Penuh": nama_log,
                    "Peranan": role_log,
                    "Masa_Log_Masuk": masa_sekarang
                }])

                try:
                    try:
                        log_db = conn.read(worksheet="Log_Masuk", ttl=0)
                    except Exception:
                        log_db = pd.DataFrame(columns=["Username", "Nama_Penuh", "Peranan", "Masa_Log_Masuk"])

                    updated_log = pd.concat([log_db, log_baru], ignore_index=True)
                    conn.update(worksheet="Log_Masuk", data=updated_log)
                except Exception:
                    pass

                st.success("✅ Log masuk berjaya! Memuatkan sistem...")

                st.session_state["logged_in"] = True
                st.session_state["username"] = username_log
                st.session_state["role"] = role_log
                st.session_state["full_name"] = nama_log

                st.rerun()
            else:
                st.error("❌ Username atau Password salah! Sila cuba lagi.")
