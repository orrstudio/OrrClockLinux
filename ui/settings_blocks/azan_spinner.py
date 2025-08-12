"""
Модуль для работы с выпадающим списком выбора азана (Spinner).
Содержит классы и функции для управления выбором азана в настройках.
"""

from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


def create_azan_spinner_section(settings_window):
    """
    Создает секцию с выпадающим списком для выбора азана.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройкой выбора азана
    """
    # Секция выбора азана
    azan_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Такая же высота, как у остальных блоков
        padding=[dp(20), dp(15), dp(20), dp(20)],
        spacing=dp(10),
        row_force_default=True,
        row_default_height=dp(30),  # Высота строки по умолчанию
        size_hint=(1, None)
    )
    
    # Заголовок блока выбора азана
    azan_title = Label(
        text='Настройка азанов',
        color=(1, 1, 1, 1),
        font_size=Window.width * 0.04,  # Адаптивный размер шрифта
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        padding=(0, dp(5)),
        shorten=True,
        shorten_from='right'
    )
    
    def update_azan_title_size(*args):
        azan_title.text_size = (Window.width - dp(40), None)
        azan_title.texture_update()
    
    Window.bind(width=update_azan_title_size)
    Clock.schedule_once(update_azan_title_size)
    
    # Выпадающий список для выбора азана
    azan_spinner = Spinner(
        text='Azan 1',
        values=('Azan 1', 'Azan 2', 'Azan 3'),
        size_hint_y=None,
        height=dp(40),
        background_color=(0.3, 0.3, 0.3, 1),
        color=(1, 1, 1, 1),
        font_size=sp(18)
    )
    
    # Обработчик выбора значения
    azan_spinner.bind(text=settings_window.on_azan_selected)
    
    # Добавляем виджеты в секцию
    azan_section.add_widget(azan_title)
    azan_section.add_widget(azan_spinner)
    
    # Сохраняем ссылку на спиннер для последующего обновления
    settings_window.azan_spinner = azan_spinner
    
    return azan_section


def on_azan_selected(instance, text):
    """
    Обработчик выбора азана в Spinner.
    
    Args:
        instance: Экземпляр Spinner
        text: Выбранное значение
    """
    if hasattr(instance, 'settings_window'):
        instance.settings_window.selected_azan_spinner = text
