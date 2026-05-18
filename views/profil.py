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
    
    # Skop akses penuh untuk manipulasi fail yang dicipta
    creds = service_account.Credentials.from_service_account_info(
        secret_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    # Sediakan fail buffer
    file_buffer = io.BytesIO(fail_gambar.getvalue())
    
    # Ditukar resumable=False untuk fail kecil (gambar) bagi mengelakkan HttpError/ResumableUploadError
    media = MediaIoBaseUpload(file_buffer, mimetype=fail_gambar.type, resumable=False)

    folder_id = "13vyENRsNFDgJbmcUaQxzLUp2tZS_fjM-"

    file_metadata = {
        'name': nama_fail,
        'parents': [folder_id]
    }

    # PEMBETULAN UTAMA: Menghantar metadata bersama media_body dengan betul
    fail_diupload = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    fail_id = fail_diupload.get('id')

    # Tukar permission folder/fail supaya boleh diakses sebagai 'reader' oleh sesiapa sahaja (Public Link)
    service.permissions().create(
        fileId=fail_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    # Trik menukar link menjadi Direct Download Link supaya st.image boleh baca dan paparkan gambar terus
    direct_link = f"https://drive.google.com/uc?export=view&id={fail_id}"
    return direct_link
# -------------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Paksa kolum menjadi teks untuk elak error perpuluhan
for col in ['Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

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
            st.warning("Gambar profil tidak dapat dipaparkan atau pautan tamat tempoh.")
    else:
        st.info("Tiada gambar profil.")

    # Butang muat naik fail
    gambar_baru = st.file_uploader("📸 Muat Naik Gambar Profil Baru", type=['jpg', 'jpeg', 'png'])

    new_phone = st.text_input("No. Telefon", value=user_data['Phone_No'])
    new_emergency = st.text_input("No. Telefon Kecemasan (Waris)", value=user_data['Emergency_Contact'])
    
    update_btn = st.form_submit_button("Simpan Perubahan")
    
    if update_btn:
        if gambar_baru is not None:
            with st.spinner("Sedang memuat naik gambar ke Google Drive..."):
                nama_fail = f"profil_{current_user}_{gambar_baru.name}"
                try:
                    link_gambar_baru = muat_naik_ke_gdrive(gambar_baru, nama_fail)
                    users_db.at[user_index, 'Profile_Pic_URL'] = str(link_gambar_baru)
                except Exception as e:
                    st.error(f"Gagal memuat naik gambar: {e}")
                    st.stop()

        # Kemaskini maklumat lain
        users_db.at[user_index, 'Phone_No'] = str(new_phone).strip()
        users_db.at[user_index, 'Emergency_Contact'] = str(new_emergency).strip()
        
        # Hantar DataFrame yang telah dikemaskini ke Google Sheets
        conn.update(worksheet="Users", data=users_db)
        
        st.success("Profil berjaya dikemaskini!")
        st.cache_data.clear()
        st.rerun()
