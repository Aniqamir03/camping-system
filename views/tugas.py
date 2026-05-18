
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔥 Jadual Tugasan Ahli (Duty Roster)")
st.write("Pembahagian tugas secara adil demi keharmonian bersama sepanjang perkhemahan.")

conn = st.connection("gsheets", type=GSheetsConnection)
tugas_db = conn.read(worksheet="Tugasan", ttl=0)

# Paparkan jadual tugasan semasa
st.subheader("📋 Senarai Tugas Perkhemahan")
if not tugas_db.empty:
    st.dataframe(tugas_db, use_container_width=True, hide_index=True)
else:
    st.info("Jadual tugasan masih kosong.")

# Khas untuk Admin mengemaskini jadual tugasan terus dari app
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("⚙️ Kemaskini Penugasan Ahli (Admin Sahaja)")
    
    with st.form("borang_tugas"):
        # Ambil senarai ahli untuk dijadikan pilihan drop-down
        users_db = conn.read(worksheet="Users", ttl=60)
        senarai_ahli = users_db['Full_Name'].tolist()
        
        slot_masa = st.text_input("Slot Masa / Hari (Contoh: Jumaat - Malam)")
        jenis_tugas = st.text_input("Jenis Tugasan (Contoh: Memasak Makan Malam & Sediakan Air)")
        ahli_pilihan = st.selectbox("Pilih Ahli Bertanggungjawab:", senarai_ahli)
        
        submit_tugas = st.form_submit_button("Simpan & Kemaskini Jadual")
        
        if submit_tugas:
            if not slot_masa or not jenis_tugas:
                st.warning("Sila isi semua maklumat slot dan tugasan!")
            else:
                # Sediakan data baharu
                tugas_baru = pd.DataFrame([{
                    "Slot_Masa": slot_masa,
                    "Tugasan": jenis_tugas,
                    "Ahli_Bertanggungjawab": ahli_pilihan
                }])
                
                # Append data ke database semasa
                updated_tugas = pd.concat([tugas_db, tugas_baru], ignore_index=True)
                
                # Update ke Google Sheets
                conn.update(worksheet="Tugasan", data=updated_tugas)
                st.success("Jadual tugasan berjaya dikemaskini!")
                st.cache_data.clear()
                st.rerun()
