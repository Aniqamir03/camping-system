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
    senarai_trip = pd.DataFrame()

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
            st.success("🎉 **HARI INI KITA BERTOLAK!** Jangan ada barang yang tertinggal!")
        else:
            st.write(f"✨ Kenangan Indah {nama_trip}.")
    except:
        st.warning("⚠️ Format tarikh trip tidak sah. Pastikan format YYYY-MM-DD.")
        
st.divider()

# --- 2. RINGKASAN STATISTIK (KPI CARDS) ---
try:
    kewangan_db = conn.read(worksheet="Kewangan", ttl=0)
except:
    kewangan_db = pd.DataFrame()
    
try:
    inventory_db = conn.read(worksheet="Inventory", ttl=0)
except:
    inventory_db = pd.DataFrame()

col1, col2, col3 = st.columns(3)

# Kira Baki Kewangan (Ditapis)
if not kewangan_db.empty and 'ID_Trip' in kewangan_db.columns and current_trip:
    kewangan_semasa = kewangan_db[kewangan_db['ID_Trip'] == current_trip].copy()
    if not kewangan_semasa.empty:
        kewangan_semasa['Jumlah'] = pd.to_numeric(kewangan_semasa['Jumlah'], errors='coerce').fillna(0)
        total_masuk = kewangan_semasa[kewangan_semasa['Jenis'] == 'Masuk']['Jumlah'].sum()
        total_keluar = kewangan_semasa[kewangan_semasa['Jenis'] == 'Keluar']['Jumlah'].sum()
        baki_duit = total_masuk - total_keluar
        col1.metric("Baki Tabung Semasa", f"RM {baki_duit:.2f}")
    else:
        col1.metric("Baki Tabung Semasa", "RM 0.00")
else:
    col1.metric("Baki Tabung Semasa", "RM 0.00")
    
# Kira Status Barang (Ditapis)
if not inventory_db.empty and 'ID_Trip' in inventory_db.columns and current_trip:
    inventory_semasa = inventory_db[inventory_db['ID_Trip'] == current_trip].copy()
    if not inventory_semasa.empty:
        total_barang = len(inventory_semasa)
        inventory_semasa['Dibawa_Oleh'] = inventory_semasa['Dibawa_Oleh'].astype(str).str.strip()
        barang_claimed = len(inventory_semasa[inventory_semasa['Dibawa_Oleh'] != ''])
        
        col2.metric("Barang Dah Berpunya", f"{barang_claimed} / {total_barang}")
        col3.metric("Barang Belum di-Claim", f"{total_barang - barang_claimed}")
    else:
        col2.metric("Barang Dah Berpunya", "0")
        col3.metric("Barang Belum di-Claim", "0")
else:
    col2.metric("Barang Dah Berpunya", "0")
    col3.metric("Barang Belum di-Claim", "0")

st.divider()

# --- 3. PENGUMUMAN / NOTA RINGKAS ---
st.subheader("📢 Pengumuman Penting")
st.markdown(f"""
* **Peringatan Admin:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk tujuan kecemasan.
* **Maklumat Trip:** Anda sedang melihat ringkasan status bagi projek **{nama_trip}**.
""")

# --- 4. PANEL TAMBAH TRIP KHAS UNTUK ADMIN (AUTO-GENERATE ID) ---
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Pengurusan Sistem Aktiviti (Admin Sahaja)")
    
    with st.expander("➕ Daftar Aktiviti / Trip Baharu", expanded=True):
        with st.form("form_tambah_trip"):
            st.write("Isi borang di bawah untuk mendaftarkan aktiviti baharu tanpa perlu membuka Google Sheets.")
            
            new_nama_trip = st.text_input("Nama Aktiviti (Contoh: Trip Janda Baik 2026)")
            new_tarikh = st.date_input("Tarikh Bertolak")
            new_status = st.selectbox("Status Trip", ["Aktif", "Selesai"])
            
            submit_trip = st.form_submit_button("Simpan Aktiviti Baharu")
            
            if submit_trip:
                if not new_nama_trip:
                    st.warning("Nama aktiviti tidak boleh dibiarkan kosong!")
                else:
                    # Logik Automatik ID Trip (Cari jumlah ID sedia ada dan tambah +1)
                    try:
                        db_trip_semasa = conn.read(worksheet="Senarai_Trip", ttl=0)
                        if not db_trip_semasa.empty:
                            next_id = f"TRP{len(db_trip_semasa) + 1:03d}"
                        else:
                            next_id = "TRP001"
                    except:
                        db_trip_semasa = pd.DataFrame(columns=["ID_Trip", "Nama_Trip", "Tarikh", "Status_Trip"])
                        next_id = "TRP001"
                        
                    trip_baru = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Nama_Trip": new_nama_trip.strip(),
                        "Tarikh": new_tarikh.strftime("%Y-%m-%d"),
                        "Status_Trip": new_status
                    }])
                    
                    if not db_trip_semasa.empty:
                        updated_trip = pd.concat([db_trip_semasa, trip_baru], ignore_index=True)
                    else:
                        updated_trip = trip_baru
                        
                    # Simpan ke GSheet
                    conn.update(worksheet="Senarai_Trip", data=updated_trip)
                    st.success(f"Berjaya! Aktiviti '{new_nama_trip}' telah didaftarkan dengan ID: {next_id}.")
                    st.cache_data.clear()
                    st.rerun()
