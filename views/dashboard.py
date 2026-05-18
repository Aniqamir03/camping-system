import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.title("🏕️ Papan Pemuka (Dashboard) Kem Redang")
st.write(f"Selamat Datang, **{st.session_state['full_name']}**! Semak status persiapan trip kita di sini.")

# --- 1. KIRAAN DETIK (COUNTDOWN) ---
tarikh_kem = datetime(2026, 5, 22) # Tarikh trip Redang
hari_ini = datetime.now()
baki_hari = (tarikh_kem - hari_ini).days

if baki_hari > 0:
    st.info(f"⏳ **{baki_hari} Hari Lagi** sebelum kita bertolak ke Pulau Redang! Sediakan mental dan fizikal.")
elif baki_hari == 0:
    st.success("🎉 **HARI INI KITA BERTOLAK!** Jangan ada barang yang tertinggal!")
else:
    st.write("✨ Kenangan Indah Perkhemahan Pulau Redang 2026.")

st.divider()

# --- 2. RINGKASAN STATISTIK (KPI CARDS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Ambil data dari Kewangan & Inventory
    kewangan_db = conn.read(worksheet="Kewangan", ttl=0)
    inventory_db = conn.read(worksheet="Inventory", ttl=0)
    
    col1, col2, col3 = st.columns(3)
    
    # Kira Baki Kewangan
    if not kewangan_db.empty:
        kewangan_db['Jumlah'] = pd.to_numeric(kewangan_db['Jumlah'], errors='coerce').fillna(0)
        total_masuk = kewangan_db[kewangan_db['Jenis'] == 'Masuk']['Jumlah'].sum()
        total_keluar = kewangan_db[kewangan_db['Jenis'] == 'Keluar']['Jumlah'].sum()
        baki_duit = total_masuk - total_keluar
        col1.metric("Baki Tabung Semasa", f"RM {baki_duit:.2f}")
    else:
        col1.metric("Baki Tabung Semasa", "RM 0.00")
        
    # Kira Status Barang
    if not inventory_db.empty:
        total_barang = len(inventory_db)
        # Tukar kolum Dibawa_Oleh kepada string dan buang space untuk elak error
        inventory_db['Dibawa_Oleh'] = inventory_db['Dibawa_Oleh'].astype(str).str.strip()
        barang_claimed = len(inventory_db[inventory_db['Dibawa_Oleh'] != ''])
        
        col2.metric("Barang Dah Berpunya", f"{barang_claimed} / {total_barang}")
        col3.metric("Barang Belum di-Claim", f"{total_barang - barang_claimed}")
    else:
        col2.metric("Barang Dah Berpunya", "0")
        col3.metric("Barang Belum di-Claim", "0")

except Exception as e:
    st.warning("Isi data pada tab 'Kewangan' & 'Inventory' di GSheet dahulu untuk melihat ringkasan statistik.")

st.divider()

# --- 3. PENGUMUMAN / NOTA RINGKAS ---
st.subheader("📢 Pengumuman Penting")
st.markdown("""
* **Peringatan Admin:** Sila pastikan no. telefon waris diisi lengkap di bahagian **Profil Saya** untuk tujuan kecemasan.
* **Barang Peribadi:** Setiap orang wajib bawa ubat peribadi, powerbank, dan baju salin secukupnya.
""")
