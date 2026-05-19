import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import altair as alt
import streamlit.components.v1 as components
import re

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI PEMPROSESAN URL YOUTUBE ---
def get_yt_embed_url(url):
    if not url or url == 'nan':
        return None
    # Ekstrak ID video menggunakan regex
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        video_id = video_id_match.group(1)
        # Tambah parameter autoplay=1 dan mute=1 (diperlukan oleh browser moden untuk autoplay)
        return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"
    return None

# --- 0. TARIK INFO TRIP UTAMA ---
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=600)
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

# --- PERSEDIAAN DATA: TARIK INFO_KEM (VIDEO & KENANGAN) ---
yt_url_raw = ""
k1, k2, k3, k4, k5 = "", "", "", "", ""
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if not info_db.empty and current_trip in info_db['ID_Trip'].values:
        info_semasa = info_db[info_db['ID_Trip'] == current_trip].iloc[0]
        yt_url_raw = str(info_semasa.get('Youtube_URL', '')).replace('nan', '').strip()
        k1 = str(info_semasa.get('Kenangan_1', '')).replace('nan', '').strip()
        k2 = str(info_semasa.get('Kenangan_2', '')).replace('nan', '').strip()
        k3 = str(info_semasa.get('Kenangan_3', '')).replace('nan', '').strip()
        k4 = str(info_semasa.get('Kenangan_4', '')).replace('nan', '').strip()
        k5 = str(info_semasa.get('Kenangan_5', '')).replace('nan', '').strip()
except:
    pass

senarai_kenangan = [k for k in [k1, k2, k3, k4, k5] if k != ""]

# --- PERSEDIAAN DATA: USERS & KEHADIRAN ---
try:
    users_db = conn.read(worksheet="Users", ttl=600)
    for col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()
    users_member = users_db[users_db['Role'].str.lower() == 'member']
except:
    users_member = pd.DataFrame()

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=600)
    kehadiran_semasa = kehadiran_db[kehadiran_db['ID_Trip'] == current_trip]
except:
    kehadiran_semasa = pd.DataFrame()

if not users_member.empty:
    merged_df = pd.merge(users_member, kehadiran_semasa[['Username', 'Status']], on='Username', how='left')
    merged_df['Status'] = merged_df['Status'].fillna('Belum Sahkan')
else:
    merged_df = pd.DataFrame()


# --- 2. SUSUNAN ATAS: PROFIL AHLI (KIRI) & YOUTUBE (KANAN) ---
col_profil_utama, col_yt_utama = st.columns([1.8, 1.2])

with col_profil_utama:
    st.subheader("👥 Kad Profil Ahli")
    avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    
    if not merged_df.empty:
        # Gunakan 3 kolum di dalam ruang kiri supaya lebih kompak
        kolum_grid = 3
        pecahan_baris = [merged_df[i:i + kolum_grid] for i in range(0, len(merged_df), kolum_grid)]
        
        for baris_data in pecahan_baris:
            cols = st.columns(kolum_grid)
            for indeks, (_, r) in enumerate(baris_data.iterrows()):
                with cols[indeks]:
                    url_gambar = r['Profile_Pic_URL'] if r['Profile_Pic_URL'] != "" else avatar_default
                    status_rsvp = r['Status']
                    warna = "#28a745" if status_rsvp == "Hadir" else "#dc3545" if status_rsvp == "Tidak Hadir" else "#ffc107" if status_rsvp == "Belum Pasti" else "#6c757d"
                    
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; border: 1px solid #4d4d4d; border-radius: 10px; margin-bottom: 10px; background-color: rgba(255,255,255,0.05);">
                        <img src="{url_gambar}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%; border: 2px solid {warna};">
                        <p style="margin: 5px 0 3px 0; font-size: 12px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{r['Full_Name']}</p>
                        <span style="background-color: {warna}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; display: inline-block;">{status_rsvp}</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Tiada ahli ditemui.")

with col_yt_utama:
    st.subheader("📺 Video Aktiviti")
    yt_embed = get_yt_embed_url(yt_url_raw)
    if yt_embed:
        # Embed video dengan autoplay
        st.markdown(f"""
        <iframe width="100%" height="250" src="{yt_embed}" 
        title="YouTube video player" frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        allowfullscreen style="border-radius:12px;"></iframe>
        """, unsafe_allow_html=True)
    else:
        st.warning("Admin belum menetapkan pautan video YouTube untuk trip ini.")

st.divider()


# --- 3. GABUNGAN CARTA PAI (KIRI) & SLIDESHOW KENANGAN (KANAN) ---
st.subheader("📊 Rumusan Kehadiran & 📸 Kenang-Kenangan")

col_kiri, col_kanan = st.columns([1, 1.2])

with col_kiri:
    if not merged_df.empty:
        status_counts = merged_df['Status'].value_counts()
        kategori_status = ['Hadir', 'Tidak Hadir', 'Belum Pasti', 'Belum Sahkan']
        warna_status = ['#28a745', '#dc3545', '#ffc107', '#6c757d']
        df_pie = pd.DataFrame({'Status': kategori_status, 'Jumlah': [int(status_counts.get(s, 0)) for s in kategori_status], 'Warna': warna_status})
        df_pie = df_pie[df_pie['Jumlah'] > 0]
        
        if not df_pie.empty:
            pie_chart = alt.Chart(df_pie).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Jumlah", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=alt.Scale(domain=kategori_status, range=warna_status), legend=alt.Legend(title="Status")),
                tooltip=['Status', 'Jumlah']
            ).properties(width=280, height=280).configure_view(strokeWidth=0)
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.write("Belum ada rekod.")

with col_kanan:
    if len(senarai_kenangan) > 0:
        divs_gambar = "".join([f'<div class="mySlidesMemory fadeMemory"><img src="{url}" style="width:100%; height:280px; object-fit:cover; border-radius:10px;"></div>' for url in senarai_kenangan])
        html_kod = f"""
        <div class="slideshow-container-mem">{divs_gambar}</div>
        <style>
            .mySlidesMemory {{display: none; text-align: center;}}
            .fadeMemory {{animation: fadeMem 1.5s;}}
            @keyframes fadeMem {{from {{opacity: .4}} to {{opacity: 1}}}}
        </style>
        <script>
            let slideIndex = 0;
            function show() {{
                let s = document.getElementsByClassName("mySlidesMemory");
                for (let i=0; i<s.length; i++) s[i].style.display = "none";
                slideIndex++; if (slideIndex > s.length) slideIndex = 1;
                s[slideIndex-1].style.display = "block";
                setTimeout(show, 4000);
            }}
            show();
        </script>
        """
        components.html(html_kod, height=300)
    else:
        st.info("Ruangan memori kosong.")

st.divider()

# --- 4. BUTANG RSVP ---
if st.button("🚀 Buka Halaman Pengesahan Kehadiran (RSVP)", use_container_width=True, type="primary"):
    st.switch_page("views/kehadiran.py")

# --- 5. PANEL ADMIN: URUS VIDEO & GAMBAR ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Admin: Urus Media")
    
    with st.form("form_media_admin"):
        st.write("### 📺 Pautan YouTube")
        in_yt = st.text_input("Masukkan URL YouTube (Contoh: https://www.youtube.com/watch?v=xxxx)", value=yt_url_raw)
        
        st.write("### 🖼️ Gambar Kenangan")
        in_k1 = st.text_input("Kenangan 1", value=k1)
        in_k2 = st.text_input("Kenangan 2", value=k2)
        in_k3 = st.text_input("Kenangan 3", value=k3)
        in_k4 = st.text_input("Kenangan 4", value=k4)
        in_k5 = st.text_input("Kenangan 5", value=k5)
        
        submit_media = st.form_submit_button("Simpan Semua Media")
        
        if submit_media:
            if not current_trip:
                st.error("Pilih trip di sidebar!")
            else:
                try:
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=600)
                    
                    # PASTIKAN KOLUM WUJUD DAN DIPAKSA MENJADI STRING (KALIS RALAT FLOAT64)
                    kolum_media = ['Youtube_URL', 'Kenangan_1', 'Kenangan_2', 'Kenangan_3', 'Kenangan_4', 'Kenangan_5']
                    for col in kolum_media:
                        if col not in info_pukal.columns: 
                            info_pukal[col] = ""
                        # Paksa kolum menjadi teks sebelum sumbat link!
                        info_pukal[col] = info_pukal[col].astype(str).replace('nan', '')
                    
                    if current_trip in info_pukal['ID_Trip'].values:
                        idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                        info_pukal.at[idx, 'Youtube_URL'] = str(in_yt).strip()
                        info_pukal.at[idx, 'Kenangan_1'] = str(in_k1).strip()
                        info_pukal.at[idx, 'Kenangan_2'] = str(in_k2).strip()
                        info_pukal.at[idx, 'Kenangan_3'] = str(in_k3).strip()
                        info_pukal.at[idx, 'Kenangan_4'] = str(in_k4).strip()
                        info_pukal.at[idx, 'Kenangan_5'] = str(in_k5).strip()
                        
                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Media dikemaskini!")
                        
                        # MAGIC REFRESH
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"Ralat: {e}")
