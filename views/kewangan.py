import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("💰 Laporan Tabung Perkhemahan")
st.markdown("Transparensi kewangan kumpulan kita. Segala kutipan dan perbelanjaan direkod di sini.")

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    kewangan_db = conn.read(worksheet="Kewangan", ttl=0)

    if not kewangan_db.empty:
        # Semak dan bersihkan kolum ID_Trip
        if 'ID_Trip' in kewangan_db.columns:
            kewangan_db['ID_Trip'] = kewangan_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            
            # KOD MAGIK (FILTERING): Tarik data ikut trip semasa
            current_trip = st.session_state.get('current_trip_id', '')
            kewangan_semasa = kewangan_db[kewangan_db['ID_Trip'] == current_trip].copy() 
            
            if not kewangan_semasa.empty:
                kewangan_semasa['Jumlah'] = pd.to_numeric(kewangan_semasa['Jumlah'], errors='coerce').fillna(0)
                
                total_masuk = kewangan_semasa[kewangan_semasa['Jenis'] == 'Masuk']['Jumlah'].sum()
                total_keluar = kewangan_semasa[kewangan_semasa['Jenis'] == 'Keluar']['Jumlah'].sum()
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
                df_papar = kewangan_semasa[['Perkara', 'Jumlah', 'Jenis', 'Oleh_Siapa']].copy()
                st.dataframe(df_papar, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Tiada rekod transaksi kewangan untuk aktiviti/trip ini setakat ini.")
        else:
            st.error("⚠️ Kolum 'ID_Trip' tidak wujud di dalam tab Kewangan (Google Sheets).")
    else:
        st.info("Tiada rekod transaksi setakat ini.")
except Exception as e:
    st.error(f"Gagal memuatkan data kewangan: {e}")

if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Mod Admin: Sila rekod semua transaksi masuk/keluar ke dalam Google Sheets tab 'Kewangan' (Pastikan letak ID_Trip yang betul).")
