import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🎒 Status Logistik & Peralatan")
st.markdown("Senarai rasmi peralatan perkhemahan. **Sila semak nama anda dan pastikan barang dibawa!**")

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    inventory_db = conn.read(worksheet="Inventory", ttl=0)
    
    if not inventory_db.empty:
        # Bersihkan data
        for col in ['ID_Barang', 'Nama_Barang', 'Kategori', 'Kuantiti', 'Dibawa_Oleh']:
            if col in inventory_db.columns:
                inventory_db[col] = inventory_db[col].astype(str).replace('nan', '').str.strip()

        total_barang = len(inventory_db)
        barang_settle = len(inventory_db[inventory_db['Dibawa_Oleh'] != ''])
        peratus = int((barang_settle / total_barang) * 100) if total_barang > 0 else 0

        # UI Menarik: Kad Metrik & Progress Bar
        st.write("### 📊 Status Persiapan Logistik")
        st.progress(peratus, text=f"Tahap Persiapan: {peratus}% Selesai")
        
        col1, col2 = st.columns(2)
        col1.metric("✅ Barang Sedia", f"{barang_settle} Item")
        col2.metric("⚠️ Barang Belum Berpunya", f"{total_barang - barang_settle} Item")

        st.divider()

        # UI Menarik: Paparan ikut kategori guna Expander
        st.write("### 📦 Senarai Semak Peralatan")
        kategori_list = inventory_db['Kategori'].unique()
        
        for kat in kategori_list:
            if kat != "":
                with st.expander(f"📌 Kategori: {kat}", expanded=True):
                    df_kat = inventory_db[inventory_db['Kategori'] == kat]
                    # Format jadual supaya lebih kemas
                    df_papar = df_kat[['Nama_Barang', 'Kuantiti', 'Dibawa_Oleh']].copy()
                    df_papar.rename(columns={'Nama_Barang': 'Barang', 'Dibawa_Oleh': 'Tanggungjawab'}, inplace=True)
                    st.dataframe(df_papar, use_container_width=True, hide_index=True)
    else:
        st.info("Senarai peralatan sedang dikemaskini oleh Admin.")
except Exception as e:
    st.error("Gagal memuatkan data peralatan.")

# Borang Admin sahaja yang tinggal
if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Anda adalah Admin. Kemaskini senarai ini terus melalui fail Google Sheets untuk lebih pantas.")
