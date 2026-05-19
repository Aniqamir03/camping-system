import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")

# Inisialisasi session state untuk status log masuk
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["full_name"] = ""

# Fungsi untuk baca database
@st.cache_data(ttl=60)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet="Users")

users_db = load_data()

# --- HALAMAN LOG MASUK ---
if not st.session_state["logged_in"]:
    st.title("🔐 Log Masuk Sistem Perkhemahan")
    
    with st.form("login_form"):
        input_user = st.text_input("Username")
        input_pass = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log Masuk")
        
        if submit_button:
            # Semak padanan di dalam GSheet
            user_match = users_db[(users_db['Username'] == input_user) & (users_db['Password'] == input_pass)]
            
            if not user_match.empty:
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_match.iloc[0]['Username']
                st.session_state["role"] = user_match.iloc[0]['Role']
                st.session_state["full_name"] = user_match.iloc[0]['Full_Name']
                st.rerun() # Refresh page untuk papar dashboard
            else:
                st.error("Username atau Password salah!")

# --- HALAMAN UTAMA (DASHBOARD) ---
else:
    # Sidebar untuk butang Log Keluar
    with st.sidebar:
        st.write(f"Selamat datang, **{st.session_state['full_name']}**!")
        st.write(f"Peranan: {st.session_state['role']}")
        if st.button("Log Keluar"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🏕️ Papan Pemuka Perkhemahan")

    # KAWALAN AKSES: Paparan berbeza mengikut peranan (Role)
    if st.session_state["role"] == "Admin":
        st.info("Anda mempunyai akses Admin.")
        
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Urus Ahli (Admin)", "Kewangan"])
        
        with tab1:
            st.write("Maklumat terkini perkhemahan...")
            
        with tab2:
            st.subheader("Borang Tambah Ahli Baru")
            st.write("Fungsi ini hanya dilihat oleh Admin. (Kod untuk tambah data ke GSheet akan diletakkan di sini).")
            # Nanti kita akan buat borang tambah ahli di sini menggunakan st.form
            
    else:
        # Paparan untuk Member biasa (seperti Fitri, Mok Hanafi, Paktam)
        tab1, tab2 = st.tabs(["Dashboard", "Profil Saya"])
        
        with tab1:
            st.write("Maklumat terkini perkhemahan...")
            st.write("Sila sahkan kehadiran (RSVP) anda.")
            
        with tab2:
            st.subheader("Kemaskini Profil")
            st.write("Di sini ahli boleh letak URL gambar profil baru dan kemaskini nombor telefon waris.")
