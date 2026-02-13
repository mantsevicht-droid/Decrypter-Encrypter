import flet as ft
import hashlib

def crypt_logic(text, password, encrypt=True):
    if not text or not password:
        return ""
    try:
        key_hash = hashlib.sha256(password.encode()).hexdigest()
        key_a = int(key_hash[:8], 16)
        result = []
        items = text.split() if not encrypt else list(text)
        for i, item in enumerate(items):
            dynamic_key = (key_a + i) & 0xFFFF
            if encrypt:
                res = ~( ((ord(item) ^ dynamic_key) << 5 | (ord(item) ^ dynamic_key) >> 11) ^ dynamic_key ) & 0xFFFF
                result.append(str(res))
            else:
                temp = (~int(item) & 0xFFFF) ^ dynamic_key
                res = ((temp >> 5) | (temp << 11)) & 0xFFFF ^ dynamic_key
                result.append(chr(res))
        return " ".join(result) if encrypt else "".join(result)
    except:
        return "Ошибка!"

def main(page: ft.Page):
    # Настройки для мобилок
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.window_width = 400 # Эмуляция размера
    
    input_text = ft.TextField(label="Текст", multiline=True)
    pass_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    output_text = ft.TextField(label="Результат", read_only=True, multiline=True)

    def btn_click(e):
        # Определяем какую кнопку нажали по тексту на ней
        is_encrypt = e.control.text == "Зашифровать"
        output_text.value = crypt_logic(input_text.value, pass_field.value, is_encrypt)
        page.update()

    # Упрощенная верстка без сложных Row/Column для теста
    page.add(
        ft.Text("🛡️ Crypto App", size=25, weight="bold"),
        input_text,
        pass_field,
        ft.ElevatedButton("Зашифровать", on_click=btn_click),
        ft.ElevatedButton("Расшифровать", on_click=btn_click),
        output_text
    )

# ОЧЕНЬ ВАЖНО: для Android убираем лишние аргументы в ft.app
if __name__ == "__main__":
    ft.app(target=main)
