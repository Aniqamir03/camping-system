import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.title("🔐 Log Masuk Sistem")
st.write("Sila masukkan Username dan Kata Laluan anda untuk mengakses sistem.")

# --- 1. SAMBUNGAN DENGAN PERISAI KEBAL ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    users_db = conn.read(worksheet="Users", ttl=0)
except Exception as e:
    st.error("⚠️ Ralat Pangkalan Data: Tab 'Users' tidak dijumpai di dalam Google Sheets. Sila hubungi Admin.")
    st.stop()

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
            # --- 3. PROSES PENCUCIAN DATA ---
            db_user = users_db['Username'].astype(str).str.strip().str.lower()
            db_pass = users_db['Password'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            in_user = str(input_user).strip().lower()
            in_pass = str(input_pass).strip()
            
            # --- 4. PADANAN (MATCHING) ---
            match = users_db[(db_user == in_user) & (db_pass == in_pass)]
            
            if not match.empty:
                # --- 5. FUNGSI BARU: REKOD LOG MASUK KE DATABASE ---
                user_terpilih = match.iloc[0]
                username_log = user_terpilih['Username']
                nama_log = user_terpilih['Full_Name']
                role_log = user_terpilih['Role']
                masa_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Bina baris log baru
                log_baru = pd.DataFrame([{
                    "Username": username_log,
                    "Nama_Penuh": nama_log,
                    "Peranan": role_log,
                    "Masa_Log_Masuk": masa_sekarang
                }])
                
                try:
                    # Cuba baca log sedia ada, kalau kosong bina dataframe baru
                    try:
                        log_db = conn.read(worksheet="Log_Masuk", ttl=0)
                    except:
                        log_db = pd.DataFrame(columns=["Username", "Nama_Penuh", "Peranan", "Masa_Log_Masuk"])
                    
                    # Gabungkan log lama dengan log baru
                    updated_log = pd.concat([log_db, log_baru], ignore_index=True)
                    
                    # Kemaskini ke Google Sheets
                    conn.update(worksheet="Log_Masuk", data=updated_log)
                except Exception as log_error:
                    # Jika gagal simpan log (cth: tab tak wujud), sistem tetap teruskan log masuk supaya user tak tersangkut
                    pass
                
                # --- 6. SET MEMORI SISTEM & REDIRECT ---
                st.success("✅ Log masuk berjaya! Memuatkan sistem...")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_log
                st.session_state["role"] = role_log
                st.session_state["full_name"] = nama_log
                st.rerun()
            else:
                st.error("❌ Username atau Password salah! Sila cuba lagi.")
