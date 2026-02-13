import flet as ft
import hashlib

def crypt_logic(text, password, encrypt=True):
    # Защита от пустых полей
    if not text or not password:
        return "Введите текст и пароль!"
        
    key_hash = hashlib.sha256(password.encode()).hexdigest()
    key_a = int(key_hash[:8], 16)
    
    result = []
    # Для дешифровки разбиваем по пробелам, для шифровки берем символы
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
            except: 
                return "Ошибка: неверный формат чисел!"
    return " ".join(result) if encrypt else "".join(result)

def main(page: ft.Page):
    page.title = "XOR Crypto"
    page.theme_mode = ft.ThemeMode.DARK
    # Добавляем скролл, чтобы на телефонах всё влезло
    page.scroll = "adaptive"
    page.padding = 20

    input_text = ft.TextField(label="Сообщение или числа", multiline=True, min_lines=3)
    pass_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    output_text = ft.TextField(label="Результат", read_only=True, color="green", multiline=True)

    def on_encrypt(e):
        output_text.value = crypt_logic(input_text.value, pass_field.value, True)
        page.update()

    def on_decrypt(e):
        output_text.value = crypt_logic(input_text.value, pass_field.value, False)
        page.update()

    # Собираем интерфейс в колонку
    page.add(
        ft.Column([
            ft.Text("🛡️ Битовый Шифратор", size=28, weight="bold"),
            ft.Divider(),
            input_text,
            pass_field,
            ft.Row([
                ft.ElevatedButton("Зашифровать", on_click=on_encrypt, icon=ft.icons.LOCK),
                ft.ElevatedButton("Расшифровать", on_click=on_decrypt, icon=ft.icons.LOCK_OPEN),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            output_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

# Важно для Android:
ft.app(target=main)
