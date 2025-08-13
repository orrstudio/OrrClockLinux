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
        logger.info(f'Settings: Voice notifications switch state: {enabled}')
    except Exception as e:
        logger.error(f'Ошибка при сохранении настроек уведомлений: {e}')

def on_notification_switch(switch_instance, value, settings_window):
    """Обработчик изменения состояния переключателя уведомлений."""
    try:
        # Сохраняем новое состояние
        save_notification_settings(settings_window, value)
        
        # Здесь можно добавить дополнительную логику при включении/выключении уведомлений
        if value:
            logger.info('Settings: Voice notifications enabled')
        else:
            logger.info('Settings: Voice notifications disabled')
    except Exception as e:
        logger.error(f'Ошибка при обработке изменения состояния уведомлений: {e}')

def show_notification_settings(instance):
    """Показывает всплывающее окно с настройками уведомлений."""
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    
    # Заголовок
    title_label = Label(
        text='Notifications settings',
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
        text='Close',
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
    # Блок уведомлений
    audio_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(200),  # Увеличиваем высоту для лучшего отображения
        padding=[dp(20), dp(15), dp(20), dp(15)],  # Увеличиваем горизонтальные отступы
        spacing=dp(15),  # Увеличиваем отступ между элементами
        size_hint=(0.95, None),  # Уменьшаем ширину блока для отступов по бокам
        pos_hint={'center_x': 0.5}  # Центрируем блок
    )
    
    # Добавляем фон для всей секции
    with audio_section.canvas.before:
        from kivy.graphics import Color, RoundedRectangle
        Color(0.15, 0.15, 0.15, 1)  # Темно-серый фон
        audio_section.rect = RoundedRectangle(
            size=audio_section.size,
            pos=audio_section.pos,
            radius=[(10, 10), (10, 10), (10, 10), (10, 10)]
        )
    
    # Обновляем размер и позицию фона при изменении размера секции
    def update_rect(instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    audio_section.bind(pos=update_rect, size=update_rect)
    
    # Заголовок блока
    audio_title = Label(
        text='Notifications',
        font_size='14sp',
        size_hint_y=None,
        height=dp(35),
        color=(0.8, 0.8, 0.8, 1),
        bold=True,
        halign='left',
        padding=(0, dp(5)),
        shorten=True,
        shorten_from='right'
    )
    
    def update_audio_title_size(*args):
        audio_title.text_size = (Window.width - dp(40), None)
        audio_title.texture_update()
    
    Window.bind(width=update_audio_title_size)
    Clock.schedule_once(update_audio_title_size)
    
    # Контейнер для всех строк уведомлений
    notifications_container = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        height=dp(120),  # Высота под 3 строки с отступами
        spacing=dp(10)
    )
    
    # Функция для создания строки уведомления
    def create_notification_row(label_text, switch_active, switch_prop, button_prop, switch_handler=None, button_handler=None):
        # Контейнер для элементов управления
        row_layout = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(25),  # Фиксированная высота строки
            spacing=dp(5),  # 5% отступа между колонками
            padding=[dp(5), dp(5)]  # Отступы слева/справа и сверху/снизу
        )
        
        # Метка с названием (30% ширины)
        label = Label(
            text=label_text,
            size_hint_x=0.3,  # 30% ширины для метки
            size_hint_min_x=dp(100),  # Минимальная ширина метки
            font_size='18sp',  # Увеличиваем размер шрифта
            halign='left',
            valign='middle',
            text_size=(Window.width * 0.25, None),  # Фиксированная ширина текстового блока
            padding_x=dp(5)
        )
        
        # Переключатель (30% ширины)
        switch = Switch(
            active=switch_active,
            pos_hint={'center_y': 0.5}  # Выравнивание по вертикали
        )
        
        # Кнопка настроек (30% ширины)
        button = Button(
            text='Settings',
            size_hint_x=0.2,  # Ширина кнопки
            background_color=(0.2, 0.5, 0.8, 1) if button_handler else (0.3, 0.3, 0.3, 0.5),
            color=(1, 1, 1, 1),
            disabled=button_handler is None,
            font_size='18sp',

        )
        
        # Сохраняем ссылки в settings_window
        setattr(settings_window, switch_prop, switch)
        setattr(settings_window, button_prop, button)
        
        # Привязываем обработчики, если они предоставлены
        if switch_handler:
            switch.bind(active=switch_handler)
        if button_handler:
            button.bind(on_release=button_handler)
        
        # Добавляем виджеты в строку
        row_layout.add_widget(label)
        row_layout.add_widget(switch)
        row_layout.add_widget(button)
        
        return row_layout
    
    # Создаем строки уведомлений
    audio_row = create_notification_row(
        'Voice:',
        load_notification_settings(settings_window),
        'audio_switch',
        'audio_button',
        lambda instance, value: on_notification_switch(instance, value, settings_window),
        show_notification_settings
    )
    
    visual_row = create_notification_row(
        'Visual:',
        False,
        'visual_switch',
        'visual_button'
    )
    
    # Создаем строку для уведомлений Азан
    azan_row = create_notification_row(
        'Adhan:',
        False,  # По умолчанию выключены
        'azan_switch',
        'azan_button'
    )
    
    # Добавляем все виджеты в секцию
    audio_section.add_widget(audio_title)
    audio_section.add_widget(audio_row)
    audio_section.add_widget(visual_row)
    audio_section.add_widget(azan_row)
    
    # Увеличиваем высоту секции в зависимости от количества строк
    audio_section.height = dp(180)  # Базовая высота + высота строк
    
    # Сохраняем ссылку на секцию для доступа из других методов
    settings_window.notifications_section = audio_section
    
    return audio_section
