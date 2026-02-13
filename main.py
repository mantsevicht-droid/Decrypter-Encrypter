import flet as ft
import hashlib

def crypt_logic(text, password, encrypt=True):
    # Твоя логика (немного адаптированная под типы данных)
    key_hash = hashlib.sha256(password.encode()).hexdigest()
    key_a = int(key_hash[:8], 16)
    
    result = []
    items = text.split() if not encrypt else list(text)
    
    for i, item in enumerate(items):
        dynamic_key = (key_a + i) & 0xFFFF
        if encrypt:
            val = ord(item)
            x = val ^ dynamic_key
            rol_x = ((x << 5) | (x >> 11)) & 0xFFFF
            res = ~(rol_x ^ dynamic_key) & 0xFFFF
            result.append(str(res))
        else:
            try:
                val = int(item)
                temp = (~val & 0xFFFF) ^ dynamic_key
                ror_x = ((temp >> 5) | (temp << 11)) & 0xFFFF
                res = ror_x ^ dynamic_key
                result.append(chr(res))
            except: return "Ошибка данных!"
    return " ".join(result) if encrypt else "".join(result)

def main(page: ft.Page):
    page.title = "XOR Crypto"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Поля ввода
    input_text = ft.TextField(label="Сообщение или числа", multiline=True)
    pass_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    output_text = ft.TextField(label="Результат", read_only=True, color="green")

    def on_encrypt(e):
        output_text.value = crypt_logic(input_text.value, pass_field.value, True)
        page.update()

    def on_decrypt(e):
        output_text.value = crypt_logic(input_text.value, pass_field.value, False)
        page.update()

    page.add(
        ft.Text("🛡️ Битовый Шифратор", size=30, weight="bold"),
        input_text,
        pass_field,
        ft.Row([
            ft.ElevatedButton("Зашифровать", on_click=on_encrypt, icon=ft.icons.LOCK),
            ft.ElevatedButton("Расшифровать", on_click=on_decrypt, icon=ft.icons.LOCK_OPEN),
        ], alignment=ft.MainAxisAlignment.CENTER),
        output_text
    )

ft.app(target=main)
