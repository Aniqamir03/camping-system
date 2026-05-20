import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import html as html_lib


current_trip = st.session_state.get('current_trip_id', '')
username_semasa = st.session_state.get('username', '')
nama_semasa = st.session_state.get('full_name', 'Pengguna')

if not username_semasa:
    st.error("Sila log masuk terlebih dahulu.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)


def clean_text(value, default=""):
    try:
        if value is None or pd.isna(value):
            return default
    except:
        pass

    value = str(value).replace("nan", "").strip()
    return value if value else default


def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
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
    max-width: 980px !important;
    padding: 2rem 1.2rem 7rem !important;
    position: relative;
    z-index: 1;
}

[data-testid="stSidebar"] {
    background: rgba(5, 20, 31, 0.78) !important;
    backdrop-filter: blur(24px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(145%) !important;
    border-right: 1px solid rgba(255,255,255,0.12) !important;
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.88) !important;
}

h1 {
    font-size: clamp(1.55rem, 4vw, 2.35rem) !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    background: linear-gradient(135deg, #ffffff 0%, #9fffe0 45%, #39c9ff 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: 0 !important;
    animation: fadeDown 0.7s ease both !important;
}

h2, h3 {
    color: rgba(255,255,255,0.95) !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
}

p, .stMarkdown p, .stText p, li {
    color: rgba(255,255,255,0.78) !important;
}

strong {
    color: #ffffff !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.16), transparent) !important;
    margin: 1.4rem 0 !important;
}

[data-testid="stAlert"],
[data-testid="stForm"],
[data-testid="stMetric"],
[data-testid="stExpander"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.075) !important;
    backdrop-filter: blur(20px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(145%) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 18px !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.28),
        inset 0 1px 0 rgba(255,255,255,0.10) !important;
    animation: fadeUp 0.65s ease both !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] strong {
    color: rgba(255,255,255,0.94) !important;
}

div[data-testid="stInfo"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.16), rgba(0,119,182,0.12)) !important;
    border: 1px solid rgba(10,191,138,0.36) !important;
}

div[data-testid="stError"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(255,255,255,0.055)) !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
}

.stButton > button {
    min-height: 44px !important;
    border: 0 !important;
    border-radius: 999px !important;
    padding: 0.68rem 1.2rem !important;
    background: linear-gradient(135deg, #0abf8a 0%, #00a6c8 52%, #0077b6 100%) !important;
    color: white !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    box-shadow: 0 12px 30px rgba(10,191,138,0.28) !important;
    transition: transform 0.28s ease, box-shadow 0.28s ease, filter 0.28s ease !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.015) !important;
    filter: brightness(1.08) saturate(1.08) !important;
    box-shadow: 0 18px 42px rgba(10,191,138,0.42) !important;
}

[data-testid="stChatInput"] {
    background: rgba(5,20,31,0.74) !important;
    backdrop-filter: blur(24px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(145%) !important;
    border-top: 1px solid rgba(255,255,255,0.12) !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.09) !important;
    color: rgba(255,255,255,0.94) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 26px rgba(0,0,0,0.20) !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(10,191,138,0.72) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.16) !important;
}

.chat-hero {
    margin: 0.2rem 0 1rem;
    padding: 1rem 1.05rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.62s ease both;
}

.chat-hero-title {
    color: rgba(255,255,255,0.96);
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.chat-hero-sub {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    line-height: 1.45;
}

.chat-shell {
    height: 470px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 22px;
    background:
        linear-gradient(135deg, rgba(10,191,138,0.08), rgba(0,119,182,0.08)),
        rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.08);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.7s ease both;
}

.chat-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    margin: 0 0 13px;
    animation: messageIn 0.35s ease both;
}

.chat-row.self {
    justify-content: flex-end;
}

.chat-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255,255,255,0.18);
    box-shadow: 0 8px 22px rgba(0,0,0,0.24);
    flex-shrink: 0;
}

.chat-bubble {
    max-width: min(78%, 620px);
    padding: 0.76rem 0.86rem;
    border-radius: 18px 18px 18px 6px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 12px 30px rgba(0,0,0,0.22);
    backdrop-filter: blur(16px) saturate(145%);
    -webkit-backdrop-filter: blur(16px) saturate(145%);
    overflow-wrap: anywhere;
}

.chat-row.self .chat-bubble {
    border-radius: 18px 18px 6px 18px;
    background: linear-gradient(135deg, rgba(10,191,138,0.30), rgba(0,119,182,0.28));
    border-color: rgba(10,191,138,0.32);
}

.chat-meta {
    display: flex;
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 4px;
}

.chat-name {
    color: white;
    font-size: 0.82rem;
    font-weight: 800;
}

.chat-self-pill {
    color: #9fffe0;
    background: rgba(10,191,138,0.14);
    border: 1px solid rgba(10,191,138,0.34);
    border-radius: 999px;
    padding: 1px 7px;
    font-size: 0.66rem;
    font-weight: 800;
}

.chat-time {
    color: rgba(255,255,255,0.52);
    font-size: 0.72rem;
    font-weight: 700;
}

.chat-text {
    color: rgba(255,255,255,0.88);
    font-size: 0.94rem;
    line-height: 1.45;
    white-space: pre-wrap;
}

.empty-chat {
    height: 100%;
    display: grid;
    place-items: center;
    text-align: center;
    color: rgba(255,255,255,0.72);
    padding: 1rem;
}

.empty-chat strong {
    display: block;
    font-size: 1rem;
    margin-bottom: 4px;
}

::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.04);
}

::-webkit-scrollbar-thumb {
    background: rgba(10,191,138,0.45);
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(10,191,138,0.7);
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

@keyframes messageIn {
    from { opacity: 0; transform: translateY(8px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.75rem 7rem !important;
    }

    h1 {
        font-size: 1.42rem !important;
    }

    .chat-hero,
    .chat-shell {
        border-radius: 16px;
    }

    .chat-shell {
        height: 520px;
        padding: 0.78rem;
    }

    .chat-bubble {
        max-width: 82%;
        padding: 0.72rem 0.78rem;
    }

    .chat-avatar {
        width: 34px;
        height: 34px;
    }

    .chat-name {
        font-size: 0.78rem;
    }

    .chat-time {
        font-size: 0.68rem;
    }

    .chat-text {
        font-size: 0.9rem;
    }

    .stButton > button {
        width: 100% !important;
        min-height: 46px !important;
    }
}

@media (max-width: 390px) {
    .chat-bubble {
        max-width: 86%;
    }

    .chat-avatar {
        width: 32px;
        height: 32px;
    }
}
</style>
""", unsafe_allow_html=True)


inject_css()

nama_trip_sembang = "Bilik Sembang"

try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip_sembang = clean_text(trip_info.iloc[0].get('Nama_Trip', 'Bilik Sembang'), "Bilik Sembang")
except:
    pass

st.title(f"💬 Group Chat: {nama_trip_sembang}")

st.markdown(
    '<div class="chat-hero">'
    '<div class="chat-hero-title">Ruang Chat bersama ahli</div>'
    '<div class="chat-hero-sub">Bincang persiapan, logistik, agihan tugasan, dan maklumat penting perkhemahan dalam satu tempat.</div>'
    '</div>',
    unsafe_allow_html=True
)

try:
    users_db = conn.read(worksheet="Users", ttl=600)
    for col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()
except:
    users_db = pd.DataFrame(columns=['Username', 'Full_Name', 'Profile_Pic_URL'])

try:
    chat_db = conn.read(worksheet="Group_Chat", ttl=0)
except:
    chat_db = pd.DataFrame(columns=["ID_Trip", "Username", "Nama_Penuh", "Mesej", "Masa_Hantar"])

avatar_map = {}
avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if not users_db.empty:
    for _, u_row in users_db.iterrows():
        username = clean_text(u_row.get('Username', ''))
        pic = clean_text(u_row.get('Profile_Pic_URL', ''))
        if username:
            avatar_map[username] = pic if pic else avatar_default

chat_semasa = pd.DataFrame()

if not chat_db.empty and 'ID_Trip' in chat_db.columns:
    for col in chat_db.columns:
        chat_db[col] = chat_db[col].astype(str).replace('nan', '').str.strip()

    chat_semasa = chat_db[chat_db['ID_Trip'] == current_trip]

chat_html = ['<div class="chat-shell" id="chatShell">']

if not chat_semasa.empty:
    for _, msg in chat_semasa.iterrows():
        sender_username = clean_text(msg.get('Username', ''))
        sender_name = clean_text(msg.get('Nama_Penuh', sender_username), sender_username or "Ahli")
        text_mesej = clean_text(msg.get('Mesej', ''))
        masa_log = clean_text(msg.get('Masa_Hantar', ''))

        img_avatar = avatar_map.get(sender_username, avatar_default)
        is_self = sender_username == username_semasa

        row_class = "chat-row self" if is_self else "chat-row"
        self_pill = '<span class="chat-self-pill">Anda</span>' if is_self else ""

        chat_html.append(
            f'<div class="{row_class}">'
        )

        if not is_self:
            chat_html.append(
                f'<img class="chat-avatar" src="{html_lib.escape(img_avatar, quote=True)}" alt="{html_lib.escape(sender_name, quote=True)}">'
            )

        chat_html.append(
            f'<div class="chat-bubble">'
            f'<div class="chat-meta">'
            f'<span class="chat-name">{html_lib.escape(sender_name, quote=False)}</span>'
            f'{self_pill}'
            f'<span class="chat-time">{html_lib.escape(masa_log, quote=False)}</span>'
            f'</div>'
            f'<div class="chat-text">{html_lib.escape(text_mesej, quote=False)}</div>'
            f'</div>'
        )

        if is_self:
            chat_html.append(
                f'<img class="chat-avatar" src="{html_lib.escape(img_avatar, quote=True)}" alt="{html_lib.escape(sender_name, quote=True)}">'
            )

        chat_html.append('</div>')

else:
    chat_html.append(
        '<div class="empty-chat">'
        '<div><strong>Belum ada mesej.</strong><span>Mulakan perbualan pertama anda di bawah.</span></div>'
        '</div>'
    )

chat_html.append('</div>')

st.markdown(''.join(chat_html), unsafe_allow_html=True)

st.markdown("""
<script>
const shell = window.parent.document.querySelector('.chat-shell');
if (shell) {
    shell.scrollTop = shell.scrollHeight;
}
</script>
""", unsafe_allow_html=True)

if st.button("👇 Ke Mesej Terkini"):
    st.rerun()

mesej_baru = st.chat_input("Tulis mesej anda di sini...")

if mesej_baru:
    if not current_trip:
        st.error("Ralat: Sila pilih trip aktif di menu tepi dahulu!")
    else:
        mesej_bersih = clean_text(mesej_baru)

        if not mesej_bersih:
            st.warning("Mesej kosong tidak boleh dihantar.")
        else:
            waktu_kl = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%Y-%m-%d %H:%M:%S")

            row_mesej = pd.DataFrame([{
                "ID_Trip": current_trip,
                "Username": username_semasa,
                "Nama_Penuh": nama_semasa,
                "Mesej": mesej_bersih,
                "Masa_Hantar": waktu_kl
            }])

            try:
                try:
                    chat_db_terkini = conn.read(worksheet="Group_Chat", ttl=600)
                except:
                    chat_db_terkini = pd.DataFrame(columns=["ID_Trip", "Username", "Nama_Penuh", "Mesej", "Masa_Hantar"])

                updated_chat = pd.concat([chat_db_terkini, row_mesej], ignore_index=True)
                conn.update(worksheet="Group_Chat", data=updated_chat)

                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menghantar mesej: {e}")
