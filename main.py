import streamlit as st

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# 1. Inisialisasi Session State (Memori Sistem)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = ""
    st.session_state["full_name"] = ""

# 2. Daftarkan SEMUA Muka Surat (Pages) dari folder 'views'
# (Pastikan nama fail dalam folder 'views' sama sebiji macam di bawah)
login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
tentatif_page = st.Page("views/tentatif.py", title="Tentatif & Lokasi", icon="📅")
tugas_page = st.Page("views/tugas.py", title="Jadual Tugasan", icon="🔥")
inventory_page = st.Page("views/inventory.py", title="Peralatan", icon="🎒")
kewangan_page = st.Page("views/kewangan.py", title="Kewangan", icon="💰")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")

# 3. Kawalan Navigasi (Routing Logic)
if not st.session_state["logged_in"]:
    # Jika BELUM log masuk, hanya tunjuk page Login
    pg = st.navigation([login_page])
else:
    # Jika DAH log masuk, tunjuk page mengikut Role masing-masing
    if st.session_state["role"] == "Admin":
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
