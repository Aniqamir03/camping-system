import streamlit as st

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# 1. Inisialisasi Session State (Memori Sistem)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

# 2. Daftarkan Muka Surat (Pages) dari folder 'views'
login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")

# 3. Kawalan Navigasi (Routing Logic)
if not st.session_state["logged_in"]:
    # Jika belum log masuk, hanya tunjuk page Login
    pg = st.navigation([login_page])
else:
    # Jika dah log masuk, tunjuk page mengikut Role
    if st.session_state["role"] == "Admin":
        pg = st.navigation([dashboard_page, profil_page, admin_page])
    else:
        # Ahli biasa tidak akan nampak page admin_page
        pg = st.navigation([dashboard_page, profil_page])

# 4. Jalankan Navigasi
pg.run()