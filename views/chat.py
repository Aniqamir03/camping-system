import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Ambil memori sistem pengguna semasa
current_trip = st.session_state.get('current_trip_id', '')
username_semasa = st.session_state.get('username', '')
nama_semasa = st.session_state.get('full_name', '')

if not username_semasa:
    st.error("Sila log masuk terlebih dahulu.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 0. TARIK INFO TRIP AKTIF UNTUK TAJUK CHAT ---
nama_trip_sembang = "Bilik Sembang"
try:
    senarai_trip = conn.read(worksheet="Senarai_Trip", ttl=0)
    if not senarai_trip.empty and current_trip:
        trip_info = senarai_trip[senarai_trip['ID_Trip'] == current_trip]
        if not trip_info.empty:
            nama_trip_sembang = trip_info.iloc[0]['Nama_Trip']
except:
    pass

st.title(f"💬 Sembang Kumpulan: {nama_trip_sembang}")
st.write("Ruang santai untuk berbincang mengenai persiapan, logistik, dan agihan tugasan perkhemahan.")
st.divider()

# --- 1. AMBIL DATA USERS & CHAT DARI DATABASE ---
try:
    users_db = conn.read(worksheet="Users", ttl=600)
    # Bersihkan strings
    for col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').str.strip()
except:
    users_db = pd.DataFrame(columns=['Username', 'Full_Name', 'Profile_Pic_URL'])

try:
    chat_db = conn.read(worksheet="Group_Chat", ttl=0)
except:
    # Bina rangka kalau tab masih kosong kosong
    chat_db = pd.DataFrame(columns=["ID_Trip", "Username", "Nama_Penuh", "Mesej", "Masa_Hantar"])

# Kamus (Dictionary) Avatar untuk dapatkan gambar profil ahli dengan pantas
avatar_map = {}
avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
if not users_db.empty:
    for _, u_row in users_db.iterrows():
        pic = u_row.get('Profile_Pic_URL', '')
        avatar_map[u_row['Username']] = pic if pic != "" else avatar_default

# --- 2. PAPARKAN SEJARAH SEMBANG (CHAT HISTORY) ---
# KITA BAGI NILAI AWAL SUPAYA TAK ERROR
chat_semasa = pd.DataFrame() 

# Tapis mesej yang berkaitan dengan trip ini sahaja
if not chat_db.empty and 'ID_Trip' in chat_db.columns:
    # Pastikan kolum adalah string sebelum proses
    chat_db['ID_Trip'] = chat_db['ID_Trip'].astype(str).str.strip()
    chat_semasa = chat_db[chat_db['ID_Trip'] == current_trip]

# Kotak Sembang yang boleh di-scroll (Tinggi tetap 450px)
chat_container = st.container(height=450, border=True)

with chat_container:
    if not chat_semasa.empty:
        # Loop mesej
        for _, msg in chat_semasa.iterrows():
            sender_username = msg['Username']
            sender_name = msg['Nama_Penuh']
            text_mesej = msg['Mesej']
            masa_log = msg['Masa_Hantar']
            
            img_avatar = avatar_map.get(sender_username, avatar_default)
            is_self = " (Anda)" if sender_username == username_semasa else ""
            
            with st.chat_message(name=sender_username, avatar=img_avatar):
                st.write(f"**{sender_name}**{is_self} *at {masa_log}*")
                st.write(text_mesej)
        
        # Marker untuk anchor "Ke Bawah"
        st.empty() 
    else:
        st.info("ℹ️ Bilik sembang masih sunyi. Mulakan perbualan pertama anda di bawah!")

# --- 3. BUTANG "KE BAWAH" & INPUT ---
# Butang Jump to Bottom
if st.button("👇 Ke Mesej Terkini"):
    st.rerun() # Refresh untuk paparkan mesej paling baru di bawah

# Ruangan Input Mesej Baru
mesej_baru = st.chat_input("Tulis mesej anda di sini...")

if mesej_baru:
    if not current_trip:
        st.error("Ralat: Sila pilih trip aktif di menu tepi dahulu!")
    else:
        waktu_kl = datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).strftime("%Y-%m-%d %H:%M:%S")
        row_mesej = pd.DataFrame([{
            "ID_Trip": current_trip,
            "Username": username_semasa,
            "Nama_Penuh": nama_semasa,
            "Mesej": mesej_baru.strip(),
            "Masa_Hantar": waktu_kl
        }])
        
        try:
            try:
                chat_db_terkini = conn.read(worksheet="Group_Chat", ttl=600)
            except:
                chat_db_terkini = pd.DataFrame(columns=["ID_Trip", "Username", "Nama_Penuh", "Mesej", "Masa_Hantar"])
                
            updated_chat = pd.concat([chat_db_terkini, row_mesej], ignore_index=True)
            conn.update(worksheet="Group_Chat", data=updated_chat)
            
            # MAGIC REFRESH
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menghantar mesej: {e}")
