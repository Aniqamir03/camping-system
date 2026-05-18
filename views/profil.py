import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

st.title("👤 Profil Saya")

# --- FUNGSI UPLOAD KE GOOGLE DRIVE ---

def muat_naik_ke_gdrive(fail_gambar, nama_fail):
    # Ambil kunci dari st.secrets GSheets yang sedia ada
    secret_dict = dict(st.secrets["connections"]["gsheets"])
    
    # KITA PERLUASKAN SCOPES UNTUK DRIVE DAN SPREADSHEETS DEMI KESELAMATAN AKSES
    creds = service_account.Credentials.from_service_account_info(
        secret_dict,
        scopes=[
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
    )
    service = build('drive', 'v3', credentials=creds)

    # Sediakan fail untuk di-upload
    file_buffer = io.BytesIO(fail_gambar.getvalue())
    media = MediaIoBaseUpload(file_buffer, mimetype=fail_gambar.type, resumable=True)

    # MASUKKAN FOLDER ID GOOGLE DRIVE ANDA DI SINI
    folder_id = "13vyENRsNFDgJbmcUaQxzLUp2tZS_fjM-"

    file_metadata = {
        'name': nama_fail,
        'parents': [folder_id]
    }

    # Proses Upload dan dapatkan ID fail
    fail_diupload = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webContentLink'
    ).execute()

    fail_id = fail_diupload.get('id')

    # Tukar permission supaya gambar boleh dilihat di website (Public View)
    service.permissions().create(
        fileId=fail_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return fail_diupload.get('webContentLink')
# -------------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Paksa kolum menjadi teks untuk elak error perpuluhan
for col in ['Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '')

current_user = st.session_state["username"]
user_index = users_db.index[users_db['Username'] == current_user].tolist()[0]
user_data = users_db.loc[user_index]

st.write(f"Kemaskini maklumat peribadi anda, **{user_data['Full_Name']}**.")

with st.form("update_profil_form"):
    # Paparkan gambar profil jika ada
    pic_url = user_data['Profile_Pic_URL']
    if pd.notna(pic_url) and pic_url != "":
        try:
            st.image(pic_url, width=150)
        except:
            st.warning("Pautan gambar lama tidak sah.")
    else:
        st.info("Tiada gambar profil.")

    # TUKAR KEPADA BUTANG UPLOAD FAIL DARI TELEFON/PC
    gambar_baru = st.file_uploader("📸 Muat Naik Gambar Profil Baru", type=['jpg', 'jpeg', 'png'])

    new_phone = st.text_input("No. Telefon", value=user_data['Phone_No'])
    new_emergency = st.text_input("No. Telefon Kecemasan (Waris)", value=user_data['Emergency_Contact'])
    
    update_btn = st.form_submit_button("Simpan Perubahan")
    
    if update_btn:
        # Jika ahli ada pilih gambar baru
        if gambar_baru is not None:
            with st.spinner("Sedang memuat naik gambar ke Google Drive..."):
                # Buat nama fail jadi unik (contoh: profil_amir_gambar.jpg)
                nama_fail = f"profil_{current_user}_{gambar_baru.name}"
                link_gambar_baru = muat_naik_ke_gdrive(gambar_baru, nama_fail)
                # Kemaskini link GDrive ke dalam database
                users_db.at[user_index, 'Profile_Pic_URL'] = str(link_gambar_baru)

        # Kemaskini maklumat lain
        users_db.at[user_index, 'Phone_No'] = str(new_phone)
        users_db.at[user_index, 'Emergency_Contact'] = str(new_emergency)
        
        # Hantar DataFrame yang telah dikemaskini ke Google Sheets
        conn.update(worksheet="Users", data=users_db)
        
        st.success("Profil berjaya dikemaskini!")
        st.cache_data.clear()
        st.rerun()
