from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from logic.clock_functions import BaseClockLabel

class ClockWidget(GridLayout):
    colors = {
        'lime': (0, 1, 0, 1),
        'aqua': (0, 1, 1, 1),
        'blue': (0, 0, 1, 1),
        'red': (1, 0, 0, 1),
        'yellow': (1, 1, 0, 1),
        'magenta': (1, 0, 1, 1),
        'pink': (1, 0.75, 0.8, 1),
        'grey': (0.7, 0.7, 0.7, 1),
        'white': (1, 1, 1, 1)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        
        # Создаем базовый виджет часов
        self.clock_widget = BaseClockLabel()
        self.add_widget(self.clock_widget)
        
        # Запускаем обновление времени
        Clock.schedule_interval(self.update_time, 0.5)

    def update_time(self, dt):
        """Обновляем время и мигание двоеточия"""
        self.clock_widget.toggle_colon_visibility()

    def update_color(self, color_name):
        """Обновляем цвет часов"""
        color_key = color_name.lower()
        color_tuple = self.colors.get(color_key, (1, 1, 1, 1))
        self.clock_widget.color = color_tuple

    def bind_on_clock_widget_created(self, callback):
        """Вызываем коллбэк с виджетом часов"""
        callback(self.clock_widget)
