import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io
from PIL import Image
import base64

st.title("👤 Profil Saya")
st.write("Kemaskini maklumat peribadi, kesihatan, dan nombor telefon kecemasan anda di sini.")

# Semak siapa yang sedang log masuk
username_semasa = st.session_state.get('username', '')

if not username_semasa:
    st.error("Sila log masuk terlebih dahulu dari halaman utama.")
    st.stop()

# 1. Sambung ke Google Sheets dengan Perisai Kebal
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    users_db = conn.read(worksheet="Users", ttl=600)
except Exception as e:
    st.error("⚠️ Ralat API: Tab 'Users' tidak dijumpai di dalam Google Sheets. Sila pastikan ejaannya tepat.")
    st.stop()

# 2. Bersihkan data untuk elak ralat NaN
for col in users_db.columns:
    users_db[col] = users_db[col].astype(str).replace('nan', '').replace('NaN', '').str.strip()

# Pastikan semua kolum lama dan baharu wujud
kolum_wajib = [
    'Phone_No', 'Emergency_Name', 'Emergency_Contact', 'Emergency_Relationship', 
    'Blood_Type', 'Medical_Condition', 'Profile_Pic_URL', 'Password'
]
for col in kolum_wajib:
    if col not in users_db.columns:
        users_db[col] = ""

# Cari data pengguna semasa
user_info = users_db[users_db['Username'] == username_semasa]

if not user_info.empty:
    idx = user_info.index[0]
    rekod = user_info.iloc[0]
    
    # Ambil data sedia ada dari database
    nama_semasa = rekod.get('Full_Name', '')
    phone_semasa = rekod.get('Phone_No', '')
    waris_nama_semasa = rekod.get('Emergency_Name', '')
    emg_semasa = rekod.get('Emergency_Contact', '')
    hubungan_semasa = rekod.get('Emergency_Relationship', 'Ibu')
    darah_semasa = rekod.get('Blood_Type', 'Tidak Pasti')
    kesihatan_semasa = rekod.get('Medical_Condition', '')
    pic_semasa = rekod.get('Profile_Pic_URL', '')
    pass_semasa = rekod.get('Password', '')
    
    # 3. Paparan Profil Ringkas (Visual Atas)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
        
        # --- PENAPIS IMEJ PINTAR (Sokong URL & Base64) ---
        pic_semasa_str = str(pic_semasa).strip()
        if pic_semasa_str.startswith("http") or pic_semasa_str.startswith("data:image"):
            url_gambar = pic_semasa_str
        else:
            url_gambar = avatar_default
            
        try:
            st.image(url_gambar, width=150, caption="Gambar Profil")
        except:
            st.image(avatar_default, width=150, caption="Gambar Default")
        # -------------------------------------------------------------
        
    with col2:
        st.subheader(nama_semasa)
        st.write(f"**Username:** {username_semasa}")
        st.write(f"**Peranan (Role):** {rekod.get('Role', 'Member')}")
        
        # Paparan info kesihatan pantas
        c_darah, c_kesihatan = st.columns(2)
        with c_darah:
            st.write(f"🩸 **Kumpulan Darah:** `{darah_semasa}`")
        with c_kesihatan:
            status_kesihatan = f"`{kesihatan_semasa}`" if kesihatan_semasa else "*Tiada / Tiada Rekod*"
            st.write(f"🏥 **Alergi / Kesihatan:** {status_kesihatan}")
        
    st.divider()
    
    # 4. Borang Kemaskini Profil Luas
    st.subheader("⚙️ Kemaskini Maklumat Peribadi")
    with st.form("form_kemaskini_profil"):
        
        # BAHAGIAN A: PERHUBUNGAN ASAS
        st.write("### 📞 Maklumat Perhubungan")
        edit_nama = st.text_input("Nama Penuh", value=nama_semasa)
        edit_phone = st.text_input("Nombor Telefon Anda", value=phone_semasa)
        
        st.divider()
        
        # BAHAGIAN B: KECEMASAN & WARIS
        st.write("### 🚨 Maklumat Kecemasan & Waris")
        edit_waris_nama = st.text_input("Nama Penuh Waris / Kenalan Kecemasan", value=waris_nama_semasa)
        edit_emg = st.text_input("Nombor Telefon Waris / Kecemasan", value=emg_semasa)
        
        senarai_hubungan = ["Ibu", "Ayah", "Kakak", "Abang", "Adik", "Pasangan", "Saudara", "Lain-lain"]
        idx_hubungan = senarai_hubungan.index(hubungan_semasa) if hubungan_semasa in senarai_hubungan else 0
        edit_hubungan = st.selectbox("Hubungan dengan Waris tersebut:", senarai_hubungan, index=idx_hubungan)
        
        st.divider()
        
        # BAHAGIAN C: KESIHATAN KUMPULAN
        st.write("### 🏥 Maklumat Kesihatan & Alergi")
        senarai_darah = ["Tidak Pasti", "A", "B", "AB", "O"]
        idx_darah = senarai_darah.index(darah_semasa) if darah_semasa in senarai_darah else 0
        edit_darah = st.selectbox("Kumpulan Darah:", senarai_darah, index=idx_darah)
        
        edit_kesihatan = st.text_input(
            "Alergi / Masalah Kesihatan / Pantang Larang (Jika Ada)", 
            value=kesihatan_semasa, 
            placeholder="Contoh: Alergi Kacang / Ada Asma / Tiada"
        )
        
        st.divider()
        
        # BAHAGIAN D: GAMBAR & KESELAMATAN (DIUBAH KE UPLOAD TERUS)
        st.write("### 🖼️ Gambar Profil & Kata Laluan")
        
        # Tunjuk info kalau imej sedia ada guna Base64 (panjang gila)
        if pic_semasa_str.startswith("data:image"):
            st.info("💡 Anda sedang menggunakan gambar profil yang dimuat naik secara langsung.")
        
        # --- FUNGSI UPLOAD GAMBAR TERUS ---
        # Kita pakai file_uploader menggantikan text_input
        new_pic_file = st.file_uploader("📸 Muat Naik Gambar Profil Baru (JPG/JPEG/PNG)", type=['jpg', 'jpeg', 'png'])
        # ----------------------------------
        
        edit_pass = st.text_input("Tukar Kata Laluan Baru", value=pass_semasa, type="password")
        
        submit_profil = st.form_submit_button("Simpan & Kemaskini Profil")
        
        if submit_profil:
            if not edit_nama or not edit_pass:
                st.warning("Nama Penuh dan Kata Laluan tidak boleh dikosongkan!")
            else:
                # --- PROSES FAIL GAMBAR KEPADA BASE64 (DENGAN RESIZING) ---
                # Kekalkan gambar lama secara lalai
                final_pic_data = pic_semasa 
                
                if new_pic_file is not None:
                    try:
                        # 1. Buka fail gambar
                        image = Image.open(new_pic_file)
                        
                        # 2. KECILKAN SAIZ (DOWNSIZING) - PENTING UNTUK GSHEETS!
                        # Kita thumbnail kan imej jadi max 200x200 pixel. 
                        # Base64 ori phone boleh cecah 1MB+ (limit GSheets cell 50k char).
                        # Downsized base64 biasanya bawah 20k char. Selamat.
                        image.thumbnail((200, 200))
                        
                        # 3. Tukar balik jadi bytes
                        buffered = io.BytesIO()
                        # Simpan sebagai JPEG untuk compression, guna RGB kalau PNG rosak
                        if image.mode in ("RGBA", "P"):
                            image = image.convert("RGB")
                        image.save(buffered, format="JPEG", quality=85) # Quality 85 balance size/look
                        
                        # 4. Encode jadi Base64 string
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        # 5. Tambah header required oleh st.image
                        final_pic_data = f"data:image/jpeg;base64,{img_str}"
                        
                    except Exception as e:
                        st.error(f"Gagal memproses fail imej: {e}")
                        final_pic_data = pic_semasa # Pakai balik imej lama kalau error
                # ----------------------------------------------------------
                
                # Masukkan data ke DataFrame
                users_db.at[idx, 'Full_Name'] = edit_nama.strip()
                users_db.at[idx, 'Phone_No'] = edit_phone.strip()
                users_db.at[idx, 'Emergency_Name'] = edit_waris_nama.strip()
                users_db.at[idx, 'Emergency_Contact'] = edit_emg.strip()
                users_db.at[idx, 'Emergency_Relationship'] = edit_hubungan
                users_db.at[idx, 'Blood_Type'] = edit_darah
                users_db.at[idx, 'Medical_Condition'] = edit_kesihatan.strip()
                
                # Simpan teks Base64 atau URL lama ke dalam kolum Profile_Pic_URL
                users_db.at[idx, 'Profile_Pic_URL'] = final_pic_data
                users_db.at[idx, 'Password'] = edit_pass.strip()
                
                try:
                    conn.update(worksheet="Users", data=users_db)
                    st.session_state['full_name'] = edit_nama.strip()
                    
                    st.success("Profil anda berjaya dikemaskini dengan imej baru!")
                    # MAGIC REFRESH
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    # Kalau fail terlalu besar, Google Sheets akan reject.
                    # Kita dah resize ke 200px di atas, sepatutnya isu ni dah selesai.
                    st.error(f"Gagal menyimpan data ke Google Sheets. Pastikan imej tidak terlalu besar. Ralat: {e}")
else:
    st.error("Rekod akaun anda tidak dijumpai di pangkalan data. Sila hubungi Admin.")
