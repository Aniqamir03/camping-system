import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import html as html_lib


current_trip = st.session_state.get('current_trip_id', '')
username_semasa = st.session_state.get('username', '')
nama_semasa = st.session_state.get('full_name', 'Pengguna')

conn = st.connection("gsheets", type=GSheetsConnection)


def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
}

:root {
    --teal: #0abf8a;
    --cyan: #00a6c8;
    --blue: #0077b6;
    --glass: rgba(255,255,255,0.075);
    --border: rgba(255,255,255,0.14);
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
    max-width: 960px !important;
    padding: 2rem 1.2rem 3rem !important;
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
    font-size: clamp(1.65rem, 4vw, 2.45rem) !important;
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
    animation: fadeDown 0.7s ease both !important;
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
    margin: 1.6rem 0 !important;
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

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 46px !important;
    border: 0 !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.35rem !important;
    background: linear-gradient(135deg, #0abf8a 0%, #00a6c8 52%, #0077b6 100%) !important;
    color: white !important;
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

.stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(0) scale(0.98) !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] {
    background: rgba(255,255,255,0.085) !important;
    color: rgba(255,255,255,0.94) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 14px !important;
    min-height: 45px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transition: border 0.25s ease, box-shadow 0.25s ease, background 0.25s ease !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(10,191,138,0.72) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.16) !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label {
    color: rgba(255,255,255,0.76) !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    animation: fadeUp 0.7s ease both !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

[data-testid="stMetric"] {
    padding: 1rem !important;
}

[data-testid="stMetric"] label,
[data-testid="stMetric"] div {
    color: rgba(255,255,255,0.92) !important;
}

[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    box-shadow: 0 18px 45px rgba(0,0,0,0.24) !important;
}

.rsvp-hero {
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

.rsvp-hero-title {
    color: rgba(255,255,255,0.96);
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.rsvp-hero-sub {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    line-height: 1.45;
}

.status-card {
    display: flex;
    align-items: center;
    gap: 13px;
    margin: 1rem 0 1.1rem;
    padding: 1rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.65s ease both;
}

.status-icon {
    width: 52px;
    height: 52px;
    border-radius: 17px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.45rem;
    flex-shrink: 0;
    box-shadow: 0 12px 28px rgba(0,0,0,0.22);
}

.status-label {
    color: rgba(255,255,255,0.60);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.status-value {
    color: rgba(255,255,255,0.97);
    font-size: 1.06rem;
    font-weight: 800;
    line-height: 1.25;
}

.status-note {
    color: rgba(255,255,255,0.66);
    font-size: 0.88rem;
    margin-top: 4px;
    overflow-wrap: anywhere;
}

.section-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 0.9rem 1.05rem;
    margin: 1.2rem 0 0.9rem;
    box-shadow: 0 18px 45px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeDown 0.6s ease both;
}

.section-icon {
    width: 42px;
    height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(10,191,138,0.28), rgba(0,119,182,0.28));
    border: 1px solid rgba(255,255,255,0.14);
    font-size: 1.35rem;
    flex-shrink: 0;
}

.section-title {
    color: white;
    font-weight: 800;
    font-size: 1.16rem;
    line-height: 1.2;
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

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.75rem 2.4rem !important;
    }

    h1 {
        font-size: 1.45rem !important;
    }

    h2, h3 {
        font-size: 1.08rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.9rem !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    [data-testid="stForm"] {
        padding: 1rem !important;
        border-radius: 16px !important;
    }

    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 0.9rem !important;
    }

    .rsvp-hero,
    .status-card,
    .section-heading {
        border-radius: 16px;
    }

    .status-card {
        align-items: flex-start;
        padding: 0.92rem;
    }

    .status-icon {
        width: 46px;
        height: 46px;
        border-radius: 15px;
        font-size: 1.25rem;
    }

    .status-value {
        font-size: 0.98rem;
    }

    .section-icon {
        width: 38px;
        height: 38px;
        font-size: 1.2rem;
    }

    .section-title {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


def section_header(icon: str, title: str):
    st.markdown(
        f'<div class="section-heading"><span class="section-icon">{html_lib.escape(icon, quote=False)}</span><span class="section-title">{html_lib.escape(title, quote=False)}</span></div>',
        unsafe_allow_html=True
    )

def clean_text(value, default=""):
    try:
        if value is None or pd.isna(value):
            return default
    except:
        pass

    value = str(value).replace("nan", "").strip()
    return value if value else default


def status_card(status: str, catatan: str):
    status = clean_text(status, "Belum Sahkan")
    catatan = clean_text(catatan, "")

    config = {
        "Hadir": ("✅", "#0abf8a", "rgba(10,191,138,0.16)", "Kehadiran Disahkan"),
        "Tidak Hadir": ("❌", "#ef4444", "rgba(239,68,68,0.16)", "Tidak Dapat Hadir"),
        "Belum Pasti": ("⚠️", "#f59e0b", "rgba(245,158,11,0.16)", "Masih Belum Pasti"),
        "Belum Sahkan": ("ℹ️", "#00a6c8", "rgba(0,166,200,0.16)", "Belum Buat Pengesahan"),
    }

    icon, color, bg, label = config.get(status, config["Belum Sahkan"])
    note = html_lib.escape(catatan, quote=False) if catatan else "Tiada catatan tambahan."
    status_safe = html_lib.escape(status, quote=False)
    label_safe = html_lib.escape(label, quote=False)

    st.markdown(
        f'<div class="status-card">'
        f'<div class="status-icon" style="background:{bg}; border:1px solid {color}66; color:{color};">{icon}</div>'
        f'<div>'
        f'<div class="status-label">{label_safe}</div>'
        f'<div class="status-value">{status_safe}</div>'
        f'<div class="status-note">{note}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


inject_css()

st.title("📝 Attendance Confirmation (RSVP)")

st.markdown(
    '<div class="rsvp-hero">'
    '<div class="rsvp-hero-title">Confirm your attendance status</div>'
    '<div class="rsvp-hero-sub">This information helps with logistics, campsite planning, and group coordination.</div>'
    '</div>',
    unsafe_allow_html=True
)

nama_trip_paparan = "Aktiviti Semasa"

try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=600)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip_paparan = trip_info.iloc[0]['Nama_Trip']
except:
    pass

st.info(f"📍 You are currently managing the attendance status for: **{nama_trip_paparan}**")

status_semasa_user = "Belum Sahkan"
catatan_semasa_user = ""

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=600)

    if not kehadiran_db.empty:
        for col in kehadiran_db.columns:
            kehadiran_db[col] = kehadiran_db[col].astype(str).replace('nan', '').str.strip()

        rekod_user = kehadiran_db[
            (kehadiran_db['ID_Trip'] == current_trip) &
            (kehadiran_db['Username'] == username_semasa)
        ]

        if not rekod_user.empty:
            status_semasa_user = clean_text(rekod_user.iloc[0].get('Status', 'Belum Sahkan'), "Belum Sahkan")
            catatan_semasa_user = clean_text(rekod_user.iloc[0].get('Catatan', ''), "")
except:
    kehadiran_db = pd.DataFrame(columns=["ID_Trip", "Username", "Full_Name", "Status", "Catatan", "Masa_Sahkan"])

status_card(status_semasa_user, catatan_semasa_user)

with st.form("form_rsvp_page"):
    st.write("### Pilihan Kehadiran")
    st.write("Please update your attendance status below.")

    list_status = ["Hadir", "Tidak Hadir", "Belum Pasti"]
    default_idx = list_status.index(status_semasa_user) if status_semasa_user in list_status else 0

    inp_status = st.selectbox("Status Kehadiran:", list_status, index=default_idx)
    inp_catatan = st.text_input("Catatan / Nota Tambahan (Pilihan):", value=catatan_semasa_user)

    submit_rsvp = st.form_submit_button("Submit")

    if submit_rsvp:
        if not current_trip:
            st.error("Ralat: Tiada aktiviti aktif dikesan di menu tepi!")
        else:
            masa_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data_rsvp_baru = pd.DataFrame([{
                "ID_Trip": current_trip,
                "Username": username_semasa,
                "Full_Name": nama_semasa,
                "Status": inp_status,
                "Catatan": inp_catatan.strip(),
                "Masa_Sahkan": masa_sekarang
            }])

            try:
                if not kehadiran_db.empty and 'ID_Trip' in kehadiran_db.columns and 'Username' in kehadiran_db.columns:
                    kehadiran_db = kehadiran_db[
                        ~((kehadiran_db['ID_Trip'] == current_trip) &
                          (kehadiran_db['Username'] == username_semasa))
                    ]
                    updated_kehadiran = pd.concat([kehadiran_db, data_rsvp_baru], ignore_index=True)
                else:
                    updated_kehadiran = data_rsvp_baru
            except:
                updated_kehadiran = data_rsvp_baru

            conn.update(worksheet="Kehadiran", data=updated_kehadiran)
            st.success("Attendance status updated successfully!")
            st.cache_data.clear()
            st.rerun()


if st.session_state.get("role", "") == "Admin":
    st.divider()
    section_header("📊", "Panel Pemantauan Kehadiran Kumpulan")

    try:
        db_kehadiran_papar = conn.read(worksheet="Kehadiran", ttl=600)

        if not db_kehadiran_papar.empty and 'ID_Trip' in db_kehadiran_papar.columns:
            for col in db_kehadiran_papar.columns:
                db_kehadiran_papar[col] = db_kehadiran_papar[col].astype(str).replace('nan', '').str.strip()

            kehadiran_trip_ini = db_kehadiran_papar[db_kehadiran_papar['ID_Trip'] == current_trip]

            if not kehadiran_trip_ini.empty:
                k_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Hadir'])
                k_tak_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Tidak Hadir'])
                k_pasti = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Belum Pasti'])

                c1, c2, c3 = st.columns(3)
                c1.metric("🟢 Jumlah Hadir", f"{k_hadir} Orang")
                c2.metric("🔴 Tidak Hadir", f"{k_tak_hadir} Orang")
                c3.metric("🟡 Belum Pasti", f"{k_pasti} Orang")

                st.write("▼ **Senarai Status Respon Keseluruhan Ahli:**")
                kolum_papar_kehadiran = ['Full_Name', 'Status', 'Catatan', 'Masa_Sahkan']
                kolum_wujud = [col for col in kolum_papar_kehadiran if col in kehadiran_trip_ini.columns]

                st.dataframe(
                    kehadiran_trip_ini[kolum_wujud],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Belum ada mana-mana ahli yang merekodkan status maklum balas mereka.")
        else:
            st.info("ℹ️ Pangkalan data maklum balas kehadiran masih kosong.")
    except Exception:
        st.write("Buku rekod kehadiran sedia ada masih bersih daripada data.")
