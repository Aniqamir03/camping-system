import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("⚙️ Panel Pentadbir (Admin) - Versi Pro")
st.write("Hub utama untuk menguruskan ahli, melihat statistik, dan mengawal keselamatan sistem.")

# Sambung ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# Bersihkan data daripada sebarang nan atau space tersembunyi
for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()

# Pecahkan fungsi Admin kepada 3 Tab yang kemas
tab1, tab2, tab3 = st.tabs(["📊 Statistik & Senarai", "➕ Tambah Ahli Baru", "🔧 Urus / Padam Ahli"])

# ==========================================
# TAB 1: STATISTIK & SENARAI AHLI
# ==========================================
with tab1:
    st.write("### 📊 Ringkasan Ahli Trip")
    total_ahli = len(users_db)
    total_admin = len(users_db[users_db['Role'] == 'Admin'])
    total_user = len(users_db[users_db['Role'] == 'User'])

    # Papar kad metrik yang cantik
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Ahli Berdaftar", total_ahli)
    col2.metric("Pegawai (Admin)", total_admin)
    col3.metric("Ahli (User)", total_user)

    st.write("---")
    st.write("### 👥 Senarai Maklumat Penuh")
    
    if not users_db.empty:
        papar_df = users_db.copy()
        # Buat penanda sama ada user dah upload gambar profil atau belum
        if 'Profile_Pic_URL' in papar_df.columns:
            papar_df['Gambar Profil'] = papar_df['Profile_Pic_URL'].apply(lambda x: "✅ Ada" if x.startswith("data:image") else "❌ Tiada")
        
        # Susun kolum yang mahu dipaparkan sahaja (Sembunyikan password & kod base64 panjang)
        kolum_pilihan = ['User_ID', 'Username', 'Full_Name', 'Role', 'Phone_No', 'Emergency_Contact', 'Gambar Profil']
        st.dataframe(papar_df[kolum_pilihan], use_container_width=True)
    else:
        st.info("Tiada data ahli dijumpai.")

# ==========================================
# TAB 2: TAMBAH AHLI BARU
# ==========================================
with tab2:
    st.write("### ➕ Pendaftaran Akaun Ahli Baru")
    with st.form("daftar_ahli_form", clear_on_submit=True):
        username_input = st.text_input("Username (Guna huruf kecil & tiada space, cth: fitri)")
        password_input = st.text_input("Password Sementara", value="123456")
        fullname_input = st.text_input("Nama Penuh")
        role_input = st.selectbox("Peranan (Role)", ["User", "Admin"])
        
        submit_btn = st.form_submit_button("Daftar Ahli")
        
        if submit_btn:
            username_clean = username_input.strip().lower()
            password_clean = password_input.strip()
            fullname_clean = fullname_input.strip()
            
            if not username_clean or not password_clean or not fullname_clean:
                st.error("Semua ruangan wajib diisi!")
            elif username_clean in users_db['Username'].values:
                st.error(f"Username '{username_clean}' sudah wujud! Sila guna nama lain.")
            else:
                with st.spinner("Sedang mendaftarkan ahli..."):
                    if not users_db.empty and 'User_ID' in users_db.columns and len(users_db['User_ID']) > 0:
                        try:
                            last_id = users_db['User_ID'].iloc[-1]
                            last_num = int(last_id.replace("USR", ""))
                            new_id = f"USR{str(last_num + 1).zfill(3)}"
                        except:
                            new_id = f"USR{str(len(users_db) + 1).zfill(3)}"
                    else:
                        new_id = "USR001"
                    
                    new_user = {
                        'User_ID': new_id, 'Username': username_clean, 'Password': password_clean,
                        'Full_Name': fullname_clean, 'Role': role_input, 'Profile_Pic_URL': '',
                        'Phone_No': '', 'Emergency_Contact': ''
                    }
                    
                    users_db = pd.concat([users_db, pd.DataFrame([new_user])], ignore_index=True)
                    conn.update(worksheet="Users", data=users_db)
                    
                    st.success(f"Akaun untuk {fullname_clean} berjaya dicipta!")
                    st.cache_data.clear()
                    st.rerun()

# ==========================================
# TAB 3: URUS / KEMASKINI / PADAM AHLI
# ==========================================
with tab3:
    st.write("### 🔧 Pengurusan Dan Sekatan Ahli")
    
    # Elakkan admin daripada tersilap urus atau padam akaun diri sendiri yang tengah login
    senarai_ahli_lain = users_db[users_db['Username'] != st.session_state["username"]]
    
    if senarai_ahli_lain.empty:
        st.info("Tiada ahli lain untuk diuruskan buat masa ini.")
    else:
        # Pilih nama kawan yang nak diurus
        pilihan_nama = st.selectbox("Pilih Ahli Kumpulan:", senarai_ahli_lain['Full_Name'])
        
        # Ambil data spesifik ahli tersebut
        data_ahli = users_db[users_db['Full_Name'] == pilihan_nama].iloc[0]
        indeks_ahli = users_db.index[users_db['Full_Name'] == pilihan_nama].tolist()[0]
        
        st.info(f"📍 **ID:** {data_ahli['User_ID']} | **Username:** `{data_ahli['Username']}` | **Role Semasa:** {data_ahli['Role']}")
        
        # Pecah skrin kepada 2 bahagian (Kiri untuk Edit, Kanan untuk Padam)
        col_edit, col_padam = st.columns(2)
        
        with col_edit:
            st.write("#### 📝 Kemaskini Peranan & Akses")
            tukar_role = st.selectbox("Tukar Role Kepada:", ["User", "Admin"], index=0 if data_ahli['Role'] == 'User' else 1)
            checkbox_reset = st.checkbox("Reset password ahli ini kepada '123456'")
            
            if st.button("Simpan Tetapan Akses"):
                users_db.at[indeks_ahli, 'Role'] = tukar_role
                if checkbox_reset:
                    users_db.at[indeks_ahli, 'Password'] = "123456"
                
                conn.update(worksheet="Users", data=users_db)
                st.success(f"Akses untuk {pilihan_nama} berjaya dikemaskini!")
                st.cache_data.clear()
                st.rerun()
                
        with col_padam:
            st.write("#### ❌ Padam Ahli Dari Trip")
            st.warning(f"Amaran! Akaun {pilihan_nama} akan dipadam terus dari Google Sheets.")
            
            # Kotak pengesahan wajib ditanda untuk mengelakkan tersilap tekan butang padam
            sahkan_padam = st.checkbox(f"Saya sahkan ingin membuang {pilihan_nama}")
            
            if st.button("🚨 PADAM AHLI SEKARANG", type="primary"):
                if sahkan_padam:
                    # Padam baris data di dalam DataFrame
                    users_db = users_db.drop(indeks_ahli).reset_index(drop=True)
                    conn.update(worksheet="Users", data=users_db)
                    
                    st.success(f"Akaun {pilihan_nama} telah dipadam sepenuhnya!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Sila tanda kotak pengesahan terlebih dahulu sebelum memadam akaun!")
