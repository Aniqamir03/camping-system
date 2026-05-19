import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import altair as alt

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


# --- 2. GRID DIREKTORI PROFIL & STATUS LIVE AHLI (DI NAIKKAN KE ATAS) ---
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


# --- 3. CARTA PAI (PIE CHART) KECIL UNTUK KEHADIRAN ---
st.subheader("📊 Rumusan Kehadiran")

if not merged_df.empty:
    status_counts = merged_df['Status'].value_counts()
    
    kategori_status = ['Hadir', 'Tidak Hadir', 'Belum Pasti', 'Belum Sahkan']
    warna_status = ['#28a745', '#dc3545', '#ffc107', '#6c757d']
    
    # Bina DataFrame kecil khusus untuk Pie Chart
    df_pie = pd.DataFrame({
        'Status': kategori_status,
        'Jumlah': [int(status_counts.get(s, 0)) for s in kategori_status],
        'Warna': warna_status
    })
    
    # Buang status yang jumlahnya sifar (0) supaya carta pai lebih cantik
    df_pie = df_pie[df_pie['Jumlah'] > 0]
    
    # Kita pecahkan paparan kepada 3 kolum supaya carta boleh duduk kemas di tengah dan kecil
    col_kiri, col_tengah, col_kanan = st.columns([1, 2, 1])
    
    with col_tengah:
        if not df_pie.empty:
            # Bina Carta Pai bentuk "Donut" menggunakan Altair (Kalis ralat)
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Jumlah", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", 
                                scale=alt.Scale(domain=kategori_status, range=warna_status),
                                legend=alt.Legend(title="Petunjuk Status")),
                tooltip=['Status', 'Jumlah']
            ).properties(
                width=300, # Saiz dikecilkan!
                height=300 # Saiz dikecilkan!
            ).configure_view(strokeWidth=0)
            
            st.altair_chart(pie_chart, use_container_width=False)
        else:
            st.write("Belum ada data secukupnya untuk carta ini.")
else:
    st.info("Data ahli tidak dijumpai untuk menjana statistik carta.")

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
