import flet as ft
import hashlib
import base64
import sqlite3
from datetime import datetime

# --- ЛОГИКА ШИФРОВАНИЯ (твоя база) ---
def crypt_logic(text, password, encrypt=True):
    if len(password) != 8: return "Пароль 8 символов!"
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
    except: return "Ошибка!"

def main(page: ft.Page):
    page.title = "Побитовый шифратор"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Поля для шифратора
    txt_in = ft.TextField(label="Текст", multiline=True)
    txt_ps = ft.TextField(label="Пароль (8 симв.)", password=True, max_length=8)
    txt_out = ft.TextField(label="Результат", read_only=True, multiline=True)

    # Элементы чата
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    new_msg = ft.TextField(hint_text="Зашифрованное сообщение...", expand=True)

    def send_to_chat(e):
        if new_msg.value and txt_ps.value:
            # Шифруем сообщение перед отправкой в "эфир"
            encrypted = crypt_logic(new_msg.value, txt_ps.value, True)
            chat_messages.controls.append(
                ft.Text(f"Я: {encrypted}", color="blue")
            )
            new_msg.value = ""
            page.update()

    def on_encrypt_click(e):
        txt_out.value = crypt_logic(txt_in.value, txt_ps.value, True)
        page.update()

    def on_decrypt_click(e):
        txt_out.value = crypt_logic(txt_in.value, txt_ps.value, False)
        page.update()

    # Интерфейс с вкладками
    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Шифратор",
                icon=ft.icons.LOCK_OPEN,
                content=ft.Column([
                    ft.Text("🔐 ИНСТРУМЕНТ", size=20, weight="bold"),
                    txt_in, txt_ps,
                    ft.Row([
                        ft.ElevatedButton("Зашифровать", on_click=on_encrypt_click),
                        ft.ElevatedButton("Расшифровать", on_click=on_decrypt_click),
                    ]),
                    txt_out
                ], spacing=10, padding=10)
            ),
            ft.Tab(
                text="Чат",
                icon=ft.icons.CHAT,
                content=ft.Column([
                    ft.Text("💬 СЕКРЕТНЫЙ ЭФИР", size=20, weight="bold"),
                    chat_messages,
                    ft.Row([new_msg, ft.IconButton(ft.icons.SEND, on_click=send_to_chat)])
                ], spacing=10, padding=10)
            ),
        ],
        expand=1
    )

    page.add(t)

if __name__ == "__main__":
    ft.app(target=main)
