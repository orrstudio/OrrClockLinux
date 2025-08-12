from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

class SettingsSection(ScrollView):
    """
    Секция настроек с возможностью прокрутки.
    
    Атрибуты:
        layout: Основной контейнер для виджетов секции
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(500)  # Будет обновляться динамически
        
        # Фон секции
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Основной layout с адаптивными отступами
        self.layout = GridLayout(
            cols=1,
            orientation='vertical', 
            spacing=0,
            padding=0,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.add_widget(self.layout)
    
    def _update_rect(self, instance, value):
        """Обновляет позицию и размер фонового прямоугольника."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
