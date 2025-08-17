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
    'gray': (0.7, 0.7, 0.7, 1)
}

# Цветовые схемы для различных тем
COLOR_SCHEMES = {
    'lime': {
        'prayer_names': COLORS['dark_goldenrod'],
        'prayer_times': COLORS['dark_goldenrod'],
        'active_time': COLORS['aqua'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    },
    'aqua': {
        'prayer_names': COLORS['dark_goldenrod'],
        'prayer_times': COLORS['dark_goldenrod'],
        'active_time': COLORS['lime'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    },
    'blue': {
        'prayer_names': COLORS['dark_goldenrod'],
        'prayer_times': COLORS['dark_goldenrod'],
        'active_time': COLORS['red'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    },
    'red': {
        'prayer_names': COLORS['dark_goldenrod'],
        'prayer_times': COLORS['dark_goldenrod'],
        'active_time': COLORS['red'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    },
    'yellow': {
        'prayer_names': COLORS['dark_goldenrod'],
        'prayer_times': COLORS['dark_goldenrod'],
        'active_time': COLORS['lime'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    },
    'white': {
        'prayer_names': COLORS['gray'],
        'prayer_times': COLORS['gray'],
        'active_time': COLORS['red'],
        'next_time': COLORS['yellow'],
        'countdown': COLORS['red']
    }
}

def get_theme_scheme(theme_name):
    """Возвращает цветовую схему для указанной темы."""
    return COLOR_SCHEMES.get(theme_name, COLOR_SCHEMES['lime'])

def get_available_themes():
    """Возвращает список доступных тем."""
    return list(COLOR_SCHEMES.keys())
