import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# FUNGSI CACHE: Panggil Google Sheets sekali sahaja setiap 10 minit
@st.cache_data(ttl=600)
def get_senarai_trip():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet="Senarai_Trip", ttl=600)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = ""
    st.session_state["full_name"] = ""

# Daftarkan Muka Surat
login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
tentatif_page = st.Page("views/tentatif.py", title="Tentatif & Lokasi", icon="📅")
kehadiran_page = st.Page("views/kehadiran.py", title="Pengesahan Kehadiran", icon="📝")
chat_page = st.Page("views/chat.py", title="Sembang Kumpulan", icon="💬")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")

# Kawalan Navigasi
if not st.session_state["logged_in"]:
    pg = st.navigation([login_page])
else:
    nav_list = [dashboard_page, tentatif_page, kehadiran_page, chat_page, profil_page]
    if st.session_state["role"] == "Admin":
        nav_list.append(admin_page)
    pg = st.navigation(nav_list)

# Sidebar
if st.session_state["logged_in"]:
    with st.sidebar:
        st.write("---")
        st.write(f"Log masuk sebagai: **{st.session_state['full_name']}**")
        st.write("🌍 **Pilih Aktiviti / Trip:**")
        
        try:
            senarai_trip = get_senarai_trip()
            if not senarai_trip.empty:
                pilihan_trip = st.selectbox("Sila Pilih:", senarai_trip['Nama_Trip'].tolist(), label_visibility="collapsed")
                id_terpilih = senarai_trip[senarai_trip['Nama_Trip'] == pilihan_trip]['ID_Trip'].values[0]
                st.session_state['current_trip_id'] = id_terpilih
            else:
                st.warning("Tiada trip ditemui.")
        except Exception as e:
            st.warning("⚠️ Sila pastikan tab 'Senarai_Trip' wujud.")
        
        st.write("---")
        if st.button("🚪 Log Keluar", use_container_width=True):
            st.session_state["logged_in"] = False
            st.cache_data.clear() # Kosongkan cache masa log keluar
            st.rerun()

pg.run()
