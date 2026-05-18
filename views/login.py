import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Log Masuk Sistem")

conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

# --- DEBUGGING (Buang hashtag '#' di bawah ni kalau nak tengok data mentah) ---
# st.write("Data mentah dari GSheet:", users_db[['Username', 'Password']]) 
# ------------------------------------------------------------------------------

with st.form("login_form"):
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log Masuk")
    
    if submit:
        # KOD KEBAL: Cuci column GSheet (buang ".0" dan buang space depan/belakang)
        db_user = users_db['Username'].astype(str).str.strip()
        db_pass = users_db['Password'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        # Cuci input pengguna (buang space kalau tertekan)
        in_user = str(input_user).strip()
        in_pass = str(input_pass).strip()
        
        # Padankan data yang dah dicuci
        match = users_db[(db_user == in_user) & (db_pass == in_pass)]
        
        if not match.empty:
            st.session_state["logged_in"] = True
            st.session_state["username"] = match.iloc[0]['Username']
            st.session_state["role"] = match.iloc[0]['Role']
            st.session_state["full_name"] = match.iloc[0]['Full_Name']
            st.rerun()
        else:
            st.error("Username atau Password salah!")
