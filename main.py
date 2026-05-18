import streamlit as st

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# 1. Inisialisasi Session State (Memori Sistem)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

# 2. Daftarkan Muka Surat (Pages) dari folder 'views'
tentatif_page = st.Page("views/tentatif.py", title="Tentatif & Lokasi", icon="📅")
tugas_page = st.Page("views/tugas.py", title="Jadual Tugasan", icon="🔥")
login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")

# 3. Kawalan Navigasi (Routing Logic)
if not st.session_state["logged_in"]:
    # SITUASI A: Jika BELUM log masuk, hanya tunjuk page Login sahaja
    pg = st.navigation([login_page])
else:
    # SITUASI B: Jika DAH log masuk, tapis menu mengikut Role masing-masing
    if st.session_state["role"] == "Admin":
        # Menu penuh termasuk "Urus Ahli (admin_page)" untuk Admin
        pg = st.navigation([
            dashboard_page, 
            tentatif_page, 
            tugas_page, 
            inventory_page, 
            kewangan_page, 
            profil_page, 
            admin_page
        ])
    else:
        # Menu penuh TANPA "admin_page" untuk Member biasa (Fitri, Mok Hanafi, Paktam, dll)
        pg = st.navigation([
            dashboard_page, 
            tentatif_page, 
            tugas_page, 
            inventory_page, 
            kewangan_page, 
            profil_page
        ])

# 4. Jalankan Navigasi
pg.run()
