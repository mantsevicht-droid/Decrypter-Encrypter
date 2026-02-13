import flet as ft
import hashlib

# Чистая логика без лишних библиотек
def crypt_logic(text, password, encrypt=True):
    try:
        if not text or not password:
            return ""
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        key_a = int(key_hash[:8], 16)
        result = []
        items = text.split() if not encrypt else list(text)
        for i, item in enumerate(items):
            dynamic_key = (key_a + i) & 0xFFFF
            if encrypt:
                char_code = ord(item) ^ dynamic_key
                rol_x = ((char_code << 5) | (char_code >> 11)) & 0xFFFF
                res = ~(rol_x ^ dynamic_key) & 0xFFFF
                result.append(str(res))
            else:
                temp = (~int(item) & 0xFFFF) ^ dynamic_key
                ror_x = ((temp >> 5) | (temp << 11)) & 0xFFFF
                res = ror_x ^ dynamic_key
                result.append(chr(res))
        return " ".join(result) if encrypt else "".join(result)
    except Exception as ex:
        return f"Ошибка: {str(ex)}"

def main(page: ft.Page):
    # Самые базовые настройки для стабильности на Android
    page.title = "Crypto"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    # Элементы интерфейса
    txt_input = ft.TextField(label="Ввод", multiline=True, min_lines=2)
    txt_pass = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    txt_output = ft.TextField(label="Результат", read_only=True, multiline=True)

    def handle_click(e):
        # Логика определения действия по тексту кнопки
        is_enc = e.control.text == "🔒"
        txt_output.value = crypt_logic(txt_input.value, txt_pass.value, is_enc)
        page.update()

    # Простейшая верстка: просто список элементов друг под другом
    content = ft.Column(
        controls=[
            ft.Text("🔐 BIT CRYPTO", size=20, weight="bold"),
            txt_input,
            txt_pass,
            ft.Row(
                controls=[
                    ft.ElevatedButton("🔒", on_click=handle_click, expand=True),
                    ft.ElevatedButton("🔓", on_click=handle_click, expand=True),
                ]
            ),
            txt_output,
        ],
        tight=True,
        spacing=15
    )

    # Добавляем всё на страницу
    page.add(content)
    page.update()

# Точка входа, обязательная для корректной сборки APK
if __name__ == "__main__":
    ft.app(target=main)
