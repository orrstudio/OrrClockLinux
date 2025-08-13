"""
Модуль для создания заголовка окна настроек.
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import ObjectProperty


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
    def update_rect(instance, value):
        title_rect.pos = instance.pos
        title_rect.size = instance.size
    
    title_layout.bind(pos=update_rect, size=update_rect)
    
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
