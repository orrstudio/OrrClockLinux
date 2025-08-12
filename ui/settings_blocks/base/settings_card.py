from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp

class SettingsCard(GridLayout):
    """
    Карточка для группы настроек.
    
    Атрибуты:
        title (str): Заголовок карточки
    """
    
    def __init__(self, title="", **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.row_default_height = dp(5)
        self.size_hint_y = None
        self.height = dp(200)  # Начальная высота
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        # Фон карточки
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Заголовок секции
        if title:
            title_label = Label(
                text=title.upper(),
                color=(1, 1, 1, 0.8),
                font_size=sp(16),
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            title_label.bind(size=title_label.setter('text_size'))
            self.add_widget(title_label)
    
    def _update_rect(self, instance, value):
        """Обновляет позицию и размер фонового прямоугольника."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
