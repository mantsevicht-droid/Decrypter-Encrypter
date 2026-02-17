import flet as ft
import hashlib
import base64
import requests # Легкая библиотека вместо supabase-py
import threading
import time
from datetime import datetime

# --- КОНФИГУРАЦИЯ SUPABASE ---
URL = "https://ottnumxrvyerotigrxhk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90dG51bXhydnllcm90aWdyeGhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTg5NjcsImV4cCI6MjA4NjczNDk2N30.HV0hqLAsOsSQYIf36_jMu8xOdzUfVwkZCCCDBs1qEYw"
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def crypt_logic(text, password, encrypt=True):
    if len(password) != 8: return None
    try:
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        key_a = int(key_hash[:8], 16)
        if encrypt:
            binary_data = bytearray()
            for i, char in enumerate(text):
                dk = (key_a + i) & 0xFFFF
                res = ~( ((ord(char) ^ dk) << 5 | (ord(char) ^ dk) >> 11) ^ dk ) & 0xFFFF
                binary_data.extend(res.to_bytes(2, 'big'))
            return base64.b64encode(binary_data).decode()
        else:
            data = base64.b64decode(text)
            res_chars = []
            for i in range(0, len(data), 2):
                item = int.from_bytes(data[i:i+2], 'big')
                dk = (key_a + (i // 2)) & 0xFFFF
                temp = (~item & 0xFFFF) ^ dk
                res_chars.append(chr(((temp >> 5) | (temp << 11)) & 0xFFFF ^ dk))
            return "".join(res_chars)
    except: return None

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Pobit Online"
    
    txt_ps = ft.TextField(label="Ключ (8 симв.)", password=True, max_length=8)
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    msg_input = ft.TextField(hint_text="Сообщение...", expand=True)

    def load_messages():
        try:
            # Запрос данных через GET
            params = {"order": "created_at.desc", "limit": "20"}
            r = requests.get(URL, headers=HEADERS, params=params)
            if r.status_code == 200:
                new_controls = []
                for m in reversed(r.json()):
                    raw = m['text']
                    dec = crypt_logic(raw, txt_ps.value, False) if len(txt_ps.value) == 8 else None
                    new_controls.append(ft.Text(f"🔓 {dec}" if dec else f"🔒 {raw[:15]}..."))
                chat_list.controls = new_controls
                page.update()
        except: pass

    def send_message(e):
        if msg_input.value and len(txt_ps.value) == 8:
            enc = crypt_logic(msg_input.value, txt_ps.value, True)
            if enc:
                requests.post(URL, headers=HEADERS, json={"text": enc})
                msg_input.value = ""
                load_messages()

    # Фоновое обновление
    def auto_refresh():
        while True:
            load_messages()
            time.sleep(4)

    threading.Thread(target=auto_refresh, daemon=True).start()

    page.add(
        ft.Tabs(
            expand=True,
            tabs=[
                ft.Tab(text="Шифратор", content=ft.Column([
                    ft.Text("🔑 НАСТРОЙКИ"), txt_ps
                ])),
                ft.Tab(text="Чат", content=ft.Column([
                    chat_list,
                    ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=send_message)])
                ], expand=True))
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
