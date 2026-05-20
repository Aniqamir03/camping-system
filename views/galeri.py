import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import io
import base64
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- KOD OPTIMASI SKRIN MOBILE & PAKSAAN 3 KOLUM (FIX IPHONE 12 PM) ---
st.markdown("""
<style>
/* 1. Penuhkan skrin telefon (Kurangkan ruang kosong kiri kanan) */
.block-container {
    padding-top: 1.5rem !important;
    padding-left: 0.2rem !important;
    padding-right: 0.2rem !important;
}
h1, p { margin-left: 8px; }

/* 2. GODAM STREAMLIT SUPAYA KEKAL 3 SEBARIS DI MOBILE */
@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 3px !important; /* Jarak rapat ala Instagram */
    }
    [data-testid="column"] {
        width: 33.33% !important;
        min-width: 33.33% !important;
        flex: 1 1 33.33% !important;
        padding: 0 2px !important; /* Elak gambar bercantum teruk */
    }
}

/* 3. Kelas CSS untuk tetapkan gambar jadi petak sempurna (1:1) */
.media-box {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    margin-bottom: 5px;
}
.media-box img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# --- 1. SETUP GOOGLE DRIVE API ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=["https://www.googleapis.com/auth/drive.readonly"] 
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error("Ralat API Google Drive.")
        return None

drive_service = get_drive_service()

def get_folder_id(url_folder):
    if not url_folder or url_folder == 'nan': return None
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_folder.strip())
    if match: return match.group(1)
    return None

@st.cache_data(ttl=600)
def dapatkan_media_dari_folder(url_folder):
    folder_id = get_folder_id(url_folder)
    if not folder_id or not drive_service: return []
    
    try:
        query = f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed = false"
        results = drive_service.files().list(
            q=query, fields="files(id, thumbnailLink, mimeType)", pageSize=300 
        ).execute()
        
        items = results.get('files', [])
        senarai_media = []
        for item in items:
            if 'thumbnailLink' in item:
                hd_link = item['thumbnailLink'].replace('=s220', '=s800')
                senarai_media.append({'id': item['id'], 'link': hd_link, 'is_video': 'video/' in item.get('mimeType', '')})
        return senarai_media
    except Exception as e:
        return []

# --- 2. FUNGSI UPLOAD MENGGUNAKAN APPS SCRIPT ---
def muat_naik_ke_gdrive(fail_buffer, nama_fail, jenis_mime, folder_id):
    url_api = st.secrets.get("APPS_SCRIPT_URL")
    if not url_api: return None
    try:
        encoded_file = base64.b64encode(fail_buffer.getvalue()).decode('utf-8')
        payload = {"action": "upload", "filename": nama_fail, "mimeType": jenis_mime, "base64": encoded_file, "folderId": folder_id}
        res = requests.post(url_api, json=payload)
        if res.status_code == 200 and res.json().get('status') == 'success':
            return res.json().get('id')
        return None
    except: return None


st.title("🖼️ Galeri Media Kumpulan")
st.write("Ruang memori foto dan video. Klik pada media untuk muat turun fail kualiti asal.")

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if 'Vault_URL' not in info_db.columns: info_db['Vault_URL'] = ""
    info_db['Vault_URL'] = info_db['Vault_URL'].astype(str).replace('nan', '')
except:
    info_db = pd.DataFrame(columns=['ID_Trip', 'Vault_URL'])

val_vault = str(info_db[info_db['ID_Trip'] == current_trip].iloc[0]['Vault_URL']) if not info_db.empty and current_trip in info_db['ID_Trip'].values else ""
folder_id_semasa = get_folder_id(val_vault)

# --- 3. RUANGAN UPLOAD ---
if folder_id_semasa:
    with st.expander("📤 Klik Sini Untuk Tambah Gambar / Video"):
        st.markdown("**Format Disokong:** `PNG`, `JPG`, `JPEG`, `WEBP`, `GIF`, `HEIC`, `MP4`, `MOV`, `AVI`")
        uploaded_files = st.file_uploader("Pilih Fail Media:", type=['png', 'jpg', 'jpeg', 'webp', 'gif', 'heic', 'mp4', 'mov', 'avi', 'mkv', '3gp'], accept_multiple_files=True)
        
        if st.button("🚀 Muat Naik Sekarang", type="primary", use_container_width=True):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                jumlah_fail = len(uploaded_files)
                berjaya = 0
                
                for i, fail in enumerate(uploaded_files):
                    status_text.text(f"Memuat naik fail {i+1} dari {jumlah_fail}: {fail.name}...")
                    if muat_naik_ke_gdrive(fail, fail.name, fail.type, folder_id_semasa): berjaya += 1
                    progress_bar.progress((i + 1) / jumlah_fail)
                
                status_text.text("Selesai!")
                st.success(f"Berjaya memasukkan {berjaya} media baharu ke dalam sistem!")
                st.cache_data.clear()
                dapatkan_media_dari_folder.clear()
                st.rerun()
            else:
                st.warning("Sila pilih fail media terlebih dahulu.")
st.write("---")

# --- 4. PAPARAN GALERI & BUTANG HAPUS ---
senarai_media = dapatkan_media_dari_folder(val_vault)

# Butang Sync biasa (tanpa kolum supaya tidak diganggu oleh CSS mobile hack)
if st.button("🔄 Segerakkan Galeri (Sync)", type="secondary"):
    st.cache_data.clear()
    dapatkan_media_dari_folder.clear()
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

if len(senarai_media) > 0:
    # Membina 3 kolum utama
    cols = st.columns(3)
    
    for idx, item in enumerate(senarai_media):
        with cols[idx % 3]:
            icon_overlay = '<div style="position:absolute; top:4px; right:4px; background:rgba(0,0,0,0.7); color:white; padding:2px 4px; border-radius:3px; font-size:9px; z-index:10;">🎥 VIDEO</div>' if item['is_video'] else ''
            
            # HTML Media Box
            st.markdown(f"""
            <div class="media-box">
                <a href="https://drive.google.com/file/d/{item['id']}/view?usp=drivesdk" target="_blank">
                    <img src="{item['link']}" loading="lazy">
                </a>
                {icon_overlay}
            </div>
            """, unsafe_allow_html=True)
            
            # Butang Hapus (Teks dipendekkan supaya nampak kemas dalam 33% skrin)
            if user_role == "Admin":
                if st.button("🗑️ Padam", key=f"del_{item['id']}", use_container_width=True):
                    with st.spinner("..."):
                        try:
                            url_api = st.secrets.get("APPS_SCRIPT_URL")
                            payload_delete = {"action": "delete", "fileId": item['id']}
                            res = requests.post(url_api, json=payload_delete)
                            if res.status_code == 200 and res.json().get('status') == 'success':
                                st.cache_data.clear()
                                dapatkan_media_dari_folder.clear()
                                st.rerun()
                            else:
                                st.error("Gagal.")
                        except:
                            st.error("Gagal memadam.")
else:
    st.info("📷 Galeri masih kosong.")

# --- 5. PANEL CONFIGURATION ADMIN ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Konfigurasi Folder (Admin)")
    with st.form("form_folder_drive"):
        new_vault = st.text_input("Pautan Folder GDrive:", value=val_vault)
        if st.form_submit_button("🚀 Simpan Kunci Folder"):
            if current_trip:
                info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                if 'Vault_URL' not in info_pukal.columns: info_pukal['Vault_URL'] = ""
                info_pukal['Vault_URL'] = info_pukal['Vault_URL'].astype(str).replace('nan', '')
                if current_trip in info_pukal['ID_Trip'].values:
                    info_pukal.at[info_pukal.index[info_pukal['ID_Trip'] == current_trip][0], 'Vault_URL'] = new_vault.strip()
                else:
                    info_pukal = pd.concat([info_pukal, pd.DataFrame([{'ID_Trip': current_trip, 'Vault_URL': new_vault.strip()}])], ignore_index=True)
                
                conn.update(worksheet="Info_Kem", data=info_pukal)
                st.cache_data.clear()
                dapatkan_media_dari_folder.clear()
                st.success("Folder berjaya disetkan!")
                st.rerun()
