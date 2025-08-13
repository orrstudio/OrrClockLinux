"""
Модуль для управления настройками и поведением окна настроек.
"""
from kivy.metrics import dp
from kivy.core.window import Window


def apply_window_settings(settings_window):
    """
    Применяет сохраненные настройки окна после его полной инициализации.
    
    Args:
        settings_window: Экземпляр окна настроек
    """
    if hasattr(settings_window, 'db'):
        # Получаем текущие настройки окна из базы данных
        settings = settings_window.db.get_settings_window_settings()
        if settings:
            width, height, x, y = settings
            
            # Устанавливаем размеры окна
            Window.size = (width, height)
            
            # Устанавливаем позицию окна
            Window.left = x
            Window.top = y
            
            # Принудительно обновляем окно
            Window.update_viewport()


def on_window_resize(settings_window, instance, width, height):
    """
    Обновляет размеры окна при изменении размера экрана.
    
    Args:
        settings_window: Экземпляр окна настроек
        instance: Экземпляр виджета, вызвавшего событие
        width: Новая ширина окна
        height: Новая высота окна
    """
    settings_window.width = min(dp(400), width * 0.95)
    settings_window.height = min(dp(500), height * 0.95)


def save_window_settings(settings_window):
    """
    Сохраняет текущие настройки окна в базу данных.
    
    Args:
        settings_window: Экземпляр окна настроек
    """
    if not hasattr(settings_window, 'db') or not hasattr(Window, 'width'):
        return
        
    # Получаем текущую позицию окна
    x, y = Window.left, Window.top
    
    # Сохраняем настройки окна
    settings_window.db.save_settings_window_settings(
        width=Window.width,
        height=Window.height,
        x=x,
        y=y
    )
