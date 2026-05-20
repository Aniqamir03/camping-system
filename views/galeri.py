import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Ambil ID Trip aktif & Role
current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. SETUP GOOGLE DRIVE API (Scope Penuh) ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        # Scope ditukar untuk membenarkan sistem membaca & memuat naik (write) fail
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive"]
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

# --- 3. FUNGSI SEDUT GAMBAR DARI GDRIVE ---
@st.cache_data(ttl=300)
def dapatkan_gambar_dari_folder(url_folder):
    folder_id = get_folder_id(url_folder)
    if not folder_id or not drive_service: return []
    
    try:
        query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        results = drive_service.files().list(
            q=query, 
            fields="files(id, thumbnailLink)", 
            pageSize=300 
        ).execute()
        
        items = results.get('files', [])
        return [item['thumbnailLink'].replace('=s220', '=s800') for item in items if 'thumbnailLink' in item]
    except Exception as e:
        return []

# --- 4. FUNGSI UPLOAD KE GDRIVE (DIRECT DARI WEBSITE) ---
def muat_naik_ke_gdrive(fail_buffer, nama_fail, jenis_mime, folder_id):
    try:
        # Tukar fail kepada bentuk bait (bytes) yang Google faham
        fh = io.BytesIO(fail_buffer.getvalue())
        media = MediaIoBaseUpload(fh, mimetype=jenis_mime, resumable=True)
        metadata = {
            'name': nama_fail,
            'parents': [folder_id] # Masukkan terus ke dalam folder trip
        }
        # Arahkan API untuk hantar fail
        fail_baru = drive_service.files().create(body=metadata, media_body=media, fields='id').execute()
        return fail_baru.get('id')
    except Exception as e:
        st.error(f"Ralat muat naik {nama_fail}: {e}")
        return None


st.title("🖼️ Galeri Automatik")
st.write("Disegerakkan secara terus dari awan. Kualiti HD tanpa had storan luar.")

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


# --- 6. RUANGAN MUAT NAIK GAMBAR (UNTUK SEMUA USER) ---
if folder_id_semasa:
    with st.expander("📤 Klik Sini Untuk Tambah Gambar Ke Galeri"):
        st.write("Pilih gambar dari telefon/PC anda. (Dinasihatkan max 10-15 gambar setiap kali muat naik supaya website tak *hang*).")
        uploaded_files = st.file_uploader("Pilih Fail:", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        if st.button("🚀 Muat Naik Sekarang", type="primary", use_container_width=True):
            if uploaded_files:
                # Paparkan progress bar supaya user tak bosan tunggu
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                jumlah_fail = len(uploaded_files)
                berjaya = 0
                
                for i, fail in enumerate(uploaded_files):
                    status_text.text(f"Memuat naik fail {i+1} dari {jumlah_fail}...")
                    id_baru = muat_naik_ke_gdrive(fail, fail.name, fail.type, folder_id_semasa)
                    if id_baru:
                        berjaya += 1
                    
                    # Update progress bar
                    progress_bar.progress((i + 1) / jumlah_fail)
                
                status_text.text("Selesai!")
                st.success(f"Berjaya memuat naik {berjaya} keping gambar!")
                
                # Cuci cache supaya gambar baru terus keluar di bawah
                dapatkan_gambar_dari_folder.clear()
                st.rerun()
            else:
                st.warning("Sila pilih gambar terlebih dahulu.")
st.write("---")


# --- 7. PAPARAN GRID INSTAGRAM YANG CANTIK ---
senarai_gambar = dapatkan_gambar_dari_folder(val_vault)

if st.button("🔄 Segerakkan (Sync) Galeri", use_container_width=True):
    dapatkan_gambar_dari_folder.clear()
    st.rerun()

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


# --- 8. PANEL PENGURUSAN ADMIN ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Konfigurasi Folder (Admin)")
    
    with st.form("form_folder_drive"):
        st.write("Tampal pautan folder Google Drive untuk trip ini.")
        st.warning("Wajib kongsi folder GDrive tersebut kepada alamat emel Service Account sebagai **EDITOR** supaya user boleh upload.")
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
                st.success("Folder berjaya disetkan!")
                st.rerun()
