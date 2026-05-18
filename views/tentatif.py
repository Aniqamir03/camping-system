import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📅 Tentatif & Maklumat Lokasi")

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. PENGURUSAN DATA INFO LOKASI (DINAMIK & DITAPIS) ---
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = "-"
default_out = "-"
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty:
        # Bersihkan data kolom ID_Trip
        if 'ID_Trip' in info_db.columns:
            info_db['ID_Trip'] = info_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            
            # Tapis info lokasi berdasarkan trip saat ini
            info_semasa = info_db[info_db['ID_Trip'] == current_trip]
            
            if not info_semasa.empty:
                lokasi_kem = info_semasa.iloc[0].get('Lokasi', default_lokasi)
                check_in = info_semasa.iloc[0].get('Check_In', default_in)
                check_out = info_semasa.iloc[0].get('Check_Out', default_out)
                maps_url = info_semasa.iloc[0].get('Maps_URL', default_maps)
                waze_url = info_semasa.iloc[0].get('Waze_URL', default_waze)
except:
    pass

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


# --- 2. JADUAL AKTIVITI (TENTATIF DITAPIS) ---
st.subheader("🗓️ Jadual Aktiviti Kumpulan")
try:
    tentatif_db = conn.read(worksheet="Tentatif", ttl=0)
    
    if not tentatif_db.empty:
        if 'ID_Trip' in tentatif_db.columns:
            tentatif_db['ID_Trip'] = tentatif_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            
            # Tapis jadwal aktivitas berdasarkan trip saat ini
            tentatif_semasa = tentatif_db[tentatif_db['ID_Trip'] == current_trip].copy()
            
            for col in ['Hari', 'Masa', 'Aktiviti', 'Nota']:
                if col in tentatif_semasa.columns:
                    tentatif_semasa[col] = tentatif_semasa[col].astype(str).replace('nan', '').str.strip()
                    
            if not tentatif_semasa.empty:
                st.dataframe(tentatif_semasa[['Hari', 'Masa', 'Aktiviti', 'Nota']], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Jadual tentatif masih kosong untuk aktiviti/trip ini.")
        else:
            st.error("⚠️ Kolum 'ID_Trip' tidak wujud di dalam tab Tentatif (Google Sheets).")
    else:
        st.info("Jadual tentatif masih kosong.")
except Exception as e:
    st.error(f"Gagal memuatkan data tentatif: {e}")

st.divider()


# --- 3. INTEGRASI BUTANG PINTAR YAHOO WEATHER (DINAMIK) ---
st.subheader("🌦️ Ramalan Cuaca Kumpulan")
if lokasi_kem != default_lokasi:
    lokasi_url = lokasi_kem.split(",")[0].strip().replace(" ", "+")
    yahoo_weather_url = f"https://search.yahoo.com/search?p={lokasi_url}+weather"
    
    st.write(f"Sistem dikesan bersambung dengan lokasi: **{lokasi_kem.split(',')[0]}**.")
    st.link_button("✉️ Semak Cuaca Live di Yahoo Weather", yahoo_weather_url, type="primary")
else:
    st.info("Butang ramalan cuaca Yahoo akan diaktifkan sebaik sahaja Admin menetapkan lokasi tapak.")


# --- 4. KAWALAN KHAS UNTUK ADMIN (DENGAN LOGIKA MULTI-TRIP) ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Pengurusan Tentatif & Lokasi (Admin Sahaja)")
    
    tab_lokasi, tab_aktiviti = st.tabs(["📍 Urus Info Lokasi", "➕ Tambah Aktiviti Jadual"])
    
    with tab_lokasi:
        with st.form("form_kemaskini_lokasi"):
            inp_lokasi = st.text_input("Nama Lokasi Tapak", value=lokasi_kem if lokasi_kem != default_lokasi else "")
            inp_in = st.text_input("Tarikh / Hari Check-In", value=check_in if check_in != "-" else "")
            inp_out = st.text_input("Tarikh / Hari Check-Out", value=check_out if check_out != "-" else "")
            inp_maps = st.text_input("Pautan Google Maps (URL Penuh)", value=maps_url if maps_url != default_maps else "")
            inp_waze = st.text_input("Pautan Waze (URL Penuh)", value=waze_url if waze_url != default_waze else "")
            
            submit_lokasi = st.form_submit_button("Simpan & Kemaskini Info Lokasi")
            
            if submit_lokasi:
                info_baru = pd.DataFrame([{
                    "ID_Trip": current_trip,
                    "Lokasi": inp_lokasi.strip(),
                    "Check_In": inp_in.strip(),
                    "Check_Out": inp_out.strip(),
                    "Maps_URL": inp_maps.strip(),
                    "Waze_URL": inp_waze.strip()
                }])
                
                # Baca data lama untuk mempertahankan data trip lain
                try:
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                    if 'ID_Trip' in info_pukal.columns:
                        info_pukal['ID_Trip'] = info_pukal['ID_Trip'].astype(str).str.strip()
                        # Hapus data lama untuk trip ini saja agar tidak duplikat
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
