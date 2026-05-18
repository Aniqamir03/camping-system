import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
import streamlit.components.v1 as components

# =========================
# 🎨 GLOBAL UI DESIGN
# =========================
st.set_page_config(page_title="Tentatif Trip", layout="wide")

st.markdown("""
<style>

/* 🌈 BACKGROUND */
html, body, [class*="css"]  {
    background: linear-gradient(135deg, #87CEEB, #FF7F50, #FF914D);
    background-attachment: fixed;
    font-family: 'Segoe UI', sans-serif;
}

/* 🧊 GLASS CARD */
.glass-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.2);
    margin-bottom: 20px;
    animation: fadeIn 0.8s ease-in-out;
}

/* 🎭 TEXT */
h1, h2, h3 {
    color: white !important;
}
.stMarkdown, .stText {
    color: white !important;
}

/* 🚀 BUTTON */
.stButton>button, .stLinkButton a {
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
}

/* ✨ ANIMATION */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

</style>
""", unsafe_allow_html=True)

st.title("📅 Tentatif & Maklumat Lokasi")

# =========================
# SESSION
# =========================
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)

# =========================
# HELPER
# =========================
def parse_tarikh(tarikh_str):
    try:
        return datetime.datetime.strptime(tarikh_str, "%Y-%m-%d").date()
    except:
        return datetime.date.today()

# =========================
# DEFAULT DATA
# =========================
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = str(datetime.date.today())
default_out = str(datetime.date.today())
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze
p1, p2, p3 = "", "", ""

# =========================
# LOAD DATA
# =========================
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty:
        if current_trip and 'ID_Trip' in info_db.columns:
            info_db['ID_Trip'] = info_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            info_semasa = info_db[info_db['ID_Trip'] == current_trip]
        else:
            info_semasa = info_db
            
        if not info_semasa.empty:
            row = info_semasa.iloc[0]

            lokasi_kem = str(row.get('Lokasi', default_lokasi)).strip()
            check_in = str(row.get('Check_In', default_in)).strip()
            check_out = str(row.get('Check_Out', default_out)).strip()

            maps_url = str(row.get('Maps_URL', default_maps)).strip()
            waze_url = str(row.get('Waze_URL', default_waze)).strip()

            p1 = str(row.get('Poster_Pic_1', '')).strip()
            p2 = str(row.get('Poster_Pic_2', '')).strip()
            p3 = str(row.get('Poster_Pic_3', '')).strip()
except:
    pass

# =========================
# AUTO MAP LINK
# =========================
lokasi_url = urllib.parse.quote(lokasi_kem)
if maps_url == default_maps and lokasi_kem != default_lokasi:
    maps_url = f"https://maps.google.com/maps?q={lokasi_url}"
    waze_url = f"https://waze.com/ul?q={lokasi_url}"

embed_map_url = f"https://maps.google.com/maps?q={lokasi_url}&output=embed"

# =========================
# 📍 INFO SECTION
# =========================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

st.subheader("📍 Info Tapak Perkhemahan")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **Lokasi:** {lokasi_kem}
    **Check-in:** {check_in}
    **Check-out:** {check_out}
    """)
    st.link_button("🗺️ Google Maps", maps_url)
    st.link_button("🚙 Waze", waze_url)

with col2:
    if lokasi_kem != default_lokasi:
        components.iframe(embed_map_url, height=250)
    else:
        st.warning("Lokasi belum ditetapkan.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 🖼️ SLIDESHOW
# =========================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

st.subheader("🗓️ Poster Aktiviti")

senarai_poster = [p for p in [p1, p2, p3] if p and p.lower() != "nan"]

if senarai_poster:
    slides = ""
    for img in senarai_poster:
        slides += f"""
        <div class="mySlides">
            <img src="{img}" style="width:100%; border-radius:15px;">
        </div>
        """

    html = f"""
    <div class="slideshow-container">
    {slides}
    </div>

    <script>
    let i = 0;
    function showSlides() {{
        let slides = document.getElementsByClassName("mySlides");
        for (let s of slides) s.style.display = "none";
        i++;
        if (i > slides.length) i = 1;
        slides[i-1].style.display = "block";
        setTimeout(showSlides, 4000);
    }}
    showSlides();
    </script>
    """

    components.html(html, height=400)
else:
    st.info("Tiada poster lagi.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 🌦️ WEATHER
# =========================
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

st.subheader("🌦️ Ramalan Cuaca")

if lokasi_kem != default_lokasi:
    lokasi_cuaca = lokasi_kem.split(",")[0]
    url = f"https://search.yahoo.com/search?p={urllib.parse.quote(lokasi_cuaca)}+weather"
    st.link_button("Semak Cuaca", url)
else:
    st.info("Lokasi belum ada.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ⚙️ ADMIN PANEL
# =========================
if st.session_state.get("role") == "Admin":

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.subheader("⚙️ Admin Panel")

    with st.form("add_trip"):
        nama = st.text_input("Nama Trip")
        lokasi = st.text_input("Lokasi")
        tarikh = st.date_input("Tarikh")

        if st.form_submit_button("Tambah Trip"):
            if nama and lokasi:
                st.success("Trip berjaya ditambah!")
            else:
                st.warning("Isi semua maklumat")

    st.markdown('</div>', unsafe_allow_html=True)
