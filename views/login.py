import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🔐 Log Masuk Sistem")
st.write("Sila masukkan Username dan Kata Laluan anda untuk mengakses sistem.")

# --- 1. SAMBUNGAN DENGAN PERISAI KEBAL ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    users_db = conn.read(worksheet="Users", ttl=0)
except Exception as e:
    st.error("⚠️ Ralat Pangkalan Data: Tab 'Users' tidak dijumpai di dalam Google Sheets. Sila hubungi Admin.")
    st.stop() # Hentikan kod dari membaca ke bawah jika database rosak

# --- 2. BORANG LOG MASUK ---
with st.form("login_form"):
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log Masuk")
    
    if submit:
        # Semak jika pengguna tertinggal tempat kosong
        if not input_user or not input_pass:
            st.warning("⚠️ Sila isi Username dan Password terlebih dahulu!")
        else:
            # --- 3. PROSES PENCUCIAN DATA (DATA CLEANSING) ---
            # Cuci column GSheet (buang ".0", buang space, paksa huruf kecil untuk username)
            db_user = users_db['Username'].astype(str).str.strip().str.lower()
            db_pass = users_db['Password'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Cuci input pengguna (paksa huruf kecil untuk elak masalah auto-capitalize phone)
            in_user = str(input_user).strip().lower()
            in_pass = str(input_pass).strip()
            
            # --- 4. PADANAN (MATCHING) ---
            match = users_db[(db_user == in_user) & (db_pass == in_pass)]
            
            if not match.empty:
                st.success("✅ Log masuk berjaya! Memuatkan sistem...")
                st.session_state["logged_in"] = True
                st.session_state["username"] = match.iloc[0]['Username']
                st.session_state["role"] = match.iloc[0]['Role']
                st.session_state["full_name"] = match.iloc[0]['Full_Name']
                st.rerun()
            else:
                st.error("❌ Username atau Password salah! Sila cuba lagi.")
