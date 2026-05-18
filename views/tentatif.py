import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
import streamlit.components.v1 as components

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

# --- 1. PENGURUSAN DATA INFO LOKASI & POSTER (DINAMIK) ---
default_lokasi = "Belum Ditetapkan (Sila isi di Panel Admin)"
default_in = str(datetime.date.today())
default_out = str(datetime.date.today())
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem, check_in, check_out, maps_url, waze_url = default_lokasi, default_in, default_out, default_maps, default_waze
p1, p2, p3 = "", "", ""

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
            
            p1 = str(info_semasa.iloc[0].get('Poster_Pic_1', '')).strip()
            p2 = str(info_semasa.iloc[0].get('Poster_Pic_2', '')).strip()
            p3 = str(info_semasa.iloc[0].get('Poster_Pic_3', '')).strip()
except:
    pass

lokasi_url = urllib.parse.quote(lokasi_kem)
if maps_url == default_maps and lokasi_kem != default_lokasi:
    maps_url = f"https://maps.google.com/maps?q={lokasi_url}"
    waze_url = f"https://waze.com/ul?q={lokasi_url}"

embed_map_url = f"https://maps.google.com/maps?q={lokasi_url}&output=embed"

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


# --- 2. PAPARAN SLIDESHOW POSTER AKTIVITI (AUTO & MANUAL) ---
st.subheader("🗓️ Poster & Jadual Aktiviti Kumpulan")

senarai_poster = [p for p in [p1, p2, p3] if p and p.lower() != "nan"]

if len(senarai_poster) > 0:
    # Membina kod HTML dan JS dinamik untuk jadikan ia slideshow
    divs_gambar = ""
    for img_url in senarai_poster:
        divs_gambar += f"""
        <div class="mySlides fade">
            <img src="{img_url}" style="width:100%; max-height:600px; object-fit:contain; border-radius:10px; background:#2e2e2e;">
        </div>
        """
        
    html_kod = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    * {{box-sizing: border-box}}
    body {{font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: transparent;}}
    .slideshow-container {{
      max-width: 800px;
      position: relative;
      margin: auto;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }}
    .mySlides {{display: none; text-align: center;}}
    .prev, .next {{
      cursor: pointer;
      position: absolute;
      top: 50%;
      width: auto;
      padding: 16px;
      margin-top: -22px;
      color: white;
      font-weight: bold;
      font-size: 20px;
      transition: 0.6s ease;
      border-radius: 0 3px 3px 0;
      user-select: none;
      background-color: rgba(0,0,0,0.4);
      text-decoration: none;
    }}
    .next {{right: 0; border-radius: 3px 0 0 3px;}}
    .prev:hover, .next:hover {{background-color: rgba(0,0,0,0.9);}}
    .fade {{
      animation-name: fade;
      animation-duration: 1.5s;
    }}
    @keyframes fade {{
      from {{opacity: .4}} 
      to {{opacity: 1}}
    }}
    </style>
    </head>
    <body>

    <div class="slideshow-container">
      {divs_gambar}
      <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
      <a class="next" onclick="plusSlides(1)">&#10095;</a>
    </div>

    <script>
    let slideIndex = 0;
    let timer;
    showSlides();

    function plusSlides(n) {{
      clearTimeout(timer);
      showSlides(slideIndex += n);
    }}

    function showSlides(n) {{
      let i;
      let slides = document.getElementsByClassName("mySlides");
      if (slides.length === 0) return;
      if (n !== undefined) {{ slideIndex = n; }}
      if (slideIndex >= slides.length) {{slideIndex = 0}}    
      if (slideIndex < 0) {{slideIndex = slides.length - 1}}
      for (i = 0; i < slides.length; i++) {{
        slides[i].style.display = "none";  
      }}
      slides[slideIndex].style.display = "block";  
      // Auto tukar setiap 5 saat (5000 ms)
      timer = setTimeout(function(){{ plusSlides(1); }}, 5000);
    }}
    </script>

    </body>
    </html>
    """
    
    # Paparkan HTML komponen di dalam Streamlit
    components.html(html_kod, height=620)
    
else:
    st.info("ℹ️ Belum ada poster jadual aktiviti untuk trip ini. Admin akan kemaskini sebentar lagi.")

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
    
    tab_trip_baru, tab_poster, tab_urus_trip = st.tabs([
        "✨ Daftar Trip & Lokasi", 
        "🖼️ Urus Poster (Slideshow)",
        "✏️ Urus & Padam Trip"
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
            with col_new_out: 
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
                        "Poster_Pic_1": "",
                        "Poster_Pic_2": "",
                        "Poster_Pic_3": ""
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
                
    # TAB 2: PENGURUSAN SLIDESHOW (3 POSTER)
    with tab_poster:
        with st.form("form_unggah_poster"):
            id_trip_save = current_trip if current_trip else "TRP001"
            st.write(f"🖼️ **Urus Pautan Poster (Slideshow)** untuk Trip ID Aktif: **{id_trip_save}**")
            st.markdown("💡 *Sila tampal Direct Link (berakhir .jpg/.png) ke dalam ruangan di bawah. Anda boleh masukkan sehingga 3 keping poster.*")
            
            url_p1 = st.text_input("🔗 Poster Utama (Wajib)", value=p1 if p1 != "nan" else "")
            url_p2 = st.text_input("🔗 Poster Kedua (Pilihan)", value=p2 if p2 != "nan" else "")
            url_p3 = st.text_input("🔗 Poster Ketiga (Pilihan)", value=p3 if p3 != "nan" else "")
            
            submit_poster = st.form_submit_button("Simpan Koleksi Poster")
            
            if submit_poster:
                with st.spinner("Sedang menyelaraskan koleksi poster ke pangkalan data..."):
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                        
                        if info_pukal.empty or 'ID_Trip' not in info_pukal.columns:
                            info_pukal = pd.DataFrame(columns=["ID_Trip", "Lokasi", "Check_In", "Check_Out", "Maps_URL", "Waze_URL", "Poster_Pic_1", "Poster_Pic_2", "Poster_Pic_3"])
                        else:
                            for col in info_pukal.columns:
                                info_pukal[col] = info_pukal[col].astype(str).replace('nan', '').str.strip()
                        
                        for col_name in ['Poster_Pic_1', 'Poster_Pic_2', 'Poster_Pic_3']:
                            if col_name not in info_pukal.columns:
                                info_pukal[col_name] = ""
                        
                        if id_trip_save in info_pukal['ID_Trip'].values:
                            idx = info_pukal.index[info_pukal['ID_Trip'] == id_trip_save][0]
                            info_pukal.at[idx, 'Poster_Pic_1'] = url_p1.strip()
                            info_pukal.at[idx, 'Poster_Pic_2'] = url_p2.strip()
                            info_pukal.at[idx, 'Poster_Pic_3'] = url_p3.strip()
                        else:
                            new_row = pd.DataFrame([{
                                "ID_Trip": id_trip_save,
                                "Lokasi": default_lokasi,
                                "Check_In": default_in,
                                "Check_Out": default_out,
                                "Maps_URL": default_maps,
                                "Waze_URL": default_waze,
                                "Poster_Pic_1": url_p1.strip(),
                                "Poster_Pic_2": url_p2.strip(),
                                "Poster_Pic_3": url_p3.strip()
                            }])
                            info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)
                        
                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Koleksi poster (Slideshow) berjaya disimpan dan diselaraskan!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memproses pautan poster: {e}")
                    
    # TAB 3: URUS & PADAM TRIP SEMASA
    with tab_urus_trip:
        if not current_trip:
            st.info("Sila pilih aktiviti/trip di menu tepi (sidebar) terlebih dahulu sebelum menguruskannya.")
        else:
            try:
                db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=0)
                trip_semasa_info = db_trip_pukal[db_trip_pukal['ID_Trip'] == current_trip]
                
                if not trip_semasa_info.empty:
                    info_trip = trip_semasa_info.iloc[0]
                    nama_semasa = str(info_trip.get('Nama_Trip', ''))
                    tarikh_semasa = str(info_trip.get('Tarikh', ''))
                    status_semasa = str(info_trip.get('Status_Trip', 'Aktif'))
                    
                    st.write(f"### ⚙️ Pengurusan: **{nama_semasa}** ({current_trip})")
                    
                    tindakan_trip = st.radio("Pilih Tindakan Pengurusan:", ["Kemaskini Maklumat Trip", "Padam Trip ❌"])
                    
                    with st.form("form_urus_trip"):
                        if tindakan_trip == "Kemaskini Maklumat Trip":
                            edit_nama = st.text_input("Nama Aktiviti", value=nama_semasa)
                            edit_tarikh = st.date_input("Tarikh Bertolak", value=parse_tarikh(tarikh_semasa))
                            idx_status = 0 if status_semasa == "Aktif" else 1
                            edit_status = st.selectbox("Status", ["Aktif", "Selesai"], index=idx_status)
                            
                        elif tindakan_trip == "Padam Trip ❌":
                            st.warning(f"⚠️ AMARAN: Adakah anda pasti mahu memadam aktiviti **{nama_semasa}**? Semua maklumat lokasi dan poster berkaitan trip ini juga akan terpadam.")
                            sahkan_padam = st.checkbox("Ya, saya pasti mahu padam trip ini sepenuhnya.")
                            
                        submit_urus = st.form_submit_button("Laksanakan Tindakan")
                        
                        if submit_urus:
                            if tindakan_trip == "Kemaskini Maklumat Trip":
                                if not edit_nama:
                                    st.error("Nama aktiviti tidak boleh dibiarkan kosong!")
                                else:
                                    idx = db_trip_pukal.index[db_trip_pukal['ID_Trip'] == current_trip][0]
                                    db_trip_pukal.at[idx, 'Nama_Trip'] = edit_nama.strip()
                                    db_trip_pukal.at[idx, 'Tarikh'] = edit_tarikh.strftime("%Y-%m-%d")
                                    db_trip_pukal.at[idx, 'Status_Trip'] = edit_status
                                    
                                    conn.update(worksheet="Senarai_Trip", data=db_trip_pukal)
                                    st.success("Maklumat aktiviti berjaya dikemaskini!")
                                    st.cache_data.clear()
                                    st.rerun()
                                    
                            elif tindakan_trip == "Padam Trip ❌":
                                if not sahkan_padam:
                                    st.error("Sila tanda (tick) pada kotak pengesahan sebelum memadam!")
                                else:
                                    db_trip_baru = db_trip_pukal[db_trip_pukal['ID_Trip'] != current_trip]
                                    conn.update(worksheet="Senarai_Trip", data=db_trip_baru)
                                    
                                    try:
                                        info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                                        info_baru = info_pukal[info_pukal['ID_Trip'] != current_trip]
                                        conn.update(worksheet="Info_Kem", data=info_baru)
                                    except:
                                        pass
                                        
                                    st.session_state['current_trip_id'] = "" 
                                    st.success(f"Aktiviti {nama_semasa} berjaya dipadamkan sepenuhnya.")
                                    st.cache_data.clear()
                                    st.rerun()
                else:
                    st.error("Rekod aktiviti ini tidak dijumpai di pangkalan data.")
            except Exception as e:
                st.error(f"Gagal membaca sistem pangkalan data: {e}")
