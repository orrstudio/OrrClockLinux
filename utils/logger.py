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
        _original_print(f"[ERROR] Error getting debug setting: {e}", file=sys.stderr)
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
            status = 'Enabled' if _DEBUG_ENABLED else 'Disabled'
            _original_print(f"[INFO   ] [Debug Mode] {status}", file=sys.stderr)
        return _DEBUG_ENABLED
    except Exception as e:
        _original_print(f"[ERROR] Error updating debug state: {e}", file=sys.stderr)
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
        _original_print(message, *args, **kwargs, file=_original_stdout)
    
    @classmethod
    def info(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит информационное сообщение."""
        _original_print(f"[INFO] {message}", *args, **kwargs, file=_original_stdout)
    
    @classmethod
    def warning(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит предупреждающее сообщение."""
        _original_print(f"[WARNING] {message}", *args, **kwargs, file=_original_stderr)
    
    @classmethod
    def error(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит сообщение об ошибке."""
        _original_print(f"[ERROR] {message}", *args, **kwargs, file=_original_stderr)
    
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
            _original_print(f"[ERROR] Failed to save debug state: {e}", file=sys.stderr)
            return False
    
    @classmethod
    def set_debug(cls, enabled: bool):
        """
        Переключает режим отладки и сохраняет его в базу данных.
        
        Args:
            enabled (bool): Включить или выключить отладочный режим
        """
        global logger, _DEBUG_ENABLED
        
        # Сохраняем новое состояние в БД
        if not cls.save_debug_state(enabled):
            _original_print("[ERROR] Failed to save debug state to database", file=sys.stderr)
            return
        
        # Обновляем глобальное состояние
        _DEBUG_ENABLED = enabled
        
        # Меняем класс логгера в зависимости от состояния
        if enabled:
            logger = DebugLogger()
        else:
            logger = NoopLogger()
            
        # Принудительно обновляем состояние в логгере
        _update_global_debug_state()

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
        _original_print(f"[INFO] {message}", *args, **kwargs, file=_original_stdout)
    
    @classmethod
    def warning(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит предупреждающее сообщение."""
        _original_print(f"[WARNING] {message}", *args, **kwargs, file=_original_stderr)
    
    @classmethod
    def error(cls, message: str, *args: Any, **kwargs: Any) -> None:
        """Выводит сообщение об ошибке."""
        _original_print(f"[ERROR] {message}", *args, **kwargs, file=_original_stderr)
    
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
            
            # Устанавливаем соответствующий класс логгера
            if enabled:
                if not isinstance(logger, DebugLogger):
                    logger = DebugLogger()
                    from kivy.logger import Logger
                    Logger.info("Logger: Debug Mode ENABLED")
            else:
                if not isinstance(logger, NoopLogger):
                    logger = NoopLogger()
                    from kivy.logger import Logger
                    Logger.info("Logger: Debug Mode DISABLED")
                    
            # Принудительно обновляем глобальное состояние
            _update_global_debug_state()
            
        except Exception as e:
            from kivy.logger import Logger
            Logger.error(f"Logger: Не удалось обновить отладочный режим: {e}")

# Создаем глобальный экземпляр логгера
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
        self.original_print(*args, **kwargs)

# Переопределяем глобальный print
builtins.print = PrintInterceptor()
