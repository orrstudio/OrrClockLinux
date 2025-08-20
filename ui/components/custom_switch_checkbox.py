from kivy.uix.widget import Widget
from kivy.properties import (
    BooleanProperty, 
    ColorProperty, 
    ListProperty, 
    NumericProperty
)
from kivy.lang import Builder
from kivy.metrics import dp

Builder.load_string('''
<CustomCheckBox>:
    size_hint: None, None
    width: self.height * 3  # Соотношение ширины к высоте 2:1
    height: dp(30)  # Высота по умолчанию
    
    # Цвета (аналогично CustomSwitch)
    thumb_color_active: 0.1, 0.5, 0.8, 1  # Голубой (активное состояние)
    thumb_color_inactive: 0.8, 0.2, 0.2, 1  # Красный (неактивное состояние)
    track_color_active: 0.05, 0.25, 0.4, 1  # Темно-синий (фон активного состояния)
    track_color_inactive: 0.2, 0.1, 0.1, 1  # Темно-красный (фон неактивного состояния)
    
    # Отступы
    padding: dp(4)  # Общие отступы
    thumb_padding: dp(8)  # Отступы ползунка (чем больше значение, тем меньше ползунок)
    
    canvas.before:
        # Фон трека
        Color:
            rgba: self.track_color_active if self.active else self.track_color_inactive
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height/2,]
        
        # Ползунок
        Color:
            rgba: self.thumb_color_active if self.active else self.thumb_color_inactive
        RoundedRectangle:
            pos: (self.right - self.height + self.thumb_padding/2, self.y + self.thumb_padding/2) if self.active else (self.x + self.thumb_padding/2, self.y + self.thumb_padding/2)
            size: self.height - self.thumb_padding, self.height - self.thumb_padding
            radius: [(self.height - self.thumb_padding)/2,]
''')

class CustomCheckBox(Widget):
    """
    Кастомный переключатель с настраиваемыми размерами и цветами.
    
    Атрибуты:
        active (bool): Состояние переключателя (вкл/выкл)
        thumb_color_active (list): Цвет ползунка в активном состоянии [R, G, B, A]
        thumb_color_inactive (list): Цвет ползунка в неактивном состоянии [R, G, B, A]
        track_color_active (list): Цвет фона в активном состоянии [R, G, B, A]
        track_color_inactive (list): Цвет фона в неактивном состоянии [R, G, B, A]
        padding (float): Отступ ползунка от краев
    """
    active = BooleanProperty(False)
    
    # Цвета ползунка
    thumb_color_active = ColorProperty([0.1, 0.5, 0.8, 1])  # Голубой
    thumb_color_inactive = ColorProperty([0.8, 0.2, 0.2, 1])  # Красный
    
    # Цвета фона
    track_color_active = ColorProperty([0.05, 0.25, 0.4, 1])  # Темно-синий
    track_color_inactive = ColorProperty([0.2, 0.1, 0.1, 1])  # Темно-красный
    
    padding = NumericProperty(dp(4))  # Общие отступы
    thumb_padding = NumericProperty(dp(8))  # Отступы ползунка (чем больше значение, тем меньше ползунок)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return super().on_touch_down(touch)
    
    def set_size(self, width=None, height=None):
        """
        Установка размера переключателя
        
        Args:
            width (float, optional): Ширина в пикселях. Если None, будет рассчитана автоматически
            height (float): Высота в пикселях
        """
        if height is not None:
            self.height = height
        if width is not None:
            self.width = width
        elif height is not None:
            # Автоматическая ширина, если не указана
            self.width = height * 3  # Соотношение 2:1 по умолчанию
        
        # Привязка обработчиков
        self.bind(active=self._on_active_change)
    
    def _on_active_change(self, instance, value):
        """Обработчик изменения состояния переключателя."""
        # Принудительно обновляем отрисовку
        self.canvas.ask_update()
    
    def on_touch_down(self, touch):
        """Обработчик нажатия на переключатель."""
        if self.collide_point(*touch.pos):
            # Инвертируем состояние при клике
            self.active = not self.active
            return True
        return super().on_touch_down(touch)
