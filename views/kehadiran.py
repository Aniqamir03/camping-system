import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.title("📝 Pengesahan Kehadiran (RSVP)")
st.write("Sahkan status kehadiran anda untuk memudahkan urusan perancangan logistik dan tapak perkhemahan.")

# Ambil maklumat pengguna dan trip aktif dari memori sistem
current_trip = st.session_state.get('current_trip_id', '')
username_semasa = st.session_state.get('username', '')
nama_semasa = st.session_state.get('full_name', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# Dapatkan nama trip semasa untuk paparan info kontekstual
nama_trip_paparan = "Aktiviti Semasa"
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip_paparan = trip_info.iloc[0]['Nama_Trip']
except:
    pass

st.info(f"📍 Anda sedang menguruskan status kehadiran untuk aktiviti: **{nama_trip_paparan}**")

# Sediakan nilai default awal
status_semasa_user = "Belum Sahkan"
catatan_semasa_user = ""

try:
    kehadiran_db = conn.read(worksheet="Kehadiran", ttl=0)
    if not kehadiran_db.empty:
        # Bersihkan data awal untuk elak ralat NaN
        for col in kehadiran_db.columns:
            kehadiran_db[col] = kehadiran_db[col].astype(str).replace('nan', '').str.strip()
            
        # Cari rekod lama pengguna untuk trip ini
        rekod_user = kehadiran_db[(kehadiran_db['ID_Trip'] == current_trip) & (kehadiran_db['Username'] == username_semasa)]
        if not rekod_user.empty:
            status_semasa_user = rekod_user.iloc[0].get('Status', 'Belum Sahkan')
            catatan_semasa_user = rekod_user.iloc[0].get('Catatan', '')
except:
    kehadiran_db = pd.DataFrame(columns=["ID_Trip", "Username", "Full_Name", "Status", "Catatan", "Masa_Sahkan"])

# Papar kad informasi status semasa pengguna
if status_semasa_user == "Hadir":
    st.success(f"✅ Status Semasa Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
elif status_semasa_user == "Tidak Hadir":
    st.error(f"❌ Status Semasa Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
elif status_semasa_user == "Belum Pasti":
    st.warning(f"⚠️ Status Semasa Anda: **{status_semasa_user}** {f'({catatan_semasa_user})' if catatan_semasa_user else ''}")
else:
    st.info("ℹ️ Anda belum membuat sebarang pengesahan kehadiran untuk aktiviti/trip ini.")

# Borang Penghantaran RSVP Ahli
with st.form("form_rsvp_page"):
    st.write("Sila buat atau tukar pilihan status anda di sini:")
    
    list_status = ["Hadir", "Tidak Hadir", "Belum Pasti"]
    default_idx = list_status.index(status_semasa_user) if status_semasa_user in list_status else 0
    
    inp_status = st.selectbox("Status Kehadiran:", list_status, index=default_idx)
    inp_catatan = st.text_input("Catatan / Nota Tambahan (Pilihan):", value=catatan_semasa_user)
    
    submit_rsvp = st.form_submit_button("Hantar Status Kehadiran")
    
    if submit_rsvp:
        if not current_trip:
            st.error("Ralat: Tiada aktiviti aktif dikesan di menu tepi!")
        else:
            masa_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            data_rsvp_baru = pd.DataFrame([{
                "ID_Trip": current_trip,
                "Username": username_semasa,
                "Full_Name": nama_semasa,
                "Status": inp_status,
                "Catatan": inp_catatan.strip(),
                "Masa_Sahkan": masa_sekarang
            }])
            
            try:
                if not kehadiran_db.empty and 'ID_Trip' in kehadiran_db.columns and 'Username' in kehadiran_db.columns:
                    kehadiran_db = kehadiran_db[~((kehadiran_db['ID_Trip'] == current_trip) & (kehadiran_db['Username'] == username_semasa))]
                    updated_kehadiran = pd.concat([kehadiran_db, data_rsvp_baru], ignore_index=True)
                else:
                    updated_kehadiran = data_rsvp_baru
            except:
                updated_kehadiran = data_rsvp_baru
                
            conn.update(worksheet="Kehadiran", data=updated_kehadiran)
            st.success("Status kehadiran anda berjaya dikemaskini!")
            st.cache_data.clear()
            st.rerun()


# --- JADUAL PEMANTAUAN PINTAR (KHAS UNTUK ADMIN SAHAJA) ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("📊 Panel Pemantauan Kehadiran Kumpulan (Admin Sahaja)")
    
    try:
        db_kehadiran_papar = conn.read(worksheet="Kehadiran", ttl=0)
        if not db_kehadiran_papar.empty and 'ID_Trip' in db_kehadiran_papar.columns:
            for col in db_kehadiran_papar.columns:
                db_kehadiran_papar[col] = db_kehadiran_papar[col].astype(str).replace('nan', '').str.strip()
                
            kehadiran_trip_ini = db_kehadiran_papar[db_kehadiran_papar['ID_Trip'] == current_trip]
            
            if not kehadiran_trip_ini.empty:
                k_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Hadir'])
                k_tak_hadir = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Tidak Hadir'])
                k_pasti = len(kehadiran_trip_ini[kehadiran_trip_ini['Status'] == 'Belum Pasti'])
                
                c1, c2, c3 = st.columns(3)
                c1.metric("🟢 Jumlah Hadir", f"{k_hadir} Orang")
                c2.metric("🔴 Tidak Hadir", f"{k_tak_hadir} Orang")
                c3.metric("🟡 Belum Pasti", f"{k_pasti} Orang")
                
                st.write("▼ **Senarai Status Respon Keseluruhan Ahli:**")
                kolum_papar_kehadiran = ['Full_Name', 'Status', 'Catatan', 'Masa_Sahkan']
                st.dataframe(kehadiran_trip_ini[kolum_papar_kehadiran], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Belum ada mana-mana ahli yang merekodkan status maklum balas mereka.")
        else:
            st.info("ℹ️ Pangkalan data maklum balas kehadiran masih kosong.")
    except Exception as e:
        st.write("Buku rekod kehadiran sedia ada masih bersih daripada data.")
