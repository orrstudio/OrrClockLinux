"""
Модуль для централизованного управления логированием в приложении.
Позволяет включать/отключать отладочные сообщения во всем приложении.
"""

import sys
import builtins
from typing import Any

# Сохраняем оригинальный print
_original_print = builtins.print
_original_stdout = sys.stdout
_original_stderr = sys.stderr

def _get_debug_state() -> bool:
    """
    Получает текущее состояние отладочного режима из базы данных.
    
    Returns:
        bool: True, если отладка включена, иначе False.
    """
    try:
        from data.database import SettingsDatabase
        db = SettingsDatabase()
        debug_mode = db.get_setting('debug_mode', '0')
        return debug_mode == '1'
    except Exception as e:
        from kivy.logger import Logger
        Logger.error(f'Ошибка получения настройки отладки: {e}')
        return False

# Глобальная переменная для хранения состояния отладки
_DEBUG_ENABLED = _get_debug_state()

def _update_global_debug_state():
    """
    Обновляет глобальное состояние отладки на основе текущих настроек из базы данных.
    
    Returns:
        bool: Текущее состояние отладки (True - включено, False - выключено)
    """
    global _DEBUG_ENABLED
    try:
        new_state = _get_debug_state()
        if _DEBUG_ENABLED != new_state:
            _DEBUG_ENABLED = new_state
            status = 'ENABLED' if _DEBUG_ENABLED else 'DISABLED'
            from kivy.logger import Logger
            Logger.info(f'Debug Mode {status}')
        return _DEBUG_ENABLED
    except Exception as e:
        from kivy.logger import Logger
        Logger.error(f'Error updating debug state: {e}')
        return _DEBUG_ENABLED

# Определяем классы для разных режимов работы логгера
class DebugLogger:
    """Класс логгера с включенным отладочным выводом."""
    
    @classmethod
    def debug_enabled(cls) -> bool:
        return True
    
    @classmethod
    def debug(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит отладочное сообщение."""
        if not message.startswith('[DEBUG]'):
            message = f'[DEBUG] {message}'
        from kivy.logger import Logger
        Logger.info(message)
    
    @classmethod
    def info(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит информационное сообщение."""
        from kivy.logger import Logger
        Logger.info(message)
    
    @classmethod
    def warning(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит предупреждающее сообщение."""
        from kivy.logger import Logger
        Logger.warning(message)
    @classmethod
    def error(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит сообщение об ошибке."""
        from kivy.logger import Logger
        Logger.error(message)
    
    @classmethod
    def save_debug_state(cls, enabled: bool) -> bool:
        """
        Сохраняет состояние отладки в базу данных.
        
        Args:
            enabled (bool): Включён ли отладочный режим
            
        Returns:
            bool: True, если сохранение прошло успешно, иначе False
        """
        try:
            from data.database import SettingsDatabase
            db = SettingsDatabase()
            db.save_setting('debug_mode', '1' if enabled else '0')
            return True
        except Exception as e:
            from kivy.logger import Logger
            Logger.error(f'Failed to save debug state: {e}')
            return False
    
    @classmethod
    def set_debug(cls, enabled: bool) -> None:
        """
        Переключает режим отладки и сохраняет его в базу данных.
        
        Args:
            enabled (bool): Включить или выключить отладочный режим
        """
        global logger
        try:
            # Сохраняем состояние в базу данных
            if not cls.save_debug_state(enabled):
                from kivy.logger import Logger
                Logger.error('Failed to save debug state to database')
                return
            
            # Обновляем глобальное состояние отладки
            _update_global_debug_state()
            
            # Обновляем уровень логирования Kivy
            update_kivy_logger_level(enabled)
            
            # Меняем класс логгера в зависимости от состояния отладки
            if enabled:
                logger = DebugLogger()
            else:
                logger = NoopLogger()
                
            from kivy.logger import Logger
            Logger.info(f"Debug Mode {'Enabled' if enabled else 'Disabled'}")
            
        except Exception as e:
            from kivy.logger import Logger
            Logger.error(f'Failed to set debug mode: {e}')

class NoopLogger:
    """Класс логгера с отключенным отладочным выводом."""
    
    @classmethod
    def debug_enabled(cls) -> bool:
        return False
    
    @classmethod
    def debug(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Не делает ничего (отладочный вывод отключен)."""
        pass
    
    @classmethod
    def info(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит информационное сообщение."""
        from kivy.logger import Logger
        Logger.info(message)
    
    @classmethod
    def warning(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит предупреждающее сообщение."""
        from kivy.logger import Logger
        Logger.warning(message)
    
    @classmethod
    def error(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит сообщение об ошибке."""
        from kivy.logger import Logger
        Logger.error(message)
    
    @classmethod
    def set_debug(cls, enabled: bool) -> None:
        """
        Устанавливает режим отладки.
        
        Args:
            enabled: Включить (True) или выключить (False) отладочный режим
        """
        global logger, _DEBUG_ENABLED
        
        try:
            # Обновляем значение в базе данных
            from data.database import SettingsDatabase
            db = SettingsDatabase()
            db.save_setting('debug_mode', '1' if enabled else '0')
            
            # Обновляем глобальное состояние
            _DEBUG_ENABLED = enabled
            
            # Обновляем уровень логирования Kivy
            update_kivy_logger_level(enabled)
            
            # Устанавливаем соответствующий класс логгера
            if enabled:
                if not isinstance(logger, DebugLogger):
                    logger = DebugLogger()
                    from kivy.logger import Logger
            else:
                if not isinstance(logger, NoopLogger):
                    logger = NoopLogger()
                    
            # Принудительно обновляем глобальное состояние
            _update_global_debug_state()
            
        except Exception as e:
            from kivy.logger import Logger
            Logger.error(f"Logger: Failed to update debug mode: {e}")

def update_kivy_logger_level(debug_enabled):
    """
    Updates the Kivy logger level based on the debug mode.
    
    Args:
        debug_enabled (bool): Whether debug mode is enabled
    """
    try:
        from kivy.logger import Logger, LOG_LEVELS
        if debug_enabled:
            Logger.setLevel(LOG_LEVELS['debug'])
        else:
            # Set to 'info' level when debug is disabled
            Logger.setLevel(LOG_LEVELS['info'])
    except Exception as e:
        from kivy.logger import Logger
        Logger.error(f'Failed to update Kivy logger level: {e}')

# Update Kivy logger level based on current debug state
update_kivy_logger_level(_get_debug_state())

# Create global logger instance
logger = DebugLogger() if _get_debug_state() else NoopLogger()

# Перехватываем стандартный print
class PrintInterceptor:
    def __init__(self):
        self.original_print = _original_print
    
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        # Если это отладочное сообщение и отладка выключена, полностью подавляем вывод
        if args and isinstance(args[0], str) and '[DEBUG]' in args[0]:
            # Используем глобальное состояние отладки
            if not _DEBUG_ENABLED:
                return
            # Если отладка включена, добавляем префикс [DEBUG], если его нет
            if not args[0].startswith('[DEBUG]'):
                args = (f'[DEBUG] {args[0]}',) + args[1:]
        
        # Выводим сообщение, если это не отладочное или отладка включена
        from kivy.logger import Logger
        message = ' '.join(str(arg) for arg in args)
        Logger.info(message)

# Переопределяем глобальный print
builtins.print = PrintInterceptor()
