import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔥 Jadual Tugasan Ahli")
st.markdown("Kerjasama membawa berkat. Sila laksanakan tugas masing-masing demi kelancaran trip kita!")

# Ambil ID_Trip aktif dari memori sistem (sidebar)
current_trip = st.session_state.get('current_trip_id', '')

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    tugas_db = conn.read(worksheet="Tugasan", ttl=0)

    if not tugas_db.empty:
        # Semak dan bersihkan kolum ID_Trip
        if 'ID_Trip' in tugas_db.columns:
            tugas_db['ID_Trip'] = tugas_db['ID_Trip'].astype(str).replace('nan', '').str.strip()
            
            # KOD MAGIK (FILTERING): Tarik data ikut trip semasa
            tugas_semasa = tugas_db[tugas_db['ID_Trip'] == current_trip]
            
            if not tugas_semasa.empty:
                # Loop untuk buat UI jenis "Kad" (Card view) yang nampak gempak di telefon
                for index, row in tugas_semasa.iterrows():
                    st.success(f"🗓️ **Slot:** {row['Slot_Masa']}\n\n"
                               f"🛠️ **Tugas:** {row['Tugasan']}\n\n"
                               f"👤 **Person In Charge:** {row['Ahli_Bertanggungjawab']}")
            else:
                st.info("ℹ️ Tiada tugasan direkodkan untuk aktiviti/trip ini setakat ini.")
        else:
            st.error("⚠️ Kolum 'ID_Trip' tidak wujud di dalam tab Tugasan (Google Sheets).")
    else:
        st.info("Jadual tugasan belum dikeluarkan oleh Admin.")
except Exception as e:
    st.error(f"Gagal memuatkan jadual tugasan: {e}")

if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Mod Admin: Buka Google Sheets tab 'Tugasan' untuk agihkan kerja kepada ahli. (Pastikan letak ID_Trip yang betul pada Kolum A)")
