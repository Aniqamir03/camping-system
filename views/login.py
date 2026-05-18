import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Log Masuk Sistem")

# ttl=0 bermaksud sistem akan sentiasa ambil data terkini (Live) dari GSheet
conn = st.connection("gsheets", type=GSheetsConnection)
users_db = conn.read(worksheet="Users", ttl=0)

with st.form("login_form"):
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")
    submit = st.form_submit_button("Log Masuk")
    
    if submit:
        # Kita tambah .astype(str) supaya tak ada lagi isu nombor (123456) tak sama dengan teks ("123456")
        match = users_db[
            (users_db['Username'].astype(str) == str(input_user)) & 
            (users_db['Password'].astype(str) == str(input_pass))
        ]
        
        if not match.empty:
            st.session_state["logged_in"] = True
            st.session_state["username"] = match.iloc[0]['Username']
            st.session_state["role"] = match.iloc[0]['Role']
            st.session_state["full_name"] = match.iloc[0]['Full_Name']
            st.rerun() # Refresh untuk masuk ke Dashboard
        else:
            st.error("Username atau Password salah!")
