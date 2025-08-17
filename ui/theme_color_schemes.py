"""
Модуль для хранения цветовых схем приложения.
Содержит все предустановленные темы и их цветовые настройки.
"""

# Базовые цвета для удобства
COLORS = {
    'lime': (0.0, 1.0, 0.0, 1),
    'aqua': (0.0, 1.0, 1.0, 1),
    'blue': (0.0, 0.0, 1.0, 1),
    'red': (1.0, 0.0, 0.0, 1),
    'yellow': (1.0, 1.0, 0.0, 1),
    'white': (1.0, 1.0, 1.0, 1),
    'dark_goldenrod': (0.6, 0.5, 0.0, 1),
    'gray': (0.3, 0.3, 0.3, 1)
}

# Цветовые схемы для различных тем
COLOR_SCHEMES = {
    'lime': {
        'prayer_names': COLORS['red'],  # Названия молитв
        'prayer_times': COLORS['lime'],    # Время молитв
        'active_time': COLORS['lime'],     # Активное время (текущая молитва)
        'next_time': COLORS['lime'],       # Следующая молитва
        'countdown': COLORS['lime'],       # Счетчик времени до следующей молитвы
        'prayer_icons': COLORS['lime'],    # Иконки молитв
        'date_text': COLORS['lime'],       # Текст даты
        'separator': COLORS['lime']        # Разделители
    },
    'aqua': {
        'prayer_names': COLORS['red'],
        'prayer_times': COLORS['aqua'],
        'active_time': COLORS['aqua'],
        'next_time': COLORS['aqua'],
        'countdown': COLORS['aqua'],
        'prayer_icons': COLORS['aqua'],
        'date_text': COLORS['aqua'],
        'separator': COLORS['aqua']
    },
    'blue': {
        'prayer_names': COLORS['lime'],
        'prayer_times': COLORS['blue'],
        'active_time': COLORS['blue'],
        'next_time': COLORS['blue'],
        'countdown': COLORS['blue'],
        'prayer_icons': COLORS['blue'],
        'date_text': COLORS['blue'],
        'separator': COLORS['blue']
    },
    'red': {
        'prayer_names': COLORS['red'],
        'prayer_times': COLORS['red'],
        'active_time': COLORS['red'],
        'next_time': COLORS['red'],
        'countdown': COLORS['red'],
        'prayer_icons': COLORS['red'],
        'date_text': COLORS['red'],
        'separator': COLORS['red']
    },
    'yellow': {
        'prayer_names': COLORS['yellow'],
        'prayer_times': COLORS['yellow'],
        'active_time': COLORS['yellow'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['yellow'],
        'prayer_icons': COLORS['yellow'],
        'date_text': COLORS['yellow'],
        'separator': COLORS['yellow']
    },
    'white': {
        'prayer_names': COLORS['white'],
        'prayer_times': COLORS['white'],
        'active_time': COLORS['white'],
        'next_time': COLORS['white'],
        'countdown': COLORS['white'],
        'prayer_icons': COLORS['white'],
        'date_text': COLORS['white'],
        'separator': COLORS['white']
    }
}

def get_theme_scheme(theme_name):
    """Возвращает цветовую схему для указанной темы."""
    return COLOR_SCHEMES.get(theme_name, COLOR_SCHEMES['lime'])

def get_available_themes():
    """Возвращает список доступных тем."""
    return list(COLOR_SCHEMES.keys())
