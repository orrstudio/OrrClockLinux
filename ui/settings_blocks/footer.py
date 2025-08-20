"""
Модуль для создания нижней панели с кнопками окна настроек.
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp

# Импортируем пользовательские компоненты
from ui.settings_blocks.base import CustomButton


def _update_bottom_rect(instance, value, bottom_rect):
    """
    Обновляет позицию и размер фона нижней панели.
    
    Args:
        instance: Виджет, к которому привязан обработчик
        value: Новое значение позиции/размера
        bottom_rect: Прямоугольник фона нижней панели
    """
    bottom_rect.pos = instance.pos
    bottom_rect.size = instance.size


def create_footer(dismiss_callback, accept_callback):
    """
    Создает и возвращает виджет нижней панели с кнопками.
    
    Args:
        dismiss_callback: Функция, вызываемая при нажатии кнопки отмены
        accept_callback: Функция, вызываемая при нажатии кнопки принятия
        
    Returns:
        tuple: Кортеж из (bottom_panel, bottom_rect) - контейнер панели и его фоновый прямоугольник
    """
    # Стили для кнопок
    button_style = {
        'size_hint_x': 0.5,
        'size_hint_y': None,
        'height': dp(50),
        'font_size': sp(22)
    }
    
    # Создаем контейнер для нижней панели
    bottom_panel = GridLayout(
        cols=2,
        size_hint_y=None,
        height=dp(60),
        spacing=dp(10),
        padding=[dp(20), dp(5)]
    )
    
    # Создаем фон для нижней панели
    bottom_rect = None
    with bottom_panel.canvas.before:
        Color(0.2, 0.2, 0.2, 1) # Цвет фона
        bottom_rect = Rectangle(pos=bottom_panel.pos, size=bottom_panel.size)
    
    # Привязываем обновление фона при изменении размера/позиции
    bottom_panel.bind(
        pos=lambda instance, value: _update_bottom_rect(instance, value, bottom_rect),
        size=lambda instance, value: _update_bottom_rect(instance, value, bottom_rect)
    )

    # Создаем кнопку принятия
    accept_button = CustomButton(
        icon_path='fonts/Awesome/use/ok.png',
        text="",  # Убираем текст, используем только иконку
        background_color=(0.1, 0.5, 0.8, 1),  # Синий цвет
        **button_style
    )

    # Создаем кнопку отмены
    cancel_button = CustomButton(
        icon_path='fonts/Awesome/use/x.png',
        text="",  # Убираем текст, используем только иконку
        background_color=(0.8, 0.2, 0.2, 1),  # Красный цвет
        **button_style
    )
    
    # Привязываем обработчики событий
    accept_button.bind(on_release=accept_callback)
    cancel_button.bind(on_release=dismiss_callback)

    
    # Добавляем кнопки на панель
    bottom_panel.add_widget(accept_button)
    bottom_panel.add_widget(cancel_button)

    
    return bottom_panel, bottom_rect
