from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty


class RoundedButton(Button):
    """Кнопка с закругленными углами и анимацией нажатия."""
    
    # Свойства для настройки внешнего вида
    bg_color = ColorProperty([0.1, 0.4, 0.7, 1]) # цвет кнопки
    bg_color_press = ColorProperty([0.2, 0.6, 0.9, 1]) # цвет кнопки при нажатии
    border_radius = NumericProperty(dp(10)) # радиус закругления углов
    
    def __init__(self, **kwargs):
        # Настройки по умолчанию
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('border', (0, 0, 0, 0))
        kwargs.setdefault('background_color', (0, 0, 0, 0))  # Прозрачный фон
        
        super().__init__(**kwargs)
        
        # Настройки текста
        self.color = [1, 1, 1, 1]  # Белый цвет текста
        self.font_size = '20sp'     # Размер шрифта
        self.bold = True           # Жирный шрифт
        
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
            # Устанавливаем цвет фона
            if self.state == 'down':
                Color(*self.bg_color_press)
            else:
                Color(*self.bg_color)
                
            # Рисуем фон с закругленными углами
            RoundedRectangle(
                pos=(self.x, self.y),
                size=(self.width, self.height),
                radius=[self.border_radius]
            )
        
        # Настройка текста
        self.text_size = (self.width - 10, None)
        self.halign = 'center'
        self.valign = 'middle'


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
            self.icon_color = Color(1, 1, 1, 1) # Белый цвет иконки
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
