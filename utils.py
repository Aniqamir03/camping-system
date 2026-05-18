import requests
import streamlit as st

def hantar_telegram_alert(mesej):
    try:
        # Tarik token & chat id dari Streamlit Secrets yang dah diset sebelum ni
        token = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mesej,
            "parse_mode": "Markdown"
        }
        
        # Hantar request ke API Telegram
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Gagal hantar Telegram: {e}")
