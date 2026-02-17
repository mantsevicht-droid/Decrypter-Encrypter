import flet as ft
import hashlib
import base64
import sqlite3
from datetime import datetime

# --- БАЗА ДАННЫХ (Локальная) ---
def init_db():
    conn = sqlite3.connect("access.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            input_text TEXT,
            output_text TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(mode, inp, out):
    try:
        conn = sqlite3.connect("access.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, mode, input_text, output_text) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mode, inp, out)
        )
        conn.commit()
        conn.close()
    except: pass

# --- ЛОГИКА ШИФРОВАНИЯ ---
def crypt_logic(text, password, encrypt=True):
    if len(password) != 8: return "Ошибка: Пароль 8 символов!"
    if not text: return ""
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
    except: return "Ошибка данных!"

# --- ИНТЕРФЕЙС ---
def main(page: ft.Page):
    init_db()
    page.title = "Pobit Crypt"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.scroll = ft.ScrollMode.AUTO

    txt_in = ft.TextField(label="Введите текст", multiline=True)
    txt_ps = ft.TextField(label="Пароль (8 симв.)", password=True, max_length=8)
    txt_out = ft.TextField(label="Результат", read_only=True, multiline=True)

    def handle_action(e):
        is_enc = "Зашифровать" in e.control.text
        res = crypt_logic(txt_in.value, txt_ps.value, is_enc)
        txt_out.value = res
        
        if res and "Ошибка" not in res:
            mode_label = "ENC" if is_enc else "DEC"
            save_to_db(mode_label, txt_in.value, res)
        page.update()

    page.add(
        ft.Column([
            ft.Text("🔐 POBIT SHIFRATOR", size=24, weight="bold"),
            txt_in, txt_ps,
            ft.Row([
                ft.ElevatedButton("🔒 Зашифровать", on_click=handle_action, expand=True),
                ft.ElevatedButton("🔓 Расшифровать", on_click=handle_action, expand=True),
            ]),
            ft.Divider(),
            ft.Text("Результат:", weight="bold"),
            txt_out,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )

if __name__ == "__main__":
    ft.app(target=main)
