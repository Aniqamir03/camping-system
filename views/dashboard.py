import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Ambil maklumat pengguna dan trip aktif dari memori sistem (session state)
current_trip = st.session_state.get('current_trip_id', '')
username_semasa = st.session_state.get('username', '')
nama_semasa = st.session_state.get('full_name', '')

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
st.write(f"Selamat Datang, **{nama_semasa}**! Semak status persiapan trip kita di sini.")

# --- 1. KIRAAN DETIK (COUNTDOWN) DINAMIK ---
if tarikh_str and tarikh_str.lower() != 'nan':
    try:
        tarikh_kem = pd.to_datetime(tarikh_str).to_pydatetime()
        hari_ini = datetime.now()
        baki_hari = (tarikh_kem - hari_ini).days

        if baki_hari > 0:
            st.info(f"⏳ **{baki_hari} Hari Lagi** sebelum kita bertolak ke {nama_trip}! Sediakan mental dan fizikal.")
        elif baki_hari == 0:
            st.success("🎉 **HARI INI KITA BERTOLAK!** Jangan ada barang yang tertinggal!")
        else:
            st.write(f"✨ Kenangan Indah {nama_trip}.")
    except:
        st.warning("⚠️ Format tarikh trip tidak sah. Pastikan format YYYY-MM-DD.")
        
st.divider()


# --- 2. BORANG PENGESAHAN KEHADIRAN (RSVP) AHLI ---
st.subheader("📝 Pengesahan Kehadiran Anda (RSVP)")

# Sediakan nilai default awal
status_semasa_user = "Belum Sahkan"
catatan_semasa_user = ""

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=0)
    if not kehadiran_db.empty:
        # Bersihkan data awal
        for col in kehadiran_db.columns:
            kehadiran_db[col] = kehadiran_db[col].astype(str).replace('nan', '').str.strip()
            
        # Cari kalau user ni dah pernah hantar rsvp untuk trip ini
        rekod_user = kehadiran_db[(kehadiran_db['ID_Trip'] == current_trip) & (kehadiran_db['Username'] == username_semasa)]
        if not rekod_user.empty:
            status_semasa_user = rekod_user.iloc[0].get('Status', 'Belum Sahkan')
            catatan_semasa_user = rekod_user.iloc[0].get('Catatan', '')
except:
    kehadiran_db = pd.DataFrame(columns=["ID_Trip", "Username", "Full_Name", "Status", "Catatan", "Masa_Sahkan"])

# Papar status semasa user dalam kotak alert yang cantik
if status_semasa_user == "Hadir":
    st.success(f"✅ Status Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
elif status_semasa_user == "Tidak Hadir":
    st.error(f"❌ Status Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
elif status_semasa_user == "Belum Pasti":
    st.warning(f"⚠️ Status Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
else:
    st.info("ℹ️ Anda belum membuat pengesahan kehadiran untuk aktiviti/trip ini.")

# Borang kemaskini RSVP
with st.form("form_rsvp_user"):
    st.write("Kemaskini atau sahkan status kehadiran anda di bawah:")
    
    list_status = ["Hadir", "Tidak Hadir", "Belum Pasti"]
    default_idx = list_status.index(status_semasa_user) if status_semasa_user in list_status else 0
    
    inp_status = st.selectbox("Status Kehadiran:", list_status, index=default_idx)
    inp_catatan = st.text_input("Catatan / Nota Tambahan (Pilihan):", value=catatan_semasa_user)
    
    submit_rsvp = st.form_submit_button("Hantar Pengesahan")
    
    if submit_rsvp:
        if not current_trip:
            st.error("Ralat: Sila pilih trip/aktiviti aktif di menu tepi dahulu!")
        else:
            id_trip_save = current_trip
            masa_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Bina baris data baharu
            data_rsvp_baru = pd.DataFrame([{
                "ID_Trip": id_trip_save,
                "Username": username_semasa,
                "Full_Name": nama_semasa,
                "Status": inp_status,
                "Catatan": inp_catatan.strip(),
                "Masa_Sahkan": masa_sekarang
            }])
            
            try:
                # Muat naik semula pangkalan data tanpa rekod lama user tersebut (untuk elak data bertindih)
                if not kehadiran_db.empty and 'ID_Trip' in kehadiran_db.columns and 'Username' in kehadiran_db.columns:
                    kehadiran_db = kehadiran_db[~((kehadiran_db['ID_Trip'] == id_trip_save) & (kehadiran_db['Username'] == username_semasa))]
                    updated_kehadiran = pd.concat([kehadiran_db, data_rsvp_baru], ignore_index=True)
                else:
                    updated_kehadiran = data_rsvp_baru
            except:
                updated_kehadiran = data_rsvp_baru
                
            # Hantar kemaskini ke Google Sheets
            conn.update(worksheet="Kehadiran", data=updated_kehadiran)
            st.success("Kehadiran anda berjaya disahkan dan disimpan!")
            st.cache_data.clear()
            st.rerun()

st.divider()


# --- 3. PAPARAN STATISTIK KEHADIRAN (KHAS UNTUK ADMIN) ---
if st.session_state["role"] == "Admin":
    st.subheader("📊 Panel Pemantauan Kehadiran Kumpulan (Admin Sahaja)")
    
    try:
        db_kehadiran_papar = conn.read(worksheet="Kehadiran", ttl=0)
        if not db_kehadiran_papar.empty and 'ID_Trip' in db_kehadiran_papar.columns:
            # Bersihkan data
            for col in db_kehadiran_papar.columns:
                db_kehadiran_papar[col] = db_kehadiran_papar[col].astype(str).replace('nan', '').str.strip()
                
            # Tapis senarai kehadiran mengikut trip aktif sahaja
            kehadiran_trip_ini = db_kehadiran_papar[db_kehadiran_papar['ID_Trip'] == current_trip]
            
            if not kehadiran_trip_ini.empty:
                # Ringkasan KPI kecil
                k_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Hadir'])
                k_tak_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Tidak Hadir'])
                k_pasti = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Belum Pasti'])
                
                c1, c2, c3 = st.columns(3)
                c1.metric("🟢 Jumlah Hadir", f"{k_hadir} Orang")
                c2.metric("🔴 Tidak Hadir", f"{k_tak_hadir} Orang")
                c3.metric("🟡 Belum Pasti", f"{k_pasti} Orang")
                
                st.write("▼ **Senarai Pengesahan Ahli Kumpulan:**")
                # Paparkan jadual ahli yang dah respon
                kolum_papar_kehadiran = ['Full_Name', 'Status', 'Catatan', 'Masa_Sahkan']
                st.dataframe(kehadiran_trip_ini[kolum_papar_kehadiran], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Belum ada mana-mana ahli kelompok yang membuat pengesahan kehadiran untuk trip ini.")
        else:
            st.info("ℹ️ Pangkalan data kehadiran masih kosong.")
    except Exception as e:
        st.write("Buku rekod kehadiran masih bersih daripada data.")

    st.divider()


# --- 4. PENGUMUMAN / NOTA RINGKAS ---
st.subheader("📢 Pengumuman Penting")
st.markdown(f"""
* **Peringatan Kumpulan:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk memudahkan urusan kecemasan.
* **Maklumat Sistem:** Anda sedang melihat ringkasan status bagi projek **{nama_trip}**.
""")
