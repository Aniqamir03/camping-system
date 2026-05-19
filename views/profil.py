import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io
from PIL import Image
import base64
import html as html_lib


username_semasa = st.session_state.get('username', '')

if not username_semasa:
    st.error("Sila log masuk terlebih dahulu dari halaman utama.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)


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
    max-width: 1040px !important;
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

/* FIX LIGHT MODE INPUT TEXT */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] span {
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

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
    -webkit-text-fill-color: #0f172a !important;
    box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
[data-testid="stFileUploader"] label {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.075) !important;
    border: 1px dashed rgba(10,191,138,0.42) !important;
    border-radius: 18px !important;
}

[data-testid="stFileUploader"] section:hover {
    background: rgba(10,191,138,0.10) !important;
    border-color: rgba(10,191,138,0.70) !important;
}

[data-testid="stFileUploader"] section * {
    color: rgba(255,255,255,0.88) !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    animation: fadeUp 0.7s ease both !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

.profile-hero {
    display: grid;
    grid-template-columns: 170px 1fr;
    gap: 1.1rem;
    align-items: center;
    margin: 1rem 0 1.2rem;
    padding: 1rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 18px 45px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(20px) saturate(145%);
    -webkit-backdrop-filter: blur(20px) saturate(145%);
    animation: fadeUp 0.65s ease both;
}

.profile-avatar-wrap {
    display: flex;
    justify-content: center;
}

.profile-avatar {
    width: 146px;
    height: 146px;
    border-radius: 50%;
    padding: 4px;
    background: linear-gradient(135deg, #0abf8a, #00a6c8, #0077b6);
    box-shadow: 0 18px 42px rgba(10,191,138,0.26);
}

.profile-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    display: block;
    border: 3px solid rgba(5,20,31,0.88);
}

.profile-name {
    color: rgba(255,255,255,0.97);
    font-size: 1.42rem;
    font-weight: 800;
    line-height: 1.18;
    margin-bottom: 6px;
}

.profile-meta {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    margin-bottom: 0.85rem;
}

.profile-chip-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.7rem;
}

.profile-chip {
    min-width: 0;
    padding: 0.78rem 0.85rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 10px 26px rgba(0,0,0,0.18);
}

.profile-chip-label {
    color: rgba(255,255,255,0.56);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 3px;
}

.profile-chip-value {
    color: rgba(255,255,255,0.94);
    font-size: 0.9rem;
    font-weight: 800;
    overflow-wrap: anywhere;
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

    .profile-hero {
        grid-template-columns: 1fr;
        text-align: center;
        border-radius: 18px;
        padding: 1rem 0.85rem;
    }

    .profile-avatar {
        width: 128px;
        height: 128px;
    }

    .profile-name {
        font-size: 1.2rem;
    }

    .profile-chip-grid {
        grid-template-columns: 1fr;
        text-align: left;
    }

    .section-heading {
        border-radius: 16px;
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


def render_profile_hero(url_gambar, nama, username, role, darah, kesihatan):
    nama_safe = html_lib.escape(clean_text(nama, "Pengguna"), quote=False)
    username_safe = html_lib.escape(clean_text(username, "-"), quote=False)
    role_safe = html_lib.escape(clean_text(role, "Member"), quote=False)
    darah_safe = html_lib.escape(clean_text(darah, "Tidak Pasti"), quote=False)
    kesihatan_safe = html_lib.escape(clean_text(kesihatan, "Tiada / Tiada Rekod"), quote=False)
    url_safe = html_lib.escape(url_gambar, quote=True)

    st.markdown(
        f'<div class="profile-hero">'
        f'<div class="profile-avatar-wrap"><div class="profile-avatar"><img src="{url_safe}" alt="{nama_safe}"></div></div>'
        f'<div>'
        f'<div class="profile-name">{nama_safe}</div>'
        f'<div class="profile-meta">@{username_safe} · {role_safe}</div>'
        f'<div class="profile-chip-grid">'
        f'<div class="profile-chip"><div class="profile-chip-label">Kumpulan Darah</div><div class="profile-chip-value">🩸 {darah_safe}</div></div>'
        f'<div class="profile-chip"><div class="profile-chip-label">Alergi / Kesihatan</div><div class="profile-chip-value">🏥 {kesihatan_safe}</div></div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


inject_css()

st.title("👤 Profil Saya")
st.write("Kemaskini maklumat peribadi, kesihatan, dan nombor telefon kecemasan anda di sini.")

try:
    users_db = conn.read(worksheet="Users", ttl=600)
except Exception:
    st.error("⚠️ Ralat API: Tab 'Users' tidak dijumpai di dalam Google Sheets. Sila pastikan ejaannya tepat.")
    st.stop()

for col in users_db.columns:
    users_db[col] = users_db[col].astype(str).replace('nan', '').replace('NaN', '').str.strip()

kolum_wajib = [
    'Phone_No',
    'Emergency_Name',
    'Emergency_Contact',
    'Emergency_Relationship',
    'Blood_Type',
    'Medical_Condition',
    'Profile_Pic_URL',
    'Password'
]

for col in kolum_wajib:
    if col not in users_db.columns:
        users_db[col] = ""

user_info = users_db[users_db['Username'] == username_semasa]

if not user_info.empty:
    idx = user_info.index[0]
    rekod = user_info.iloc[0]

    nama_semasa = clean_text(rekod.get('Full_Name', ''))
    phone_semasa = clean_text(rekod.get('Phone_No', ''))
    waris_nama_semasa = clean_text(rekod.get('Emergency_Name', ''))
    emg_semasa = clean_text(rekod.get('Emergency_Contact', ''))
    hubungan_semasa = clean_text(rekod.get('Emergency_Relationship', 'Ibu'), 'Ibu')
    darah_semasa = clean_text(rekod.get('Blood_Type', 'Tidak Pasti'), 'Tidak Pasti')
    kesihatan_semasa = clean_text(rekod.get('Medical_Condition', ''))
    pic_semasa = clean_text(rekod.get('Profile_Pic_URL', ''))
    pass_semasa = clean_text(rekod.get('Password', ''))
    role_semasa = clean_text(rekod.get('Role', 'Member'), 'Member')

    avatar_default = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

    if pic_semasa.startswith("http") or pic_semasa.startswith("data:image"):
        url_gambar = pic_semasa
    else:
        url_gambar = avatar_default

    render_profile_hero(
        url_gambar=url_gambar,
        nama=nama_semasa,
        username=username_semasa,
        role=role_semasa,
        darah=darah_semasa,
        kesihatan=kesihatan_semasa
    )

    st.divider()

    section_header("⚙️", "Kemaskini Maklumat Peribadi")

    with st.form("form_kemaskini_profil"):
        st.write("### 📞 Maklumat Perhubungan")
        edit_nama = st.text_input("Nama Penuh", value=nama_semasa)
        edit_phone = st.text_input("Nombor Telefon Anda", value=phone_semasa)

        st.divider()

        st.write("### 🚨 Maklumat Kecemasan & Waris")
        edit_waris_nama = st.text_input("Nama Penuh Waris / Kenalan Kecemasan", value=waris_nama_semasa)
        edit_emg = st.text_input("Nombor Telefon Waris / Kecemasan", value=emg_semasa)

        senarai_hubungan = ["Ibu", "Ayah", "Kakak", "Abang", "Adik", "Pasangan", "Saudara", "Lain-lain"]
        idx_hubungan = senarai_hubungan.index(hubungan_semasa) if hubungan_semasa in senarai_hubungan else 0
        edit_hubungan = st.selectbox("Hubungan dengan Waris tersebut:", senarai_hubungan, index=idx_hubungan)

        st.divider()

        st.write("### 🏥 Maklumat Kesihatan & Alergi")
        senarai_darah = ["Tidak Pasti", "A", "B", "AB", "O"]
        idx_darah = senarai_darah.index(darah_semasa) if darah_semasa in senarai_darah else 0
        edit_darah = st.selectbox("Kumpulan Darah:", senarai_darah, index=idx_darah)

        edit_kesihatan = st.text_input(
            "Alergi / Masalah Kesihatan / Pantang Larang (Jika Ada)",
            value=kesihatan_semasa,
            placeholder="Contoh: Alergi Kacang / Ada Asma / Tiada"
        )

        st.divider()

        st.write("### 🖼️ Gambar Profil & Kata Laluan")

        if pic_semasa.startswith("data:image"):
            st.info("💡 Anda sedang menggunakan gambar profil yang dimuat naik secara langsung.")

        new_pic_file = st.file_uploader("📸 Muat Naik Gambar Profil Baru (JPG/JPEG/PNG)", type=['jpg', 'jpeg', 'png'])

        edit_pass = st.text_input("Tukar Kata Laluan Baru", value=pass_semasa, type="password")

        submit_profil = st.form_submit_button("Simpan & Kemaskini Profil")

        if submit_profil:
            if not edit_nama or not edit_pass:
                st.warning("Nama Penuh dan Kata Laluan tidak boleh dikosongkan!")
            else:
                final_pic_data = pic_semasa

                if new_pic_file is not None:
                    try:
                        image = Image.open(new_pic_file)
                        image.thumbnail((200, 200))

                        buffered = io.BytesIO()

                        if image.mode in ("RGBA", "P"):
                            image = image.convert("RGB")

                        image.save(buffered, format="JPEG", quality=85)
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        final_pic_data = f"data:image/jpeg;base64,{img_str}"

                    except Exception as e:
                        st.error(f"Gagal memproses fail imej: {e}")
                        final_pic_data = pic_semasa

                users_db.at[idx, 'Full_Name'] = edit_nama.strip()
                users_db.at[idx, 'Phone_No'] = edit_phone.strip()
                users_db.at[idx, 'Emergency_Name'] = edit_waris_nama.strip()
                users_db.at[idx, 'Emergency_Contact'] = edit_emg.strip()
                users_db.at[idx, 'Emergency_Relationship'] = edit_hubungan
                users_db.at[idx, 'Blood_Type'] = edit_darah
                users_db.at[idx, 'Medical_Condition'] = edit_kesihatan.strip()
                users_db.at[idx, 'Profile_Pic_URL'] = final_pic_data
                users_db.at[idx, 'Password'] = edit_pass.strip()

                try:
                    conn.update(worksheet="Users", data=users_db)
                    st.session_state['full_name'] = edit_nama.strip()

                    st.success("Profil anda berjaya dikemaskini!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data ke Google Sheets. Pastikan imej tidak terlalu besar. Ralat: {e}")
else:
    st.error("Rekod akaun anda tidak dijumpai di pangkalan data. Sila hubungi Admin.")
