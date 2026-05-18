import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📅 Tentatif & Maklumat Lokasi")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. PENGURUSAN DATA INFO LOKASI (DINAMIK) ---
# Kita tukar jadi placeholder umum supaya tak mengelirukan awak lagi bos
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = "-"
default_out = "-"
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty:
        # Jika GSheet ada data, dia AMBIL data tebaca (Dinamik!)
        lokasi_kem = info_db.iloc[0].get('Lokasi', default_lokasi)
        check_in = info_db.iloc[0].get('Check_In', default_in)
        check_out = info_db.iloc[0].get('Check_Out', default_out)
        maps_url = info_db.iloc[0].get('Maps_URL', default_maps)
        waze_url = info_db.iloc[0].get('Waze_URL', default_waze)
    else:
        lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze
except:
    # Jika tab 'Info_Kem' tak wujud langsung lagi, baru dia guna sandaran ini
    lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze


# Paparkan Maklumat Lokasi Tapak Semasa
st.subheader("📍 Info Tapak Perkhemahan")
col1, col2 = st.columns(2)
with col1:
    st.info(f"""
    **Lokasi:** {lokasi_kem}
    **Check-in:** {check_in}
    **Check-out:** {check_out}
    """)
with col2:
    st.write("🚘 Pautan Navigasi:")
    st.link_button("🗺️ Buka Google Maps", maps_url)
    st.link_button("🚙 Buka Waze", waze_url)

st.divider()


# --- 2. JADUAL AKTIVITI (TENTATIF) ---
st.subheader("🗓️ Jadual Aktiviti Kumpulan")
try:
    tentatif_db = conn.read(worksheet="Tentatif", ttl=0)
    
    for col in ['Hari', 'Masa', 'Aktiviti', 'Nota']:
        if col in tentatif_db.columns:
            tentatif_db[col] = tentatif_db[col].astype(str).replace('nan', '').str.strip()
            
    if not tentatif_db.empty:
        st.dataframe(tentatif_db, use_container_width=True, hide_index=True)
    else:
        st.info("Jadual tentatif masih kosong. Sila hubungi Admin untuk kemaskini.")
except:
    st.error("Gagal memuatkan data tentatif. Pastikan tab 'Tentatif' wujud di GSheet.")
    tentatif_db = pd.DataFrame(columns=['Hari', 'Masa', 'Aktiviti', 'Nota'])

st.divider()


# --- 3. WIDGET CUACA LIVE (VERSI KEBAL & DINAMIK) ---
# Sistem hanya akan tarik cuaca jika Admin dah set lokasi sebenar
if lokasi_kem != default_lokasi:
    st.subheader(f"🌦️ Ramalan Cuaca Semasa")
    
    # Pecahkan string, ambil nama bandar/kawasan depan sahaja
    lokasi_pendek = lokasi_kem.split(",")[0].strip()
    lokasi_url = lokasi_pendek.replace(" ", "+")
    
    url_gambar_cuaca = f"https://wttr.in/{lokasi_url}_3p_lang=ms.png?m"
    
    try:
        st.image(url_gambar_cuaca, caption=f"Status cuaca terkini di {lokasi_pendek}.", use_container_width=True)
    except:
        st.warning("Gagal memuatkan imej ramalan cuaca semasa.")
else:
    st.info("🌦️ Ramalan cuaca akan dipaparkan sebaik sahaja Admin menetapkan lokasi tapak.")
