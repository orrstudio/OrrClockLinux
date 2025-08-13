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
    def print_separator():
        """Печатает разделитель."""
        logger.info("=" * 37)
        
    def print_header(title):
        """Печатает заголовок секции."""
        logger.info(f"| {title.center(34)}|")
        logger.info("-" * 37)
        
    def print_row(label, value1, value2):
        """Печатает строку с двумя значениями."""
        logger.info(f"| {label.ljust(16)}|{str(value1).center(8)}|{str(value2).center(8)}|")
        
    def print_single_row(label, value):
        """Печатает строку с одним значением."""
        logger.info(f"| {label.ljust(16)}| {str(value).center(16)}|")
    
    try:
        # Раздел: Главное окно
        print_separator()
        print_header("App Window")
        try:
            main_settings = db.get_window_settings()
            if main_settings:
                width, height, x, y = main_settings
                print_row("Size", int(width), int(height))
                print_row("Position", int(x), int(y))
            else:
                logger.info("| No data found" + " " * 21 + "|")
        except Exception as e:
            logger.error(f"| Error: {str(e)[:25]}" + " " * (36 - 9 - len(str(e)[:25])) + "|")
        
        # Раздел: Окно настроек
        print_separator()
        print_header("Settings Window")
        try:
            settings = db.get_settings_window_settings()
            if settings:
                width, height, x, y = settings
                print_row("Size", int(width), int(height))
                print_row("Position", int(x), int(y))
            else:
                logger.info("| No data found" + " " * 21 + "|")
        except Exception as e:
            logger.error(f"| Error: {str(e)[:25]}" + " " * (36 - 9 - len(str(e)[:25])) + "|")
        
        # Раздел: Тема
        print_separator()
        theme = db.get_setting('color', 'Not set')
        print_single_row("Theme", theme.capitalize() if theme else "Not set")
        
        # Раздел: Отладочный режим
        print_separator()
        debug_mode = db.get_setting('debug_mode', '0')
        print_single_row("Debug Mode", "ENABLE" if debug_mode == '1' else "DISABLE")
        
        # Раздел: Данные из базы
        try:
            from logic.prayer_times import prayer_times_manager
            from datetime import datetime, timedelta
            
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            date_format = "%Y-%m-%d"
            today_str = today.strftime(date_format)
            tomorrow_str = tomorrow.strftime(date_format)
            
            cursor = prayer_times_manager.db.connection.cursor()
            cursor.execute('''
                SELECT * FROM prayer_times 
                WHERE date = ? OR date = ?
                ORDER BY date ASC
            ''', (today_str, tomorrow_str))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            skip_columns = {'date', 'created_at'}
            prayer_columns = [col for col in columns if col not in skip_columns]
            
            prayer_data = {
                today_str: {col: '00:00' for col in prayer_columns},
                tomorrow_str: {col: '00:00' for col in prayer_columns}
            }
            
            for row in rows:
                row_dict = dict(zip(columns, row))
                date = row_dict['date']
                if date in prayer_data:
                    for col in prayer_columns:
                        if col in row_dict and row_dict[col]:
                            prayer_data[date][col] = row_dict[col][:5]
            
            today_display = f"{today.day:02d}/{today.month:02d}"
            tomorrow_display = f"{tomorrow.day:02d}/{tomorrow.month:02d}"
            
            print_separator()
            print_header("Data from Base")
            
            logger.info(f"| {'Date'.ljust(16)}|{today_display.center(8)}|{tomorrow_display.center(8)}|")
            logger.info("|" + "-" * 17 + "|" + "-" * 8 + "|" + "-" * 8 + "|")
            
            prayer_map = {
                'Midnight': 'Midnight',
                'Fajr': 'Fajr',
                'Sunrise': 'Sunrise',
                'Dhuhr': 'Dhuhr',
                'Asr': 'Asr',
                'Maghrib': 'Maghrib',
                'Isha': 'Isha'
            }
            
            for eng_name, display_name in prayer_map.items():
                today_time = prayer_data[today_str].get(eng_name, '--:--')
                tomorrow_time = prayer_data[tomorrow_str].get(eng_name, '--:--')
                logger.info(f"| {display_name.ljust(16)}|{str(today_time).center(8)}|{str(tomorrow_time).center(8)}|")
            
            print_separator()
            logger.info("\n")  # Пустая строка после таблицы
                
        except Exception as e:
            logger.error(f"Ошибка при получении данных из базы: {e}\n")
            
    except Exception as e:
        logger.error(f"Ошибка при выводе отладочной информации: {e}")
        
    return True


# Экспортируемые функции
__all__ = [
    'add_border',
    'print_debug_info',
    'print_sizes'
]
