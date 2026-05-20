import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import re

# Ambil ID Trip aktif
current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)

def get_gdrive_folder_embed(url):
    if not url or url == 'nan': return None
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url.strip())
    if match:
        return f"https://drive.google.com/embeddedfolderview?id={match.group(1)}#grid"
    return None

st.title("🖼️ Galeri HD & Album Bersama")
st.write("Ruang khas untuk berkongsi dan memuat turun gambar kenangan kualiti asal (High-Res) tanpa pecah.")

# Tarik Vault_URL dari GSheets
vault_url = ""
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    if not info_db.empty and current_trip in info_db['ID_Trip'].values:
        vault_url = str(info_db[info_db['ID_Trip'] == current_trip].iloc[0].get('Vault_URL', '')).replace('nan', '').strip()
except:
    pass

embed_url = get_gdrive_folder_embed(vault_url)

if embed_url:
    # Butang interaktif untuk ahli tambah gambar sendiri
    st.link_button("➕ Muat Naik / Tambah Koleksi Gambar Anda", vault_url, use_container_width=True, type="primary")
    st.write("---")
    
    # Paparan Folder Integrated
    components.html(f"""
        <iframe src="{embed_url}" width="100%" height="600" frameborder="0" 
        style="border: 1px solid #4d4d4d; border-radius: 12px; background-color: #ffffff;"></iframe>
    """, height=620)
else:
    st.info("🔒 Galeri bagi trip ini masih dikunci atau belum disediakan oleh Admin.")
