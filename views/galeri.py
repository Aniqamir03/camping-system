import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import requests
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CSS GRID TULEN (TANPA ST.COLUMNS) ---
st.markdown("""
<style>
    .gallery-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2px;
        width: 100%;
    }
    .media-item {
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 1;
    }
    .media-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .video-badge {
        position: absolute; top: 5px; right: 5px;
        background: rgba(0,0,0,0.6); color: white;
        padding: 2px 4px; border-radius: 3px; font-size: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI DRIVE ---
@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive.readonly"])
        return build('drive', 'v3', credentials=creds)
    except: return None

drive_service = get_drive_service()

def get_folder_id(url):
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

@st.cache_data(ttl=600)
def get_media(url):
    fid = get_folder_id(url)
    if not fid or not drive_service: return []
    query = f"'{fid}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed = false"
    res = drive_service.files().list(q=query, fields="files(id, thumbnailLink, mimeType)", pageSize=300).execute()
    return [{'id': f['id'], 'link': f['thumbnailLink'].replace('=s220', '=s800'), 'is_vid': 'video/' in f.get('mimeType', '')} for f in res.get('files', [])]

# --- UI & LOGIK ---
st.title("🖼️ Galeri Media")

# Ambil URL folder
info_db = conn.read(worksheet="Info_Kem", ttl=600)
val_vault = str(info_db.loc[info_db['ID_Trip'] == current_trip, 'Vault_URL'].values[0]) if current_trip in info_db['ID_Trip'].values else ""
folder_id = get_folder_id(val_vault)

# Upload Area
if folder_id:
    with st.expander("📤 Muat Naik Media"):
        files = st.file_uploader("Pilih Fail:", accept_multiple_files=True)
        if st.button("🚀 Upload"):
            for f in files:
                url_api = st.secrets.get("APPS_SCRIPT_URL")
                encoded = base64.b64encode(f.getvalue()).decode('utf-8')
                requests.post(url_api, json={"action":"upload", "filename":f.name, "mimeType":f.type, "base64":encoded, "folderId":folder_id})
            st.rerun()

# --- PAPARAN GALERI (HTML TULEN) ---
media = get_media(val_vault)
if media:
    html_grid = '<div class="gallery-container">'
    for m in media:
        badge = '<div class="video-badge">🎥</div>' if m['is_vid'] else ''
        html_grid += f'<div class="media-item"><a href="https://drive.google.com/file/d/{m["id"]}/view" target="_blank"><img src="{m["link"]}" loading="lazy"></a>{badge}</div>'
    html_grid += '</div>'
    st.markdown(html_grid, unsafe_allow_html=True)
else:
    st.info("Tiada media.")

# --- ADMIN DELETE ---
if user_role == "Admin":
    with st.expander("🗑️ Pengurusan Padam"):
        for m in media:
            c1, c2 = st.columns([1, 4])
            c1.image(m['link'], width=60)
            if c2.button("Padam", key=m['id']):
                requests.post(st.secrets["APPS_SCRIPT_URL"], json={"action":"delete", "fileId":m['id']})
                st.rerun()
