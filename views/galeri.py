import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Ambil ID Trip aktif & Role
current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. SETUP GOOGLE DRIVE API (Guna Kredensial GSheets Sedia Ada) ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error("Ralat API Google Drive. Pastikan emel Service Account dimasukkan.")
        return None

drive_service = get_drive_service()

# --- 2. FUNGSI SEDUT GAMBAR & TUKAR JADI GRID ---
@st.cache_data(ttl=300) # Cache 5 minit supaya tak spam API Google
def dapatkan_gambar_dari_folder(url_folder):
    if not url_folder or url_folder == 'nan' or not drive_service: return []
    
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_folder.strip())
    if not match: return []
    folder_id = match.group(1)
    
    try:
        # Carian automatik semua gambar dalam folder
        query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        # Tarik thumbnailLink CDN Google untuk kelajuan maksima
        results = drive_service.files().list(
            q=query, 
            fields="files(id, thumbnailLink)", 
            pageSize=300 # Tarik maksimum 300 gambar sekaligus
        ).execute()
        
        items = results.get('files', [])
        pautan_pantas = []
        
        for item in items:
            if 'thumbnailLink' in item:
                # Tukar saiz paparan dari s220 kepada s800 (Resolusi Tinggi tapi pantas)
                hd_link = item['thumbnailLink'].replace('=s220', '=s800')
                pautan_pantas.append(hd_link)
        return pautan_pantas
    except Exception as e:
        return []

st.title("🖼️ Galeri Automatik")
st.write("Disegerakkan secara terus dari awan. Kualiti HD tanpa had storan luar.")

# --- 3. TARIK DATA FOLDER DARI GSHEETS ---
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

# --- 4. PAPARAN GRID INSTAGRAM YANG CANTIK ---
senarai_gambar = dapatkan_gambar_dari_folder(val_vault)

if val_vault:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.link_button("📤 Muat Naik Ke GDrive", val_vault, use_container_width=True)
    with col2:
        if st.button("🔄 Segerakkan (Sync) Galeri", use_container_width=True):
            dapatkan_gambar_dari_folder.clear()
            st.rerun()

st.write("---")

if len(senarai_gambar) > 0:
    imej_html = "".join([f'<img src="{link}" loading="lazy" alt="Memori">' for link in senarai_gambar])
    
    grid_css = f"""
    <style>
        .insta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3px;
            width: 100%;
        }}
        .insta-grid img {{
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 4px;
        }}
        @media (max-width: 430px) {{
            .block-container {{
                padding-top: 1rem !important;
                padding-left: 0.2rem !important;
                padding-right: 0.2rem !important;
            }}
            h1, p {{ margin-left: 10px; }}
        }}
    </style>
    <div class="insta-grid">{imej_html}</div>
    """
    st.markdown(grid_css, unsafe_allow_html=True)
else:
    st.info("📷 Belum ada gambar, atau Admin belum meletakkan pautan folder Google Drive yang sah.")


# --- 5. PANEL PENGURUSAN ADMIN ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Konfigurasi Folder (Admin)")
    
    with st.form("form_folder_drive"):
        st.write("Tampal pautan (Anyone with link) folder Google Drive untuk trip ini.")
        st.warning("Wajib kongsi folder GDrive tersebut kepada alamat emel Service Account (Viewer).")
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
                dapatkan_gambar_dari_folder.clear()
                st.rerun()
