import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit.components.v1 as components
import re

# Ambil ID Trip aktif & Role pengguna semasa
current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI TUKAR LINK FOLDER GDRIVE KEPADA INTEGRATED GRID ---
def get_gdrive_folder_embed(url):
    if not url or url == 'nan': 
        return None
    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url.strip())
    if match:
        return f"https://drive.google.com/embeddedfolderview?id={match.group(1)}#grid"
    return None

st.title("🖼️ Galeri HD & Album Bersama")
st.write("Ruang khas untuk berkongsi dan memuat turun gambar kenangan kualiti asal (High-Res) tanpa pecah.")

# --- KOD OPTIMASI UI MOBILE (IPHONE 12 PRO MAX) ---
st.markdown("""
<style>
/* Sasaran spesifik untuk skrin telefon pintar (iPhone 12 Pro Max max-width: 430px) */
@media (max-width: 430px) {
    /* 1. Buang ruang kosong (padding) kiri kanan supaya galeri guna 100% skrin */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* 2. Besarkan ketinggian Iframe supaya pengguna tak perlu double-scroll */
    iframe {
        height: 750px !important;
        border-radius: 8px !important;
    }
    
    /* 3. Kecilkan saiz tajuk supaya tak makan ruang di mobile */
    h1 {
        font-size: 1.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 1. TARIK DATA DARI GSHEETS ---
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    # Pastikan kolum Vault_URL selamat (tak perlu usik kolum Kenangan lain)
    if 'Vault_URL' not in info_db.columns:
        info_db['Vault_URL'] = ""
    info_db['Vault_URL'] = info_db['Vault_URL'].astype(str).replace('nan', '')
except:
    info_db = pd.DataFrame(columns=['ID_Trip', 'Vault_URL'])

# Ambil data spesifik mengikut trip semasa
if not info_db.empty and current_trip in info_db['ID_Trip'].values:
    info_semasa = info_db[info_db['ID_Trip'] == current_trip]
    val_vault = str(info_semasa.iloc[0]['Vault_URL'])
else:
    val_vault = ""

embed_url = get_gdrive_folder_embed(val_vault)


# --- 2. PAPARAN UTAMA GALERI (DILIHAT OLEH SEMUA AHLI) ---
if embed_url:
    # Butang muat naik gambar bersama
    st.link_button("➕ Muat Naik / Tambah Koleksi Gambar Anda", val_vault, use_container_width=True, type="primary")
    st.write("---")
    
    # Bingkai Grid Folder Google Drive
    components.html(f"""
        <iframe src="{embed_url}" width="100%" height="600" frameborder="0" 
        style="border: 1px solid #4d4d4d; border-radius: 12px; background-color: #ffffff;"></iframe>
    """, height=620)
else:
    st.info("🔒 Bilik kebal gambar masih dikunci. Admin belum menetapkan pautan folder bagi trip ini.")


# --- 3. PANEL PENGURUSAN GALERI (HANYA MUNCUL JIKA USER = ADMIN) ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Pengurusan Galeri (Admin Sahaja)")
    
    with st.form("form_galeri_internal_admin"):
        st.markdown("### 🔑 Akses Bilik Kebal (Google Drive)")
        st.write("Masukkan pautan folder Google Drive yang telah ditetapkan **'Anyone with link (Editor)'**.")
        new_vault = st.text_input("Pautan Folder Google Drive Semasa:", value=val_vault)
        
        submit_internal = st.form_submit_button("🚀 Simpan Pautan Galeri")
        
        if submit_internal:
            if not current_trip:
                st.error("Ralat: Sila pilih trip aktif di sidebar terlebih dahulu!")
            else:
                try:
                    # Baca semula database paling segar (ttl=0)
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                    
                    if 'Vault_URL' not in info_pukal.columns: 
                        info_pukal['Vault_URL'] = ""
                    info_pukal['Vault_URL'] = info_pukal['Vault_URL'].astype(str).replace('nan', '')
                    
                    # Semak sama ada data trip sudah wujud
                    if current_trip in info_pukal['ID_Trip'].values:
                        idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                        info_pukal.at[idx, 'Vault_URL'] = new_vault.strip()
                    else:
                        # Bina data row baru jika trip tak wujud lagi
                        new_row = pd.DataFrame([{'ID_Trip': current_trip, 'Vault_URL': new_vault.strip()}])
                        info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)
                    
                    # Tolak kemaskini ke Google Sheets
                    conn.update(worksheet="Info_Kem", data=info_pukal)
                    st.success("Pautan Bilik Kebal berjaya disimpan!")
                    
                    # MAGIC REFRESH
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Gagal mengemaskini pangkalan data: {e}")
