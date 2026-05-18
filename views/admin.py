import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("⚙️ Panel Pentadbir (Admin)")
st.write("Urus ahli kumpulan perkhemahan dan pantau status profil mereka.")

# 1. Sambung ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# 2. Bersihkan data awal untuk elak error perpuluhan/NaN
for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Profile_Pic_URL']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

# 3. Cipta DataFrame salinan untuk paparan (Ini yang mambang tadi terpadam)
papar_df = users_db.copy()

# 4. Semak status Gambar Profil mengikut format Base64 (Kebal dari Error)
if 'Profile_Pic_URL' in papar_df.columns:
    papar_df['Gambar Profil'] = papar_df['Profile_Pic_URL'].apply(
        lambda x: "✅ Ada" if pd.notna(x) and str(x).startswith("data:image") else "❌ Tiada"
    )
else:
    papar_df['Gambar Profil'] = "❌ Tiada"

# 5. Papar senarai ahli dalam bentuk jadual (Sembunyikan password demi keselamatan)
kolum_papar = ['User_ID', 'Username', 'Full_Name', 'Role', 'Gambar Profil']
kolum_wujud = [c for c in kolum_papar if c in papar_df.columns]

st.subheader("👥 Senarai Ahli Semasa")
st.dataframe(papar_df[kolum_wujud], use_container_width=True, hide_index=True)

st.divider()

# 6. --- BORANG TAMBAH AHLI BAHARU ---
st.subheader("➕ Tambah Ahli Kumpulan Baru")
with st.form("borang_tambah_user"):
    new_username = st.text_input("Username (Guna huruf kecil, tiada space)").lower().strip()
    new_password = st.text_input("Password", type="password").strip()
    new_fullname = st.text_input("Nama Penuh").strip()
    new_role = st.selectbox("Peranan (Role)", ["Member", "Admin"])
    
    submit_user = st.form_submit_button("Daftarkan Ahli")
    
    if submit_user:
        if not new_username or not new_password or not new_fullname:
            st.warning("Sila isi semua ruangan yang wajib!")
        elif new_username in users_db['Username'].values:
            st.error("Username ini sudah wujud! Sila guna username lain.")
        else:
            # Jana ID baru secara automatik (contoh: USR002, USR003)
            next_id = f"USR{len(users_db) + 1:03d}"
            
            user_baru = pd.DataFrame([{
                "User_ID": next_id,
                "Username": new_username,
                "Password": new_password,
                "Full_Name": new_fullname,
                "Role": new_role,
                "Profile_Pic_URL": "",
                "Phone_No": "",
                "Emergency_Contact": ""
            }])
            
            # Gabungkan ke database asal
            updated_db = pd.concat([users_db, user_baru], ignore_index=True)
            
            # Simpan terus ke GSheet
            conn.update(worksheet="Users", data=updated_db)
            st.success(f"Ahli baharu **{new_fullname}** ({new_role}) berjaya didaftarkan!")
            st.cache_data.clear()
            st.rerun()
