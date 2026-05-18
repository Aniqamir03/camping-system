import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🎒 Status Logistik & Peralatan")
st.markdown("Senarai rasmi peralatan perkhemahan. **Sila semak nama anda dan pastikan barang dibawa!**")

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    inventory_db = conn.read(worksheet="Inventory", ttl=0)
    
    if not inventory_db.empty:
        # 1. Bersihkan semua data terlebih dahulu (termasuk ID_Trip) untuk elak error NaN
        for col in ['ID_Trip', 'ID_Barang', 'Nama_Barang', 'Kategori', 'Kuantiti', 'Dibawa_Oleh']:
            if col in inventory_db.columns:
                inventory_db[col] = inventory_db[col].astype(str).replace('nan', '').str.strip()

        # 2. KOD MAGIK (FILTERING): Tapis data mengikut ID_Trip yang dipilih di sidebar
        current_trip = st.session_state.get('current_trip_id', '')
        inventory_semasa = inventory_db[inventory_db['ID_Trip'] == current_trip]

        # 3. Proses paparan HANYA jika trip tersebut ada senarai barang
        if not inventory_semasa.empty:
            total_barang = len(inventory_semasa)
            barang_settle = len(inventory_semasa[inventory_semasa['Dibawa_Oleh'] != ''])
            peratus = int((barang_settle / total_barang) * 100) if total_barang > 0 else 0

            # UI Status Persiapan
            st.write("### 📊 Status Persiapan Logistik")
            st.progress(peratus, text=f"Tahap Persiapan: {peratus}% Selesai")
            
            col1, col2 = st.columns(2)
            col1.metric("✅ Barang Sedia", f"{barang_settle} Item")
            col2.metric("⚠️ Barang Belum Berpunya", f"{total_barang - barang_settle} Item")

            st.divider()

            # UI Senarai Semak mengikut Kategori Expander
            st.write("### 📦 Senarai Semak Peralatan")
            kategori_list = inventory_semasa['Kategori'].unique()
            
            for kat in kategori_list:
                if kat != "":
                    with st.expander(f"📌 Kategori: {kat}", expanded=True):
                        df_kat = inventory_semasa[inventory_semasa['Kategori'] == kat]
                        
                        # Format dan cantikkan jadual paparan
                        df_papar = df_kat[['Nama_Barang', 'Kuantiti', 'Dibawa_Oleh']].copy()
                        df_papar.rename(columns={'Nama_Barang': 'Barang', 'Dibawa_Oleh': 'Tanggungjawab'}, inplace=True)
                        st.dataframe(df_papar, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Tiada senarai peralatan direkodkan untuk aktiviti/trip ini.")
    else:
        st.info("Senarai peralatan sedang dikemaskini oleh Admin.")
except Exception as e:
    st.error(f"Gagal memuatkan data peralatan: {e}")

# Paparan khusus untuk Admin
if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Anda adalah Admin. Kemaskini atau tambah senarai ini terus melalui fail Google Sheets (tab 'Inventory') dengan memasukkan ID_Trip yang betul.")
