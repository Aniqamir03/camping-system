import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
import streamlit.components.v1 as components
import html as html_lib


current_trip = st.session_state.get('current_trip_id', '')
conn = st.connection("gsheets", type=GSheetsConnection)


def inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    scroll-behavior: smooth;
}

:root {
    --teal: #0abf8a;
    --cyan: #00a6c8;
    --blue: #0077b6;
    --dark: #06131f;
    --dark-2: #082539;
    --glass: rgba(255,255,255,0.075);
    --glass-strong: rgba(255,255,255,0.11);
    --border: rgba(255,255,255,0.14);
    --text: rgba(255,255,255,0.92);
    --muted: rgba(255,255,255,0.68);
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
[data-testid="stFormSubmitButton"] > button,
div[data-testid="stLinkButton"] > a {
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
    text-decoration: none !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stLinkButton"] > a:hover {
    transform: translateY(-3px) scale(1.015) !important;
    filter: brightness(1.08) saturate(1.08) !important;
    box-shadow: 0 18px 42px rgba(10,191,138,0.42) !important;
}

.stTextInput input,
.stDateInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] {
    background: rgba(255,255,255,0.085) !important;
    color: rgba(255,255,255,0.94) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 14px !important;
    min-height: 45px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

.stTextInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(10,191,138,0.72) !important;
    box-shadow: 0 0 0 4px rgba(10,191,138,0.16) !important;
}

.stTextInput label,
.stDateInput label,
.stTextArea label,
.stSelectbox label,
.stRadio label,
.stCheckbox label {
    color: rgba(255,255,255,0.76) !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
    animation: fadeUp 0.7s ease both !important;
}

[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
}

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

div[data-testid="stCheckbox"] > label {
    background: rgba(255,255,255,0.075) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 14px !important;
    padding: 0.55rem 0.8rem !important;
}

iframe {
    border-radius: 18px !important;
    box-shadow: 0 18px 45px rgba(0,0,0,0.34) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
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

.badge {
    display: inline-flex;
    align-items: center;
    margin-left: auto;
    min-height: 26px;
    padding: 0 10px;
    border-radius: 999px;
    background: rgba(10,191,138,0.14);
    border: 1px solid rgba(10,191,138,0.38);
    color: #9fffe0;
    font-size: 0.72rem;
    font-weight: 800;
}

.info-stack {
    display: grid;
    gap: 0.72rem;
}

.stat-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 0.9rem;
    box-shadow: 0 14px 34px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.08);
    backdrop-filter: blur(18px) saturate(145%);
    -webkit-backdrop-filter: blur(18px) saturate(145%);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    animation: fadeUp 0.55s ease both;
}

.stat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(10,191,138,0.36);
    box-shadow: 0 20px 46px rgba(0,0,0,0.30);
}

.stat-icon {
    width: 46px;
    height: 46px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--teal), var(--blue));
    box-shadow: 0 10px 24px rgba(10,191,138,0.25);
    font-size: 1.28rem;
    flex-shrink: 0;
}

.stat-label {
    color: rgba(255,255,255,0.60);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.stat-value {
    color: rgba(255,255,255,0.96);
    font-size: 0.98rem;
    font-weight: 800;
    line-height: 1.28;
    overflow-wrap: anywhere;
}

.helper-text {
    color: rgba(255,255,255,0.70);
    font-size: 0.92rem;
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
        font-size: 1.48rem !important;
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

    div[data-testid="stTabs"] > div:first-child {
        border-radius: 18px !important;
        overflow-x: auto !important;
    }

    button[data-baseweb="tab"] {
        min-width: max-content !important;
        font-size: 0.82rem !important;
    }

    .section-heading {
        padding: 0.82rem;
        border-radius: 16px;
    }

    .section-icon {
        width: 38px;
        height: 38px;
        font-size: 1.2rem;
    }

    .section-title {
        font-size: 1rem;
    }

    .badge {
        font-size: 0.66rem;
        padding: 0 8px;
    }

    [data-testid="stForm"] {
        padding: 1rem !important;
        border-radius: 16px !important;
    }

    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    div[data-testid="stLinkButton"] > a {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 0.9rem !important;
    }

  
}

@media (max-width: 430px) {
    .main .block-container {
        padding-left: 0.68rem !important;
        padding-right: 0.68rem !important;
    }

    .stat-card {
        padding: 0.82rem;
        gap: 10px;
    }

    .stat-icon {
        width: 42px;
        height: 42px;
    }

    .stat-value {
        font-size: 0.9rem;
    }
}
</style>
""", unsafe_allow_html=True)


def parse_tarikh(tarikh_str):
    try:
        return datetime.datetime.strptime(str(tarikh_str), "%Y-%m-%d").date()
    except:
        return datetime.date.today()


def section_header(icon: str, title: str, badge: str = ""):
    icon_safe = html_lib.escape(icon, quote=False)
    title_safe = html_lib.escape(title, quote=False)
    badge_html = f'<span class="badge">{html_lib.escape(badge, quote=False)}</span>' if badge else ""

    st.markdown(
        f'<div class="section-heading"><span class="section-icon">{icon_safe}</span><span class="section-title">{title_safe}</span>{badge_html}</div>',
        unsafe_allow_html=True
    )


def stat_card(icon: str, label: str, value: str):
    icon_safe = html_lib.escape(icon, quote=False)
    label_safe = html_lib.escape(label, quote=False)
    value_safe = html_lib.escape(str(value), quote=False)

    st.markdown(
        f'<div class="stat-card"><div class="stat-icon">{icon_safe}</div><div><div class="stat-label">{label_safe}</div><div class="stat-value">{value_safe}</div></div></div>',
        unsafe_allow_html=True
    )


inject_css()

st.title("📅 Tentative & Location Details")

default_lokasi = "Not Set (Please configure in Admin Panel)"
default_in = str(datetime.date.today())
default_out = str(datetime.date.today())
default_maps = "https://maps.google.com"
default_waze = "https://waze.com"

lokasi_kem = default_lokasi
check_in = default_in
check_out = default_out
maps_url = default_maps
waze_url = default_waze
p1 = p2 = p3 = ""

try:
    info_db = conn.read(worksheet="Info_Kem", ttl=600)

    if not info_db.empty:
        if current_trip and "ID_Trip" in info_db.columns:
            info_db["ID_Trip"] = info_db["ID_Trip"].astype(str).replace("nan", "").str.strip()
            info_semasa = info_db[info_db["ID_Trip"] == current_trip]
        else:
            info_semasa = info_db

        if not info_semasa.empty:
            lokasi_kem = str(info_semasa.iloc[0].get("Lokasi", default_lokasi)).replace("nan", "").strip() or default_lokasi
            check_in = str(info_semasa.iloc[0].get("Check_In", default_in)).replace("nan", "").strip() or default_in
            check_out = str(info_semasa.iloc[0].get("Check_Out", default_out)).replace("nan", "").strip() or default_out

            raw_maps = str(info_semasa.iloc[0].get("Maps_URL", default_maps)).strip()
            raw_waze = str(info_semasa.iloc[0].get("Waze_URL", default_waze)).strip()

            maps_url = default_maps if raw_maps.lower() in ["nan", ""] else raw_maps
            waze_url = default_waze if raw_waze.lower() in ["nan", ""] else raw_waze

            p1 = str(info_semasa.iloc[0].get("Poster_Pic_1", "")).replace("nan", "").strip()
            p2 = str(info_semasa.iloc[0].get("Poster_Pic_2", "")).replace("nan", "").strip()
            p3 = str(info_semasa.iloc[0].get("Poster_Pic_3", "")).replace("nan", "").strip()
except:
    pass

lokasi_url = urllib.parse.quote(lokasi_kem)

if maps_url == default_maps and lokasi_kem != default_lokasi:
    maps_url = f"https://maps.google.com/maps?q={lokasi_url}"
    waze_url = f"https://waze.com/ul?q={lokasi_url}"

embed_map_url = f"https://maps.google.com/maps?q={lokasi_url}&output=embed"

section_header("📍", "Info Lokasi Percutian", "LIVE")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="info-stack">', unsafe_allow_html=True)
    stat_card("🏕️", "Location", lokasi_kem)
    stat_card("📥", "Check-In", check_in)
    stat_card("📤", "Check-Out", check_out)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<p class="helper-text">🚘 <strong>Quick Navigation Links</strong></p>', unsafe_allow_html=True)
    st.link_button("🗺️ Google Maps", maps_url)
    st.link_button("🚙 Waze", waze_url)

with col2:
    if lokasi_kem != default_lokasi:
        components.iframe(embed_map_url, height=310)
    else:
        st.warning("The map will be displayed once the location is set.")

st.divider()

section_header("🖼️", "Group Activity Posters & Schedule")

senarai_poster = [p for p in [p1, p2, p3] if p and p.lower() != "nan"]

if senarai_poster:
    divs_gambar = ""
    dots_html = ""

    for i, img_url in enumerate(senarai_poster):
        img_safe = html_lib.escape(img_url, quote=True)

        divs_gambar += (
            f'<div class="poster-slide">'
            f'<div class="slide-number">{i + 1} / {len(senarai_poster)}</div>'
            f'<img src="{img_safe}" alt="Poster aktiviti {i + 1}">'
            f'</div>'
        )

        dots_html += f'<button class="poster-dot" onclick="goToSlide({i})" aria-label="Poster {i + 1}"></button>'

    html_kod = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html,
body {{
    width: 100%;
    margin: 0;
    background: transparent;
    font-family: 'Plus Jakarta Sans', sans-serif;
    overflow: hidden;
}}

.poster-wrap {{
    width: 100%;
    height: 100%;
    border-radius: 22px;
    overflow: hidden;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow: 0 18px 45px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.10);
    backdrop-filter: blur(18px) saturate(145%);
    -webkit-backdrop-filter: blur(18px) saturate(145%);
    padding: 12px;
}}

.poster-slider {{
    position: relative;
    width: 100%;
    height: 610px;
    overflow: hidden;
    border-radius: 18px;
    background:
        linear-gradient(135deg, rgba(10,191,138,0.12), rgba(0,119,182,0.12)),
        rgba(0,0,0,0.32);
    touch-action: pan-y;
}}

.poster-slide {{
    display: none;
    position: relative;
    width: 100%;
    height: 100%;
    animation: posterFade 0.62s ease both;
}}

.poster-slide img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    display: block;
    background: rgba(0,0,0,0.18);
    transform: none;
    animation: none;
}}

.slide-number {{
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 6;
    min-height: 28px;
    padding: 5px 12px;
    border-radius: 999px;
    background: rgba(5,20,31,0.54);
    border: 1px solid rgba(255,255,255,0.18);
    color: white;
    font-size: 0.78rem;
    font-weight: 800;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

.poster-nav {{
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 42px;
    height: 42px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.24);
    background: rgba(5,20,31,0.54);
    color: white;
    font-size: 25px;
    font-weight: 800;
    line-height: 1;
    cursor: pointer;
    z-index: 8;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: transform 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
}}

.poster-nav:hover {{
    background: rgba(10,191,138,0.72);
    transform: translateY(-50%) scale(1.08);
    box-shadow: 0 10px 28px rgba(10,191,138,0.32);
}}

.poster-prev {{
    left: 12px;
}}

.poster-next {{
    right: 12px;
}}

.poster-controls {{
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 12px;
    padding: 12px 2px 0;
}}

.progress-track {{
    height: 7px;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.10);
}}

.progress-fill {{
    width: 0%;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #0abf8a, #00a6c8, #0077b6);
    transition: width 0.42s ease;
}}

.poster-dots {{
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 6px 8px;
    border-radius: 999px;
    background: rgba(5,20,31,0.36);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

.poster-dot {{
    width: 8px;
    height: 8px;
    border: 0;
    border-radius: 999px;
    background: rgba(255,255,255,0.42);
    cursor: pointer;
    transition: width 0.28s ease, background 0.28s ease, transform 0.28s ease;
}}

.poster-dot.active {{
    width: 24px;
    background: #0abf8a;
    transform: scale(1.03);
}}

@keyframes posterFade {{
    from {{ opacity: 0; transform: translateX(10px) scale(1.01); }}
    to {{ opacity: 1; transform: translateX(0) scale(1); }}
}}

@media (max-width: 520px) {{
    .poster-wrap {{
        border-radius: 18px;
        padding: 9px;
    }}

    .poster-slider {{
        height: 520px;
        border-radius: 15px;
    }}

    .poster-nav {{
        width: 34px;
        height: 34px;
        font-size: 21px;
    }}

    .poster-prev {{
        left: 9px;
    }}

    .poster-next {{
        right: 9px;
    }}

    .poster-controls {{
        grid-template-columns: 1fr;
        justify-items: center;
        gap: 9px;
        padding-top: 10px;
    }}

    .progress-track {{
        width: 100%;
    }}

    .slide-number {{
        top: 10px;
        right: 10px;
        font-size: 0.72rem;
    }}
}}

@media (max-width: 390px) {{
    .poster-slider {{
        height: 520px;
    }}
}}
</style>
</head>
<body>
<div class="poster-wrap">
    <div class="poster-slider" id="posterSlider">
        {divs_gambar}
        <button class="poster-nav poster-prev" onclick="changeSlide(-1)" aria-label="Poster sebelum">‹</button>
        <button class="poster-nav poster-next" onclick="changeSlide(1)" aria-label="Poster seterusnya">›</button>
    </div>

    <div class="poster-controls">
        <div class="progress-track"><div class="progress-fill" id="progressBar"></div></div>
        <div class="poster-dots" id="posterDots">{dots_html}</div>
    </div>
</div>

<script>
let slideIndex = 0;
let timer = null;

const slides = document.querySelectorAll(".poster-slide");
const dots = document.querySelectorAll(".poster-dot");
const slider = document.getElementById("posterSlider");
const progressBar = document.getElementById("progressBar");

function showSlide(index) {{
    if (!slides.length) return;

    slides.forEach(slide => slide.style.display = "none");
    dots.forEach(dot => dot.classList.remove("active"));

    slideIndex = (index + slides.length) % slides.length;
    slides[slideIndex].style.display = "block";

    if (dots[slideIndex]) {{
        dots[slideIndex].classList.add("active");
    }}

    if (progressBar) {{
        progressBar.style.width = (((slideIndex + 1) / slides.length) * 100) + "%";
    }}

    clearTimeout(timer);
    timer = setTimeout(() => showSlide(slideIndex + 1), 5000);
}}

function changeSlide(direction) {{
    clearTimeout(timer);
    showSlide(slideIndex + direction);
}}

function goToSlide(index) {{
    clearTimeout(timer);
    showSlide(index);
}}

let touchStartX = 0;

slider.addEventListener("touchstart", function(event) {{
    touchStartX = event.touches[0].clientX;
}}, {{ passive: true }});

slider.addEventListener("touchend", function(event) {{
    const touchEndX = event.changedTouches[0].clientX;
    const difference = touchStartX - touchEndX;

    if (Math.abs(difference) > 45) {{
        changeSlide(difference > 0 ? 1 : -1);
    }}
}});

showSlide(0);
</script>
</body>
</html>
"""

    components.html(html_kod, height=740, scrolling=False)

else:
    st.info("ℹ️ No activity posters are available for this trip yet. The admin will update them shortly.")

st.divider()

section_header("🌦️", "Weather Forecast")

if lokasi_kem != default_lokasi:
    lokasi_cuaca = lokasi_kem.split(",")[0].strip()
    lokasi_cuaca_url = urllib.parse.quote(lokasi_cuaca)
    yahoo_weather_url = f"https://search.yahoo.com/search?p={lokasi_cuaca_url}+weather"

    st.write(f"System connected to location: **{lokasi_cuaca}**.")
    st.link_button("✉️ Check Location Weather", yahoo_weather_url, type="primary")
else:
    st.info("The weather forecast button will be activated once the admin sets the campsite location.")

if st.session_state.get("role") == "Admin":
    st.divider()
    section_header("⚙️", "Panel Pengurusan Tentatif & Lokasi", "ADMIN")

    tab_trip_baru, tab_poster, tab_urus_trip = st.tabs([
        "✨ Daftar Trip & Lokasi",
        "🖼️ Urus Poster",
        "✏️ Urus & Padam Trip",
    ])

    with tab_trip_baru:
        with st.form("form_daftar_trip_dan_lokasi"):
            st.write("### 🆕 Pendaftaran Aktiviti & Lokasi Baharu")
            st.write("Isi maklumat di bawah. Sistem akan auto-jana ID Trip, auto-link navigasi peta, dan sync ke database berkaitan.")

            new_nama_trip = st.text_input("Nama Aktiviti Baru (Contoh: Camping Janda Baik 2026)")
            new_lokasi = st.text_input("Nama Lokasi Tapak (Contoh: Riverside Camp, Pahang)")

            col_new_in, col_new_out = st.columns(2)

            with col_new_in:
                new_in = st.date_input("Tarikh Check-In / Bertolak", value=datetime.date.today(), key="new_in")

            with col_new_out:
                new_out = st.date_input("Tarikh Check-Out / Pulang", value=datetime.date.today(), key="new_out")

            submit_trip_baru = st.form_submit_button("🚀 Daftarkan Trip & Lokasi Serta-merta")

            if submit_trip_baru:
                if not new_nama_trip or not new_lokasi:
                    st.warning("Nama Aktiviti dan Nama Lokasi wajib diisi!")
                else:
                    try:
                        db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=600)
                        next_id = f"TRP{len(db_trip_pukal) + 1:03d}" if not db_trip_pukal.empty else "TRP001"
                    except:
                        db_trip_pukal = pd.DataFrame(columns=["ID_Trip", "Nama_Trip", "Tarikh", "Status_Trip"])
                        next_id = "TRP001"

                    trip_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Nama_Trip": new_nama_trip.strip(),
                        "Tarikh": new_in.strftime("%Y-%m-%d"),
                        "Status_Trip": "Aktif",
                    }])

                    lokasi_url_new = urllib.parse.quote(new_lokasi.strip())

                    info_row = pd.DataFrame([{
                        "ID_Trip": next_id,
                        "Lokasi": new_lokasi.strip(),
                        "Check_In": new_in.strftime("%Y-%m-%d"),
                        "Check_Out": new_out.strftime("%Y-%m-%d"),
                        "Maps_URL": f"https://maps.google.com/maps?q={lokasi_url_new}",
                        "Waze_URL": f"https://waze.com/ul?q={lokasi_url_new}",
                        "Poster_Pic_1": "",
                        "Poster_Pic_2": "",
                        "Poster_Pic_3": "",
                    }])

                    try:
                        updated_trip_db = pd.concat([db_trip_pukal, trip_row], ignore_index=True)
                    except:
                        updated_trip_db = trip_row

                    try:
                        db_info_pukal = conn.read(worksheet="Info_Kem", ttl=600)
                        updated_info_db = pd.concat([db_info_pukal, info_row], ignore_index=True)
                    except:
                        updated_info_db = info_row

                    conn.update(worksheet="Senarai_Trip", data=updated_trip_db)
                    conn.update(worksheet="Info_Kem", data=updated_info_db)

                    st.success(f"Mantap! Trip **{new_nama_trip}** berjaya direkodkan dengan kod **{next_id}**.")
                    st.cache_data.clear()
                    st.rerun()

    with tab_poster:
        with st.form("form_unggah_poster"):
            id_trip_save = current_trip if current_trip else "TRP001"

            st.write(f"🖼️ **Urus Pautan Poster (Slideshow)** untuk Trip ID Aktif: **{id_trip_save}**")
            st.markdown("Tampal direct link gambar poster. Boleh masukkan sehingga 3 keping poster.")

            url_p1 = st.text_input("🔗 Poster Utama (Wajib)", value=p1 if p1 != "nan" else "")
            url_p2 = st.text_input("🔗 Poster Kedua (Pilihan)", value=p2 if p2 != "nan" else "")
            url_p3 = st.text_input("🔗 Poster Ketiga (Pilihan)", value=p3 if p3 != "nan" else "")

            submit_poster = st.form_submit_button("💾 Simpan Koleksi Poster")

            if submit_poster:
                with st.spinner("Sedang menyelaraskan koleksi poster ke pangkalan data..."):
                    try:
                        info_pukal = conn.read(worksheet="Info_Kem", ttl=600)

                        if info_pukal.empty or "ID_Trip" not in info_pukal.columns:
                            info_pukal = pd.DataFrame(columns=[
                                "ID_Trip", "Lokasi", "Check_In", "Check_Out",
                                "Maps_URL", "Waze_URL", "Poster_Pic_1", "Poster_Pic_2", "Poster_Pic_3"
                            ])
                        else:
                            for col in info_pukal.columns:
                                info_pukal[col] = info_pukal[col].astype(str).replace("nan", "").str.strip()

                        for col_name in ["Poster_Pic_1", "Poster_Pic_2", "Poster_Pic_3"]:
                            if col_name not in info_pukal.columns:
                                info_pukal[col_name] = ""

                        if id_trip_save in info_pukal["ID_Trip"].values:
                            idx = info_pukal.index[info_pukal["ID_Trip"] == id_trip_save][0]
                            info_pukal.at[idx, "Poster_Pic_1"] = url_p1.strip()
                            info_pukal.at[idx, "Poster_Pic_2"] = url_p2.strip()
                            info_pukal.at[idx, "Poster_Pic_3"] = url_p3.strip()
                        else:
                            new_row = pd.DataFrame([{
                                "ID_Trip": id_trip_save,
                                "Lokasi": default_lokasi,
                                "Check_In": default_in,
                                "Check_Out": default_out,
                                "Maps_URL": default_maps,
                                "Waze_URL": default_waze,
                                "Poster_Pic_1": url_p1.strip(),
                                "Poster_Pic_2": url_p2.strip(),
                                "Poster_Pic_3": url_p3.strip(),
                            }])

                            info_pukal = pd.concat([info_pukal, new_row], ignore_index=True)

                        conn.update(worksheet="Info_Kem", data=info_pukal)
                        st.success("Koleksi poster berjaya disimpan dan diselaraskan!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memproses pautan poster: {e}")

    with tab_urus_trip:
        if not current_trip:
            st.info("Sila pilih aktiviti/trip di menu tepi terlebih dahulu sebelum menguruskannya.")
        else:
            try:
                db_trip_pukal = conn.read(worksheet="Senarai_Trip", ttl=600)
                trip_semasa_info = db_trip_pukal[db_trip_pukal["ID_Trip"] == current_trip]

                if not trip_semasa_info.empty:
                    info_trip = trip_semasa_info.iloc[0]
                    nama_semasa = str(info_trip.get("Nama_Trip", ""))
                    tarikh_semasa = str(info_trip.get("Tarikh", ""))
                    status_semasa = str(info_trip.get("Status_Trip", "Aktif"))

                    st.write(f"### ⚙️ Pengurusan: **{nama_semasa}** ({current_trip})")
                    tindakan_trip = st.radio("Pilih Tindakan Pengurusan:", ["Kemaskini Maklumat Trip", "Padam Trip ❌"])

                    with st.form("form_urus_trip"):
                        if tindakan_trip == "Kemaskini Maklumat Trip":
                            edit_nama = st.text_input("Nama Aktiviti", value=nama_semasa)
                            edit_tarikh = st.date_input("Tarikh Bertolak", value=parse_tarikh(tarikh_semasa))
                            idx_status = 0 if status_semasa == "Aktif" else 1
                            edit_status = st.selectbox("Status", ["Aktif", "Selesai"], index=idx_status)

                        elif tindakan_trip == "Padam Trip ❌":
                            st.warning(f"⚠️ AMARAN: Adakah anda pasti mahu memadam aktiviti **{nama_semasa}**? Semua maklumat lokasi dan poster berkaitan trip ini juga akan terpadam.")
                            sahkan_padam = st.checkbox("Ya, saya pasti mahu padam trip ini sepenuhnya.")

                        submit_urus = st.form_submit_button("⚡ Laksanakan Tindakan")

                        if submit_urus:
                            if tindakan_trip == "Kemaskini Maklumat Trip":
                                if not edit_nama:
                                    st.error("Nama aktiviti tidak boleh dibiarkan kosong!")
                                else:
                                    idx = db_trip_pukal.index[db_trip_pukal["ID_Trip"] == current_trip][0]
                                    db_trip_pukal.at[idx, "Nama_Trip"] = edit_nama.strip()
                                    db_trip_pukal.at[idx, "Tarikh"] = edit_tarikh.strftime("%Y-%m-%d")
                                    db_trip_pukal.at[idx, "Status_Trip"] = edit_status

                                    conn.update(worksheet="Senarai_Trip", data=db_trip_pukal)
                                    st.success("Maklumat aktiviti berjaya dikemaskini!")
                                    st.cache_data.clear()
                                    st.rerun()

                            elif tindakan_trip == "Padam Trip ❌":
                                if not sahkan_padam:
                                    st.error("Sila tanda pada kotak pengesahan sebelum memadam!")
                                else:
                                    db_trip_baru = db_trip_pukal[db_trip_pukal["ID_Trip"] != current_trip]
                                    conn.update(worksheet="Senarai_Trip", data=db_trip_baru)

                                    try:
                                        info_pukal = conn.read(worksheet="Info_Kem", ttl=600)
                                        info_baru = info_pukal[info_pukal["ID_Trip"] != current_trip]
                                        conn.update(worksheet="Info_Kem", data=info_baru)
                                    except:
                                        pass

                                    st.session_state["current_trip_id"] = ""
                                    st.success(f"Aktiviti {nama_semasa} berjaya dipadamkan sepenuhnya.")
                                    st.cache_data.clear()
                                    st.rerun()
                else:
                    st.error("Rekod aktiviti ini tidak dijumpai di pangkalan data.")
            except Exception as e:
                st.error(f"Gagal membaca sistem pangkalan data: {e}")
