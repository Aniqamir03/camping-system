import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import base64
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import html as html_lib


current_trip = st.session_state.get('current_trip_id', '')
user_role = st.session_state.get('role', '')

conn = st.connection("gsheets", type=GSheetsConnection)


def clean_text(value, default=""):
    try:
        if value is None or pd.isna(value):
            return default
    except Exception:
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
    max-width: 1180px !important;
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

.stTextInput input,
.stTextArea textarea {
    background: rgba(248,250,252,0.96) !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: #0f172a !important;
    border: 1px solid rgba(255,255,255,0.26) !important;
    border-radius: 14px !important;
    min-height: 45px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.80), 0 10px 24px rgba(0,0,0,0.12) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    background: #ffffff !important;
    border-color: rgba(10,191,138,0.82) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.18), 0 12px 28px rgba(0,0,0,0.16) !important;
}

.stTextInput label,
.stTextArea label,
[data-testid="stFileUploader"] label {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.075) !important;
    border: 1px dashed rgba(10,191,138,0.55) !important;
    border-radius: 18px !important;
}

[data-testid="stFileUploader"] section:hover {
    background: rgba(10,191,138,0.10) !important;
    border-color: rgba(10,191,138,0.82) !important;
}

[data-testid="stFileUploader"] section div,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section p {
    color: rgba(255,255,255,0.90) !important;
    -webkit-text-fill-color: rgba(255,255,255,0.90) !important;
}

[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] section button,
[data-testid="stFileUploader"] [role="button"] {
    background: linear-gradient(135deg, #0abf8a 0%, #00a6c8 52%, #0077b6 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 0 !important;
    border-radius: 999px !important;
    min-height: 40px !important;
    padding: 0.55rem 1.05rem !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 24px rgba(10,191,138,0.30) !important;
}

[data-testid="stFileUploader"] button *,
[data-testid="stFileUploader"] section button *,
[data-testid="stFileUploader"] [role="button"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, #0abf8a, #00a6c8, #0077b6) !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    animation: fadeUp 0.7s ease both !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

.gallery-hero {
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

.gallery-hero-title {
    color: rgba(255,255,255,0.96);
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.gallery-hero-sub {
    color: rgba(255,255,255,0.68);
    font-size: 0.92rem;
    line-height: 1.45;
}

.gallery-stat {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 34px;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(10,191,138,0.14);
    border: 1px solid rgba(10,191,138,0.34);
    color: #9fffe0;
    font-size: 0.82rem;
    font-weight: 800;
    margin: 0.2rem 0 1rem;
}

.insta-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    width: 100%;
    box-sizing: border-box;
    animation: fadeUp 0.7s ease both;
}

.media-item {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    overflow: hidden;
    border-radius: 18px;
    background:
        linear-gradient(135deg, rgba(10,191,138,0.16), rgba(0,119,182,0.16)),
        rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 16px 36px rgba(0,0,0,0.28);
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
}

.media-item:hover {
    transform: translateY(-5px) scale(1.015);
    border-color: rgba(10,191,138,0.42);
    box-shadow: 0 22px 48px rgba(0,0,0,0.38);
}

.media-item a {
    display: block;
    width: 100%;
    height: 100%;
    text-decoration: none;
}

.media-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.45s ease, filter 0.3s ease;
}

.media-item:hover img {
    transform: scale(1.055);
    filter: saturate(1.08) brightness(1.05);
}

.media-item::after {
    content: "Buka";
    position: absolute;
    left: 10px;
    bottom: 10px;
    z-index: 4;
    padding: 4px 9px;
    border-radius: 999px;
    color: white;
    background: rgba(5,20,31,0.50);
    border: 1px solid rgba(255,255,255,0.18);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    font-size: 0.68rem;
    font-weight: 800;
    opacity: 0;
    transform: translateY(6px);
    transition: opacity 0.25s ease, transform 0.25s ease;
}

.media-item:hover::after {
    opacity: 1;
    transform: translateY(0);
}

.video-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 6;
    min-width: 30px;
    height: 30px;
    padding: 0 7px;
    border-radius: 999px;
    background: rgba(5,20,31,0.62);
    border: 1px solid rgba(255,255,255,0.18);
    color: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.86rem;
    font-weight: 800;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    pointer-events: none;
}

.admin-media-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.72rem;
    margin-bottom: 0.72rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 12px 28px rgba(0,0,0,0.20);
}

.admin-media-row img {
    width: 68px;
    height: 68px;
    object-fit: cover;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.14);
    flex-shrink: 0;
}

.admin-media-meta {
    color: rgba(255,255,255,0.78);
    font-size: 0.82rem;
    font-weight: 700;
    overflow-wrap: anywhere;
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

@media (max-width: 900px) {
    .insta-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
    }
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

    .gallery-hero {
        border-radius: 18px;
    }

    .insta-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 6px;
    }

    .media-item {
        border-radius: 12px;
    }

    .video-badge {
        top: 6px;
        right: 6px;
        min-width: 26px;
        height: 26px;
        font-size: 0.76rem;
    }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_drive_service():
    try:
        creds_dict = st.secrets["connections"]["gsheets"]
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        return build("drive", "v3", credentials=credentials)
    except Exception:
        st.error("Ralat API Google Drive. Pastikan emel Service Account dimasukkan.")
        return None


drive_service = get_drive_service()


def get_folder_id(url_folder):
    url_folder = clean_text(url_folder)
    if not url_folder:
        return None

    match = re.search(r"folders/([a-zA-Z0-9_-]+)", url_folder.strip())
    if match:
        return match.group(1)

    return None


@st.cache_data(ttl=300)
def dapatkan_media_dari_folder(url_folder):
    folder_id = get_folder_id(url_folder)

    if not folder_id or not drive_service:
        return []

    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = drive_service.files().list(
            q=query,
            fields="files(id, thumbnailLink, mimeType, createdTime)",
            pageSize=300,
            orderBy="createdTime desc",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        items = results.get("files", [])
        senarai_media = []

        for item in items:
            mime = clean_text(item.get("mimeType", "")).lower()

            if "folder" in mime:
                continue

            link_gambar = clean_text(item.get("thumbnailLink", ""))

            if link_gambar:
                link_gambar = re.sub(r"=s\d+", "=s800", link_gambar)
            else:
                link_gambar = f"https://drive.google.com/uc?export=view&id={item['id']}"

            senarai_media.append({
                "id": item["id"],
                "link": link_gambar,
                "is_video": "video" in mime,
                "view_link": f"https://drive.google.com/file/d/{item['id']}/view?usp=drivesdk"
            })

        return senarai_media

    except Exception:
        return []


def muat_naik_ke_gdrive(fail_buffer, nama_fail, jenis_mime, folder_id):
    url_api = st.secrets.get("APPS_SCRIPT_URL")

    if not url_api:
        return None

    try:
        encoded_img = base64.b64encode(fail_buffer.getvalue()).decode("utf-8")
        payload = {
            "action": "upload",
            "filename": nama_fail,
            "mimeType": jenis_mime,
            "base64": encoded_img,
            "folderId": folder_id
        }

        res = requests.post(url_api, json=payload, timeout=120)

        if res.status_code == 200 and res.json().get("status") == "success":
            return res.json().get("id")

        return None

    except Exception:
        return None


def padam_media_gdrive(file_id):
    url_api = st.secrets.get("APPS_SCRIPT_URL")

    if not url_api:
        return False

    try:
        payload = {
            "action": "delete",
            "fileId": file_id
        }

        res = requests.post(url_api, json=payload, timeout=60)
        return res.status_code == 200 and res.json().get("status") == "success"

    except Exception:
        return False


inject_css()

st.title("🖼️ Galeri Automatik")

st.markdown(
    '<div class="gallery-hero">'
    '<div class="gallery-hero-title">Ruang memori foto dan video</div>'
    '<div class="gallery-hero-sub">Klik pada media untuk paparan HD atau muat turun terus daripada Google Drive.</div>'
    '</div>',
    unsafe_allow_html=True
)

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)

    if "Vault_URL" not in info_db.columns:
        info_db["Vault_URL"] = ""

    if "ID_Trip" not in info_db.columns:
        info_db["ID_Trip"] = ""

    info_db["ID_Trip"] = info_db["ID_Trip"].astype(str).replace("nan", "").str.strip()
    info_db["Vault_URL"] = info_db["Vault_URL"].astype(str).replace("nan", "").str.strip()

except Exception:
    info_db = pd.DataFrame(columns=["ID_Trip", "Vault_URL"])

if not info_db.empty and current_trip in info_db["ID_Trip"].values:
    val_vault = clean_text(info_db[info_db["ID_Trip"] == current_trip].iloc[0].get("Vault_URL", ""))
else:
    val_vault = ""

folder_id_semasa = get_folder_id(val_vault)

if folder_id_semasa:
    with st.expander("📤 Klik Sini Untuk Tambah Gambar / Video Ke Galeri"):
        st.markdown("**Sokongan Fail:** `PNG`, `JPG`, `JPEG`, `WEBP`, `GIF`, `HEIC`, `MP4`, `MOV`, `AVI`, `MKV`, `3GP`")

        uploaded_files = st.file_uploader(
            "Pilih Fail Media:",
            type=["png", "jpg", "jpeg", "webp", "gif", "heic", "mp4", "mov", "avi", "mkv", "3gp"],
            accept_multiple_files=True
        )

        if st.button("🚀 Muat Naik Sekarang", type="primary", use_container_width=True):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()

                jumlah_fail = len(uploaded_files)
                berjaya = 0

                for i, fail in enumerate(uploaded_files):
                    status_text.text(f"Memuat naik fail {i + 1} dari {jumlah_fail}...")

                    if muat_naik_ke_gdrive(fail, fail.name, fail.type, folder_id_semasa):
                        berjaya += 1

                    progress_bar.progress((i + 1) / jumlah_fail)

                status_text.text("Selesai!")
                st.success(f"Berjaya memuat naik {berjaya} fail media!")

                dapatkan_media_dari_folder.clear()
                st.rerun()
            else:
                st.warning("Sila pilih fail terlebih dahulu.")
else:
    st.info("Folder galeri belum ditetapkan. Admin boleh tampal pautan folder Google Drive di panel bawah.")

st.divider()

senarai_media = dapatkan_media_dari_folder(val_vault)

if st.button("🔄 Segerakkan (Sync) Galeri", use_container_width=True, type="secondary"):
    dapatkan_media_dari_folder.clear()
    st.rerun()

st.markdown(
    f'<div class="gallery-stat">📊 {len(senarai_media)} media aktif dikesan dalam folder Drive</div>',
    unsafe_allow_html=True
)

if len(senarai_media) > 0:
    html_items = []

    for m in senarai_media:
        view_link = html_lib.escape(clean_text(m.get("view_link", "#")), quote=True)
        link_gambar = html_lib.escape(clean_text(m.get("link", "")), quote=True)
        video_badge = '<div class="video-badge">🎥</div>' if m.get("is_video") else ""

        html_items.append(
            f'<div class="media-item">'
            f'<a href="{view_link}" target="_blank" rel="noopener noreferrer">'
            f'<img src="{link_gambar}" loading="lazy" onerror="this.style.opacity=\'0\';">'
            f'</a>'
            f'{video_badge}'
            f'</div>'
        )

    st.markdown(
        '<div class="insta-grid">' + ''.join(html_items) + '</div>',
        unsafe_allow_html=True
    )
else:
    st.info("📷 Belum ada gambar.")

if user_role == "Admin":
    st.divider()
    st.subheader("⚙️ Panel Pengurusan (Admin)")

    if len(senarai_media) > 0:
        with st.expander("🗑️ Buang Gambar / Video Dari Awan"):
            for item in senarai_media:
                item_id = clean_text(item.get("id", ""))
                link_gambar = clean_text(item.get("link", ""))

                st.markdown(
                    f'<div class="admin-media-row">'
                    f'<img src="{html_lib.escape(link_gambar, quote=True)}">'
                    f'<div class="admin-media-meta">ID Fail: {html_lib.escape(item_id, quote=False)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if st.button("Padam", key=f"del_{item_id}"):
                    if padam_media_gdrive(item_id):
                        st.success("Terpadam!")
                        dapatkan_media_dari_folder.clear()
                        st.rerun()
                    else:
                        st.error("Gagal dipadam.")

            st.write("---")

    with st.form("form_folder_drive"):
        st.write("Tampal pautan folder Google Drive untuk trip ini.")

        new_vault = st.text_input("Pautan Folder GDrive:", value=val_vault)

        if st.form_submit_button("🚀 Simpan Kunci Folder"):
            if current_trip:
                try:
                    info_pukal = conn.read(worksheet="Info_Kem", ttl=0)

                    if "ID_Trip" not in info_pukal.columns:
                        info_pukal["ID_Trip"] = ""

                    if "Vault_URL" not in info_pukal.columns:
                        info_pukal["Vault_URL"] = ""

                    info_pukal["ID_Trip"] = info_pukal["ID_Trip"].astype(str).replace("nan", "").str.strip()
                    info_pukal["Vault_URL"] = info_pukal["Vault_URL"].astype(str).replace("nan", "").str.strip()

                    if current_trip in info_pukal["ID_Trip"].values:
                        idx = info_pukal.index[info_pukal["ID_Trip"] == current_trip][0]
                        info_pukal.at[idx, "Vault_URL"] = new_vault.strip()
                    else:
                        info_pukal = pd.concat([
                            info_pukal,
                            pd.DataFrame([{
                                "ID_Trip": current_trip,
                                "Vault_URL": new_vault.strip()
                            }])
                        ], ignore_index=True)

                    conn.update(worksheet="Info_Kem", data=info_pukal)

                    st.cache_data.clear()
                    dapatkan_media_dari_folder.clear()

                    st.success("Tersimpan!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Gagal menyimpan pautan folder: {e}")
            else:
                st.error("Sila pilih trip aktif dahulu.")
