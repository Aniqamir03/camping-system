import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("💰 Laporan Tabung Perkhemahan")
st.markdown("Transparensi kewangan kumpulan kita. Segala kutipan dan perbelanjaan direkod di sini.")

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    kewangan_db = conn.read(worksheet="Kewangan", ttl=0)

    if not kewangan_db.empty:
        kewangan_db['Jumlah'] = pd.to_numeric(kewangan_db['Jumlah'], errors='coerce').fillna(0)
        
        total_masuk = kewangan_db[kewangan_db['Jenis'] == 'Masuk']['Jumlah'].sum()
        total_keluar = kewangan_db[kewangan_db['Jenis'] == 'Keluar']['Jumlah'].sum()
        baki = total_masuk - total_keluar
        
        # UI ala-ala Dashboard Bank
        st.write("### 💳 Ringkasan Akaun")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Duit Masuk (RM)", f"{total_masuk:.2f}")
        col2.metric("Total Belanja (RM)", f"{total_keluar:.2f}")
        col3.metric("Baki Tabung (RM)", f"{baki:.2f}")
        
        st.divider()
        
        # Paparan Rekod Cantik
        st.write("### 🧾 Sejarah Transaksi")
        # Warnakan duit keluar dan masuk (Guna styler dalam DataFrame)
        df_papar = kewangan_db[['Perkara', 'Jumlah', 'Jenis', 'Oleh_Siapa']].copy()
        st.dataframe(df_papar, use_container_width=True, hide_index=True)
    else:
        st.info("Tiada rekod transaksi setakat ini.")
except:
    st.error("Gagal memuatkan data kewangan.")

if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Mod Admin: Sila rekod semua transaksi masuk/keluar ke dalam Google Sheets tab 'Kewangan'.")
