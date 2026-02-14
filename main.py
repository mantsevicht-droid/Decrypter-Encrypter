import flet as ft
import hashlib
import base64

def crypt_logic(text, password, encrypt=True):
    if len(password) != 8:
        return "Ошибка: Пароль должен быть ровно 8 символов!"
    if not text:
        return ""
        
    try:
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        key_a = int(key_hash[:8], 16)
        
        if encrypt:
            # Шифруем и пакуем в байты (по 2 байта на символ)
            binary_data = bytearray()
            for i, char in enumerate(text):
                dynamic_key = (key_a + i) & 0xFFFF
                char_code = ord(char) ^ dynamic_key
                rol_x = ((char_code << 5) | (char_code >> 11)) & 0xFFFF
                res = ~(rol_x ^ dynamic_key) & 0xFFFF
                # Разрезаем 16-битное число на два байта
                binary_data.extend(res.to_bytes(2, 'big'))
            # Превращаем байты в короткую строку Base64
            return base64.b64encode(binary_data).decode()
        else:
            # Декодируем Base64 обратно в байты
            binary_data = base64.b64decode(text)
            result = []
            for i in range(0, len(binary_data), 2):
                # Собираем число из двух байт
                item = int.from_bytes(binary_data[i:i+2], 'big')
                dynamic_key = (key_a + (i // 2)) & 0xFFFF
                temp = (~item & 0xFFFF) ^ dynamic_key
                res = ((temp >> 5) | (temp << 11)) & 0xFFFF ^ dynamic_key
                result.append(chr(res))
            return "".join(result)
    except:
        return "Ошибка: Неверный формат данных!"

def main(page: ft.Page):
    page.title = "Побитовый шифратор"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    txt_input = ft.TextField(label="Текст или шифр", multiline=True, min_lines=2)
    txt_pass = ft.TextField(label="Пароль", password=True, can_reveal_password=True, max_length=8)
    pass_hint = ft.Text("пароль должен состоять ровно из 8-ми символов", size=12, italic=True, color=ft.colors.GREY_400)
    txt_output = ft.TextField(label="Результат", read_only=True, multiline=True)

    def handle_click(e):
        is_enc = "Зашифровать" in e.control.text
        txt_output.value = crypt_logic(txt_input.value, txt_pass.value, is_enc)
        page.update()

    def copy_to_clipboard(e):
        if txt_output.value and "Ошибка" not in txt_output.value:
            page.set_clipboard(txt_output.value)
            page.snack_bar = ft.SnackBar(ft.Text("Скопировано!"))
            page.snack_bar.open = True
            page.update()

    page.add(
        ft.Column([
            ft.Text("🛡️ Побитовый шифратор", size=24, weight="bold"),
            txt_input,
            ft.Column([txt_pass, pass_hint], spacing=2),
            ft.Row([
                ft.ElevatedButton("🔒 Зашифровать", on_click=handle_click, expand=True),
                ft.ElevatedButton("🔓 Расшифровать", on_click=handle_click, expand=True),
            ]),
            ft.Divider(),
            ft.Row([ft.Text("Результат:", weight="bold"), ft.IconButton(icon=ft.icons.COPY_ALL, on_click=copy_to_clipboard)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            txt_output,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )

if __name__ == "__main__":
    ft.app(target=main)
