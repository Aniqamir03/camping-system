import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# 1. Inisialisasi Session State (Memori Sistem)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = ""
    st.session_state["full_name"] = ""

# 2. Daftarkan Muka Surat (Pages) - FOKUS KEPADA 4 TAB UTAMA SAHAJA
login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
tentatif_page = st.Page("views/tentatif.py", title="Tentatif & Lokasi", icon="📅")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")

# 3. Kawalan Navigasi (Routing Logic)
if not st.session_state["logged_in"]:
    # Jika BELUM log masuk
    pg = st.navigation([login_page])
else:
    # Jika DAH log masuk
    if st.session_state["role"] == "Admin":
        pg = st.navigation([
            dashboard_page, 
            tentatif_page, 
            profil_page, 
            admin_page
        ])
    else:
        pg = st.navigation([
            dashboard_page, 
            tentatif_page, 
            profil_page
        ])

# 3.5 KAWALAN SIDEBAR (PILIHAN TRIP & BUTANG LOG OUT)
if st.session_state["logged_in"]:
    with st.sidebar:
        st.write("---")
        st.write(f"Log masuk sebagai: **{st.session_state['full_name']}**")
        st.write("🌍 **Pilih Aktiviti / Trip:**")
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
            
            pilihan_trip = st.selectbox("Sila Pilih:", senarai_trip['Nama_Trip'].tolist(), label_visibility="collapsed")
            id_terpilih = senarai_trip[senarai_trip['Nama_Trip'] == pilihan_trip]['ID_Trip'].values[0]
            st.session_state['current_trip_id'] = id_terpilih
            
        except Exception as e:
            st.warning("⚠️ Sila pastikan tab 'Senarai_Trip' wujud di Google Sheets.")
        
        st.write("---")
        if st.button("🚪 Log Keluar", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state["username"] = ""
            st.session_state["full_name"] = ""
            st.cache_data.clear()
            st.rerun()

# 4. Jalankan Navigasi
pg.run()
