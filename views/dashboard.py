import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import altair as alt
import streamlit.components.v1 as components
import re

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)

# ═══════════════════════════════════════════════════════════════════
# 🎨 UI ENHANCEMENT — INJECT CSS SAHAJA (TIADA PERUBAHAN LOGIC)
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ── GLOBAL RESET & FONT ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── APP BACKGROUND ── */
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2240 40%, #0a3550 100%) !important;
    background-attachment: fixed !important;
}

/* Subtle animated grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(circle at 20% 20%, rgba(10,191,138,0.07) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(0,119,182,0.07) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ── MAIN CONTENT AREA ── */
.main .block-container {
    background: transparent !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* ── SIDEBAR GLASS ── */
[data-testid="stSidebar"] {
    background: rgba(10, 22, 40, 0.75) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── PAGE TITLE ── */
h1 {
    font-size: clamp(1.5rem, 3vw, 2rem) !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #ffffff 0%, rgba(10,191,138,0.9) 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.5px !important;
    padding-bottom: 4px !important;
    animation: fadeSlideDown 0.7s ease both !important;
}

/* ── SUBHEADERS ── */
h2, h3 {
    color: rgba(255,255,255,0.9) !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px !important;
    animation: fadeSlideDown 0.8s ease 0.1s both !important;
}

/* ── PARAGRAPH / WRITE TEXT ── */
.stMarkdown p,
.stText p,
p {
    color: rgba(255,255,255,0.75) !important;
}

strong {
    color: rgba(255,255,255,0.95) !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    margin: 1.5rem 0 !important;
}

/* ── INFO / SUCCESS / WARNING / ERROR BANNERS ── */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.9) !important;
    animation: fadeSlideUp 0.6s ease both !important;
}

[data-testid="stAlert"][data-baseweb="notification"] svg {
    color: #0abf8a !important;
}

/* ── COUNTDOWN INFO BOX ── */
div[data-testid="stInfo"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.12), rgba(0,119,182,0.12)) !important;
    border: 1px solid rgba(10,191,138,0.3) !important;
    border-radius: 14px !important;
}

div[data-testid="stSuccess"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.15), rgba(10,191,138,0.05)) !important;
    border: 1px solid rgba(10,191,138,0.4) !important;
    border-radius: 14px !important;
}

div[data-testid="stWarning"] {
    background: linear-gradient(135deg, rgba(255,193,7,0.12), rgba(255,193,7,0.04)) !important;
    border: 1px solid rgba(255,193,7,0.3) !important;
    border-radius: 14px !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #0abf8a, #0077b6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 28px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 20px rgba(10,191,138,0.28) !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 10px 30px rgba(10,191,138,0.45) !important;
    background: linear-gradient(135deg, #0dd49b, #0088cc) !important;
}

.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ── FORM & INPUT ── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 1.5rem !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.9) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.25s ease !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border: 1px solid rgba(10,191,138,0.7) !important;
    box-shadow: 0 0 0 3px rgba(10,191,138,0.15) !important;
    background: rgba(255,255,255,0.1) !important;
    outline: none !important;
}

.stTextInput label,
.stTextArea label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #0abf8a, #0077b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 16px rgba(10,191,138,0.3) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(10,191,138,0.5) !important;
}

/* ── COLUMNS ── */
[data-testid="stHorizontalBlock"] {
    gap: 1.2rem !important;
    animation: fadeSlideUp 0.7s ease 0.15s both !important;
}

/* ── ALTAIR CHART BACKGROUND ── */
.vega-embed {
    background: transparent !important;
}

.vega-embed canvas {
    border-radius: 12px !important;
}

/* ── IFRAME (video) ── */
iframe {
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); border-radius: 10px; }
::-webkit-scrollbar-thumb { background: rgba(10,191,138,0.35); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(10,191,138,0.6); }

/* ── ANIMATIONS ── */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.75rem 2rem !important;
    }
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.1rem !important; }
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.8rem !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
    }
}

@media (max-width: 480px) {
    .stButton > button {
        padding: 10px 18px !important;
        font-size: 0.85rem !important;
    }
}

</style>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════


# --- FUNGSI PEMPROSESAN URL YOUTUBE ---
def get_yt_embed_url(url):
    if not url or url == 'nan':
        return None
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"
    return None


# --- 0. TARIK INFO TRIP UTAMA ---
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=600)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip = trip_info.iloc[0]['Nama_Trip']
            tarikh_str = str(trip_info.iloc[0]['Tarikh'])
        else:
            nama_trip = "Aktiviti Semasa"
            tarikh_str = ""
    else:
        nama_trip = "Aktiviti Semasa"
        tarikh_str = ""
except:
    nama_trip = "Sistem Perkhemahan"
    tarikh_str = ""

st.title(f"🏕️ Papan Pemuka — {nama_trip}")
st.write(f"Selamat Datang, **{st.session_state['full_name']}**! Pantau profil dan kehadiran penuh ahli kumpulan di bawah.")


# --- 1. KIRAAN DETIK (COUNTDOWN) ---
if tarikh_str and tarikh_str.lower() != 'nan':
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


# --- PERSEDIAAN DATA: TARIK INFO_KEM (VIDEO & KENANGAN) ---
yt_url_raw = ""
k1, k2, k3, k4, k5 = "", "", "", "", ""
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if not info_db.empty and current_trip in info_db['ID_Trip'].values:
        info_semasa = info_db[info_db['ID_Trip'] == current_trip].iloc[0]
        yt_url_raw = str(info_semasa.get('Youtube_URL', '')).replace('nan', '').strip()
        k1 = str(info_semasa.get('Kenangan_1', '')).replace('nan', '').strip()
        k2 = str(info_semasa.get('Kenangan_2', '')).replace('nan', '').strip()
        k3 = str(info_semasa.get('Kenangan_3', '')).replace('nan', '').strip()
        k4 = str(info_semasa.get('Kenangan_4', '')).replace('nan', '').strip()
        k5 = str(info_semasa.get('Kenangan_5', '')).replace('nan', '').strip()
except:
    pass

senarai_kenangan = [k for k in [k1, k2, k3, k4, k5] if k != ""]


# --- PERSEDIAAN DATA: USERS & KEHADIRAN ---
try:
    users_db = conn.read(worksheet="Users", ttl=600)
    for col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()
    users_member = users_db[users_db['Role'].str.lower() == 'member']
except:
    users_member = pd.DataFrame()

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=600)
    kehadiran_semasa = kehadiran_db[kehadiran_db['ID_Trip'] == current_trip]
except:
    kehadiran_semasa = pd.DataFrame()

if not users_member.empty:
    merged_df = pd.merge(users_member, kehadiran_semasa[['Username', 'Status']], on='Username', how='left')
    merged_df['Status'] = merged_df['Status'].fillna('Belum Sahkan')
else:
    merged_df = pd.DataFrame()


# --- 2. SUSUNAN ATAS: PROFIL AHLI (KIRI) & YOUTUBE (KANAN) ---
col_profil_utama, col_yt_utama = st.columns([1.8, 1.2])

with col_profil_utama:
    st.subheader("👥 Kad Profil Ahli")
    avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

    if not merged_df.empty:
        kolum_grid = 3
        pecahan_baris = [merged_df[i:i + kolum_grid] for i in range(0, len(merged_df), kolum_grid)]

        for baris_data in pecahan_baris:
            cols = st.columns(kolum_grid)
            for indeks, (_, r) in enumerate(baris_data.iterrows()):
                with cols[indeks]:
                    url_gambar = r['Profile_Pic_URL'] if r['Profile_Pic_URL'] != "" else avatar_default
                    status_rsvp = r['Status']

                    # ── UI ENHANCED: richer card HTML, same logic ──
                    warna_map = {
                        "Hadir":         ("#0abf8a", "rgba(10,191,138,0.15)"),
                        "Tidak Hadir":   ("#ef4444", "rgba(239,68,68,0.15)"),
                        "Belum Pasti":   ("#f59e0b", "rgba(245,158,11,0.15)"),
                        "Belum Sahkan":  ("#6b7280", "rgba(107,114,128,0.15)"),
                    }
                    warna, warna_bg = warna_map.get(status_rsvp, ("#6b7280", "rgba(107,114,128,0.15)"))

                    st.markdown(f"""
                    <div style="
                        text-align: center;
                        padding: 14px 10px;
                        border-radius: 16px;
                        margin-bottom: 12px;
                        background: rgba(255,255,255,0.05);
                        backdrop-filter: blur(12px);
                        -webkit-backdrop-filter: blur(12px);
                        border: 1px solid rgba(255,255,255,0.1);
                        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                        animation: fadeSlideUp 0.6s ease both;
                    " onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 10px 28px rgba(0,0,0,0.4)'"
                       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 16px rgba(0,0,0,0.25)'">
                        <div style="
                            width: 62px; height: 62px;
                            border-radius: 50%;
                            border: 2.5px solid {warna};
                            padding: 2px;
                            margin: 0 auto 8px auto;
                            box-shadow: 0 0 12px {warna}55;
                        ">
                            <img src="{url_gambar}"
                                 style="width:100%; height:100%; object-fit:cover; border-radius:50%; display:block;">
                        </div>
                        <p style="
                            margin: 0 0 6px 0;
                            font-size: 12px;
                            font-weight: 600;
                            color: rgba(255,255,255,0.9);
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                            font-family: 'Plus Jakarta Sans', sans-serif;
                        ">{r['Full_Name']}</p>
                        <span style="
                            background: {warna_bg};
                            color: {warna};
                            border: 1px solid {warna}55;
                            padding: 3px 10px;
                            border-radius: 50px;
                            font-size: 10px;
                            font-weight: 600;
                            letter-spacing: 0.3px;
                            display: inline-block;
                            font-family: 'Plus Jakarta Sans', sans-serif;
                        ">{status_rsvp}</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Tiada ahli ditemui.")

with col_yt_utama:
    st.subheader("📺 Video Aktiviti")
    yt_embed = get_yt_embed_url(yt_url_raw)
    if yt_embed:
        st.markdown(f"""
        <div style="
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
            animation: fadeSlideUp 0.7s ease 0.2s both;
        ">
            <iframe width="100%" height="250" src="{yt_embed}"
            title="YouTube video player" frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen style="display:block;"></iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Admin belum menetapkan pautan video YouTube untuk trip ini.")

st.divider()


# --- 3. GABUNGAN CARTA PAI (KIRI) & SLIDESHOW KENANGAN (KANAN) ---
st.subheader("📊 Rumusan Kehadiran & 📸 Kenang-Kenangan")
col_kiri, col_kanan = st.columns([1, 1.2])

with col_kiri:
    if not merged_df.empty:
        status_counts = merged_df['Status'].value_counts()
        kategori_status = ['Hadir', 'Tidak Hadir', 'Belum Pasti', 'Belum Sahkan']
        warna_status = ['#0abf8a', '#ef4444', '#f59e0b', '#6b7280']
        df_pie = pd.DataFrame({
            'Status': kategori_status,
            'Jumlah': [int(status_counts.get(s, 0)) for s in kategori_status],
            'Warna': warna_status
        })
        df_pie = df_pie[df_pie['Jumlah'] > 0]

        if not df_pie.empty:
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Jumlah", type="quantitative"),
                color=alt.Color(
                    field="Status", type="nominal",
                    scale=alt.Scale(domain=kategori_status, range=warna_status),
                    legend=alt.Legend(title="Status", labelColor="#ccc", titleColor="#ccc")
                ),
                tooltip=['Status', 'Jumlah']
            ).properties(
                width=280, height=280
            ).configure_view(
                strokeWidth=0
            ).configure(
                background='transparent'
            )
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.write("Belum ada rekod.")

with col_kanan:
    if len(senarai_kenangan) > 0:
        # ── UI ENHANCED: upgraded slideshow with dots + arrows + swipe ──
        divs_gambar = "".join([
            f'<div class="mySlidesMemory fadeMemory">'
            f'<img src="{url}" style="width:100%; height:280px; object-fit:cover; border-radius:0;">'
            f'</div>'
            for url in senarai_kenangan
        ])

        html_kod = f"""
        <div style="
            border-radius: 16px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 8px 32px rgba(0,0,0,0.45);
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <!-- Slides -->
            <div class="slideshow-container-mem" style="position:relative;">
                {divs_gambar}
            </div>

            <!-- Arrow buttons -->
            <button onclick="changeSlide(-1)" style="
                position:absolute; top:50%; left:10px;
                transform:translateY(-50%);
                background:rgba(0,0,0,0.45); border:1px solid rgba(255,255,255,0.2);
                color:#fff; width:34px; height:34px; border-radius:50%;
                font-size:16px; cursor:pointer; z-index:10;
                display:flex; align-items:center; justify-content:center;
                backdrop-filter:blur(6px); transition:background 0.2s;
            " onmouseover="this.style.background='rgba(10,191,138,0.5)'"
               onmouseout="this.style.background='rgba(0,0,0,0.45)'">‹</button>

            <button onclick="changeSlide(1)" style="
                position:absolute; top:50%; right:10px;
                transform:translateY(-50%);
                background:rgba(0,0,0,0.45); border:1px solid rgba(255,255,255,0.2);
                color:#fff; width:34px; height:34px; border-radius:50%;
                font-size:16px; cursor:pointer; z-index:10;
                display:flex; align-items:center; justify-content:center;
                backdrop-filter:blur(6px); transition:background 0.2s;
            " onmouseover="this.style.background='rgba(10,191,138,0.5)'"
               onmouseout="this.style.background='rgba(0,0,0,0.45)'">›</button>

            <!-- Indicator dots -->
            <div id="dotsContainer" style="
                position:absolute; bottom:10px; left:50%;
                transform:translateX(-50%);
                display:flex; gap:6px; z-index:10;
            "></div>
        </div>

        <style>
            .mySlidesMemory {{ display: none; }}
            .fadeMemory {{ animation: fadeMem 0.8s ease; }}
            @keyframes fadeMem {{ from {{ opacity:0; transform:scale(1.03); }} to {{ opacity:1; transform:scale(1); }} }}
        </style>

        <script>
            let slideIndex = 0;
            let autoTimer;
            const slides = document.getElementsByClassName("mySlidesMemory");
            const dotsBox = document.getElementById("dotsContainer");

            // Build dots
            for (let i = 0; i < slides.length; i++) {{
                let d = document.createElement("div");
                d.onclick = () => {{ clearTimeout(autoTimer); goTo(i); }};
                dotsBox.appendChild(d);
            }}

            function goTo(n) {{
                for (let s of slides) s.style.display = "none";
                for (let d of dotsBox.children) {{
                    d.style.cssText = "width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.35);cursor:pointer;transition:all 0.3s;";
                }}
                slideIndex = (n + slides.length) % slides.length;
                slides[slideIndex].style.display = "block";
                slides[slideIndex].className = "mySlidesMemory fadeMemory";
                dotsBox.children[slideIndex].style.cssText =
                    "width:22px;height:8px;border-radius:50px;background:#0abf8a;cursor:pointer;transition:all 0.3s;";
                autoTimer = setTimeout(() => goTo(slideIndex + 1), 4000);
            }}

            function changeSlide(dir) {{
                clearTimeout(autoTimer);
                goTo(slideIndex + dir);
            }}

            // Swipe support
            let touchStartX = 0;
            let container = document.querySelector(".slideshow-container-mem");
            container.addEventListener("touchstart", e => {{ touchStartX = e.touches[0].clientX; }});
            container.addEventListener("touchend", e => {{
                let diff = touchStartX - e.changedTouches[0].clientX;
                if (Math.abs(diff) > 40) {{ clearTimeout(autoTimer); goTo(slideIndex + (diff > 0 ? 1 : -1)); }}
            }});

            goTo(0);
        </script>
        """
        components.html(html_kod, height=310)
    else:
        st.info("Ruangan memori kosong.")

st.divider()


# --- 4. BUTANG RSVP ---
if st.button("🚀 Buka Halaman Pengesahan Kehadiran (RSVP)", use_container_width=True, type="primary"):
    st.switch_page("views/kehadiran.py")


# --- 5. PANEL ADMIN: URUS VIDEO & GAMBAR ---
if st.session_state["role"] == "Admin":
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

                    kolum_media = ['Youtube_URL', 'Kenangan_1', 'Kenangan_2', 'Kenangan_3', 'Kenangan_4', 'Kenangan_5']
                    for col in kolum_media:
                        if col not in info_pukal.columns:
                            info_pukal[col] = ""
                        info_pukal[col] = info_pukal[col].astype(str).replace('nan', '')

                    if current_trip in info_pukal['ID_Trip'].values:
                        idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                        info_pukal.at[idx, 'Youtube_URL'] = str(in_yt).strip()
                        info_pukal.at[idx, 'Kenangan_1'] = str(in_k1).strip()
                        info_pukal.at[idx, 'Kenangan_2'] = str(in_k2).strip()
                        info_pukal.at[idx, 'Kenangan_3'] = str(in_k3).strip()
                        info_pukal.at[idx, 'Kenangan_4'] = str(in_k4).strip()
                        info_pukal.at[idx, 'Kenangan_5'] = str(in_k5).strip()

                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Media dikemaskini!")

                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Ralat: {e}")
