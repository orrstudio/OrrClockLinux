from kivy.uix.button import Button
from kivy.metrics import dp

class ColorButton(Button):
    """Кнопка выбора цвета"""
    def __init__(self, color_name, color_tuple, **kwargs):
        super().__init__(**kwargs)
        self.color_name = color_name
        self.color_tuple = color_tuple
        self.background_color = color_tuple
        self.background_normal = ''
        self.size_hint = (1, None)
        self.height = self.width  # Квадратная кнопка
