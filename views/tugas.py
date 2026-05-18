import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔥 Jadual Tugasan Ahli")
st.markdown("Kerjasama membawa berkat. Sila laksanakan tugas masing-masing demi kelancaran trip kita!")

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    tugas_db = conn.read(worksheet="Tugasan", ttl=0)

    if not tugas_db.empty:
        # Loop untuk buat UI jenis "Kad" (Card view) yang nampak gempak di telefon
        for index, row in tugas_db.iterrows():
            st.success(f"🗓️ **Slot:** {row['Slot_Masa']}\n\n"
                       f"🛠️ **Tugas:** {row['Tugasan']}\n\n"
                       f"👤 **Person In Charge:** {row['Ahli_Bertanggungjawab']}")
    else:
        st.info("Jadual tugasan belum dikeluarkan oleh Admin.")
except:
    st.error("Gagal memuatkan jadual tugasan.")

if st.session_state["role"] == "Admin":
    st.divider()
    st.warning("⚙️ Mod Admin: Buka Google Sheets tab 'Tugasan' untuk agihkan kerja kepada ahli.")
