import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image
import base64
import io

st.title("👤 Profil Saya")

# --- FUNGSI PROSES GAMBAR KEPADA BASE64 ---
def proses_gambar_ke_base64(fail_gambar):
    img = Image.open(fail_gambar)
    img.thumbnail((150, 150))
    buffer = io.BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffer, format="JPEG", quality=80)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"
# ------------------------------------------

conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Paksa kolum menjadi teks untuk elak error perpuluhan
for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

current_user = st.session_state["username"]
user_index = users_db.index[users_db['Username'] == current_user].tolist()[0]
user_data = users_db.loc[user_index]

st.write(f"Kemaskini maklumat peribadi anda, **{user_data['Full_Name']}**.")

with st.form("update_profil_form"):
    # Paparkan gambar profil jika ada kod Base64 tersimpan
    pic_url = user_data['Profile_Pic_URL']
    if pd.notna(pic_url) and pic_url.startswith("data:image"):
        try:
            st.image(pic_url, width=150)
        except:
            st.warning("Gambar profil tidak dapat dipaparkan.")
    else:
        st.info("Tiada gambar profil.")

    # Butang muat naik fail gambar
    gambar_baru = st.file_uploader("📸 Muat Naik Gambar Profil Baru", type=['jpg', 'jpeg', 'png'])

    new_phone = st.text_input("No. Telefon", value=user_data['Phone_No'])
    new_emergency = st.text_input("No. Telefon Kecemasan (Waris)", value=user_data['Emergency_Contact'])
    
    # --- BAHAGIAN TUKAR PASSWORD (BAHARU) ---
    st.write("---")
    st.write("### 🔒 Keselamatan Akaun")
    new_password = st.text_input("Kata Laluan (Password) Baharu", value=user_data['Password'], type="password")
    # -----------------------------------------
    
    update_btn = st.form_submit_button("Simpan Perubahan")
    
    if update_btn:
        # Validasi kalau user sengaja kosongkan kotak password
        if not new_password.strip():
            st.error("Kata laluan tidak boleh dibiarkan kosong!")
            st.stop()

        if gambar_baru is not None:
            with st.spinner("Sedang memproses dan menyimpan gambar profil..."):
                try:
                    kod_gambar_base64 = proses_gambar_ke_base64(gambar_baru)
                    users_db.at[user_index, 'Profile_Pic_URL'] = kod_gambar_base64
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")
                    st.stop()

        # Kemaskini maklumat peribadi & Password baharu ke dalam DataFrame
        users_db.at[user_index, 'Phone_No'] = str(new_phone).strip()
        users_db.at[user_index, 'Emergency_Contact'] = str(new_emergency).strip()
        users_db.at[user_index, 'Password'] = str(new_password).strip() # <--- Simpan password baru ke DataFrame
        
        # Hantar DataFrame yang telah dikemaskini terus ke Google Sheets
        conn.update(worksheet="Users", data=users_db)
        
        st.success("Profil dan kata laluan anda berjaya dikemaskini!")
        st.cache_data.clear()
        st.rerun()
