import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Sistem Perkhemahan", layout="wide")


@st.cache_data(ttl=600)
def get_senarai_trip():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet="Senarai_Trip", ttl=600)


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "role" not in st.session_state:
    st.session_state["role"] = None

if "username" not in st.session_state:
    st.session_state["username"] = ""

if "full_name" not in st.session_state:
    st.session_state["full_name"] = ""

if "current_trip_id" not in st.session_state:
    st.session_state["current_trip_id"] = ""


login_page = st.Page("views/login.py", title="Log Masuk", icon="🔐")
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏕️")
tentatif_page = st.Page("views/tentatif.py", title="Tentatif & Lokasi", icon="📅")
kehadiran_page = st.Page("views/kehadiran.py", title="Pengesahan Kehadiran", icon="📝")
galeri_page = st.Page("views/galeri.py", title="Galeri", icon="🖼️")
chat_page = st.Page("views/chat.py", title="Sembang Kumpulan", icon="💬")
profil_page = st.Page("views/profil.py", title="Profil Saya", icon="👤")
admin_page = st.Page("views/admin.py", title="Urus Ahli", icon="⚙️")


if not st.session_state["logged_in"]:
    pg = st.navigation([login_page])
else:
    nav_list = [
        dashboard_page,
        tentatif_page,
        kehadiran_page,
        galeri_page,
        chat_page,
        profil_page,
    ]

    if st.session_state.get("role") == "Admin":
        nav_list.append(admin_page)

    pg = st.navigation(nav_list)


if st.session_state["logged_in"]:
    with st.sidebar:
        st.write("---")
        st.write(f"Log masuk sebagai: **{st.session_state.get('full_name', '')}**")
        st.write("🌍 **Pilih Aktiviti / Trip:**")

        try:
            senarai_trip = get_senarai_trip()

            if not senarai_trip.empty and "Nama_Trip" in senarai_trip.columns and "ID_Trip" in senarai_trip.columns:
                senarai_trip["Nama_Trip"] = senarai_trip["Nama_Trip"].astype(str).replace("nan", "").str.strip()
                senarai_trip["ID_Trip"] = senarai_trip["ID_Trip"].astype(str).replace("nan", "").str.strip()

                senarai_trip = senarai_trip[senarai_trip["Nama_Trip"] != ""]

                if not senarai_trip.empty:
                    pilihan_trip = st.selectbox(
                        "Sila Pilih:",
                        senarai_trip["Nama_Trip"].tolist(),
                        label_visibility="collapsed"
                    )

                    id_terpilih = senarai_trip[
                        senarai_trip["Nama_Trip"] == pilihan_trip
                    ]["ID_Trip"].values[0]

                    st.session_state["current_trip_id"] = id_terpilih
                else:
                    st.warning("Tiada trip ditemui.")
            else:
                st.warning("Tab Senarai_Trip perlu ada kolum ID_Trip dan Nama_Trip.")

        except Exception:
            st.warning("⚠️ Sila pastikan tab 'Senarai_Trip' wujud.")

        st.write("---")

        if st.button("🚪 Log Keluar", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state["username"] = ""
            st.session_state["full_name"] = ""
            st.session_state["current_trip_id"] = ""
            st.cache_data.clear()
            st.rerun()


pg.run()
