
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📅 Tentatif & Maklumat Lokasi")

# 1. Bahagian Maklumat Lokasi Tapak
st.subheader("📍 Info Tapak Perkhemahan")
col1, col2 = st.columns(2)
with col1:
    st.info("""
    **Lokasi:** Tapak Perkhemahan Pulau Redang, Terengganu
    **Check-in:** 22 Mei 2026 (Jumaat)
    **Check-out:** 24 Mei 2026 (Ahad)
    """)
with col2:
    # Letakkan pautan koordinat sebenar ke Waze/Maps
    st.write("🚘 Pautan Navigasi:")
    st.link_button("🗺️ Buka Google Maps", "https://maps.google.com")
    st.link_button("🚙 Buka Waze", "https://waze.com")

st.divider()

# 2. Bahagian Jadual Aktiviti (Tarik dari GSheet)
st.subheader("🗓️ Jadual Aktiviti Kumpulan")
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    tentatif_db = conn.read(worksheet="Tentatif", ttl=0)
    if not tentatif_db.empty:
        st.dataframe(tentatif_db, use_container_width=True, hide_index=True)
    else:
        st.info("Jadual tentatif belum diisi oleh Admin di Google Sheets.")
except:
    st.error("Gagal memuatkan data tentatif. Pastikan tab 'Tentatif' wujud di GSheet.")

st.divider()

# 3. Widget Cuaca Ringkas (Integrasi Iframe Percuma)
st.subheader("🌦️ Ramalan Cuaca Semasa (Kuala Terengganu)")
# Menggunakan widget cuaca percuma yang mesra iframe
weather_html = """
<iframe src="https://www.weatherwidget.io/w/iframe.html?id=ww_0fb09bf00ebad&label_1=KUALA%20TERENGGANU&label_2=CUACA&theme=flat" 
        scrolling="no" 
        frameborder="0" 
        style="border:none; overflow:hidden; width:100%; height:150px;">
</iframe>
"""
st.components.v1.html(weather_html, height=160)
