"""
Модуль для работы с выпадающим списком выбора азана (Dropdown).
Содержит классы и функции для управления выпадающим списком выбора азана в настройках.
"""

from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock


def init_azan_dropdown(settings_window):
    """
    Инициализирует необходимые атрибуты для работы выпадающего списка азана.
    
    Args:
        settings_window: Экземпляр SettingsWindow
    """
    # Инициализируем атрибуты, если они еще не существуют
    if not hasattr(settings_window, 'selected_azan_dropdown'):
        settings_window.selected_azan_dropdown = 'Azan 1'
    
    # Создаем выпадающее меню, если оно еще не создано
    if not hasattr(settings_window, 'dropdown'):
        settings_window.dropdown = DropDown()
    
    # Инициализируем кнопку, если она еще не создана
    if not hasattr(settings_window, 'dropdown_btn'):
        settings_window.dropdown_btn = Button(
            text=settings_window.selected_azan_dropdown,
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )


def create_azan_dropdown_section(settings_window):
    """
    Создает секцию с выпадающим списком для выбора азана.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройкой выбора азана через DropDown
    """
    # Инициализируем необходимые атрибуты
    init_azan_dropdown(settings_window)
    
    # Секция выбора азана через DropDown
    dropdown_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Такая же высота, как у остальных блоков
        padding=[dp(20), dp(15), dp(20), dp(20)],
        spacing=dp(10),
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока с DropDown
    dropdown_title = Label(
        text='Azan (DropDown)',
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
    
    def update_dropdown_title_size(*args):
        dropdown_title.text_size = (Window.width - dp(40), None)
        dropdown_title.texture_update()
    
    Window.bind(width=update_dropdown_title_size)
    Clock.schedule_once(update_dropdown_title_size)
    
    # Очищаем старое выпадающее меню, если оно существует
    if hasattr(settings_window, 'dropdown'):
        settings_window.dropdown.clear_widgets()
    else:
        settings_window.dropdown = DropDown()
    
    # Создаем кнопки выбора азана
    for item in ['Azan 1', 'Azan 2', 'Azan 3']:
        btn = Button(
            text=item, 
            size_hint_y=None, 
            height=dp(40),
            background_color=(0.25, 0.25, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        btn.bind(on_release=lambda btn: settings_window.select_dropdown_item(btn.text))
        settings_window.dropdown.add_widget(btn)
    
    # Привязываем кнопку к выпадающему меню
    settings_window.dropdown_btn.bind(on_release=settings_window.dropdown.open)
    
    # Добавляем элементы в секцию
    dropdown_section.add_widget(dropdown_title)
    dropdown_section.add_widget(settings_window.dropdown_btn)
    
    return dropdown_section
