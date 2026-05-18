import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("⚙️ Panel Pentadbir (Admin)")
st.subheader("Ruang untuk mendaftar ahli baharu ke dalam GSheet.")

# Sambung ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Bersihkan data daripada sebarang nan atau space tersembunyi
for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

# --- 1. PAPAR SENARAI AHLI SEDIA ADA ---
st.write("---")
st.write("### 👥 Senarai Ahli Kumpulan")
if not users_db.empty:
    # Papar kolum penting sahaja supaya senarai nampak kemas
    st.dataframe(users_db[['User_ID', 'Username', 'Full_Name', 'Role']], use_container_width=True)
else:
    st.info("Tiada ahli lain berdaftar lagi.")

# --- 2. BORANG DAFTAR AHLI BAHARU ---
st.write("---")
st.write("### ➕ Daftar Ahli Baharu")

with st.form("daftar_ahli_form", clear_on_submit=True):
    username_input = st.text_input("Username (Guna huruf kecil & tiada space, cth: fitri)")
    password_input = st.text_input("Password Sementara", value="123456")
    fullname_input = st.text_input("Nama Penuh")
    role_input = st.selectbox("Peranan (Role)", ["User", "Admin"])
    
    submit_btn = st.form_submit_button("Daftar Ahli")
    
    if submit_btn:
        username_clean = username_input.strip().lower()
        password_clean = password_input.strip()
        fullname_clean = fullname_input.strip()
        
        # Validasi input kosong
        if not username_clean or not password_clean or not fullname_clean:
            st.error("Semua ruangan wajib diisi!")
        # Validasi kalau username sudah ada dalam GSheet
        elif username_clean in users_db['Username'].values:
            st.error(f"Username '{username_clean}' sudah wujud! Sila guna nama lain.")
        else:
            with st.spinner("Sedang mendaftarkan ahli..."):
                # Sistem auto-generate ID baru (Contoh: USR002)
                if not users_db.empty and 'User_ID' in users_db.columns and len(users_db['User_ID']) > 0:
                    try:
                        last_id = users_db['User_ID'].iloc[-1]
                        last_num = int(last_id.replace("USR", ""))
                        new_id = f"USR{str(last_num + 1).zfill(3)}"
                    except:
                        new_id = f"USR{str(len(users_db) + 1).zfill(3)}"
                else:
                    new_id = "USR001"
                
                # Sediakan data baris baru
                new_user = {
                    'User_ID': new_id,
                    'Username': username_clean,
                    'Password': password_clean,
                    'Full_Name': fullname_clean,
                    'Role': role_input,
                    'Profile_Pic_URL': '',
                    'Phone_No': '',
                    'Emergency_Contact': ''
                }
                
                # Gabung data baru ke dalam database asal
                new_df = pd.DataFrame([new_user])
                users_db = pd.concat([users_db, new_df], ignore_index=True)
                
                # Tolak masuk ke Google Sheets
                conn.update(worksheet="Users", data=users_db)
                
                st.success(f"Akun untuk **{fullname_clean}** ({role_input}) berjaya didaftarkan!")
                st.cache_data.clear()
                st.rerun()
