import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("backpack 🎒 Senarai Peralatan & Logistik")
st.write("Semak senarai barang perkhemahan atau 'Claim' barang yang anda boleh bawa.")

conn = st.connection("gsheets", type=GSheetsConnection)
inventory_db = conn.read(worksheet="Inventory", ttl=0)

# Paksa kolum jadi teks untuk elak error
for col in ['ID_Barang', 'Nama_Barang', 'Kategori', 'Kuantiti', 'Dibawa_Oleh']:
    if col in inventory_db.columns:
        inventory_db[col] = inventory_db[col].astype(str).replace('nan', '')

# 1. Paparkan Senarai Barang Semasa
if not inventory_db.empty:
    st.dataframe(inventory_db, use_container_width=True, hide_index=True)
else:
    st.info("Senarai peralatan masih kosong.")

st.divider()

# 2. Fungsi 'Claim' Barang untuk Ahli yang Log Masuk
st.subheader("🤝 Claim Barang untuk Dibawa")
barang_belum_claim = inventory_db[inventory_db['Dibawa_Oleh'] == '']

if not barang_belum_claim.empty:
    with st.form("borang_claim"):
        pilihan_barang = st.selectbox("Pilih barang yang anda nak bawa:", barang_belum_claim['Nama_Barang'].tolist())
        submit_claim = st.form_submit_button("Saya Boleh Bawa Barang Ini!")
        
        if submit_claim:
            idx = inventory_db.index[inventory_db['Nama_Barang'] == pilihan_barang].tolist()[0]
            inventory_db.at[idx, 'Dibawa_Oleh'] = st.session_state["full_name"]
            
            conn.update(worksheet="Inventory", data=inventory_db)
            st.success(f"Terima kasih! Anda telah claim untuk membawa '{pilihan_barang}'.")
            st.cache_data.clear()
            st.rerun()
else:
    st.success("🎉 Semua peralatan telah berjaya diclaim oleh ahli kumpulan!")

# 3. Fungsi Tambah Barang Baru (Khas untuk Admin)
if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("➕ Tambah Barang Baru (Admin Sahaja)")
    with st.form("borang_tambah_barang"):
        nama_b = st.text_input("Nama Barang")
        kat_b = st.selectbox("Kategori", ["Khemah & Tidur", "Memasak & Makanan", "Lampu & Elektrik", "Logistik & Alat", "Lain-lain"])
        kuantiti_b = st.number_input("Kuantiti/Unit", min_value=1, step=1)
        submit_b = st.form_submit_button("Tambah ke Senarai")
        
        if submit_b and nama_b:
            id_baru = f"BRG{len(inventory_db) + 1:03d}"
            barang_baru = pd.DataFrame([{
                "ID_Barang": id_baru,
                "Nama_Barang": nama_b,
                "Kategori": kat_b,
                "Kuantiti": str(kuantiti_b),
                "Dibawa_Oleh": ""
            }])
            updated_inv = pd.concat([inventory_db, barang_baru], ignore_index=True)
            conn.update(worksheet="Inventory", data=updated_inv)
            st.success(f"'{nama_b}' berjaya ditambah!")
            st.cache_data.clear()
            st.rerun()
