"""
Модуль для работы с настройками цветов в интерфейсе.
Содержит классы и функции для управления цветовой схемой приложения.
"""

import logging
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Line

logger = logging.getLogger(__name__)

def get_color_tuple(color_name):
    """
    Возвращает кортеж цвета по его имени.
    
    Args:
        color_name: Имя цвета
        
    Returns:
        tuple: Кортеж с компонентами цвета (R, G, B, A)
    """
    colors = {
        'lime': (0, 1, 0, 1),
        'aqua': (0, 1, 1, 1),
        'blue': (0, 0, 1, 1),
        'red': (1, 0, 0, 1),
        'yellow': (1, 1, 0, 1),
        'white': (1, 1, 1, 1)
    }
    return colors.get(color_name.lower(), (0, 1, 0, 1))

def get_color_name(color_tuple):
    """
    Возвращает имя цвета по его кортежу.
    
    Args:
        color_tuple: Кортеж с компонентами цвета (R, G, B, A)
        
    Returns:
        str: Имя цвета
    """
    colors = {
        (0, 1, 0, 1): 'lime',
        (0, 1, 1, 1): 'aqua',
        (0, 0, 1, 1): 'blue',
        (1, 0, 0, 1): 'red',
        (1, 1, 0, 1): 'yellow',
        (1, 1, 1, 1): 'white'
    }
    return colors.get(tuple(color_tuple), 'lime')

class ColorSettings:
    """Класс для управления настройками цветов."""
    
    def __init__(self, settings_window):
        """
        Инициализация настроек цветов.
        
        Args:
            settings_window: Ссылка на главное окно настроек
        """
        self.settings_window = settings_window
        self.active_button = None
        
        # Инициализируем словарь цветов
        self.colors = {
            'lime': (0, 1, 0, 1),
            'aqua': (0, 1, 1, 1),
            'blue': (0, 0, 1, 1),
            'red': (1, 0, 0, 1),
            'yellow': (1, 1, 0, 1),
            'white': (1, 1, 1, 1)
        }
    
    def _add_border_to_button(self, button):
        """
        Добавляет белую рамку к кнопке.
        
        Args:
            button: Кнопка, к которой добавляется рамка
        """
        if button is None:
            return
            
        # Устанавливаем флаг is_selected для кнопки
        button.is_selected = True
        
        # Обновляем рамку через метод кнопки
        button.update_border(button, True)
    
    def _on_color_button_press(self, button):
        """
        Обработка нажатия на цветную кнопку.
        
        Args:
            button: Нажатая кнопка
        """
        try:
            # Убираем выделение со старой активной кнопки
            if hasattr(self, 'active_button') and self.active_button != button:
                self.active_button.is_selected = False
                self.active_button.update_border(self.active_button, False)
            
            # Добавляем рамку на новую кнопку
            self._add_border_to_button(button)
            
            # Сохраняем ссылку на активную кнопку
            self.active_button = button
            
            # Устанавливаем выбранный цвет из нажатой кнопки
            self.settings_window.selected_color = button.color_name.lower()
            
        except Exception as e:
            logger.error(f"Ошибка в _on_color_button_press: {e}")
    
    def save_color_settings(self):
        """
        Сохраняет настройки цвета в базу данных и применяет их.
        
        Returns:
            bool: True, если настройки успешно сохранены, иначе False
        """
        try:
            if not hasattr(self.settings_window, 'selected_color') or not self.settings_window.selected_color:
                return False
                
            # Получаем выбранный цвет
            color_key = self.settings_window.selected_color.lower()
            
            # Сохраняем в базу данных
            if hasattr(self.settings_window, 'db'):
                self.settings_window.db.save_setting('color', color_key)
            
            # Применяем цвет через callback, если он доступен
            if hasattr(self.settings_window, 'apply_callback') and self.settings_window.apply_callback:
                # Получаем кортеж цвета
                color_tuple = self.colors.get(color_key, (0, 1, 0, 1))  # Зеленый по умолчанию
                self.settings_window.apply_callback(color_tuple)
            
            logger.info(f"Theme Color: {color_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving color: {e}")
            return False

class ColorOption(Button):
    """Кнопка выбора цвета с предпросмотром."""
    color_name = StringProperty()
    color_value = ListProperty([1, 1, 1, 1])
    is_selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = self.color_value
        self.size_hint_y = None
        self.height = dp(40)
        self.border = (2, 2, 2, 2)
        self.bind(color_value=self.update_color)
        self.bind(is_selected=self.update_border)
        self.bind(pos=self._update_border_pos, size=self._update_border_pos)
        
    def update_color(self, instance, value):
        self.background_color = value
        
    def _update_border_pos(self, *args):
        # Обновляем позицию рамки при изменении позиции или размера кнопки
        if hasattr(self, '_border'):
            self._border.rectangle = (self.x, self.y, self.width, self.height)
        
    def update_border(self, instance, value):
        self.background_color = self.color_value
        self.canvas.before.clear()
        
        if value:  # Если кнопка выбрана
            with self.canvas.before:
                from kivy.graphics import Color, Line
                # Рисуем белую рамку
                Color(1, 1, 1, 1)
                self._border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)


def create_color_section(settings_window):
    """
    Создает секцию выбора цвета.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройкой цветов
    """
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.metrics import dp
    from kivy.core.window import Window
    from kivy.clock import Clock
    
    # Создаем экземпляр ColorSettings для управления настройками цветов
    color_settings = ColorSettings(settings_window)
    
    # Основной вертикальный контейнер для блока выбора цвета
    color_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Увеличиваем высоту для учета отступов
        padding=[dp(20), dp(15), dp(20), dp(20)],  # Отступы: слева, сверху, справа, снизу
        spacing=dp(10),
        row_force_default=True,
        row_default_height=dp(30),  # Высота строки по умолчанию
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока выбора цвета
    color_title = Label(
        text='Application theme',
        color=(1, 1, 1, 1),
        font_size=Window.width * 0.04,  # Адаптивный размер шрифта
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        shorten=True,
        shorten_from='right',
        padding=(0, dp(5))
    )
    
    def update_color_title_size(*args):
        color_title.text_size = (Window.width - dp(40), None)
        color_title.texture_update()
    
    Window.bind(width=update_color_title_size)
    Clock.schedule_once(update_color_title_size)
    
    # Создаем экземпляр настроек цветов
    color_settings = ColorSettings(settings_window)
    
    # Сетка цветов (в один ряд)
    colors_grid = GridLayout(
        cols=6,
        spacing=dp(5),
        size_hint_y=None,
        height=dp(25)  # Фиксированная высота для строки с цветами
    )
    
    # Создаем кнопки цветов
    for color_name, color_tuple in color_settings.colors.items():
        color_button = ColorOption(
            color_name=color_name,
            color_value=color_tuple,
            text='',
            size_hint=(1, 1),
            background_normal=''
        )
        
        # Привязываем обработчик нажатия на кнопку
        color_button.bind(on_release=color_settings._on_color_button_press)
        
        # Сохраняем кнопку если это активный цвет
        if color_name == settings_window.initial_color:
            color_settings.active_button = color_button
            color_button.is_selected = True
            # Добавляем рамку к активной кнопке
            color_settings._add_border_to_button(color_button)
        
        colors_grid.add_widget(color_button)
    
    # Сохраняем ссылку на color_settings в settings_window для доступа из других методов
    settings_window.color_settings = color_settings
    
    # Собираем блок выбора цвета
    color_section.add_widget(color_title)  # Добавляем заголовок
    color_section.add_widget(colors_grid)  # Добавляем сетку цветов
    
    return color_section


# Экспортируем классы и функции для использования в других модулях
__all__ = [
    'ColorSettings',
    'ColorOption',
    'create_color_section',
    'get_color_tuple',
    'get_color_name'
]
