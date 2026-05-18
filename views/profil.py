import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("👤 Profil Saya")

conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Dapatkan username yang sedang log masuk dari session state
current_user = st.session_state["username"]

# Cari indeks (baris) pengguna ini di dalam database
user_index = users_db.index[users_db['Username'] == current_user].tolist()[0]
user_data = users_db.loc[user_index]

st.write(f"Kemaskini maklumat peribadi anda, **{user_data['Full_Name']}**.")

# Borang kemaskini
with st.form("update_profil_form"):
    # Paparkan gambar profil jika ada
    if pd.notna(user_data['Profile_Pic_URL']) and user_data['Profile_Pic_URL'] != "":
        st.image(user_data['Profile_Pic_URL'], width=150)
    else:
        st.info("Tiada gambar profil.")

    # Input untuk kemaskini
    new_pic_url = st.text_input("URL Gambar Profil (contoh: link Google Drive/Imgur)", value=user_data['Profile_Pic_URL'])
    new_phone = st.text_input("No. Telefon", value=user_data['Phone_No'])
    new_emergency = st.text_input("No. Telefon Kecemasan (Waris)", value=user_data['Emergency_Contact'])
    
    update_btn = st.form_submit_button("Simpan Perubahan")
    
    if update_btn:
        # Kemaskini data di dalam DataFrame pada baris pengguna tersebut
        users_db.at[user_index, 'Profile_Pic_URL'] = new_pic_url
        users_db.at[user_index, 'Phone_No'] = new_phone
        users_db.at[user_index, 'Emergency_Contact'] = new_emergency
        
        # Hantar DataFrame yang telah dikemaskini ke Google Sheets
        conn.update(worksheet="Users", data=users_db)
        
        st.success("Profil berjaya dikemaskini!")
        st.cache_data.clear()
        st.rerun()
