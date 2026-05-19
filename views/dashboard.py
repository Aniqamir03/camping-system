import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import altair as alt
import streamlit.components.v1 as components

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 0. TARIK INFO TRIP UTAMA ---
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
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

st.title(f"🏕️ Papan Pemuka - {nama_trip}")
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


# --- PERSEDIAAN DATA: TARIK & TAPIS DATA USERS & KEHADIRAN ---
try:
    users_db = conn.read(worksheet="Users", ttl=0)
except:
    users_db = pd.DataFrame(columns=['Username', 'Full_Name', 'Role', 'Profile_Pic_URL'])

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=0)
except:
    kehadiran_db = pd.DataFrame(columns=['ID_Trip', 'Username', 'Status'])

# Bersihkan strings untuk elak ralat data kosong
for col in users_db.columns:
    users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

if not kehadiran_db.empty:
    for col in kehadiran_db.columns:
        kehadiran_db[col] = kehadiran_db[col].astype(str).replace('nan', '').str.strip()
    kehadiran_semasa = kehadiran_db[kehadiran_db['ID_Trip'] == current_trip]
else:
    kehadiran_semasa = pd.DataFrame(columns=['ID_Trip', 'Username', 'Status'])

# TAPIS KHAS: Hanya ambil user yang Role = 'Member' (Admin tidak dipaparkan)
if not users_db.empty and 'Role' in users_db.columns:
    users_member = users_db[users_db['Role'].str.lower() == 'member']
else:
    users_member = users_db

# Gabungkan (Merge) senarai Member dengan status kehadiran semasa mereka
if not users_member.empty:
    merged_df = pd.merge(users_member, kehadiran_semasa[['Username', 'Status']], on='Username', how='left')
    merged_df['Status'] = merged_df['Status'].fillna('Belum Sahkan')
else:
    merged_df = pd.DataFrame()


# --- 2. GRID DIREKTORI PROFIL & STATUS LIVE AHLI ---
st.subheader("👥 Kad Profil & Status Ahli Kumpulan")

avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if not merged_df.empty:
    kolum_setiap_baris = 4
    pecahan_baris = [merged_df[i:i + kolum_setiap_baris] for i in range(0, len(merged_df), kolum_setiap_baris)]
    
    for baris_data in pecahan_baris:
        cols = st.columns(kolum_setiap_baris)
        for indeks, (_, r) in enumerate(baris_data.iterrows()):
            with cols[indeks]:
                url_gambar = r['Profile_Pic_URL'] if r['Profile_Pic_URL'] != "" else avatar_default
                status_rsvp = r['Status']
                
                if status_rsvp == "Hadir":
                    warna_tema = "#28a745" # Hijau
                elif status_rsvp == "Tidak Hadir":
                    warna_tema = "#dc3545" # Merah
                elif status_rsvp == "Belum Pasti":
                    warna_tema = "#ffc107" # Kuning
                else:
                    warna_tema = "#6c757d" # Kelabu
                
                kad_html = f"""
                <div style="text-align: center; 
                            padding: 15px; 
                            border: 1px solid #4d4d4d; 
                            border-radius: 12px; 
                            margin-bottom: 20px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <img src="{url_gambar}" style="width: 90px; 
                                                   height: 90px; 
                                                   object-fit: cover; 
                                                   border-radius: 50%; 
                                                   border: 3px solid {warna_tema}; 
                                                   background-color: #cccccc; 
                                                   margin-bottom: 10px;">
                    <p style="margin: 0px 0px 8px 0px; font-weight: bold; font-size: 14px; line-height: 1.2;">{r['Full_Name']}</p>
                    <span style="background-color: {warna_tema}; 
                                 color: white; 
                                 padding: 3px 10px; 
                                 border-radius: 12px; 
                                 font-size: 11px; 
                                 font-weight: bold;
                                 display: inline-block;">{status_rsvp}</span>
                </div>
                """
                st.markdown(kad_html, unsafe_allow_html=True)
else:
    st.info("Tiada ahli (Member) dijumpai untuk trip ini. Sila daftarkan ahli di menu 'Urus Ahli'.")

st.divider()


# --- PERSEDIAAN DATA: TARIK GAMBAR KENANGAN DARI INFO_KEM ---
k1, k2, k3, k4, k5 = "", "", "", "", ""
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=0)
    if not info_db.empty and current_trip in info_db['ID_Trip'].values:
        info_semasa = info_db[info_db['ID_Trip'] == current_trip].iloc[0]
        k1 = str(info_semasa.get('Kenangan_1', '')).replace('nan', '').strip()
        k2 = str(info_semasa.get('Kenangan_2', '')).replace('nan', '').strip()
        k3 = str(info_semasa.get('Kenangan_3', '')).replace('nan', '').strip()
        k4 = str(info_semasa.get('Kenangan_4', '')).replace('nan', '').strip()
        k5 = str(info_semasa.get('Kenangan_5', '')).replace('nan', '').strip()
except:
    pass

senarai_kenangan = [k for k in [k1, k2, k3, k4, k5] if k != ""]


# --- 3. GABUNGAN CARTA PAI (KIRI) & SLIDESHOW KENANGAN (KANAN) ---
st.subheader("📊 Rumusan Kehadiran & 📸 Kenang-Kenangan")

col_kiri, col_kanan = st.columns([1, 1.2])

# BAHAGIAN KIRI: CARTA PAI
with col_kiri:
    if not merged_df.empty:
        status_counts = merged_df['Status'].value_counts()
        
        kategori_status = ['Hadir', 'Tidak Hadir', 'Belum Pasti', 'Belum Sahkan']
        warna_status = ['#28a745', '#dc3545', '#ffc107', '#6c757d']
        
        df_pie = pd.DataFrame({
            'Status': kategori_status,
            'Jumlah': [int(status_counts.get(s, 0)) for s in kategori_status],
            'Warna': warna_status
        })
        df_pie = df_pie[df_pie['Jumlah'] > 0]
        
        if not df_pie.empty:
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Jumlah", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", 
                                scale=alt.Scale(domain=kategori_status, range=warna_status),
                                legend=alt.Legend(title="Petunjuk Status")),
                tooltip=['Status', 'Jumlah']
            ).properties(
                width=280, 
                height=280 
            ).configure_view(strokeWidth=0)
            
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.write("Belum ada rekod kehadiran.")
    else:
        st.info("Data ahli tidak dijumpai.")

# BAHAGIAN KANAN: SLIDESHOW KENANGAN
with col_kanan:
    if len(senarai_kenangan) > 0:
        divs_gambar = ""
        for img_url in senarai_kenangan:
            divs_gambar += f"""
            <div class="mySlidesMemory fadeMemory">
                <img src="{img_url}" style="width:100%; height:280px; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            </div>
            """
            
        html_kod_kenangan = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        * {{box-sizing: border-box}}
        body {{font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: transparent;}}
        .slideshow-container-mem {{
          max-width: 100%;
          position: relative;
          margin: auto;
          border-radius: 10px;
        }}
        .mySlidesMemory {{display: none; text-align: center;}}
        .prevMem, .nextMem {{
          cursor: pointer;
          position: absolute;
          top: 50%;
          width: auto;
          padding: 10px;
          margin-top: -22px;
          color: white;
          font-weight: bold;
          font-size: 18px;
          transition: 0.6s ease;
          border-radius: 0 3px 3px 0;
          user-select: none;
          background-color: rgba(0,0,0,0.5);
          text-decoration: none;
        }}
        .nextMem {{right: 0; border-radius: 3px 0 0 3px;}}
        .prevMem:hover, .nextMem:hover {{background-color: rgba(0,0,0,0.9);}}
        .fadeMemory {{
          animation-name: fadeMem;
          animation-duration: 1.5s;
        }}
        @keyframes fadeMem {{
          from {{opacity: .4}} 
          to {{opacity: 1}}
        }}
        </style>
        </head>
        <body>

        <div class="slideshow-container-mem">
          {divs_gambar}
          <a class="prevMem" onclick="plusSlidesMem(-1)">❮</a>
          <a class="nextMem" onclick="plusSlidesMem(1)">❯</a>
        </div>

        <script>
        let slideIndexMem = 0;
        let timerMem;
        showSlidesMem();

        function plusSlidesMem(n) {{
          clearTimeout(timerMem);
          showSlidesMem(slideIndexMem += n);
        }}

        function showSlidesMem(n) {{
          let i;
          let slides = document.getElementsByClassName("mySlidesMemory");
          if (slides.length === 0) return;
          if (n !== undefined) {{ slideIndexMem = n; }}
          if (slideIndexMem >= slides.length) {{slideIndexMem = 0}}    
          if (slideIndexMem < 0) {{slideIndexMem = slides.length - 1}}
          for (i = 0; i < slides.length; i++) {{
            slides[i].style.display = "none";  
          }}
          slides[slideIndexMem].style.display = "block";  
          timerMem = setTimeout(function(){{ plusSlidesMem(1); }}, 4000); // Auto gerak 4 saat
        }}
        </script>

        </body>
        </html>
        """
        components.html(html_kod_kenangan, height=300)
    else:
        st.info("ℹ️ Ruangan memori kosong. Admin boleh muat naik gambar kenang-kenangan di panel bawah.")

st.divider()


# --- 4. BUTANG PENGESAHAN KEHADIRAN & PENGUMUMAN ---
if st.button("🚀 Klik Di Sini Untuk Membuka Halaman Pengesahan Kehadiran Anda (RSVP)", use_container_width=True, type="primary"):
    st.switch_page("views/kehadiran.py")

st.write("---")
st.subheader("📢 Pengumuman Penting")
st.markdown(f"""
* **Peringatan Ahli:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk tujuan kecemasan.
* **Maklumat Trip:** Anda sedang melihat ringkasan status bagi projek **{nama_trip}**.
""")


# --- 5. PANEL ADMIN: URUS GAMBAR KENANGAN ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Pengurusan Gambar Kenangan (Admin Sahaja)")
    
    with st.form("form_kenangan_admin"):
        st.write(f"Sila masukkan pautan (Direct Link) gambar dari postimages.org untuk dipaparkan di *Slideshow* **{nama_trip}**.")
        
        in_k1 = st.text_input("🖼️ Gambar Kenangan 1", value=k1)
        in_k2 = st.text_input("🖼️ Gambar Kenangan 2", value=k2)
        in_k3 = st.text_input("🖼️ Gambar Kenangan 3", value=k3)
        in_k4 = st.text_input("🖼️ Gambar Kenangan 4", value=k4)
        in_k5 = st.text_input("🖼️ Gambar Kenangan 5", value=k5)
        
        submit_kenangan = st.form_submit_button("Simpan Koleksi Kenangan")
        
        if submit_kenangan:
            if not current_trip:
                st.error("Sila pilih aktiviti di sidebar terlebih dahulu.")
            else:
                with st.spinner("Sedang menyimpan pautan gambar ke pangkalan data..."):
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                        
                        # Pastikan database ada dan kolum baru wujud
                        if info_pukal.empty or 'ID_Trip' not in info_pukal.columns:
                            info_pukal = pd.DataFrame(columns=["ID_Trip"])
                        
                        for col_name in ['Kenangan_1', 'Kenangan_2', 'Kenangan_3', 'Kenangan_4', 'Kenangan_5']:
                            if col_name not in info_pukal.columns:
                                info_pukal[col_name] = ""
                                
                        # Kemaskini baris trip semasa
                        if current_trip in info_pukal['ID_Trip'].values:
                            idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                            info_pukal.at[idx, 'Kenangan_1'] = in_k1.strip()
                            info_pukal.at[idx, 'Kenangan_2'] = in_k2.strip()
                            info_pukal.at[idx, 'Kenangan_3'] = in_k3.strip()
                            info_pukal.at[idx, 'Kenangan_4'] = in_k4.strip()
                            info_pukal.at[idx, 'Kenangan_5'] = in_k5.strip()
                        else:
                            # Jika trip ni tak pernah ada di Info_Kem langsung, kita bina row baru
                            new_row = pd.DataFrame([{
                                "ID_Trip": current_trip,
                                "Kenangan_1": in_k1.strip(),
                                "Kenangan_2": in_k2.strip(),
                                "Kenangan_3": in_k3.strip(),
                                "Kenangan_4": in_k4.strip(),
                                "Kenangan_5": in_k5.strip()
                            }])
                            info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)
                            
                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Gambar kenang-kenangan berjaya disimpan! Slideshow akan dikemaskini.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memproses pangkalan data: {e}")
