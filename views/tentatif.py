import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
from PIL import Image
import base64
import io

st.title("📅 Tentatif & Maklumat Lokasi")

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI PROSES POSTER KEPADA BASE64 ---
def proses_poster_ke_base64(fail_gambar):
    img = Image.open(fail_gambar)
    img.thumbnail((800, 1200))  # Batasan resolusi optimal untuk poster di web
    buffer = io.BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffer, format="JPEG", quality=85)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# --- FUNGSI BANTUAN UNTUK KALENDAR ---
def parse_tarikh(tarikh_str):
    try:
        return datetime.datetime.strptime(tarikh_str, "%Y-%m-%d").date()
    except:
        return datetime.date.today()

# --- 1. PENGURUSAN DATA INFO LOKASI & POSTER (DINAMIK) ---
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = str(datetime.date.today())
default_out = str(datetime.date.today())
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze
poster_pic = ""

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
            
            # Tarik data poster string Base64 dari GSheets
            poster_pic = str(info_semasa.iloc[0].get('Poster_Pic', '')).strip()
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


# --- 2. PAPARAN POSTER AKTIVITI (MENGGANTIKAN JADUAL TABULAR) ---
st.subheader("🗓️ Poster Jadual Aktiviti Kumpulan")
if pd.notna(poster_pic) and poster_pic.startswith("data:image"):
    try:
        st.image(poster_pic, use_container_width=True, caption=f"Poster Resmi Aktivitas - {lokasi_kem}")
    except:
        st.error("Gagal menampilkan gambar poster aktivitas.")
else:
    st.info("ℹ️ Belum ada poster jadual aktivitas yang diunggah untuk trip ini oleh Admin.")

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
    
    tab_trip_baru, tab_poster = st.tabs([
        "✨ Daftar Trip & Lokasi Baharu", 
        "🖼️ Urus Poster Aktivitas"
    ])
                    
    # TAB 1: BORANG MAGIK UNTUK DAFTAR TRIP + LOKASI + TARIKH SERENTAK 
    with tab_trip_baru:
        with st.form("form_daftar_trip_dan_lokasi"):
            st.write("### 🆕 Pendaftaran Aktiviti & Lokasi Baharu")
            st.write("Isi maklumat di bawah. Sistem akan auto-jana ID Trip, auto-link navigasi peta, dan menyelaraskan (sync) ke semua database berkaitan serentak.")
            
            new_nama_trip = st.text_input("Nama Aktiviti Baru (Contoh: Camping Janda Baik 2026)")
            new_lokasi = st.text_input("Nama Lokasi Tapak (Contoh: Riverside Camp, Pahang)")
            
            col_new_in, col_new_out = st.columns(2)
            with col_new_in:
                new_in = st.date_input("Tarikh Check-In / Bertolak", value=datetime.date.today(), key="new_in")
            with col_out:
                new_out = st.date_input("Tarikh Check-Out / Pulang", value=datetime.date.today(), key="new_out")
                
            submit_trip_baru = st.form_submit_button("🚀 Daftarkan Trip & Lokasi Serta-merta")
            
            if submit_trip_baru:
                if not new_nama_trip or not new_lokasi:
                    st.warning("Nama Aktiviti dan Nama Lokasi wajib diisi!")
                else:
                    try:
                        db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=0)
                        if not db_trip_pukal.empty:
                            next_id = f"TRP{len(db_trip_pukal) + 1:03d}"
                        else:
                            next_id = "TRP001"
                    except:
                        db_trip_pukal = pd.DataFrame(columns=["ID_Trip", "Nama_Trip", "Tarikh", "Status_Trip"])
                        next_id = "TRP001"
                        
                    trip_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Nama_Trip": new_nama_trip.strip(),
                        "Tarikh": new_in.strftime("%Y-%m-%d"),
                        "Status_Trip": "Aktif"
                    }])
                    
                    lokasi_url_new = urllib.parse.quote(new_lokasi.strip())
                    auto_maps_new = f"https://maps.google.com/maps?q={lokasi_url_new}"
                    auto_waze_new = f"https://waze.com/ul?q={lokasi_url_new}"
                    
                    info_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Lokasi": new_lokasi.strip(),
                        "Check_In": new_in.strftime("%Y-%m-%d"),
                        "Check_Out": new_out.strftime("%Y-%m-%d"),
                        "Maps_URL": auto_maps_new,
                        "Waze_URL": auto_waze_new,
                        "Poster_Pic": ""
                    }])
                    
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
                    
                    st.success(f"Mantap! Trip **{new_nama_trip}** berjaya direkodkan dengan kod **{next_id}**.")
                    st.cache_data.clear()
                    st.rerun()
                
    # TAB 2: UNGGAH POSTER AKTIVITI KHAS UNTUK ADMIN
    with tab_poster:
        with st.form("form_unggah_poster"):
            id_trip_save = current_trip if current_trip else "TRP001"
            st.write(f"🖼️ **Unggah Gambar Poster** untuk Trip ID Aktif: **{id_trip_save}**")
            st.write("💡 *Poster yang diunggah akan menggantikan tabel jadwal lama dan langsung disinkronisasikan ke database.*")
            
            file_poster = st.file_uploader("📸 Pilih Fail Gambar Poster (JPG/JPEG/PNG)", type=['jpg', 'jpeg', 'png'])
            submit_poster = st.form_submit_button("Simpan & Kemaskini Poster")
            
            if submit_poster:
                if file_poster is not None:
                    with st.spinner("Sedang memproses dan menyimpan gambar poster ke pangkalan data..."):
                        try:
                            # Konversi file gambar menjadi string Base64
                            kod_base64 = proses_poster_ke_base64(file_poster)
                            info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                            
                            # Seragamkan tipe data menjadi string untuk menghindari ralat NaN
                            for col in info_pukal.columns:
                                info_pukal[col] = info_pukal[col].astype(str).replace('nan', '').str.strip()
                            
                            if 'Poster_Pic' not in info_pukal.columns:
                                info_pukal['Poster_Pic'] = ""
                            
                            # Periksa apakah data Trip ID saat ini sudah ada di tab Info_Kem
                            if id_trip_save in info_pukal['ID_Trip'].values:
                                idx = info_pukal.index[info_pukal['ID_Trip'] == id_trip_save][0]
                                info_pukal.at[idx, 'Poster_Pic'] = kod_base64
                            else:
                                new_row = pd.DataFrame([{
                                    "ID_Trip": id_trip_save,
                                    "Lokasi": default_lokasi,
                                    "Check_In": default_in,
                                    "Check_Out": default_out,
                                    "Maps_URL": default_maps,
                                    "Waze_URL": default_waze,
                                    "Poster_Pic": kod_base64
                                }])
                                info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)
                            
                            # Perbarui lembar kerja GSheets secara massal
                            conn.update(worksheet="Info_Kem", data=info_pukal)
                            st.success("Poster aktivitas berhasil disimpan dan disinkronisasikan ke Google Sheets!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal memproses gambar poster: {e}")
                else:
                    st.warning("Silakan pilih file gambar poster terlebih dahulu!")
