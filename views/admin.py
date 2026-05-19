import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("⚙️ Panel Pentadbir (Admin)")
st.write("Urus ahli kumpulan perkhemahan dan pantau status profil mereka.")

# 1. Sambung ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    users_db = conn.read(worksheet="Users", ttl=600)
except Exception as e:
    st.error("Gagal membaca pangkalan data Users. Pastikan tab 'Users' wujud.")
    st.stop()

# 2. Bersihkan data awal untuk elak error perpuluhan/NaN
for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

# 3. Cipta DataFrame salinan untuk paparan 
papar_df = users_db.copy()

# 4. Semak status Gambar Profil mengikut format Base64 
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

# 6. --- KAWALAN PENGURUSAN AHLI ---
st.subheader("🛠️ Pengurusan Pangkalan Data Ahli")
tab_tambah, tab_urus = st.tabs(["➕ Tambah Ahli Baru", "✏️ Urus & Padam Ahli"])

# TAB 1: TAMBAH AHLI BAHARU
with tab_tambah:
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
                updated_db = pd.concat([users_db, user_baru], ignore_index=True)
                conn.update(worksheet="Users", data=updated_db)
                st.success(f"Ahli baharu **{new_fullname}** ({new_role}) berjaya didaftarkan!")
                st.cache_data.clear()
                st.rerun()

# TAB 2: URUS (EDIT/PADAM) AHLI SEDIA ADA
with tab_urus:
    st.write("Pilih ahli untuk menukar kata laluan, peranan, atau memadam akaun mereka terus dari sistem.")
    
    senarai_username = users_db['Username'].tolist()
    pilih_user = st.selectbox("Pilih Username Ahli:", senarai_username)
    
    if pilih_user:
        user_info = users_db[users_db['Username'] == pilih_user].iloc[0]
        st.info(f"Profil Terpilih: **{user_info['Full_Name']}** (Peranan Semasa: {user_info['Role']})")
        
        tindakan = st.radio("Pilih Tindakan Pengurusan:", ["Tukar Peranan (Role)", "Reset Kata Laluan", "Padam Akaun ❌"])
        
        with st.form("borang_tindakan_user"):
            if tindakan == "Tukar Peranan (Role)":
                peranan_semasa = user_info['Role']
                index_role = 0 if peranan_semasa == "Member" else 1
                peranan_baru = st.selectbox("Pilih Peranan Baharu:", ["Member", "Admin"], index=index_role)
            
            elif tindakan == "Reset Kata Laluan":
                password_baru = st.text_input("Masukkan Kata Laluan Baharu:")
                
            elif tindakan == "Padam Akaun ❌":
                st.warning(f"⚠️ AMARAN: Adakah anda pasti mahu memadam akaun **{pilih_user}**? Data ini tidak boleh dikembalikan.")
                sahkan_padam = st.checkbox("Ya, saya pasti mahu padam akaun ini.")
            
            submit_tindakan = st.form_submit_button("Laksanakan Tindakan")
            
            if submit_tindakan:
                # Cari baris (index) ahli tersebut dalam pangkalan data
                idx = users_db.index[users_db['Username'] == pilih_user][0]
                
                if tindakan == "Tukar Peranan (Role)":
                    if peranan_baru == peranan_semasa:
                        st.info("Tiada perubahan peranan dibuat.")
                    else:
                        users_db.at[idx, 'Role'] = peranan_baru
                        conn.update(worksheet="Users", data=users_db)
                        st.success(f"Peranan {pilih_user} berjaya ditukar kepada {peranan_baru}.")
                        st.cache_data.clear()
                        st.rerun()
                        
                elif tindakan == "Reset Kata Laluan":
                    if not password_baru.strip():
                        st.error("Kata laluan baharu tidak boleh kosong!")
                    else:
                        users_db.at[idx, 'Password'] = password_baru.strip()
                        conn.update(worksheet="Users", data=users_db)
                        st.success(f"Kata laluan untuk {pilih_user} berjaya dikemaskini.")
                        st.cache_data.clear()
                        st.rerun()
                        
                elif tindakan == "Padam Akaun ❌":
                    if not sahkan_padam:
                        st.error("Sila tanda (tick) kotak pengesahan sebelum memadam akaun.")
                    elif pilih_user == st.session_state.get('username'):
                        st.error("PENGESAHAN GAGAL: Anda tidak boleh memadam akaun anda sendiri ketika sedang log masuk!")
                    else:
                        # Buang rekod ahli dari DataFrame
                        users_db_baru = users_db.drop(idx)
                        conn.update(worksheet="Users", data=users_db_baru)
                        st.success(f"Akaun {pilih_user} berjaya dipadamkan sepenuhnya dari sistem.")
                        st.cache_data.clear()
                        st.rerun()
