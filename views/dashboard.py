import streamlit as st

st.title("🏕️ Papan Pemuka Perkhemahan")
st.write(f"Selamat datang, **{st.session_state['full_name']}**!")

st.info("Maklumat tentatif perkhemahan, kewangan, dan jadual tugasan akan dipaparkan di sini.")

if st.button("Log Keluar"):
    st.session_state.clear()
    st.rerun()