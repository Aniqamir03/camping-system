import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Ambil ID_Trip dari memori (yang dipilih di sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # --- 0. TARIK INFO TRIP DARI GSHEETS ---
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
    
    # Cari rekod trip yang sepadan dengan ID yang dipilih
    trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
    
    if not trip_info.empty:
        nama_trip = trip_info.iloc[0]['Nama_Trip']
        tarikh_str = str(trip_info.iloc[0]['Tarikh'])
    else:
        nama_trip = "Aktiviti Semasa"
        tarikh_str = ""

    st.title(f"🏕️ Papan Pemuka (Dashboard) - {nama_trip}")
    st.write(f"Selamat Datang, **{st.session_state['full_name']}**! Semak status persiapan trip kita di sini.")

    # --- 1. KIRAAN DETIK (COUNTDOWN) DINAMIK ---
    if tarikh_str:
        try:
            # Tukar tarikh dari format teks ke format masa Python (Pastikan GSheet guna YYYY-MM-DD)
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
            st.warning("⚠️ Sila pastikan tarikh di tab Senarai_Trip berformat YYYY-MM-DD (Contoh: 2026-05-22) untuk membolehkan *countdown* berfungsi.")
            
    st.divider()

    # --- 2. RINGKASAN STATISTIK (KPI CARDS) BERDASARKAN TRIP ---
    kewangan_db = conn.read(worksheet="Kewangan", ttl=0)
    inventory_db = conn.read(worksheet="Inventory", ttl=0)
    
    col1, col2, col3 = st.columns(3)
    
    # Kira Baki Kewangan (Ditapis)
    if not kewangan_db.empty and 'ID_Trip' in kewangan_db.columns:
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
    if not inventory_db.empty and 'ID_Trip' in inventory_db.columns:
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

except Exception as e:
    st.error("Gagal memuatkan data. Pastikan tab 'Senarai_Trip', 'Kewangan', dan 'Inventory' mempunyai kolum 'ID_Trip'.")

st.divider()

# --- 3. PENGUMUMAN / NOTA RINGKAS ---
st.subheader("📢 Pengumuman Penting")
st.markdown(f"""
* **Peringatan Admin:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk tujuan kecemasan.
* **Maklumat Trip:** Anda sedang melihat ringkasan status bagi projek **{nama_trip}**.
""")
