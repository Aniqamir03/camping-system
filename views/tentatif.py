import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📅 Tentatif & Maklumat Lokasi")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. PENGURUSAN DATA INFO LOKASI (DINAMIK) ---
# Sediakan nilai default (fallback) jika tab Info_Kem masih kosong di GSheet
default_lokasi = "Tapak Perkhemahan Pulau Redang, Terengganu"
default_in = "22 Mei 2026 (Jumaat)"
default_out = "24 Mei 2026 (Ahad)"
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty:
        lokasi_kem = info_db.iloc[0].get('Lokasi', default_lokasi)
        check_in = info_db.iloc[0].get('Check_In', default_in)
        check_out = info_db.iloc[0].get('Check_Out', default_out)
        maps_url = info_db.iloc[0].get('Maps_URL', default_maps)
        waze_url = info_db.iloc[0].get('Waze_URL', default_waze)
    else:
        lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze
except:
    # Jika tab 'Info_Kem' belum wujud, ia guna default value supaya app tak crash
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
    
    # Bersihkan string untuk elak ralat NaN
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


# --- 3. WIDGET CUACA LIVE ---
st.subheader("🌦️ Ramalan Cuaca Semasa (Kuala Terengganu)")
weather_html = """
<iframe src="https://www.weatherwidget.io/w/iframe.html?id=ww_0fb09bf00ebad&label_1=KUALA%20TERENGGANU&label_2=CUACA&theme=flat" 
        scrolling="no" 
        frameborder="0" 
        style="border:none; overflow:hidden; width:100%; height:150px;">
</iframe>
"""
st.components.v1.html(weather_html, height=160)


# --- 4. KAWALAN KHAS UNTUK ADMIN (BAHARU) ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Pengurusan Tentatif & Lokasi (Admin Sahaja)")
    
    # Membahagikan fungsi admin kepada 2 tab supaya kemas
    tab_lokasi, tab_aktiviti = st.tabs(["📍 Urus Info Lokasi", "➕ Tambah Aktiviti Jadual"])
    
    # TAB A: KEMASKINI LOKASI TAPAK
    with tab_lokasi:
        with st.form("form_kemaskini_lokasi"):
            inp_lokasi = st.text_input("Nama Lokasi Tapak", value=lokasi_kem)
            inp_in = st.text_input("Tarikh / Hari Check-In", value=check_in)
            inp_out = st.text_input("Tarikh / Hari Check-Out", value=check_out)
            inp_maps = st.text_input("Pautan Google Maps (URL Penuh)", value=maps_url)
            inp_waze = st.text_input("Pautan Waze (URL Penuh)", value=waze_url)
            
            submit_lokasi = st.form_submit_button("Simpan & Kemaskini Info Lokasi")
            
            if submit_lokasi:
                info_baru = pd.DataFrame([{
                    "Lokasi": inp_lokasi.strip(),
                    "Check_In": inp_in.strip(),
                    "Check_Out": inp_out.strip(),
                    "Maps_URL": inp_maps.strip(),
                    "Waze_URL": inp_waze.strip()
                }])
                
                conn.update(worksheet="Info_Kem", data=info_baru)
                st.success("Maklumat lokasi berjaya disimpan ke Google Sheets!")
                st.cache_data.clear()
                st.rerun()
                
    # TAB B: TAMBAH REKOD AKTIVITI BARU
    with tab_aktiviti:
        with st.form("form_tambah_aktiviti"):
            inp_hari = st.selectbox("Pilih Hari:", ["Hari 1 (Jumaat)", "Hari 2 (Sabtu)", "Hari 3 (Ahad)", "Lain-lain"])
            inp_masa = st.text_input("Masa Aktiviti (Contoh: 08:30 AM / 09:00 PM)")
            inp_aktiviti = st.text_input("Nama Aktiviti / Agenda")
            inp_nota = st.text_input("Nota Tambahan (Contoh: Pakai baju sukan / Sediakan alatan)")
            
            submit_akt = st.form_submit_button("Masukkan ke Jadual Tentatif")
            
            if submit_akt:
                if not inp_masa or not inp_aktiviti:
                    st.warning("Ruangan Masa dan Nama Aktiviti wajib diisi!")
                else:
                    akt_baru = pd.DataFrame([{
                        "Hari": inp_hari,
                        "Masa": inp_masa.strip(),
                        "Aktiviti": inp_aktiviti.strip(),
                        "Nota": inp_nota.strip()
                    }])
                    
                    # Gabungkan rekod baru dengan senarai sedia ada
                    if not tentatif_db.empty:
                        updated_tentatif = pd.concat([tentatif_db, akt_baru], ignore_index=True)
                    else:
                        updated_tentatif = akt_baru
                        
                    conn.update(worksheet="Tentatif", data=updated_tentatif)
                    st.success(f"Agenda '{inp_aktiviti}' berjaya ditambah ke dalam jadual!")
                    st.cache_data.clear()
                    st.rerun()
