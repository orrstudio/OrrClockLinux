"""
Модуль для работы с настройками уведомлений.
Содержит классы и функции для управления настройками уведомлений в приложении.
"""

import logging
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window

from .base import ResponsiveLabel

# Настройка логирования
logger = logging.getLogger(__name__)


def load_notification_settings(settings_window):
    """Загружает настройки уведомлений из базы данных."""
    try:
        # Загружаем состояние уведомлений из базы данных
        notifications_enabled = settings_window.db.get_setting('notifications_enabled')
        
        # Преобразуем строковое значение в булево
        if notifications_enabled is not None:
            notifications_enabled = notifications_enabled.lower() == 'true'
        else:
            # Значение по умолчанию, если настройка не найдена
            notifications_enabled = False
            # Сохраняем значение по умолчанию в базу данных
            settings_window.db.save_setting('notifications_enabled', 'false')
        
        return notifications_enabled
    except Exception as e:
        logger.error(f'Ошибка при загрузке настроек уведомлений: {e}')
        return False

def save_notification_settings(settings_window, enabled):
    """Сохраняет настройки уведомлений в базу данных."""
    try:
        settings_window.db.save_setting('notifications_enabled', str(enabled).lower())
        logger.info(f'Настройки уведомлений сохранены: {enabled}')
    except Exception as e:
        logger.error(f'Ошибка при сохранении настроек уведомлений: {e}')

def on_notification_switch(switch_instance, value, settings_window):
    """Обработчик изменения состояния переключателя уведомлений."""
    try:
        # Сохраняем новое состояние
        save_notification_settings(settings_window, value)
        
        # Здесь можно добавить дополнительную логику при включении/выключении уведомлений
        if value:
            logger.info('Уведомления включены')
        else:
            logger.info('Уведомления выключены')
    except Exception as e:
        logger.error(f'Ошибка при обработке изменения состояния уведомлений: {e}')

def show_notification_settings(instance):
    """Показывает всплывающее окно с настройками уведомлений."""
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    
    # Заголовок
    title_label = Label(
        text='Настройки уведомлений',
        size_hint_y=None,
        height=dp(40),
        font_size=sp(20),
        color=(1, 1, 1, 1)
    )
    
    # Содержимое настроек
    settings_content = BoxLayout(orientation='vertical', spacing=dp(10))
    
    # Здесь можно добавить дополнительные настройки уведомлений
    # Например, выбор звука, вибрации и т.д.
    
    # Кнопка закрытия
    close_btn = Button(
        text='Закрыть',
        size_hint_y=None,
        height=dp(50),
        background_color=(0.3, 0.3, 0.3, 1)
    )
    
    popup = Popup(
        title='',
        content=content,
        size_hint=(0.8, 0.6),
        background='',
        background_color=(0.1, 0.1, 0.1, 0.95)
    )
    
    close_btn.bind(on_release=popup.dismiss)
    
    content.add_widget(title_label)
    content.add_widget(settings_content)
    content.add_widget(close_btn)
    
    popup.open()


def create_notifications_section(settings_window):
    """
    Создает секцию с настройками уведомлений.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройками уведомлений
    """
    # Блок аудио уведомлений
    audio_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Такая же высота, как у других блоков
        padding=[dp(20), dp(15), dp(20), dp(20)],
        spacing=dp(10),
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока
    audio_title = Label(
        text='Уведомления',
        color=(1, 1, 1, 1),
        font_size=sp(22),  # Используем sp для масштабирования шрифта
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        padding=(0, dp(5)),
        shorten=True,
        shorten_from='right'
    )
    
    def update_audio_title_size(*args):
        audio_title.text_size = (Window.width - dp(40), None)
        audio_title.texture_update()
    
    Window.bind(width=update_audio_title_size)
    Clock.schedule_once(update_audio_title_size)
    
    # Контейнер для элементов управления (3 колонки по 1/3 ширины)
    controls_layout = GridLayout(
        cols=3,
        size_hint_y=None,
        height=dp(40),
        spacing=dp(10)
    )
    
    # Метка (1/3 ширины) с переносом текста
    switch_label = ResponsiveLabel(
        text='Аудио уведомления:',
        markup=True
    )
    
    # Загружаем текущее состояние уведомлений
    notifications_enabled = load_notification_settings(settings_window)
    
    # Переключатель (1/3 ширины)
    settings_window.audio_switch = Switch(
        active=notifications_enabled,
        size_hint_x=1/3
    )
    
    # Кнопка (1/3 ширины)
    settings_window.audio_button = Button(
        text='Настройки',
        size_hint_x=1/3,
        background_color=(0.3, 0.3, 0.3, 1),
        color=(1, 1, 1, 1)
    )
    
    # Привязываем обработчики событий
    settings_window.audio_switch.bind(active=lambda instance, value: on_notification_switch(instance, value, settings_window))
    settings_window.audio_button.bind(on_release=show_notification_settings)
    
    # Добавляем виджеты в контейнер
    controls_layout.add_widget(switch_label)
    controls_layout.add_widget(settings_window.audio_switch)
    controls_layout.add_widget(settings_window.audio_button)
    
    # Добавляем виджеты в секцию
    audio_section.add_widget(audio_title)
    audio_section.add_widget(controls_layout)
    
    # Сохраняем ссылку на секцию для доступа из других методов
    settings_window.notifications_section = audio_section
    
    return audio_section
