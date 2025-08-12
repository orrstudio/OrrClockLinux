"""
Модуль для работы с настройками уведомлений.
Содержит классы и функции для управления настройками уведомлений в приложении.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window

from .base import ResponsiveLabel


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
        text='Аудио уведомления',
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
        text='Включить уведомления:',
        markup=True
    )
    
    # Переключатель (1/3 ширины)
    settings_window.audio_switch = Switch(
        active=False,
        size_hint_x=1/3
    )
    
    # Кнопка (1/3 ширины)
    settings_window.audio_button = Button(
        text='Настройки',
        size_hint_x=1/3,
        background_color=(0.3, 0.3, 0.3, 1),
        color=(1, 1, 1, 1)
    )
    
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
