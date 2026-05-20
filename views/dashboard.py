import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import re
import html as html_lib

current_trip = st.session_state.get("current_trip_id", "")
conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(10,191,138,0.22), transparent 32%),
        radial-gradient(circle at bottom right, rgba(0,119,182,0.24), transparent 34%),
        linear-gradient(135deg, #06131f 0%, #082539 45%, #063b48 100%) !important;
    background-attachment: fixed !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
    z-index: 0;
    animation: bgFloat 18s ease-in-out infinite alternate;
}

.main .block-container {
    max-width: 1180px !important;
    padding: 2rem 1.2rem 3rem !important;
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
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    animation: fadeDown 0.75s ease both !important;
}

p, .stMarkdown p, .stText p {
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

[data-testid="stAlert"] {
    color: rgba(255,255,255,0.92) !important;
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

.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] {
    background: rgba(255,255,255,0.085) !important;
    color: rgba(255,255,255,0.94) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 14px !important;
    min-height: 45px !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label {
    color: rgba(255,255,255,0.72) !important;
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

.profile-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    width: 100%;
}

.profile-card {
    min-width: 0;
    text-align: center;
    padding: 14px 10px;
    border-radius: 18px;
    background: rgba(255,255,255,0.075);
    backdrop-filter: blur(18px) saturate(145%);
    -webkit-backdrop-filter: blur(18px) saturate(145%);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 12px 30px rgba(0,0,0,0.28);
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    animation: fadeUp 0.55s ease both;
    overflow: hidden;
}

.profile-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 42px rgba(0,0,0,0.38);
    border-color: rgba(10,191,138,0.36);
}

.profile-avatar {
    width: 66px;
    height: 66px;
    border-radius: 50%;
    padding: 2px;
    margin: 0 auto 9px auto;
}

.profile-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    display: block;
}

.profile-name {
    margin: 0 0 7px 0 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.92) !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.profile-status {
    max-width: 100%;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
    display: inline-block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.video-glass-card {
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 18px 45px rgba(0,0,0,0.34);
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.075);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    animation: fadeUp 0.65s ease both;
}

.video-glass-card iframe {
    width: 100% !important;
    height: 250px !important;
    border: 0 !important;
    display: block !important;
    border-radius: 18px !important;
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
        font-size: 1.55rem !important;
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

    .profile-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }

    .profile-card {
        padding: 13px 9px;
        min-height: 142px;
    }

    .profile-avatar {
        width: 64px;
        height: 64px;
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

    .video-glass-card iframe {
        height: 220px !important;
    }
}

@media (max-width: 390px) {
    .profile-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    .profile-card {
        padding: 12px 7px;
    }

    .profile-name {
        font-size: 11px !important;
    }

    .profile-status {
        font-size: 9px;
        padding: 4px 7px;
    }
}

@media (max-width: 330px) {
    .profile-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)


def get_yt_embed_url(url):
    if not url or url == "nan":
        return None

    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)

    if video_id_match:
        video_id = video_id_match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"

    return None


try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=600)

    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip["ID_Trip"] == current_trip]

        if not trip_info.empty:
            nama_trip = trip_info.iloc[0]["Nama_Trip"]
            tarikh_str = str(trip_info.iloc[0]["Tarikh"])
        else:
            nama_trip = "Aktiviti Semasa"
            tarikh_str = ""
    else:
        nama_trip = "Aktiviti Semasa"
        tarikh_str = ""
except:
    nama_trip = "Sistem Perkhemahan"
    tarikh_str = ""

st.title(f"🏕️ Papan Pemuka - {nama_trip}")
st.write(f"Selamat Datang, **{st.session_state.get('full_name', 'Pengguna')}**! Pantau profil dan kehadiran penuh ahli kumpulan di bawah.")

if tarikh_str and tarikh_str.lower() != "nan":
    try:
        tarikh_kem = pd.to_datetime(tarikh_str).to_pydatetime()
        hari_ini = datetime.now()
        baki_hari = (tarikh_kem - hari_ini).days

        if baki_hari > 0:
            st.info(f"⏳ **{baki_hari} Hari Lagi** sebelum kita bertolak ke {nama_trip}! Sediakan persiapan fizikal dan mental.")
        elif baki_hari == 0:
            st.success("🎉 **HARI INI KITA BERTOLAK!** Jangan ada barang atau ahli yang tertinggal!")
        else:
            st.write(f"✨ Kenangan Indah {nama_trip}.")
    except:
        st.warning("⚠️ Format tarikh trip tidak sah. Pastikan format YYYY-MM-DD.")

st.divider()

yt_url_raw = ""
k1, k2, k3, k4, k5 = "", "", "", "", ""

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)

    if not info_db.empty and current_trip in info_db["ID_Trip"].values:
        info_semasa = info_db[info_db["ID_Trip"] == current_trip].iloc[0]
        yt_url_raw = str(info_semasa.get("Youtube_URL", "")).replace("nan", "").strip()
        k1 = str(info_semasa.get("Kenangan_1", "")).replace("nan", "").strip()
        k2 = str(info_semasa.get("Kenangan_2", "")).replace("nan", "").strip()
        k3 = str(info_semasa.get("Kenangan_3", "")).replace("nan", "").strip()
        k4 = str(info_semasa.get("Kenangan_4", "")).replace("nan", "").strip()
        k5 = str(info_semasa.get("Kenangan_5", "")).replace("nan", "").strip()
except:
    pass

senarai_kenangan = [k for k in [k1, k2, k3, k4, k5] if k != ""]

try:
    users_db = conn.read(worksheet="Users", ttl=600)

    for col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace("nan", "").str.strip()

    users_member = users_db[users_db["Role"].str.lower() == "member"]
except:
    users_member = pd.DataFrame()

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=600)
    kehadiran_semasa = kehadiran_db[kehadiran_db["ID_Trip"] == current_trip]
except:
    kehadiran_semasa = pd.DataFrame()

if not users_member.empty:
    if not kehadiran_semasa.empty and all(col in kehadiran_semasa.columns for col in ["Username", "Status"]):
        merged_df = pd.merge(users_member, kehadiran_semasa[["Username", "Status"]], on="Username", how="left")
        merged_df["Status"] = merged_df["Status"].fillna("Belum Sahkan")
    else:
        merged_df = users_member.copy()
        merged_df["Status"] = "Belum Sahkan"
else:
    merged_df = pd.DataFrame()

col_profil_utama, col_yt_utama = st.columns([1.8, 1.2])

with col_profil_utama:
    st.subheader("👥 Kad Profil Ahli")
    avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

    if not merged_df.empty:
        warna_map = {
            "Hadir": ("#0abf8a", "rgba(10,191,138,0.15)"),
            "Tidak Hadir": ("#ef4444", "rgba(239,68,68,0.15)"),
            "Belum Pasti": ("#f59e0b", "rgba(245,158,11,0.15)"),
            "Belum Sahkan": ("#6b7280", "rgba(107,114,128,0.15)"),
        }

        profile_cards = []

        for _, r in merged_df.iterrows():
            url_gambar = str(r.get("Profile_Pic_URL", "")).strip()

            if url_gambar == "":
                url_gambar = avatar_default

            status_rsvp = str(r.get("Status", "Belum Sahkan")).strip()
            warna, warna_bg = warna_map.get(status_rsvp, ("#6b7280", "rgba(107,114,128,0.15)"))

            nama_safe = html_lib.escape(str(r.get("Full_Name", "Tanpa Nama")), quote=False)
            status_safe = html_lib.escape(status_rsvp, quote=False)
            url_safe = html_lib.escape(url_gambar, quote=True)

            profile_cards.append(
                f'<div class="profile-card">'
                f'<div class="profile-avatar" style="border: 2.5px solid {warna}; box-shadow: 0 0 14px {warna}66;">'
                f'<img src="{url_safe}" alt="{nama_safe}">'
                f'</div>'
                f'<p class="profile-name">{nama_safe}</p>'
                f'<span class="profile-status" style="background: {warna_bg}; color: {warna}; border: 1px solid {warna}55;">{status_safe}</span>'
                f'</div>'
            )

        st.markdown(
            '<div class="profile-grid">' + "".join(profile_cards) + "</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("Tiada ahli ditemui.")

with col_yt_utama:
    st.subheader("📺 Video Aktiviti")
    yt_embed = get_yt_embed_url(yt_url_raw)

    if yt_embed:
        st.markdown(f"""
<div class="video-glass-card">
    <iframe src="{yt_embed}"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>
""", unsafe_allow_html=True)
    else:
        st.warning("Admin belum menetapkan pautan video YouTube untuk trip ini.")

st.divider()

st.subheader("📊 Rumusan Kehadiran & 📸 Kenang-Kenangan")

kategori_status = ["Hadir", "Tidak Hadir", "Belum Pasti", "Belum Sahkan"]
warna_status = ["#0abf8a", "#ef4444", "#f59e0b", "#6b7280"]

if not merged_df.empty:
    status_counts = merged_df["Status"].value_counts()
else:
    status_counts = pd.Series(dtype=int)

jumlah_status = [int(status_counts.get(s, 0)) for s in kategori_status]
jumlah_semua = sum(jumlah_status)

if jumlah_semua > 0:
    gradient_parts = []
    mula = 0

    for jumlah, warna in zip(jumlah_status, warna_status):
        peratus = (jumlah / jumlah_semua) * 100
        tamat = mula + peratus

        if jumlah > 0:
            gradient_parts.append(f"{warna} {mula:.2f}% {tamat:.2f}%")

        mula = tamat

    conic_gradient = ", ".join(gradient_parts)
else:
    conic_gradient = "rgba(107,114,128,0.55) 0% 100%"

legend_html = "".join([
    f"""
    <div class="dash-legend-item">
        <span class="dash-legend-dot" style="background:{warna};"></span>
        <span class="dash-legend-label">{html_lib.escape(label, quote=False)}</span>
        <span class="dash-legend-count">{jumlah}</span>
    </div>
    """
    for label, jumlah, warna in zip(kategori_status, jumlah_status, warna_status)
])

if len(senarai_kenangan) > 0:
    slides_html = "".join([
        f"""
        <div class="dash-memory-slide">
            <img src="{html_lib.escape(url, quote=True)}" alt="Kenangan trip">
        </div>
        """
        for url in senarai_kenangan
    ])

    dots_html = "".join([
        f'<button class="dash-memory-dot" onclick="goToMemorySlide({i})" aria-label="Kenangan {i + 1}"></button>'
        for i in range(len(senarai_kenangan))
    ])
else:
    slides_html = """
    <div class="dash-memory-empty">
        <strong>Belum ada foto</strong>
        <span>Admin boleh tambah gambar kenangan di panel media.</span>
    </div>
    """
    dots_html = ""

html_kod = f"""
<div class="dash-summary-memory">
    <section class="dash-panel dash-summary-panel">
        <div class="dash-panel-head">
            <span>📊</span>
            <strong>Rumusan</strong>
        </div>

        <div class="dash-donut-wrap">
            <div class="dash-donut" style="background: conic-gradient({conic_gradient});">
                <div class="dash-donut-core">
                    <strong>{jumlah_semua}</strong>
                    <span>Ahli</span>
                </div>
            </div>
        </div>

        <div class="dash-legend">
            {legend_html}
        </div>
    </section>

    <section class="dash-panel dash-memory-panel">
        <div class="dash-panel-head">
            <span>📸</span>
            <strong>Kenangan</strong>
        </div>

        <div class="dash-memory-slider" id="dashMemorySlider">
            {slides_html}

            <button class="dash-memory-nav dash-memory-prev" onclick="changeMemorySlide(-1)">‹</button>
            <button class="dash-memory-nav dash-memory-next" onclick="changeMemorySlide(1)">›</button>

            <div class="dash-memory-dots">
                {dots_html}
            </div>
        </div>
    </section>
</div>

<style>
    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: transparent;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .dash-summary-memory {{
        width: 100%;
        display: grid;
        grid-template-columns: minmax(155px, 0.82fr) minmax(205px, 1.18fr);
        gap: 12px;
        align-items: stretch;
    }}

    .dash-panel {{
        min-width: 0;
        min-height: 286px;
        border-radius: 20px;
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(255,255,255,0.16);
        box-shadow: 0 18px 45px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.10);
        backdrop-filter: blur(18px) saturate(145%);
        -webkit-backdrop-filter: blur(18px) saturate(145%);
        overflow: hidden;
    }}

    .dash-summary-panel {{
        padding: 13px;
        display: flex;
        flex-direction: column;
    }}

    .dash-memory-panel {{
        padding: 13px;
    }}

    .dash-panel-head {{
        height: 28px;
        display: flex;
        align-items: center;
        gap: 7px;
        color: rgba(255,255,255,0.95);
        font-size: 0.88rem;
        font-weight: 800;
        margin-bottom: 10px;
    }}

    .dash-donut-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2px 0 8px;
    }}

    .dash-donut {{
        width: 145px;
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        display: grid;
        place-items: center;
        box-shadow: 0 14px 34px rgba(0,0,0,0.32);
    }}

    .dash-donut-core {{
        width: 58%;
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        background: rgba(5,20,31,0.88);
        border: 1px solid rgba(255,255,255,0.12);
        display: grid;
        place-items: center;
        align-content: center;
    }}

    .dash-donut-core strong {{
        color: white;
        font-size: 1.22rem;
        line-height: 1;
    }}

    .dash-donut-core span {{
        color: rgba(255,255,255,0.60);
        font-size: 0.66rem;
        font-weight: 800;
        margin-top: 2px;
    }}

    .dash-legend {{
        display: grid;
        gap: 6px;
        margin-top: auto;
    }}

    .dash-legend-item {{
        min-width: 0;
        display: grid;
        grid-template-columns: 10px 1fr auto;
        align-items: center;
        gap: 7px;
        padding: 6px 8px;
        border-radius: 12px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
    }}

    .dash-legend-dot {{
        width: 9px;
        height: 9px;
        border-radius: 99px;
    }}

    .dash-legend-label {{
        color: rgba(255,255,255,0.78);
        font-size: 0.72rem;
        font-weight: 800;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .dash-legend-count {{
        color: white;
        font-size: 0.75rem;
        font-weight: 900;
    }}

    .dash-memory-slider {{
        position: relative;
        width: 100%;
        height: 232px;
        overflow: hidden;
        border-radius: 16px;
        background: rgba(0,0,0,0.24);
        touch-action: pan-y;
    }}

    .dash-memory-slide {{
        display: none;
        position: relative;
        width: 100%;
        height: 100%;
        animation: memoryFade 0.55s ease both;
    }}

    .dash-memory-slide img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        display: block;
        transform: none;
        animation: none;
    }}

    .dash-memory-empty {{
        height: 100%;
        display: grid;
        place-items: center;
        align-content: center;
        gap: 4px;
        text-align: center;
        padding: 16px;
    }}

    .dash-memory-empty strong {{
        color: white;
        font-size: 0.92rem;
    }}

    .dash-memory-empty span {{
        color: rgba(255,255,255,0.62);
        font-size: 0.78rem;
        line-height: 1.35;
    }}

    .dash-memory-nav {{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 34px;
        height: 34px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.22);
        background: rgba(5,20,31,0.56);
        color: white;
        font-size: 22px;
        line-height: 1;
        cursor: pointer;
        z-index: 5;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.22s ease, background 0.22s ease;
    }}

    .dash-memory-nav:hover {{
        background: rgba(10,191,138,0.72);
        transform: translateY(-50%) scale(1.07);
    }}

    .dash-memory-prev {{
        left: 9px;
    }}

    .dash-memory-next {{
        right: 9px;
    }}

    .dash-memory-dots {{
        position: absolute;
        left: 50%;
        bottom: 9px;
        transform: translateX(-50%);
        display: flex;
        gap: 6px;
        z-index: 6;
        padding: 6px 8px;
        border-radius: 999px;
        background: rgba(5,20,31,0.36);
        border: 1px solid rgba(255,255,255,0.12);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}

    .dash-memory-dot {{
        width: 7px;
        height: 7px;
        border: 0;
        border-radius: 999px;
        background: rgba(255,255,255,0.42);
        cursor: pointer;
        transition: width 0.25s ease, background 0.25s ease;
    }}

    .dash-memory-dot.active {{
        width: 22px;
        background: #0abf8a;
    }}

    @keyframes memoryFade {{
        from {{ opacity: 0; transform: translateX(10px) scale(1.01); }}
        to {{ opacity: 1; transform: translateX(0) scale(1); }}
    }}

    @media (max-width: 520px) {{
        .dash-summary-memory {{
            grid-template-columns: minmax(132px, 0.78fr) minmax(176px, 1.22fr);
            gap: 8px;
        }}

        .dash-panel {{
            min-height: 254px;
            border-radius: 16px;
        }}

        .dash-summary-panel,
        .dash-memory-panel {{
            padding: 8px;
        }}

        .dash-panel-head {{
            height: 24px;
            font-size: 0.76rem;
            gap: 5px;
            margin-bottom: 7px;
        }}

        .dash-donut {{
            width: 104px;
        }}

        .dash-donut-core strong {{
            font-size: 0.98rem;
        }}

        .dash-donut-core span {{
            font-size: 0.56rem;
        }}

        .dash-legend {{
            gap: 4px;
        }}

        .dash-legend-item {{
            grid-template-columns: 8px 1fr auto;
            gap: 5px;
            padding: 5px 6px;
            border-radius: 10px;
        }}

        .dash-legend-dot {{
            width: 7px;
            height: 7px;
        }}

        .dash-legend-label {{
            font-size: 0.58rem;
        }}

        .dash-legend-count {{
            font-size: 0.62rem;
        }}

        .dash-memory-slider {{
            height: 215px;
            border-radius: 14px;
        }}

        .dash-memory-nav {{
            width: 30px;
            height: 30px;
            font-size: 19px;
        }}

        .dash-memory-prev {{
            left: 7px;
        }}

        .dash-memory-next {{
            right: 7px;
        }}
    }}

    @media (max-width: 360px) {{
        .dash-summary-memory {{
            grid-template-columns: 1fr;
        }}

        .dash-memory-slider {{
            height: 230px;
        }}
    }}
</style>

<script>
    let dashMemoryIndex = 0;
    let dashMemoryTimer = null;

    const dashSlides = document.querySelectorAll(".dash-memory-slide");
    const dashDots = document.querySelectorAll(".dash-memory-dot");
    const dashSlider = document.getElementById("dashMemorySlider");

    function showDashMemorySlide(index) {{
        if (!dashSlides.length) return;

        dashSlides.forEach(slide => {{
            slide.style.display = "none";
        }});

        dashDots.forEach(dot => {{
            dot.classList.remove("active");
        }});

        dashMemoryIndex = (index + dashSlides.length) % dashSlides.length;
        dashSlides[dashMemoryIndex].style.display = "block";

        if (dashDots[dashMemoryIndex]) {{
            dashDots[dashMemoryIndex].classList.add("active");
        }}

        clearTimeout(dashMemoryTimer);
        dashMemoryTimer = setTimeout(() => {{
            showDashMemorySlide(dashMemoryIndex + 1);
        }}, 4200);
    }}

    function changeMemorySlide(direction) {{
        clearTimeout(dashMemoryTimer);
        showDashMemorySlide(dashMemoryIndex + direction);
    }}

    function goToMemorySlide(index) {{
        clearTimeout(dashMemoryTimer);
        showDashMemorySlide(index);
    }}

    let dashTouchStartX = 0;

    if (dashSlider) {{
        dashSlider.addEventListener("touchstart", function(event) {{
            dashTouchStartX = event.touches[0].clientX;
        }}, {{ passive: true }});

        dashSlider.addEventListener("touchend", function(event) {{
            const touchEndX = event.changedTouches[0].clientX;
            const difference = dashTouchStartX - touchEndX;

            if (Math.abs(difference) > 45) {{
                changeMemorySlide(difference > 0 ? 1 : -1);
            }}
        }});
    }}

    showDashMemorySlide(0);
</script>
"""

components.html(html_kod, height=310)

st.divider()

if st.button("🚀 Buka Halaman Pengesahan Kehadiran (RSVP)", use_container_width=True, type="primary"):
    st.switch_page("views/kehadiran.py")

if st.session_state.get("role", "") == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Admin: Urus Media")

    with st.form("form_media_admin"):
        st.write("### 📺 Pautan YouTube")
        in_yt = st.text_input("Masukkan URL YouTube (Contoh: https://www.youtube.com/watch?v=xxxx)", value=yt_url_raw)

        st.write("### 🖼️ Gambar Kenangan")
        in_k1 = st.text_input("Kenangan 1", value=k1)
        in_k2 = st.text_input("Kenangan 2", value=k2)
        in_k3 = st.text_input("Kenangan 3", value=k3)
        in_k4 = st.text_input("Kenangan 4", value=k4)
        in_k5 = st.text_input("Kenangan 5", value=k5)

        submit_media = st.form_submit_button("Simpan Semua Media")

        if submit_media:
            if not current_trip:
                st.error("Pilih trip di sidebar!")
            else:
                try:
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=600)

                    kolum_media = ["Youtube_URL", "Kenangan_1", "Kenangan_2", "Kenangan_3", "Kenangan_4", "Kenangan_5"]

                    for col in kolum_media:
                        if col not in info_pukal.columns:
                            info_pukal[col] = ""

                        info_pukal[col] = info_pukal[col].astype(str).replace("nan", "")

                    if current_trip in info_pukal["ID_Trip"].values:
                        idx = info_pukal.index[info_pukal["ID_Trip"] == current_trip][0]
                        info_pukal.at[idx, "Youtube_URL"] = str(in_yt).strip()
                        info_pukal.at[idx, "Kenangan_1"] = str(in_k1).strip()
                        info_pukal.at[idx, "Kenangan_2"] = str(in_k2).strip()
                        info_pukal.at[idx, "Kenangan_3"] = str(in_k3).strip()
                        info_pukal.at[idx, "Kenangan_4"] = str(in_k4).strip()
                        info_pukal.at[idx, "Kenangan_5"] = str(in_k5).strip()

                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Media dikemaskini!")

                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Ralat: {e}")
