import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import html as html_lib


def clean_text(value, default=""):
    try:
        if value is None or pd.isna(value):
            return default
    except:
        pass

    value = str(value).replace("nan", "").replace("NaN", "").strip()
    return value if value else default


def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
    color-scheme: dark;
}

.stApp {
    background:
        radial-gradient(circle at 16% 10%, rgba(10,191,138,0.22), transparent 30%),
        radial-gradient(circle at 82% 84%, rgba(0,119,182,0.26), transparent 34%),
        linear-gradient(135deg, #06131f 0%, #082539 48%, #063b48 100%) !important;
    background-attachment: fixed !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,0.024) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.024) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
    z-index: 0;
    animation: bgFloat 18s ease-in-out infinite alternate;
}

.main .block-container {
    max-width: 1080px !important;
    padding: 2rem 1.2rem 3rem !important;
    position: relative;
    z-index: 1;
}

[data-testid="stSidebar"] {
    background: rgba(5, 20, 31, 0.78) !important;
    backdrop-filter: blur(24px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(145%) !important;
    border-right: 1px solid rgba(255,255,255,0.12) !important;
}

[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.88) !important;
}

h1 {
    font-size: clamp(1.65rem, 4vw, 2.45rem) !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    background: linear-gradient(135deg, #ffffff 0%, #9fffe0 45%, #39c9ff 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: 0 !important;
    animation: fadeDown 0.7s ease both !important;
}

h2, h3 {
    color: rgba(255,255,255,0.95) !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    animation: fadeDown 0.7s ease both !important;
}

p, .stMarkdown p, .stText p, li {
    color: rgba(255,255,255,0.78) !important;
}

strong {
    color: #ffffff !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.16), transparent) !important;
    margin: 1.6rem 0 !important;
}

[data-testid="stAlert"],
[data-testid="stForm"],
[data-testid="stMetric"],
[data-testid="stExpander"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.075) !important;
    backdrop-filter: blur(20px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(145%) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 18px !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,0.28),
        inset 0 1px 0 rgba(255,255,255,0.10) !important;
    animation: fadeUp 0.65s ease both !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] strong {
    color: rgba(255,255,255,0.94) !important;
}

div[data-testid="stInfo"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.16), rgba(0,119,182,0.12)) !important;
    border: 1px solid rgba(10,191,138,0.36) !important;
}

div[data-testid="stSuccess"] {
    background: linear-gradient(135deg, rgba(10,191,138,0.20), rgba(255,255,255,0.06)) !important;
    border: 1px solid rgba(10,191,138,0.42) !important;
}

div[data-testid="stWarning"] {
    background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(255,255,255,0.055)) !important;
    border: 1px solid rgba(245,158,11,0.35) !important;
}

div[data-testid="stError"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(255,255,255,0.055)) !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 46px !important;
    border: 0 !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.35rem !important;
    background: linear-gradient(135deg, #0abf8a 0%, #00a6c8 52%, #0077b6 100%) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    box-shadow: 0 12px 30px rgba(10,191,138,0.28) !important;
    transition: transform 0.28s ease, box-shadow 0.28s ease, filter 0.28s ease !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-3px) scale(1.015) !important;
    filter: brightness(1.08) saturate(1.08) !important;
    box-shadow: 0 18px 42px rgba(10,191,138,0.42) !important;
}

.stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* INPUT + SELECT FIX */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] input {
    background: rgba(248,250,252,0.96) !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: #0f172a !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] {
    border: 1px solid rgba(255,255,255,0.26) !important;
    border-radius: 14px !important;
    min-height: 45px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.80), 0 10px 24px rgba(0,0,0,0.12) !important;
    transition: border 0.25s ease, box-shadow 0.25s ease, background 0.25s ease !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border-color: rgba(10,191,138,0.82) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.18), 0 12px 28px rgba(0,0,0,0.16) !important;
}

.stTextInput input:disabled,
.stTextArea textarea:disabled,
.stSelectbox [data-baseweb="select"][aria-disabled="true"] {
    background: rgba(226,232,240,0.95) !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    opacity: 1 !important;
}

.stSelectbox [data-baseweb="select"] svg {
    color: #0f172a !important;
    fill: #0f172a !important;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
    -webkit-text-fill-color: #0f172a !important;
    box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

/* DROPDOWN MENU FIX */
div[data-baseweb="popover"] {
    background: #ffffff !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] *,
li[role="option"],
li[role="option"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-baseweb="menu"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    box-shadow: 0 18px 45px rgba(0,0,0,0.25) !important;
}

li[role="option"] {
    background: #ffffff !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: rgba(10,191,138,0.14) !important;
}

/* RADIO */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label * {
    color: rgba(255,255,255,0.88) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.88) !important;
}

[data-testid="stRadio"] > div {
    background: rgba(255,255,255,0.055) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
    padding: 0.5rem !important;
}

/* TABS */
div[data-testid="stTabs"] > div:first-child {
    background: rgba(255,255,255,0.075) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 999px !important;
    padding: 0.35rem !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    box-shadow: 0 12px 30px rgba(0,0,0,0.20) !important;
}

button[data-baseweb="tab"] {
    border-radius: 999px !important;
    color: rgba(255,255,255,0.72) !important;
    font-weight: 800 !important;
    transition: all 0.25s ease !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #0abf8a, #0077b6) !important;
    color: white !important;
    box-shadow: 0 10px 26px rgba(10,191,138,0.30) !important;
}

button[data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.10) !important;
    color: white !important;
}

/* LABELS */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
[data-testid="stFileUploader"] label {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    box-shadow: 0 18px 45px rgba(0,0,0,0.24) !important;
}

.admin-hero {
    margin: 0.2rem 0 1rem;
    padding: 1rem 1.05rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.62s ease both;
}

.admin-hero-title {
    color: rgba(255,255,255,0.96);
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.admin-hero-sub {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    line-height: 1.45;
}

.section-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 0.9rem 1.05rem;
    margin: 1.2rem 0 0.9rem;
    box-shadow: 0 18px 45px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeDown 0.6s ease both;
}

.section-icon {
    width: 42px;
    height: 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(10,191,138,0.28), rgba(0,119,182,0.28));
    border: 1px solid rgba(255,255,255,0.14);
    font-size: 1.35rem;
    flex-shrink: 0;
}

.section-title {
    color: white;
    font-weight: 800;
    font-size: 1.16rem;
    line-height: 1.2;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    animation: fadeUp 0.7s ease both !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

::-webkit-scrollbar {
    width: 7px;
    height: 7px;
}

::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.04);
}

::-webkit-scrollbar-thumb {
    background: rgba(10,191,138,0.45);
    border-radius: 999px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(10,191,138,0.7);
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-14px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes bgFloat {
    from { transform: translate3d(0,0,0); opacity: 0.7; }
    to { transform: translate3d(-16px,10px,0); opacity: 1; }
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.75rem 2.4rem !important;
    }

    h1 {
        font-size: 1.45rem !important;
    }

    h2, h3 {
        font-size: 1.08rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0.9rem !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    [data-testid="stForm"] {
        padding: 1rem !important;
        border-radius: 16px !important;
    }

    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stTabs"] > div:first-child {
        border-radius: 18px !important;
        overflow-x: auto !important;
    }

    button[data-baseweb="tab"] {
        min-width: max-content !important;
        font-size: 0.82rem !important;
    }

    .admin-hero,
    .section-heading {
        border-radius: 16px;
    }

    .section-heading {
        padding: 0.82rem;
    }

    .section-icon {
        width: 38px;
        height: 38px;
        font-size: 1.2rem;
    }

    .section-title {
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


def section_header(icon: str, title: str):
    st.markdown(
        f'<div class="section-heading"><span class="section-icon">{html_lib.escape(icon, quote=False)}</span><span class="section-title">{html_lib.escape(title, quote=False)}</span></div>',
        unsafe_allow_html=True
    )


inject_css()

st.title("⚙️ Panel Pentadbir (Admin)")

st.markdown(
    '<div class="admin-hero">'
    '<div class="admin-hero-title">Urus ahli kumpulan perkhemahan</div>'
    '<div class="admin-hero-sub">Tambah ahli baharu, tukar peranan, reset kata laluan, padam akaun, dan pantau status profil ahli.</div>'
    '</div>',
    unsafe_allow_html=True
)

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    users_db = conn.read(worksheet="Users", ttl=600)
except Exception:
    st.error("Gagal membaca pangkalan data Users. Pastikan tab 'Users' wujud.")
    st.stop()

for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col in users_db.columns:
        users_db[col] = users_db[col].astype(str).replace('nan', '').replace('NaN', '').str.strip()

for col in ['User_ID', 'Username', 'Password', 'Full_Name', 'Role', 'Profile_Pic_URL', 'Phone_No', 'Emergency_Contact']:
    if col not in users_db.columns:
        users_db[col] = ""

papar_df = users_db.copy()

if 'Profile_Pic_URL' in papar_df.columns:
    papar_df['Gambar Profil'] = papar_df['Profile_Pic_URL'].apply(
        lambda x: "✅ Ada" if pd.notna(x) and str(x).startswith("data:image") else "❌ Tiada"
    )
else:
    papar_df['Gambar Profil'] = "❌ Tiada"

kolum_papar = ['User_ID', 'Username', 'Full_Name', 'Role', 'Gambar Profil']
kolum_wujud = [c for c in kolum_papar if c in papar_df.columns]

section_header("👥", "Senarai Ahli Semasa")
st.dataframe(papar_df[kolum_wujud], use_container_width=True, hide_index=True)

st.divider()

section_header("🛠️", "Pengurusan Pangkalan Data Ahli")

tab_tambah, tab_urus = st.tabs(["➕ Tambah Ahli Baru", "✏️ Urus & Padam Ahli"])

with tab_tambah:
    with st.form("borang_tambah_user"):
        st.write("### ➕ Daftarkan Ahli Baharu")

        new_username = st.text_input("Username (Guna huruf kecil, tiada space)").lower().strip()
        new_password = st.text_input("Password", type="password").strip()
        new_fullname = st.text_input("Nama Penuh").strip()
        new_role = st.selectbox("Peranan (Role)", ["Member", "Admin"])

        submit_user = st.form_submit_button("Daftarkan Ahli")

        if submit_user:
            if not new_username or not new_password or not new_fullname:
                st.warning("Sila isi semua ruangan yang wajib!")
            elif new_username in users_db['Username'].values:
                st.error("Username ini sudah wujud! Sila guna username lain.")
            else:
                next_id = f"USR{len(users_db) + 1:03d}"

                user_baru = pd.DataFrame([{
                    "User_ID": next_id,
                    "Username": new_username,
                    "Password": new_password,
                    "Full_Name": new_fullname,
                    "Role": new_role,
                    "Profile_Pic_URL": "",
                    "Phone_No": "",
                    "Emergency_Contact": ""
                }])

                updated_db = pd.concat([users_db, user_baru], ignore_index=True)
                conn.update(worksheet="Users", data=updated_db)

                st.success(f"Ahli baharu **{new_fullname}** ({new_role}) berjaya didaftarkan!")
                st.cache_data.clear()
                st.rerun()

with tab_urus:
    st.write("Pilih ahli untuk menukar kata laluan, peranan, atau memadam akaun mereka terus dari sistem.")

    senarai_username = users_db['Username'].dropna().astype(str).replace('nan', '').str.strip().tolist()
    senarai_username = [u for u in senarai_username if u]

    if not senarai_username:
        st.info("Tiada ahli untuk diuruskan.")
    else:
        pilih_user = st.selectbox("Pilih Username Ahli:", senarai_username)

        if pilih_user:
            user_info_df = users_db[users_db['Username'] == pilih_user]

            if user_info_df.empty:
                st.error("Rekod ahli tidak dijumpai.")
            else:
                user_info = user_info_df.iloc[0]
                nama_user = clean_text(user_info.get('Full_Name', pilih_user), pilih_user)
                role_user = clean_text(user_info.get('Role', 'Member'), 'Member')

                st.info(f"Profil Terpilih: **{nama_user}** (Peranan Semasa: {role_user})")

                tindakan = st.radio(
                    "Pilih Tindakan Pengurusan:",
                    ["Tukar Peranan (Role)", "Reset Kata Laluan", "Padam Akaun ❌"]
                )

                with st.form("borang_tindakan_user"):
                    if tindakan == "Tukar Peranan (Role)":
                        peranan_semasa = role_user
                        index_role = 0 if peranan_semasa == "Member" else 1
                        peranan_baru = st.selectbox("Pilih Peranan Baharu:", ["Member", "Admin"], index=index_role)

                    elif tindakan == "Reset Kata Laluan":
                        password_baru = st.text_input("Masukkan Kata Laluan Baharu:")

                    elif tindakan == "Padam Akaun ❌":
                        st.warning(f"⚠️ AMARAN: Adakah anda pasti mahu memadam akaun **{pilih_user}**? Data ini tidak boleh dikembalikan.")
                        sahkan_padam = st.checkbox("Ya, saya pasti mahu padam akaun ini.")

                    submit_tindakan = st.form_submit_button("Laksanakan Tindakan")

                    if submit_tindakan:
                        idx = users_db.index[users_db['Username'] == pilih_user][0]

                        if tindakan == "Tukar Peranan (Role)":
                            if peranan_baru == peranan_semasa:
                                st.info("Tiada perubahan peranan dibuat.")
                            else:
                                users_db.at[idx, 'Role'] = peranan_baru
                                conn.update(worksheet="Users", data=users_db)

                                st.success(f"Peranan {pilih_user} berjaya ditukar kepada {peranan_baru}.")
                                st.cache_data.clear()
                                st.rerun()

                        elif tindakan == "Reset Kata Laluan":
                            if not password_baru.strip():
                                st.error("Kata laluan baharu tidak boleh kosong!")
                            else:
                                users_db.at[idx, 'Password'] = password_baru.strip()
                                conn.update(worksheet="Users", data=users_db)

                                st.success(f"Kata laluan untuk {pilih_user} berjaya dikemaskini.")
                                st.cache_data.clear()
                                st.rerun()

                        elif tindakan == "Padam Akaun ❌":
                            if not sahkan_padam:
                                st.error("Sila tanda kotak pengesahan sebelum memadam akaun.")
                            elif pilih_user == st.session_state.get('username'):
                                st.error("PENGESAHAN GAGAL: Anda tidak boleh memadam akaun anda sendiri ketika sedang log masuk!")
                            else:
                                users_db_baru = users_db.drop(idx)
                                conn.update(worksheet="Users", data=users_db_baru)

                                st.success(f"Akaun {pilih_user} berjaya dipadamkan sepenuhnya dari sistem.")
                                st.cache_data.clear()
                                st.rerun()
