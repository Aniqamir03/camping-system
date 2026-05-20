import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import io
import base64
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Ambil ID Trip aktif & Role
current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. SETUP GOOGLE DRIVE API (UNTUK BACA GAMBAR SAHAJA) ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive.readonly"] # Kekal readonly demi keselamatan
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error("Ralat API Google Drive. Pastikan emel Service Account dimasukkan.")
        return None

drive_service = get_drive_service()

# --- 2. FUNGSI EKSTRAK FOLDER ID ---
def get_folder_id(url_folder):
    if not url_folder or url_folder == 'nan': return None
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_folder.strip())
    if match: return match.group(1)
    return None

# --- 3. FUNGSI SEDUT MEDIA DARI GDRIVE (GAMBAR & VIDEO) ---
@st.cache_data(ttl=300)
def dapatkan_media_dari_folder(url_folder):
    folder_id = get_folder_id(url_folder)
    if not folder_id or not drive_service: return []
    
    try:
        # Carian merangkumi imej dan video
        query = f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed = false"
        results = drive_service.files().list(
            q=query, 
            fields="files(id, thumbnailLink, mimeType)", 
            pageSize=300 
        ).execute()
        
        items = results.get('files', [])
        senarai_media = []
        for item in items:
            if 'thumbnailLink' in item:
                senarai_media.append({
                    'id': item['id'],
                    'link': item['thumbnailLink'].replace('=s220', '=s800'),
                    'is_video': 'video/' in item.get('mimeType', ''),
                    'view_link': f"https://drive.google.com/file/d/{item['id']}/view?usp=drivesdk"
                })
        return senarai_media
    except Exception as e:
        return []

# --- 4. FUNGSI UPLOAD & DELETE MENGGUNAKAN APPS SCRIPT ---
def muat_naik_ke_gdrive(fail_buffer, nama_fail, jenis_mime, folder_id):
    url_api = st.secrets.get("APPS_SCRIPT_URL")
    if not url_api: return None
    try:
        encoded_img = base64.b64encode(fail_buffer.getvalue()).decode('utf-8')
        payload = {
            "action": "upload", # Penting untuk Apps Script faham ini adalah upload
            "filename": nama_fail,
            "mimeType": jenis_mime,
            "base64": encoded_img,
            "folderId": folder_id
        }
        res = requests.post(url_api, json=payload)
        if res.status_code == 200 and res.json().get('status') == 'success':
            return res.json().get('id')
        return None
    except Exception as e:
        return None

def padam_media_gdrive(file_id):
    url_api = st.secrets.get("APPS_SCRIPT_URL")
    if not url_api: return False
    try:
        payload = {"action": "delete", "fileId": file_id}
        res = requests.post(url_api, json=payload)
        return res.status_code == 200 and res.json().get('status') == 'success'
    except:
        return False


st.title("🖼️ Galeri Automatik")
st.write("Ruang memori foto dan video. Klik pada media untuk paparan HD / muat turun.")

# --- 5. TARIK DATA FOLDER DARI GSHEETS ---
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if 'Vault_URL' not in info_db.columns: info_db['Vault_URL'] = ""
    info_db['Vault_URL'] = info_db['Vault_URL'].astype(str).replace('nan', '')
except:
    info_db = pd.DataFrame(columns=['ID_Trip', 'Vault_URL'])

if not info_db.empty and current_trip in info_db['ID_Trip'].values:
    val_vault = str(info_db[info_db['ID_Trip'] == current_trip].iloc[0]['Vault_URL'])
else:
    val_vault = ""

folder_id_semasa = get_folder_id(val_vault)


# --- 6. RUANGAN MUAT NAIK PREMIUM (GAMBAR & VIDEO) ---
if folder_id_semasa:
    with st.expander("📤 Klik Sini Untuk Tambah Gambar / Video Ke Galeri"):
        st.markdown("**Sokongan Fail:** `PNG`, `JPG`, `JPEG`, `WEBP`, `GIF`, `HEIC`, `MP4`, `MOV`, `AVI`")
        uploaded_files = st.file_uploader("Pilih Fail Media (Max 15 fail dinasihatkan):", type=['png', 'jpg', 'jpeg', 'webp', 'gif', 'heic', 'mp4', 'mov', 'avi', 'mkv', '3gp'], accept_multiple_files=True)
        
        if st.button("🚀 Muat Naik Sekarang", type="primary", use_container_width=True):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                jumlah_fail = len(uploaded_files)
                berjaya = 0
                
                for i, fail in enumerate(uploaded_files):
                    status_text.text(f"Memuat naik fail {i+1} dari {jumlah_fail}...")
                    if muat_naik_ke_gdrive(fail, fail.name, fail.type, folder_id_semasa):
                        berjaya += 1
                    progress_bar.progress((i + 1) / jumlah_fail)
                
                status_text.text("Selesai!")
                st.success(f"Berjaya memuat naik {berjaya} fail media!")
                
                dapatkan_media_dari_folder.clear()
                st.rerun()
            else:
                st.warning("Sila pilih fail terlebih dahulu.")
st.write("---")


# --- 7. PAPARAN GRID CSS ASAL YANG SEMPURNA ---
senarai_media = dapatkan_media_dari_folder(val_vault)

if st.button("🔄 Segerakkan (Sync) Galeri", use_container_width=True):
    dapatkan_media_dari_folder.clear()
    st.rerun()

if len(senarai_media) > 0:
    # Membina struktur HTML yang bersih
    html_content = ""
    for item in senarai_media:
        badge_video = '<div class="video-badge">🎥</div>' if item['is_video'] else ''
        html_content += f"""
        <div class="media-item">
            <a href="{item['view_link']}" target="_blank">
                <img src="{item['link']}" loading="lazy" alt="Memori">
            </a>
            {badge_video}
        </div>
        """
    
    # CSS Kesayangan Anda (Ditambah Kunci Skrol)
    grid_css = f"""
    <style>
        /* KUNCI MATI SCROLL KE TEPI UNTUK KESELURUHAN APP */
        html, body, [data-testid="stAppViewContainer"], .block-container {{
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }}

        .insta-grid {{
            display: grid;
            /* FUNGSI AJAIB: minmax(0, 1fr) memaksa gambar mengecil fit skrin! */
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 3px;
            width: 100%;
            box-sizing: border-box;
        }}
        .media-item {{
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;
            overflow: hidden;
            border-radius: 4px;
        }}
        .media-item img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .video-badge {{
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            z-index: 10;
            pointer-events: none;
        }}
        @media (max-width: 430px) {{
            .block-container {{
                padding-top: 1rem !important;
                padding-left: 0.1rem !important;
                padding-right: 0.1rem !important;
            }}
            h1, p {{ margin-left: 10px; }}
        }}
    </style>
    <div class="insta-grid">{html_content}</div>
    """
    st.markdown(grid_css, unsafe_allow_html=True)
else:
    st.info("📷 Belum ada gambar, atau Admin belum meletakkan pautan folder Google Drive yang sah.")


# --- 8. PANEL PENGURUSAN ADMIN ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Pengurusan (Admin Sahaja)")
    
    # Bahagian 1: Padam Gambar Pelik/Video
    if len(senarai_media) > 0:
        with st.expander("🗑️ Buang Gambar / Video Dari Awan"):
            st.write("Pilih fail yang ingin dipadamkan secara kekal dari pangkalan data.")
            for item in senarai_media:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(item['link'], width=60)
                with col2:
                    if st.button("Padam Media Ini", key=f"del_{item['id']}", type="secondary"):
                        with st.spinner("Sedang memadam..."):
                            if padam_media_gdrive(item['id']):
                                st.success("Terpadam!")
                                dapatkan_media_dari_folder.clear()
                                st.rerun()
                            else:
                                st.error("Gagal dipadam.")
            st.write("---")

    # Bahagian 2: Konfigurasi GDrive
    with st.form("form_folder_drive"):
        st.write("Tampal pautan folder Google Drive untuk trip ini.")
        st.warning("Wajib kongsi folder GDrive tersebut kepada alamat emel Service Account sebagai **VIEWER**.")
        new_vault = st.text_input("Pautan Folder GDrive:", value=val_vault)
        
        if st.form_submit_button("🚀 Simpan Kunci Folder"):
            if current_trip:
                info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                if 'Vault_URL' not in info_pukal.columns: info_pukal['Vault_URL'] = ""
                info_pukal['Vault_URL'] = info_pukal['Vault_URL'].astype(str).replace('nan', '')
                
                if current_trip in info_pukal['ID_Trip'].values:
                    idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                    info_pukal.at[idx, 'Vault_URL'] = new_vault.strip()
                else:
                    new_row = pd.DataFrame([{'ID_Trip': current_trip, 'Vault_URL': new_vault.strip()}])
                    info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)
                
                conn.update(worksheet="Info_Kem", data=info_pukal)
                st.cache_data.clear()
                dapatkan_media_dari_folder.clear()
                st.success("Folder berjaya disetkan!")
                st.rerun()
