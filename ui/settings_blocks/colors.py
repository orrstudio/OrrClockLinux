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
from datetime import datetime

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
        self.background_color = (0, 0, 0, 1)  # Черный фон как у часов
        self.size_hint = (1, None)
        self.size_hint_y = None
        self.height = 0  # Будет установлено при обновлении размера
        self.border = (0, 0, 0, 0)  # Убираем стандартную границу
        self.padding = [0, 0]
        self._update_time()  # Устанавливаем текущее время
        self.font_name = 'fonts/DSEG-Classic/DSEG7Classic-Bold.ttf'  # Шрифт как у часов
        self.font_size = 24  # Начальный размер шрифта в пикселях
        self.color = self.color_value  # Цвет текста будет соответствовать выбранному цвету
        self.bold = True  # Жирный шрифт
        self.halign = 'center'  # Выравнивание по центру
        self.valign = 'middle'  # Выравнивание по вертикали по центру
        self.markup = True  # Включаем поддержку разметки
        self.text_size = (None, None)  # Снимаем ограничения на размер текста
        self.shorten = False  # Отключаем укорачивание текста
        self.bind(color_value=self.update_color)
        self.bind(is_selected=self.update_border)
        self.bind(pos=self._update_border_pos, size=self._update_border_size)
        self.bind(width=self._update_size)
        self.bind(height=self._update_size)
        self.bind(texture_size=self._adjust_font_size)
        
        # Запускаем таймер для обновления времени каждую секунду
        self._clock_event = Clock.schedule_interval(lambda dt: self._update_time(), 1)
        # Инициализируем размер шрифта после загрузки всех свойств
        Clock.schedule_once(lambda dt: self._adjust_font_size())
        
    def _update_time(self):
        """Обновляет отображаемое время на текущее."""
        current_time = datetime.now().strftime('%H:%M')
        if self.text != current_time:  # Обновляем только если время изменилось
            self.text = current_time
        return True
        
    def _adjust_font_size(self, *args):
        # Пропускаем, если размеры еще не установлены
        if not hasattr(self, 'width') or self.width == 0 or not hasattr(self, 'height') or self.height == 0:
            return
            
        # Получаем текстуру текста
        texture = self.texture
        if not texture or texture.width == 0:
            return
            
        # Вычисляем коэффициенты масштабирования по ширине и высоте
        width_ratio = (self.width * 0.9) / texture.width
        height_ratio = (self.height * 0.9) / texture.height
        
        # Выбираем минимальный коэффициент, чтобы текст поместился по обоим измерениям
        scale = min(width_ratio, height_ratio)
        
        # Устанавливаем новый размер шрифта
        new_size = int(self.font_size * scale)
        
        # Ограничиваем минимальный и максимальный размер шрифта
        min_size = 10
        max_size = min(100, int(min(self.width, self.height) * 0.9))
        new_size = max(min_size, min(new_size, max_size))
        
        # Обновляем размер шрифта, если он изменился
        if abs(new_size - self.font_size) > 1:
            self.font_size = new_size
            
    def _update_size(self, instance, value):
        # Устанавливаем высоту равной половине ширины
        if instance == self and hasattr(self, 'width'):
            self.height = self.width * 0.5
            
        # Обновляем размер шрифта при изменении размера кнопки
        self._adjust_font_size()
        
    def update_color(self, instance, value):
        # Устанавливаем цвет текста в соответствии с выбранным цветом
        self.color = value
        
    def _update_border_pos(self, *args):
        # Обновляем позицию рамки при изменении позиции кнопки
        if hasattr(self, '_border'):
            self._border.rectangle = (self.x, self.y, self.width, self.height)
            
    def _update_border_size(self, *args):
        # Обновляем размер рамки при изменении размера кнопки
        if hasattr(self, '_border'):
            self._update_border_pos()
        
    def update_border(self, instance, value):
        self.canvas.after.clear()  # Очищаем предыдущую рамку
        
        if value:  # Если кнопка выбрана
            with self.canvas.after:  # Используем after для отрисовки поверх кнопки
                Color(0.7, 0.7, 0.7, 1)  # Серый цвет рамки
                # Рисуем рамку с отступом
                border_width = 6  # Толщина рамки
                self._border = Line(
                    rectangle=(
                        self.x + border_width/2,
                        self.y + border_width/2,
                        self.width - border_width,
                        self.height - border_width
                    ),
                    width=border_width
                )


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
        height=dp(350),  # Увеличиваем высоту для размещения 3 строк с кнопками
        padding=[dp(20), dp(15), dp(20), dp(20)],  # Отступы: слева, сверху, справа, снизу
        spacing=dp(10),
        row_force_default=False,
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока выбора цвета
    color_title = Label(
        text='Application theme',  # Добавлены пробелы для отступа слева
        color=(1, 1, 1, 1),
        font_size=Window.width * 0.04,  # Адаптивный размер шрифта
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        shorten=True,
        shorten_from='right',
        padding=(dp(25), dp(5))  # Отступы: слева, сверху
    )
    
    def update_color_title_size(*args):
        color_title.text_size = (Window.width - dp(40), None)
        color_title.texture_update()
    
    Window.bind(width=update_color_title_size)
    Clock.schedule_once(update_color_title_size)
    
    # Создаем экземпляр настроек цветов
    color_settings = ColorSettings(settings_window)
    
    # Сетка цветов (2 колонки, 3 строки)
    colors_grid = GridLayout(
        cols=2,  # Две колонки
        spacing=dp(10),  # Отступы между кнопками
        size_hint_y=None,
        height=dp(300),  # Примерная высота, будет пересчитана
        row_force_default=False,
        row_default_height=dp(100),  # Примерная высота строки
        padding=[0, dp(5), 0, dp(5)]  # Отступы сверху и снизу
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
    
    # Добавляем разделитель перед блоком темы фона (но после всех кнопок цветов)
    from kivy.uix.widget import Widget
    separator = Widget(size_hint_y=None, height=1)
    with separator.canvas:
        Color(0.5, 0.5, 0.5, 0.5)  # Серый полупрозрачный цвет
        separator.rect = Line(points=[0, 0, Window.width, 0])
    
    def update_separator(instance, value):
        separator.rect.points = [0, 0, value, 0]
    
    Window.bind(width=update_separator)
    
    # Добавляем отступ перед разделителем, чтобы он не прилипал к кнопкам
    color_section.add_widget(Widget(size_hint_y=None, height=dp(220)))
    
    # Добавляем заголовок Background
    background_title = Label(
        text='Background',
        color=(1, 1, 1, 1),
        font_size=Window.width * 0.04,  # Адаптивный размер шрифта
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        shorten=True,
        shorten_from='right',
        padding=(dp(25), dp(5))  # Отступы: слева, сверху
    )
    color_section.add_widget(background_title)
    
    # Создаем блок для переключателя темы фона
    background_theme_layout = GridLayout(
        cols=2,
        spacing=dp(10),  # Отступы между кнопками
        size_hint_y=None,
        height=dp(30),
        row_force_default=False,
        row_default_height=dp(100),  # Примерная высота строки
        padding=[0, dp(5), 0, dp(5)]  # Отступы сверху и снизу
    )
    
    # Добавляем метку "Light" для переключателя темы фона
    background_label = Label(
        text='Light',
        color=(1, 1, 1, 1),
        font_size=dp(16),
        size_hint=(1, 1),
        halign='left',
        valign='middle',
        text_size=(None, None),
        padding=(dp(15), dp(5)),  # Такие же отступы, как у кнопок темы
        bold=False
    )
    
    # Контейнер для переключателя с выравниванием по правому краю
    switch_container = GridLayout(
        cols=1,
        size_hint=(None, 1),
        width=dp(60),  # Фиксированная ширина для переключателя
        padding=(0, 0, dp(15), 0)  # Отступ справа как у кнопок темы
    )
    
    # Добавляем кастомный переключатель
    from ui.components.custom_switch import CustomMDSwitch
    background_switch = CustomMDSwitch(
        width=dp(64),  # Ширина как в уведомлениях
        height=dp(36),  # Высота как в уведомлениях
        thumb_padding=dp(4),  # Отступ ползунка
        thumb_color_active=[0, 1, 0, 1],  # Ярко-зеленый при включении
        thumb_color_inactive=[1, 0, 0, 1]  # Ярко-красный при выключении
    )
    
    # Добавляем переключатель в контейнер
    switch_container.add_widget(background_switch)
    
    # Добавляем виджеты в основной layout
    background_theme_layout.add_widget(background_label)
    background_theme_layout.add_widget(switch_container)
    
    # Добавляем блок темы фона в конец секции
    color_section.add_widget(background_theme_layout)
    
    # Привязываем обновление размера шрифта метки при изменении размера окна
    def update_background_label_size(instance, value):
        background_label.font_size = Window.width * 0.04
    
    Window.bind(width=update_background_label_size)
    Clock.schedule_once(lambda dt: update_background_label_size(None, None))
    
    return color_section


# Экспортируем классы и функции для использования в других модулях
__all__ = [
    'ColorSettings',
    'ColorOption',
    'create_color_section',
    'get_color_tuple',
    'get_color_name'
]
