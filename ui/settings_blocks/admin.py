"""
Модуль для работы с админ-панелью.
Содержит классы и функции для управления отладочным режимом и другими настройками администратора.
"""

import logging
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window

from .base import ResponsiveLabel

# Настройка логирования
logger = logging.getLogger(__name__)

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
    Создает секцию с настройками админ-панели.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройками админ-панели
    """
    # Секция админ-панели
    admin_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Такая же высота, как у других блоков
        padding=[dp(20), dp(15), dp(20), dp(20)],
        spacing=dp(10),
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока
    admin_title = Label(
        text='Admin Panel',
        color=(1, 1, 1, 1),
        font_size=sp(22),
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        padding=(0, dp(5)),
        shorten=True,
        shorten_from='right'
    )
    
    def update_admin_title_size(*args):
        admin_title.text_size = (Window.width - dp(40), None)
        admin_title.texture_update()
    
    Window.bind(width=update_admin_title_size)
    Clock.schedule_once(update_admin_title_size)
    
    # Контейнер для элементов управления (3 колонки по 1/3 ширины)
    controls_layout = GridLayout(
        cols=3,
        size_hint_y=None,
        height=dp(40),
        spacing=dp(10)
    )
    
    # Загружаем текущее состояние отладочного режима
    debug_enabled = load_debug_state(settings_window)
    
    # Метка (1/3 ширины) с переносом текста
    switch_label = ResponsiveLabel(
        text='Debug mode:',
        markup=True
    )
    
    # Переключатель (1/3 ширины)
    settings_window.debug_switch = Switch(
        active=debug_enabled,
        size_hint_x=1/3
    )
    
    # Пустой виджет для выравнивания (1/3 ширины)
    empty_widget = Widget(size_hint_x=1/3)
    
    # Привязываем обработчик события изменения состояния переключателя
    # Обработчик только логирует изменение, сохранение будет при нажатии кнопки "Сохранить"
    settings_window.debug_switch.bind(active=lambda instance, value: on_debug_switch(instance, value, settings_window))
    
    # Добавляем виджеты в контейнер
    controls_layout.add_widget(switch_label)
    controls_layout.add_widget(settings_window.debug_switch)
    controls_layout.add_widget(empty_widget)
    
    # Добавляем виджеты в секцию
    admin_section.add_widget(admin_title)
    admin_section.add_widget(controls_layout)
    
    # Сохраняем ссылку на секцию для доступа из других методов
    settings_window.admin_section = admin_section
    
    return admin_section
