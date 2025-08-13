"""
Модуль для создания заголовка окна настроек.
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty


def _update_title_rect(instance, value, title_rect):
    """
    Обновляет позицию и размер фона заголовка.
    
    Args:
        instance: Виджет, к которому привязан обработчик
        value: Новое значение позиции/размера
        title_rect: Прямоугольник фона заголовка
    """
    title_rect.pos = instance.pos
    title_rect.size = instance.size


def create_header():
    """
    Создает и возвращает виджет заголовка окна настроек.
    
    Returns:
        tuple: Кортеж из (layout, title_rect) - контейнер заголовка и его фоновый прямоугольник
    """
    # Создаем контейнер для заголовка
    title_layout = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(30),
        padding=[dp(20), 0]
    )
    
    # Создаем фон заголовка
    title_rect = None
    with title_layout.canvas.before:
        Color(0.2, 0.2, 0.2, 1)
        title_rect = Rectangle(pos=title_layout.pos, size=title_layout.size)
    
    # Привязываем обновление позиции и размера фона
    title_layout.bind(
        pos=lambda instance, value: _update_title_rect(instance, value, title_rect),
        size=lambda instance, value: _update_title_rect(instance, value, title_rect)
    )
    
    # Создаем текстовую метку заголовка
    title_label = Label(
        text='SETTINGS',
        color=(1, 1, 1, 1),
        font_size='16sp',
        bold=True,
        halign='center',
        valign='center'
    )
    
    # Добавляем метку в контейнер
    title_layout.add_widget(title_label)
    
    return title_layout, title_rect
