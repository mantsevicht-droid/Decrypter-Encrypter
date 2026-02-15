import flet as ft
import hashlib
import base64
import threading
import time
import uuid # Для ID устройства
from supabase import create_client, Client

# --- КОНФИГУРАЦИЯ ---
URL = "https://ottnumxrvyerotigrxhk.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90dG51bXhydnllcm90aWdyeGhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNTg5NjcsImV4cCI6MjA4NjczNDk2N30.HV0hqLAsOsSQYIf36_jMu8xOdzUfVwkZCCCDBs1qEYw" # Твой ключ
supabase: Client = create_client(URL, KEY)
MY_ID = str(uuid.getnode()) # Уникальный ID твоего телефона

def crypt_logic(text, password, encrypt=True):
    if len(password) != 8: return None
    try:
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        key_a = int(key_hash[:8], 16)
        if encrypt:
            binary_data = bytearray()
            for i, char in enumerate(text):
                dk = (key_a + i) & 0xFFFF
                char_code = ord(char) ^ dk
                rol_x = ((char_code << 5) | (char_code >> 11)) & 0xFFFF
                res = ~(rol_x ^ dk) & 0xFFFF
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
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    txt_ps = ft.TextField(label="Ключ (8 симв.)", password=True, max_length=8)
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    msg_input = ft.TextField(hint_text="Сообщение...", expand=True, on_submit=lambda _: send_message())

    def delete_msg(msg_id):
        try:
            supabase.table("messages").delete().eq("id", msg_id).execute()
            load_messages()
        except: pass

    def load_messages():
        try:
            res = supabase.table("messages").select("*").order("created_at", desc=True).limit(30).execute()
            new_controls = []
            for m in reversed(res.data):
                is_me = str(m.get('sender_id')) == MY_ID
                raw = m['text']
                dec = crypt_logic(raw, txt_ps.value, False) if len(txt_ps.value) == 8 else None
                
                # Создаем "бабл" сообщения
                msg_content = ft.Column([
                    ft.Text(dec if dec else f"🔒 {raw[:10]}...", color="white" if dec else "grey"),
                    ft.Text(m['created_at'][11:16], size=10, color="white60")
                ], spacing=2)

                new_controls.append(
                    ft.Row([
                        ft.Container(
                            content=msg_content,
                            padding=10,
                            border_radius=15,
                            bgcolor=ft.colors.BLUE_700 if is_me else ft.colors.GREY_800,
                            alignment=ft.alignment.center_left,
                            on_click=lambda e, mid=m['id']: delete_msg(mid) if is_me else None # Удаление своих
                        )
                    ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
                )
            chat_list.controls = new_controls
            page.update()
        except: pass

    def send_message():
        if msg_input.value and len(txt_ps.value) == 8:
            enc = crypt_logic(msg_input.value, txt_ps.value, True)
            if enc:
                supabase.table("messages").insert({"text": enc, "sender_id": MY_ID}).execute()
                msg_input.value = ""
                load_messages()

    def auto_refresh():
        while True:
            load_messages()
            time.sleep(3)

    threading.Thread(target=auto_refresh, daemon=True).start()

    page.add(
        ft.Column([
            ft.Text("🛡️ POBIT CHAT", size=22, weight="bold"),
            txt_ps,
            ft.Container(content=chat_list, expand=True, padding=10),
            ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=lambda _: send_message())])
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)
