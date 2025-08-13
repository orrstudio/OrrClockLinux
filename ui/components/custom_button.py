from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty


class RoundedButton(Button):
    """Кнопка с закругленными углами и анимацией нажатия."""
    
    # Свойства для настройки внешнего вида
    bg_color = ColorProperty([0.2, 0.2, 0.2, 1])
    bg_color_press = ColorProperty([0.3, 0.3, 0.3, 1])
    border_radius = NumericProperty(dp(10))
    
    def __init__(self, **kwargs):
        # Настройки по умолчанию
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('border', (0, 0, 0, 0))
        kwargs.setdefault('background_color', (0, 0, 0, 0))  # Прозрачный фон
        
        super().__init__(**kwargs)
        
        # Привязка событий
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._on_state
        )
        
        # Инициализация отрисовки
        self._current_color = self.bg_color
        self._update_canvas()
    
    def _on_state(self, instance, value):
        """Обработчик изменения состояния кнопки (нажата/отпущена)."""
        if value == 'down':
            self._current_color = self.bg_color_press
        else:
            self._current_color = self.bg_color
        self._update_canvas()
    
    def _update_canvas(self, *args):
        """Обновление отрисовки кнопки."""
        self.canvas.before.clear()
        
        with self.canvas.before:
            # Рисуем фон с закругленными углами
            Color(*self._current_color)
            RoundedRectangle(
                pos=(self.x, self.y),
                size=(self.width, self.height),
                radius=[self.border_radius]
            )
        
        # Настройка текста
        self.text_size = (self.width - 10, None)
        self.halign = 'center'
        self.valign = 'middle'
