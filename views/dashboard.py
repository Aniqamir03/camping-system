import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Ambil ID_Trip dari memori (yang dipilih di sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 0. TARIK INFO TRIP DARI GSHEETS ---
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
st.write(f"Selamat Datang, **{st.session_state['full_name']}**! Semak status persiapan trip kita di sini.")

# --- 1. KIRAAN DETIK (COUNTDOWN) DINAMIK ---
if tarikh_str and tarikh_str.lower() != 'nan':
    try:
        tarikh_kem = pd.to_datetime(tarikh_str).to_pydatetime()
        hari_ini = datetime.now()
        baki_hari = (tarikh_kem - hari_ini).days

        if baki_hari > 0:
            st.info(f"⏳ **{baki_hari} Hari Lagi** sebelum kita bertolak ke {nama_trip}! Sediakan mental dan fizikal.")
        elif baki_hari == 0:
            st.success("🎉 **HARI INI KITA BERTOLAK!** Semoga perjalanan kita semua dipermudahkan!")
        else:
            st.write(f"✨ Kenangan Indah {nama_trip}.")
    except:
        st.warning("⚠️ Format tarikh trip tidak sah. Pastikan format YYYY-MM-DD.")
        
st.divider()

# --- 2. BUTANG NAVIGASI PINTAS KE HALAMAN KEHADIRAN (BARU) ---
st.subheader("📝 Pengesahan Kehadiran Ahli Kumpulan (RSVP)")
st.write("Sila buat pengesahan kehadiran anda atau semak senarai penuh status kehadiran rakan sekumpulan bagi trip aktiviti ini.")

# Butang magik untuk tukar muka surat secara dinamik
if st.button("🚀 Buka Halaman Pengesahan Kehadiran (RSVP)", use_container_width=True, type="primary"):
    st.switch_page("views/kehadiran.py")

st.divider()

# --- 3. PENGUMUMAN / NOTA RINGKAS ---
st.subheader("📢 Pengumuman Penting")
st.markdown(f"""
* **Peringatan Admin:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk tujuan kecemasan.
* **Maklumat Trip:** Anda sedang melihat ringkasan status bagi projek **{nama_trip}**.
""")
