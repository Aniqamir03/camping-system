import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Log Masuk Sistem")

# Sambungan ke GSheet (Pastikan secrets dah disetup)
conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl="10m")

with st.form("login_form"):
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log Masuk")
    
    if submit:
        # Semak padanan dengan GSheet
        match = users_db[(users_db['Username'] == input_user) & (users_db['Password'] == input_pass)]
        
        if not match.empty:
            st.session_state["logged_in"] = True
            st.session_state["username"] = match.iloc[0]['Username']
            st.session_state["role"] = match.iloc[0]['Role']
            st.session_state["full_name"] = match.iloc[0]['Full_Name']
            st.rerun() # Refresh untuk masuk ke Dashboard
        else:
            st.error("Username atau Password salah!")