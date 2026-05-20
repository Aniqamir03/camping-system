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

# --- 1. TARIK DATA DARI GSHEETS ---
try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)
    # Pastikan semua kolum selamat & dalam format teks (Kalis ralat float64)
    kolum_wajib = ['Vault_URL', 'Kenangan_1', 'Kenangan_2', 'Kenangan_3', 'Kenangan_4', 'Kenangan_5']
    for col in kolum_wajib:
        if col not in info_db.columns:
            info_db[col] = ""
        info_db[col] = info_db[col].astype(str).replace('nan', '')
except:
    info_db = pd.DataFrame(columns=['ID_Trip', 'Vault_URL', 'Kenangan_1', 'Kenangan_2', 'Kenangan_3', 'Kenangan_4', 'Kenangan_5'])

# Ambil data spesifik mengikut trip semasa
info_semasa = info_db[info_db['ID_Trip'] == current_trip]
val_vault = str(info_semasa.iloc[0]['Vault_URL']) if not info_semasa.empty else ""
val_k1 = str(info_semasa.iloc[0]['Kenangan_1']) if not info_semasa.empty else ""
val_k2 = str(info_semasa.iloc[0]['Kenangan_2']) if not info_semasa.empty else ""
val_k3 = str(info_semasa.iloc[0]['Kenangan_3']) if not info_semasa.empty else ""
val_k4 = str(info_semasa.iloc[0]['Kenangan_4']) if not info_semasa.empty else ""
val_k5 = str(info_semasa.iloc[0]['Kenangan_5']) if not info_semasa.empty else ""

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


# --- 3. PANEL PENGURUSAN MEDIA (HANYA MUNCUL JIKA USER = ADMIN) ---
if user_role == "Admin":
    st.write("---")
    st.subheader("⚙️ Panel Pengurusan Galeri (Admin Sahaja)")
    
    with st.form("form_galeri_internal_admin"):
        st.markdown("### 🔑 Akses Bilik Kebal (Google Drive)")
        new_vault = st.text_input("Pautan Folder Google Drive Semasa:", value=val_vault)
        
        st.markdown("### 🖼️ Gambar Sorotan Slaid Dashboard (Postimages)")
        new_k1 = st.text_input("Gambar Slaid 1 (Direct Link):", value=val_k1)
        new_k2 = st.text_input("Gambar Slaid 2 (Direct Link):", value=val_k2)
        new_k3 = st.text_input("Gambar Slaid 3 (Direct Link):", value=val_k3)
        new_k4 = st.text_input("Gambar Slaid 4 (Direct Link):", value=val_k4)
        new_k5 = st.text_input("Gambar Slaid 5 (Direct Link):", value=val_k5)
        
        submit_internal = st.form_submit_button("🚀 Simpan Semua Konfigurasi Galeri")
        
        if submit_internal:
            if not current_trip:
                st.error("Ralat: Sila pilih trip aktif di sidebar terlebih dahulu!")
            else:
                try:
                    # Baca semula database paling segar (ttl=0) untuk mengelakkan isu overwrite
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=0)
                    
                    # Double-check pembersihan kolum
                    for col in kolum_wajib:
                        if col not in info_pukal.columns: info_pukal[col] = ""
                        info_pukal[col] = info_pukal[col].astype(str).replace('nan', '')
                    
                    # Semak sama ada data trip sudah wujud atau perlu row baru
                    if current_trip in info_pukal['ID_Trip'].values:
                        idx = info_pukal.index[info_pukal['ID_Trip'] == current_trip][0]
                        info_pukal.at[idx, 'Vault_URL'] = new_vault.strip()
                        info_pukal.at[idx, 'Kenangan_1'] = new_k1.strip()
                        info_pukal.at[idx, 'Kenangan_2'] = new_k2.strip()
                        info_pukal.at[idx, 'Kenangan_3'] = new_k3.strip()
                        info_pukal.at[idx, 'Kenangan_4'] = new_k4.strip()
                        info_pukal.at[idx, 'Kenangan_5'] = new_k5.strip()
                    else:
                        new_row = {
                            'ID_Trip': current_trip,
                            'Vault_URL': new_vault.strip(),
                            'Kenangan_1': new_k1.strip(),
                            'Kenangan_2': new_k2.strip(),
                            'Kenangan_3': new_k3.strip(),
                            'Kenangan_4': new_k4.strip(),
                            'Kenangan_5': new_k5.strip()
                        }
                        info_pukal = pd.concat([info_pukal, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Tolak kemaskini ke Google Sheets
                    conn.update(worksheet="Info_Kem", data=info_pukal)
                    st.success("Media dan album berjaya diselaraskan!")
                    
                    # MAGIC REFRESH: Cuci cache lama & rerun sistem
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Gagal mengemaskini pangkalan data: {e}")
