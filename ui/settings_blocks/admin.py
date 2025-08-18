"""
Модуль для работы с админ-панелью.
Содержит классы и функции для управления отладочным режимом и другими настройками администратора.
"""

import logging
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import ListProperty

from ui.components.custom_switch import CustomSwitch
from ui.components.custom_button import RoundedButton
from .base import ResponsiveLabel

# Настройка логирования
logger = logging.getLogger(__name__)

class BorderedGridLayout(GridLayout):
    """GridLayout с границами и адаптивными линиями."""
    border_color = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*self.border_color)
            # Внешняя рамка
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

            # Вертикальные линии
            col1 = self.x + self.width * 0.4
            col2 = self.x + self.width * 0.7
            Line(points=[col1, self.y, col1, self.top], width=1)
            Line(points=[col2, self.y, col2, self.top], width=1)

def load_debug_state(settings_window):
    """Загружает состояние отладочного режима из базы данных."""
    try:
        from utils.logger import _get_debug_state
        return _get_debug_state()
    except Exception as e:
        logger.error(f'Ошибка при загрузке состояния отладочного режима: {e}')
        return False

def save_debug_state(settings_window, enabled):
    """Сохраняет состояние отладочного режима в базу данных."""
    try:
        from utils.logger import logger as app_logger
        from kivy.logger import Logger
        
        # Устанавливаем новое состояние отладки
        # Метод set_debug сам сохранит состояние в БД и обновит логгер
        app_logger.set_debug(enabled)
        
        # Выводим сообщение о результате
        status = 'Enabled' if enabled else 'Disabled'
        logger.info(f'Debug Mode: {status}')
        
    except Exception as e:
        Logger.error(f'Logger: Failed to update debug mode: {e}')
        # Пробуем сохранить состояние напрямую в БД на случай ошибки в логгере
        try:
            from data.database import SettingsDatabase
            db = SettingsDatabase()
            db.save_setting('debug_mode', '1' if enabled else '0')
            Logger.info('Logger: Debug mode value saved directly to the database')
        except Exception as db_error:
            logger.error(f'Критическая ошибка: не удалось сохранить состояние отладки: {db_error}')

def on_debug_switch(switch_instance, value, settings_window):
    """Обработчик изменения состояния переключателя отладочного режима."""
    # Только логируем изменение состояния, без сохранения
    status = 'Enabled' if value else 'Disabled'
    logger.info(f'Debug Mode: {status}')

def create_admin_section(settings_window):
    """
    Создает секцию с настройками админ-панели в виде таблицы.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройками админ-панели
    """
    # Основной контейнер секции
    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(210),  # Высота аналогична уведомлениям
        padding=(dp(30), dp(5), dp(30), dp(5)),
        spacing=dp(5)
    )
    
    # Таблица настроек
    table = BorderedGridLayout(
        cols=3,
        rows=3,
        size_hint_y=None,
        height=dp(150),
        spacing=0
    )
    
    # Настройка ширины столбцов
    def update_col_widths(*args):
        available_width = table.width
        table.cols_minimum = {
            0: available_width * 0.4,
            1: available_width * 0.3,
            2: available_width * 0.3
        }
    
    table.bind(size=update_col_widths)
    update_col_widths()
    
    # Данные для строк таблицы
    rows = [
        ("Debug Mode", 'debug_switch', 'debug_button'),
        ("Feature 2", 'feature2_switch', 'feature2_button'),
        ("Feature 3", 'feature3_switch', 'feature3_button')
    ]
    
    for text, switch_attr, button_attr in rows:
        # 1. Текст (слева по центру вертикально)
        label = Label(
            text=text,
            halign='left',
            valign='middle',
            font_size='22sp',
            bold=False,
            size_hint_x=0.8
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        
        # 2. Переключатель (по центру)
        if switch_attr == 'debug_switch':
            # Используем существующий переключатель для debug
            debug_enabled = load_debug_state(settings_window)
            switch = CustomSwitch(
                active=debug_enabled,
                size_hint=(None, None),
                size=(dp(64), dp(36)),
                thumb_color_active=[0, 1, 0, 1],
                thumb_color_inactive=[1, 0, 0, 1],
                track_color_active=[0.15, 0.3, 0.15, 1],
                track_color_inactive=[0.2, 0.1, 0.1, 1]
            )
            switch.bind(active=lambda instance, value: on_debug_switch(instance, value, settings_window))
            settings_window.debug_switch = switch
        else:
            # Пустой виджет для остальных строк
            switch = Widget()
        
        # 3. Кнопка (по центру)
        if button_attr == 'debug_button':
            button = RoundedButton(
                text='Настройки',
                size_hint=(None, None),
                size=(dp(120), dp(40)),
                font_size='16sp',
                background_color=(0.2, 0.6, 0.8, 1)
            )
            # Здесь можно добавить обработчик нажатия на кнопку
            # button.bind(on_press=...)
        else:
            # Пустой виджет для остальных строк
            button = Widget()
        
        # Добавляем элементы в таблицу
        table.add_widget(label)
        table.add_widget(switch)
        table.add_widget(button)
    
    # Добавляем таблицу в контейнер
    container.add_widget(table)
    
    # Сохраняем ссылку на секцию для доступа из других методов
    settings_window.admin_section = container
    
    return container
