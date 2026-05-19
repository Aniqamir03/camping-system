import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import altair as alt
import streamlit.components.v1 as components
import re

# --- GLOBAL UI ENHANCEMENT ---
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    background-attachment: fixed;
}

/* GLASS */
.glass {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 12px;
}

/* HOVER */
.glass:hover {
    transform: translateY(-6px) scale(1.02);
    transition: all 0.3s ease;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

/* TEXT */
h1, h2, h3, h4, p, span {
    color: white !important;
}

/* BUTTON */
.stButton>button {
    border-radius: 30px;
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    padding: 10px 18px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(0,198,255,0.6);
}

/* FADE */
.fade-in {
    animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(15px);}
    to {opacity: 1; transform: translateY(0);}
}

/* MOBILE */
@media (max-width: 768px) {
    .block-container {
        padding: 10px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# Ambil ID Trip
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCTION YOUTUBE ---
def get_yt_embed_url(url):
    if not url or url == 'nan':
        return None
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"
    return None


# --- LOAD TRIP ---
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=600)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        nama_trip = trip_info.iloc[0]['Nama_Trip']
        tarikh_str = str(trip_info.iloc[0]['Tarikh'])
    else:
        nama_trip = "Aktiviti Semasa"
        tarikh_str = ""
except:
    nama_trip = "Sistem Perkhemahan"
    tarikh_str = ""

st.title(f"🏕️ {nama_trip}")

# --- COUNTDOWN ---
if tarikh_str and tarikh_str.lower() != 'nan':
    try:
        tarikh_kem = pd.to_datetime(tarikh_str).to_pydatetime()
        baki_hari = (tarikh_kem - datetime.now()).days

        if baki_hari > 0:
            st.info(f"{baki_hari} hari lagi 🚀")
        elif baki_hari == 0:
            st.success("Hari ini! 🎉")
    except:
        pass

st.divider()

# --- DATA ---
try:
    users_db = conn.read(worksheet="Users", ttl=600)
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=600)
    users_member = users_db[users_db['Role'].str.lower() == 'member']
    kehadiran_semasa = kehadiran_db[kehadiran_db['ID_Trip'] == current_trip]
    merged_df = pd.merge(users_member, kehadiran_semasa[['Username','Status']], on='Username', how='left')
    merged_df['Status'] = merged_df['Status'].fillna('Belum Sahkan')
except:
    merged_df = pd.DataFrame()

# --- LAYOUT ---
col1, col2 = st.columns([1.8,1.2])

# === PROFILE ===
with col1:
    st.subheader("👥 Ahli")

    if not merged_df.empty:
        cols = st.columns(3)

        for i, (_, r) in enumerate(merged_df.iterrows()):
            with cols[i % 3]:
                warna = "#28a745" if r['Status']=="Hadir" else "#ffc107"

                st.markdown(f"""
                <div class="glass fade-in" style="text-align:center;">
                    <img src="{r.get('Profile_Pic_URL','https://cdn-icons-png.flaticon.com/512/149/149071.png')}"
                    style="width:60px;height:60px;border-radius:50%;border:2px solid {warna};">

                    <p style="font-size:12px;font-weight:bold;">{r['Full_Name']}</p>

                    <span style="background:{warna};padding:4px 10px;border-radius:10px;font-size:10px;">
                    {r['Status']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

# === YOUTUBE ===
with col2:
    st.subheader("📺 Video")

    yt = get_yt_embed_url("")
    if yt:
        st.markdown(f"""
        <iframe width="100%" height="250"
        src="{yt}"
        style="border-radius:16px;box-shadow:0 8px 20px rgba(0,0,0,0.4);">
        </iframe>
        """, unsafe_allow_html=True)

st.divider()

# === PIE CHART ===
if not merged_df.empty:
    status_counts = merged_df['Status'].value_counts()

    df_pie = pd.DataFrame({
        'Status': status_counts.index,
        'Jumlah': status_counts.values
    })

    chart = alt.Chart(df_pie).mark_arc(innerRadius=50).encode(
        theta="Jumlah",
        color="Status"
    )

    st.altair_chart(chart, use_container_width=True)

# === SLIDESHOW (UPGRADED) ===
images = ["https://picsum.photos/800/400","https://picsum.photos/801/400"]

slides = "".join([f'<div class="slide"><img src="{i}"></div>' for i in images])

components.html(f"""
<div class="slideshow glass">
{slides}
</div>

<style>
.slide {{display:none;}}
.slide img {{
    width:100%;
    height:280px;
    object-fit:cover;
    border-radius:12px;
}}
</style>

<script>
let index=0;
showSlides();

function showSlides(){{
let s=document.getElementsByClassName("slide");
for(let i=0;i<s.length;i++) s[i].style.display="none";
index++;
if(index>s.length) index=1;
s[index-1].style.display="block";
setTimeout(showSlides,3000);
}}
</script>
""", height=320)

st.divider()

# === BUTTON ===
if st.button("🚀 RSVP", use_container_width=True):
    st.switch_page("views/kehadiran.py")
