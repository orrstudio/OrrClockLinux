from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

class CustomButton(Button):
    """
    Кастомная кнопка с иконкой.
    
    Атрибуты:
        icon_path (str): Путь к иконке кнопки
        icon_size (float): Размер иконки в пикселях
    """
    
    def __init__(self, icon_path='', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.icon_path = icon_path
        self.icon_size = dp(30)
        
        # Фон кнопки
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        # Иконка кнопки
        with self.canvas.after:
            self.icon_color = Color(1, 1, 1, 1)
            self.icon = Rectangle(source=self.icon_path, size=(self.icon_size, self.icon_size))
        
        self.bind(pos=self._update_icon, size=self._update_icon)
        self.bind(size=self._update_background, pos=self._update_background)
    
    def _update_icon(self, *args):
        """Обновляет позицию иконки по центру кнопки."""
        if hasattr(self, 'icon'):
            # Вычисляем центр кнопки
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            
            # Устанавливаем позицию иконки по центру кнопки
            self.icon.pos = (
                center_x - self.icon_size/2,
                center_y - self.icon_size/2
            )
            self.icon.size = (self.icon_size, self.icon_size)
    
    def _update_background(self, *args):
        """Обновляет позицию и размер фона кнопки."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
