"""
Модуль с общими утилитами и хелперами для настроек.
"""
from kivy.graphics import Color, Line
from kivy.metrics import dp, sp
from kivy.clock import Clock
from functools import wraps
import logging

# Настройка логгера для модуля
logger = logging.getLogger(__name__)

def add_border(widget, border_color=(1, 1, 1, 1), border_width=1.5):
    """
    Добавляет рамку к виджету.
    
    Args:
        widget: Виджет, к которому добавляется рамка
        border_color: Цвет рамки в формате RGBA
        border_width: Толщина рамки в пикселях
        
    Returns:
        Функция для обновления рамки при изменении размера/позиции
    """
    def update_border(instance, value):
        """Обновляет позицию и размер рамки."""
        if hasattr(instance, 'border_line'):
            instance.border_line.rectangle = (
                instance.x, 
                instance.y, 
                instance.width, 
                instance.height
            )
    
    # Очищаем предыдущие отрисовки
    widget.canvas.after.clear()
    
    # Рисуем рамку
    with widget.canvas.after:
        Color(*border_color)
        widget.border_line = Line(
            rectangle=(
                widget.x, 
                widget.y, 
                widget.width, 
                widget.height
            ), 
            width=border_width
        )
    
    # Привязываем обновление рамки к изменению размера/позиции
    widget.bind(pos=update_border, size=update_border)
    
    return update_border

def print_sizes(db, show_before_save=False):
    """
    Выводит отладочную информацию о настройках приложения.
    
    Args:
        db: Объект базы данных настроек
        show_before_save (bool): Если True, показывает настройки перед сохранением
    """
    return print_debug_info(db, show_before_save)


def print_debug_info(db, show_before_save=False):
    """
    Выводит отладочную информацию о настройках приложения.
    
    Args:
        db: Объект базы данных настроек
        show_before_save: Если True, показывает настройки перед сохранением
    """
    return True


# Экспортируемые функции
__all__ = [
    'add_border',
    'print_debug_info',
    'print_sizes'
]
