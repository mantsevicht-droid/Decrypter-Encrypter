import flet as ft
import hashlib

def crypt_logic(text, password, encrypt=True):
    # Ограничение: пароль должен быть строго 8 символов
    if len(password) != 8:
        return "Ошибка: Пароль должен быть ровно 8 символов!"
    if not text:
        return "Введите текст или числа!"
        
    try:
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
        return f"Ошибка данных!"

def main(page: ft.Page):
    page.title = "Побитовый шифратор"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    txt_input = ft.TextField(label="Текст или числа", multiline=True, min_lines=2)
    
    # Поле пароля с ограничением длины в самом виджете
    txt_pass = ft.TextField(
        label="Пароль", 
        password=True, 
        can_reveal_password=True,
        max_length=8, # Визуальное ограничение
    )
    
    # Подсказка маленькими буквами
    pass_hint = ft.Text(
        "пароль должен состоять ровно из 8-ми символов", 
        size=12, 
        italic=True, 
        color=ft.colors.GREY_400
    )

    txt_output = ft.TextField(label="Результат", read_only=True, multiline=True)

    def handle_click(e):
        # Проверка длины пароля перед запуском логики
        if len(txt_pass.value) != 8:
            txt_output.value = "Ошибка: Пароль должен быть ровно 8 символов!"
            page.update()
            return
            
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
        ft.Column(
            controls=[
                ft.Text("🛡️ Побитовый шифратор", size=24, weight="bold"),
                txt_input,
                ft.Column([txt_pass, pass_hint], spacing=2), # Группируем пароль и подсказку
                ft.Row(
                    controls=[
                        ft.ElevatedButton("🔒 Зашифровать", on_click=handle_click, expand=True),
                        ft.ElevatedButton("🔓 Расшифровать", on_click=handle_click, expand=True),
                    ]
                ),
                ft.Divider(),
                ft.Row([
                    ft.Text("Результат:", weight="bold"),
                    ft.IconButton(icon=ft.icons.COPY_ALL, on_click=copy_to_clipboard),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                txt_output,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
