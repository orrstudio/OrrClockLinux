import logging
import platform
from kivy.core.window import Window
from kivy.utils import platform as kivy_platform
import subprocess
import json

def get_monitor_info():
    """
    Возвращает базовую информацию о размере экрана
    """
    return [{
        'id': 0,
        'name': 'Screen',
        'width': Window.system_size[0],
        'height': Window.system_size[1],
        'x': Window.left,
        'y': Window.top,
        'is_primary': True
    }]

def find_current_monitor():
    """
    Возвращает текущий монитор (всегда один)
    """
    return get_monitor_info()[0]

def get_window_info():
    """
    Возвращает текущие координаты и размеры окна
    """
    return {
        'x': Window.left,
        'y': Window.top,
        'width': Window.width,
        'height': Window.height
    }

def is_mobile_device():
    """
    Проверяет, является ли устройство мобильным
    """
    return platform in ('android', 'ios')
