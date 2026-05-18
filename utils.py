import requests
import streamlit as st

def hantar_notifikasi_telegram(mesej):
    # Ambil token dan chat ID dari secrets
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": mesej,
        "parse_mode": "Markdown" # Membolehkan kita guna bold/italic dalam mesej
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal menghantar mesej Telegram: {e}")