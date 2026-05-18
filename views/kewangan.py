import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("money 💰 Pengurusan Kewangan Trip")

conn = st.connection("gsheets", type=GSheetsConnection)
kewangan_db = conn.read(worksheet="Kewangan", ttl=0)

# Tukar kolum Jumlah kepada nombor untuk pengiraan matematik
if not kewangan_db.empty:
    kewangan_db['Jumlah'] = pd.to_numeric(kewangan_db['Jumlah'], errors='coerce').fillna(0)
    
    # Kira Ringkasan
    total_masuk = kewangan_db[kewangan_db['Jenis'] == 'Masuk']['Jumlah'].sum()
    total_keluar = kewangan_db[kewangan_db['Jenis'] == 'Keluar']['Jumlah'].sum()
    baki = total_masuk - total_keluar
    
    # Paparkan Kad Ringkasan (KPI)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Duit Masuk (Kutipan)", f"RM {total_masuk:.2f}")
    col2.metric("Total Duit Keluar (Belanja)", f"RM {total_keluar:.2f}")
    col3.metric("Baki Semasa Tabung", f"RM {baki:.2f}")
    
    st.divider()
    st.subheader("📊 Rekod Transaksi")
    st.dataframe(kewangan_db, use_container_width=True, hide_index=True)
else:
    st.info("Belum ada sebarang rekod transaksi kewangan.")

# Rekod Transaksi Baru (Khas untuk Admin / Bendahari)
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("✍️ Rekod Transaksi Baru (Admin Sahaja)")
    with st.form("borang_kewangan"):
        perkara = st.text_input("Perkara / Keterangan (Contoh: Kutipan yuran Fitri / Beli Arang)")
        jumlah = st.number_input("Jumlah (RM)", min_value=0.01, step=0.10)
        jenis = st.radio("Jenis Transaksi", ["Masuk", "Keluar"], horizontal=True)
        oleh = st.text_input("Oleh Siapa", value=st.session_state["full_name"])
        
        submit_kew = st.form_submit_button("Simpan Transaksi")
        
        if submit_kew and perkara:
            id_trans = f"TX{len(kewangan_db) + 1:03d}"
            transaksi_baru = pd.DataFrame([{
                "ID_Transaksi": id_trans,
                "Perkara": perkara,
                "Jumlah": jumlah,
                "Jenis": jenis,
                "Oleh_Siapa": oleh
            }])
            updated_kew = pd.concat([kewangan_db, transaksi_baru], ignore_index=True)
            conn.update(worksheet="Kewangan", data=updated_kew)
            st.success("Transaksi berjaya direkodkan!")
            st.cache_data.clear()
            st.rerun()
