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
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty:
        if current_trip and 'ID_Trip' in info_db.columns:
            info_db['ID_Trip'] = info_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            info_semasa = info_db[info_db['ID_Trip'] == current_trip]
        else:
            info_semasa = info_db
            
        if not info_semasa.empty:
            lokasi_kem = str(info_semasa.iloc[0].get('Lokasi', default_lokasi)).strip()
            check_in = str(info_semasa.iloc[0].get('Check_In', default_in)).strip()
            check_out = str(info_semasa.iloc[0].get('Check_Out', default_out)).strip()
            
            raw_maps = str(info_semasa.iloc[0].get('Maps_URL', default_maps)).strip()
            raw_waze = str(info_semasa.iloc[0].get('Waze_URL', default_waze)).strip()
            
            maps_url = default_maps if raw_maps.lower() in ['nan', ''] else raw_maps
            waze_url = default_waze if raw_waze.lower() in ['nan', ''] else raw_waze
except:
    pass

# Auto-Jana URL jika belum ditetapkan oleh Admin
lokasi_url = urllib.parse.quote(lokasi_kem)
if maps_url == default_maps and lokasi_kem != default_lokasi:
    maps_url = f"https://maps.google.com/maps?q={lokasi_url}"
    waze_url = f"https://waze.com/ul?q={lokasi_url}"

embed_map_url = f"https://maps.google.com/maps?q={lokasi_url}&output=embed"

# Paparkan Maklumat Lokasi Tapak Semasa
st.subheader("📍 Info Tapak Perkhemahan")
col1, col2 = st.columns(2)

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
    if lokasi_kem != default_lokasi:
        st.components.v1.iframe(embed_map_url, height=200)
    else:
        st.warning("Peta akan dipaparkan setelah lokasi ditetapkan.")

st.divider()


# --- 2. JADUAL AKTIVITI (TENTATIF DITAPIS) ---
st.subheader("🗓️ Jadual Aktiviti Kumpulan")
try:
    tentatif_db = conn.read(worksheet="Tentatif", ttl=0)
    if not tentatif_db.empty:
        for col in tentatif_db.columns:
            tentatif_db[col] = tentatif_db[col].astype(str).replace('nan', '').str.strip()
            
        if current_trip and 'ID_Trip' in tentatif_db.columns:
            tentatif_semasa = tentatif_db[tentatif_db['ID_Trip'] == current_trip].copy()
        else:
            tentatif_semasa = tentatif_db.copy()
                
        if not tentatif_semasa.empty:
            kolum_papar = [c for c in ['Hari', 'Masa', 'Aktiviti', 'Nota'] if c in tentatif_semasa.columns]
            st.dataframe(tentatif_semasa[kolum_papar], use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Jadual tentatif masih kosong untuk aktiviti/trip ini.")
    else:
        st.info("Jadual tentatif masih kosong.")
except Exception as e:
    st.error(f"Gagal memuatkan data tentatif: {e}")

st.divider()


# --- 3. INTEGRASI BUTANG PINTAR YAHOO WEATHER ---
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
    
    # KITA BUAT 3 TAB: Kemaskini Lokasi Semasa, Daftar Trip Baharu, dan Tambah Jadual
    tab_lokasi, tab_trip_baru, tab_aktiviti = st.tabs([
        "📍 Urus Lokasi Semasa", 
        "✨ Daftar Trip Baharu", 
        "➕ Tambah Aktiviti Jadual"
    ])
    
    # TAB 1: KEMASKINI LOKASI UNTUK TRIP YANG SEDANG DIPILIH
    with tab_lokasi:
        with st.form("form_kemaskini_lokasi"):
            st.write(f"Mengemaskini maklumat lokasi untuk Trip ID Aktif: **{current_trip if current_trip else 'TRP001'}**")
            inp_lokasi = st.text_input("Nama Lokasi Tapak", value=lokasi_kem if lokasi_kem != default_lokasi else "")
            
            col_in, col_out = st.columns(2)
            with col_in:
                inp_in = st.date_input("Tarikh Check-In", value=parse_tarikh(check_in), key="edit_in")
            with col_out:
                inp_out = st.date_input("Tarikh Check-Out", value=parse_tarikh(check_out), key="edit_out")
            
            submit_lokasi = st.form_submit_button("Simpan & Kemaskini Info Lokasi")
            
            if submit_lokasi:
                if not inp_lokasi:
                    st.warning("Nama lokasi wajib diisi!")
                else:
                    id_trip_save = current_trip if current_trip else "TRP001"
                    lokasi_url_save = urllib.parse.quote(inp_lokasi.strip())
                    auto_maps = f"https://maps.google.com/maps?q={lokasi_url_save}"
                    auto_waze = f"https://waze.com/ul?q={lokasi_url_save}"
                    
                    info_baru = pd.DataFrame([{
                        "ID_Trip": id_trip_save,
                        "Locations": inp_lokasi.strip(),
                        "Check_In": inp_in.strftime("%Y-%m-%d"),
                        "Check_Out": inp_out.strftime("%Y-%m-%d"),
                        "Maps_URL": auto_maps, 
                        "Waze_URL": auto_waze  
                    }])
                    
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                        if not info_pukal.empty and 'ID_Trip' in info_pukal.columns:
                            info_pukal['ID_Trip'] = info_pukal['ID_Trip'].astype(str).str.strip()
                            info_pukal = info_pukal[info_pukal['ID_Trip'] != id_trip_save]
                            updated_info = pd.concat([info_pukal, info_baru], ignore_index=True)
                        else:
                            updated_info = info_baru
                    except:
                        updated_info = info_baru
                    
                    conn.update(worksheet="Info_Kem", data=updated_info)
                    st.success("Maklumat lokasi berjaya dikemaskini!")
                    st.cache_data.clear()
                    st.rerun()
                    
    # TAB 2: BORANG MAGIK UNTUK DAFTAR TRIP + LOKASI + TARIKH SERENTAK (BARU)
    with tab_trip_baru:
        with st.form("form_daftar_trip_dan_lokasi"):
            st.write("### 🆕 Pendaftaran Aktiviti & Lokasi Baharu")
            st.write("Sistem akan auto-jana ID Trip dan menetapkan link navigasi peta secara automatik.")
            
            new_nama_trip = st.text_input("Nama Aktiviti Baru (Contoh: Camping Janda Baik 2026)")
            new_lokasi = st.text_input("Nama Lokasi Tapak (Contoh: Riverside Camp, Pahang)")
            
            col_new_in, col_new_out = st.columns(2)
            with col_new_in:
                new_in = st.date_input("Tarikh Check-In / Mula", value=datetime.date.today(), key="new_in")
            with col_new_out:
                new_out = st.date_input("Tarikh Check-Out / Tamat", value=datetime.date.today(), key="new_out")
                
            submit_trip_baru = st.form_submit_button("🚀 Daftarkan Trip & Lokasi Serta-merta")
            
            if submit_trip_baru:
                if not new_nama_trip or not new_lokasi:
                    st.warning("Nama Aktiviti dan Nama Lokasi wajib diisi!")
                else:
                    # 1. Kira & Auto-Generate ID_Trip baru dari tab Senarai_Trip
                    try:
                        db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=0)
                        if not db_trip_pukal.empty:
                            next_id = f"TRP{len(db_trip_pukal) + 1:03d}"
                        else:
                            next_id = "TRP001"
                    except:
                        db_trip_pukal = pd.DataFrame(columns=["ID_Trip", "Nama_Trip", "Tarikh", "Status_Trip"])
                        next_id = "TRP001"
                        
                    # 2. Bina baris data untuk tab Senarai_Trip
                    trip_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Nama_Trip": new_nama_trip.strip(),
                        "Tarikh": new_in.strftime("%Y-%m-%d"),
                        "Status_Trip": "Aktif"
                    }])
                    
                    # 3. Bina baris data untuk tab Info_Kem (Auto-link navigasi peta)
                    lokasi_url_new = urllib.parse.quote(new_lokasi.strip())
                    auto_maps_new = f"https://maps.google.com/maps?q={lokasi_url_new}"
                    auto_waze_new = f"https://waze.com/ul?q={lokasi_url_new}"
                    
                    info_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Lokasi": new_lokasi.strip(),
                        "Check_In": new_in.strftime("%Y-%m-%d"),
                        "Check_Out": new_out.strftime("%Y-%m-%d"),
                        "Maps_URL": auto_maps_new,
                        "Waze_URL": auto_waze_new
                    }])
                    
                    # 4. Gabung & Simpan terus ke fail Google Sheets
                    try:
                        updated_trip_db = pd.concat([db_trip_pukal, trip_row], ignore_index=True)
                    except:
                        updated_trip_db = trip_row
                        
                    try:
                        db_info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                        updated_info_db = pd.concat([db_info_pukal, info_row], ignore_index=True)
                    except:
                        updated_info_db = info_row
                        
                    conn.update(worksheet="Senarai_Trip", data=updated_trip_db)
                    conn.update(worksheet="Info_Kem", data=updated_info_db)
                    
                    st.success(f"Berjaya mendaftarkan trip **{new_nama_trip}** dengan kod keselamatan **{next_id}**!")
                    st.cache_data.clear()
                    st.rerun()
                
    # TAB 3: TAMBAH AKTIVITI JADUAL TENTATIF
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
                    id_trip_save = current_trip if current_trip else "TRP001"
                    akt_baru = pd.DataFrame([{
                        "ID_Trip": id_trip_save,
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
