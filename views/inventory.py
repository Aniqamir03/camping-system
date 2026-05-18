import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🎒 Senarai Semak Peralatan")
st.write("Senarai barang keperluan logistik untuk Trip Pulau Redang. Sila tanda barang yang anda boleh bawa.")

# Sambungan ke GSheet
conn = st.connection("gsheets", type=GSheetsConnection)
inv_db = conn.read(worksheet="Inventory", ttl=0)

current_user = st.session_state["full_name"]

# Bahagikan paparan kepada dua jadual: Belum Diambil (Pending) & Telah Diambil (Assigned)
st.subheader("Barang Yang Belum Diagihkan")

# Tapis (filter) barang yang belum ada 'Assigned_To' atau masih kosong
pending_items = inv_db[inv_db['Assigned_To'].isna() | (inv_db['Assigned_To'] == "")]

if not pending_items.empty:
    for index, row in pending_items.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"🏕️ **{row['Item_Name']}** (Kuantiti: {row['Quantity']})")
        with col2:
            st.write(f"Kategori: {row['Category']}")
        with col3:
            # Butang untuk claim barang
            if st.button(f"Saya Bawa", key=f"claim_{index}"):
                inv_db.at[index, 'Assigned_To'] = current_user
                inv_db.at[index, 'Status'] = "Pending" # Status 'Pending' bermaksud belum masuk beg
                conn.update(worksheet="Inventory", data=inv_db)
                st.success(f"Anda telah ditugaskan untuk membawa {row['Item_Name']}!")
                st.cache_data.clear()
                st.rerun()
else:
    st.success("Semua barang kumpulan telah diagihkan!")

st.divider()

st.subheader("Senarai Tugasan Membawa Barang")
# Tapis barang yang sudah ada orang bawa
assigned_items = inv_db[inv_db['Assigned_To'].notna() & (inv_db['Assigned_To'] != "")]

if not assigned_items.empty:
    # Paparkan dalam bentuk jadual yang kemas
    st.dataframe(
        assigned_items[['Item_Name', 'Quantity', 'Assigned_To', 'Status']], 
        use_container_width=True,
        hide_index=True
    )
    
    st.write("---")
    st.write("📋 **Tugasan Anda:**")
    
    # Cari barang yang sedang dilog masuk (current_user) perlu bawa
    my_items = assigned_items[assigned_items['Assigned_To'] == current_user]
    
    if not my_items.empty:
        for index, row in my_items.iterrows():
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(f"- {row['Item_Name']} ({row['Quantity']})")
            with col_b:
                # Fungsi untuk lepaskan (unclaim) barang jika tidak jadi bawa
                if st.button("Batal", key=f"drop_{index}"):
                    inv_db.at[index, 'Assigned_To'] = ""
                    inv_db.at[index, 'Status'] = "Pending"
                    conn.update(worksheet="Inventory", data=inv_db)
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.info("Anda belum mengambil apa-apa tugasan barang kumpulan.")