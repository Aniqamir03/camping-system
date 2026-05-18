import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse

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

# --- 1. PENGURUSAN DATA INFO LOKASI (DINAMIK) ---
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = str(datetime.date.today())
default_out = str(datetime.date.today())

lokasi_kem, check_in, check_out = default_lokasi, default_in, default_out

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty and 'ID_Trip' in info_db.columns:
        info_db['ID_Trip'] = info_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
        info_semasa = info_db[info_db['ID_Trip'] == current_trip]
        
        if not info_semasa.empty:
            lokasi_kem = info_semasa.iloc[0].get('Lokasi', default_lokasi)
            check_in = info_semasa.iloc[0].get('Check_In', default_in)
            check_out = info_semasa.iloc[0].get('Check_Out', default_out)
except:
    pass

# Auto-Jana Link & Embed Map berdasarkan Nama Lokasi
lokasi_url = urllib.parse.quote(lokasi_kem)
maps_url = f"https://www.google.com/maps/search/?api=1&query={lokasi_url}"
waze_url = f"https://waze.com/ul?q={lokasi_url}"
embed_map_url = f"https://www.google.com/maps?q={lokasi_url}&output=embed"

# Paparkan Maklumat Lokasi Tapak Semasa
st.subheader("📍 Info Tapak Perkhemahan")
col1, col2 = st.columns([1, 1])

with col1:
    st.info(f"""
    **Lokasi:** {lokasi_kem}
    **Check-in:** {check_in}
    **Check-out:** {check_out}
    """)
    st.write("🚘 **Pautan Navigasi Pantas:**")
    st.link_button("🗺️ Buka di Google Maps", maps_url)
    st.link_button("🚙 Buka di Waze", waze_url)

with col2:
    # Paparkan Embedded Google Maps secara automatik!
    if lokasi_kem != default_lokasi:
        st.components.v1.iframe(embed_map_url, height=200)
    else:
        st.warning("Peta akan dipaparkan setelah lokasi ditetapkan.")

st.divider()


# --- 2. JADUAL AKTIVITI (TENTATIF DITAPIS) ---
st.subheader("🗓️ Jadual Aktiviti Kumpulan")
try:
    tentatif_db = conn.read(worksheet="Tentatif", ttl=0)
    
    if not tentatif_db.empty and 'ID_Trip' in tentatif_db.columns:
        tentatif_db['ID_Trip'] = tentatif_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
        tentatif_semasa = tentatif_db[tentatif_db['ID_Trip'] == current_trip].copy()
        
        for col in ['Hari', 'Masa', 'Aktiviti', 'Nota']:
            if col in tentatif_semasa.columns:
                tentatif_semasa[col] = tentatif_semasa[col].astype(str).replace('nan', '').str.strip()
                
        if not tentatif_semasa.empty:
            st.dataframe(tentatif_semasa[['Hari', 'Masa', 'Aktiviti', 'Nota']], use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Jadual tentatif masih kosong untuk aktiviti/trip ini.")
    else:
        st.info("Jadual tentatif masih kosong.")
except Exception as e:
    st.error(f"Gagal memuatkan data tentatif: {e}")

st.divider()


# --- 3. INTEGRASI BUTANG PINTAR YAHOO WEATHER (DINAMIK) ---
st.subheader("🌦️ Ramalan Cuaca Kumpulan")
if lokasi_kem != default_lokasi:
    lokasi_cuaca = lokasi_kem.split(",")[0].strip()
    lokasi_cuaca_url = urllib.parse.quote(lokasi_cuaca)
    yahoo_weather_url = f"https://search.yahoo.com/search?p={lokasi_cuaca_url}+weather"
    
    st.write(f"Sistem dikesan bersambung dengan lokasi: **{lokasi_cuaca}**.")
    st.link_button("✉️ Semak Cuaca Live di Yahoo Weather", yahoo_weather_url, type="primary")
else:
    st.info("Butang ramalan cuaca Yahoo akan diaktifkan sebaik sahaja Admin menetapkan lokasi tapak.")


# --- 4. KAWALAN KHAS UNTUK ADMIN ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Pengurusan Tentatif & Lokasi (Admin Sahaja)")
    
    tab_lokasi, tab_aktiviti = st.tabs(["📍 Urus Info Lokasi", "➕ Tambah Aktiviti Jadual"])
    
    with tab_lokasi:
        with st.form("form_kemaskini_lokasi"):
            st.write("💡 *Taip sahaja nama lokasi, sistem akan automatik kesan peta dan jana link Waze/Maps!*")
            inp_lokasi = st.text_input("Nama Lokasi Tapak", value=lokasi_kem if lokasi_kem != default_lokasi else "")
            
            # WIDGET KALENDAR (DATE PICKER)
            col_in, col_out = st.columns(2)
            with col_in:
                inp_in = st.date_input("Tarikh Check-In", value=parse_tarikh(check_in))
            with col_out:
                inp_out = st.date_input("Tarikh Check-Out", value=parse_tarikh(check_out))
            
            submit_lokasi = st.form_submit_button("Simpan & Kemaskini Info Lokasi")
            
            if submit_lokasi:
                if not inp_lokasi:
                    st.warning("Nama lokasi wajib diisi!")
                else:
                    info_baru = pd.DataFrame([{
                        "ID_Trip": current_trip,
                        "Lokasi": inp_lokasi.strip(),
                        # Tukar balik ke format YYYY-MM-DD untuk simpan dalam GSheet
                        "Check_In": inp_in.strftime("%Y-%m-%d"),
                        "Check_Out": inp_out.strftime("%Y-%m-%d"),
                        "Maps_URL": "", # Kosongkan sebab sistem auto-jana
                        "Waze_URL": ""  # Kosongkan sebab sistem auto-jana
                    }])
                    
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                        if 'ID_Trip' in info_pukal.columns:
                            info_pukal['ID_Trip'] = info_pukal['ID_Trip'].astype(str).str.strip()
                            info_pukal = info_pukal[info_pukal['ID_Trip'] != current_trip]
                            updated_info = pd.concat([info_pukal, info_baru], ignore_index=True)
                        else:
                            updated_info = info_baru
                    except:
                        updated_info = info_baru
                    
                    conn.update(worksheet="Info_Kem", data=updated_info)
                    st.success("Maklumat lokasi berjaya disimpan ke Google Sheets!")
                    st.cache_data.clear()
                    st.rerun()
                
    with tab_aktiviti:
        with st.form("form_tambah_aktiviti"):
            inp_hari = st.selectbox("Pilih Hari:", ["Hari 1 (Jumaat)", "Hari 2 (Sabtu)", "Hari 3 (Ahad)", "Lain-lain"])
            inp_masa = st.text_input("Masa Aktiviti (Contoh: 08:30 AM)")
            inp_aktiviti = st.text_input("Nama Aktiviti / Agenda")
            inp_nota = st.text_input("Nota Tambahan")
            
            submit_akt = st.form_submit_button("Masukkan ke Jadual Tentatif")
            
            if submit_akt:
                if not inp_masa or not inp_aktiviti:
                    st.warning("Ruangan Masa dan Nama Aktiviti wajib diisi!")
                else:
                    akt_baru = pd.DataFrame([{
                        "ID_Trip": current_trip,
                        "Hari": inp_hari,
                        "Masa": inp_masa.strip(),
                        "Aktiviti": inp_aktiviti.strip(),
                        "Nota": inp_nota.strip()
                    }])
                    
                    try:
                        tentatif_pukal = conn.read(worksheet="Tentatif", ttl=0)
                        updated_tentatif = pd.concat([tentatif_pukal, akt_baru], ignore_index=True)
                    except:
                        updated_tentatif = akt_baru
                        
                    conn.update(worksheet="Tentatif", data=updated_tentatif)
                    st.success(f"Agenda '{inp_aktiviti}' berjaya ditambah!")
                    st.cache_data.clear()
                    st.rerun()
