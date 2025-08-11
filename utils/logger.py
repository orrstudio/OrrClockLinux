"""
Модуль для централизованного управления логированием в приложении.
Позволяет включать/отключать отладочные сообщения во всем приложении.
"""

import os
import sys
import builtins
import io
from typing import Optional, TextIO

# Сохраняем оригинальный print
_original_print = builtins.print

# Глобальная переменная для хранения состояния отладки
_DEBUG_ENABLED = None

def _update_debug_state():
    """Обновляет внутреннее состояние отладочного режима."""
    global _DEBUG_ENABLED
    debug_value = os.environ.get('ORRCLOCK_DEBUG', '0').strip().lower()
    _DEBUG_ENABLED = debug_value in ('1', 'true', 'yes')
    return _DEBUG_ENABLED

# Инициализируем состояние отладки при импорте
_update_debug_state()

class DebugFilterStream(io.TextIOBase):
    """Поток для фильтрации отладочных сообщений."""
    
    def __init__(self, stream: TextIO):
        self.stream = stream
        
    def write(self, text: str) -> int:
        # Пропускаем отладочные сообщения, если отладка отключена
        if text.startswith('[DEBUG]') and not Logger.debug_enabled():
            return len(text)
        return self.stream.write(text)
    
    def flush(self) -> None:
        self.stream.flush()

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def debug_enabled(cls) -> bool:
        """
        Проверяет, включены ли отладочные сообщения.
        
        Returns:
            bool: True, если отладочные сообщения включены, иначе False.
            По умолчанию возвращает False, если переменная ORRCLOCK_DEBUG не установлена.
        """
        # Используем глобальное состояние для повышения производительности
        return _DEBUG_ENABLED
    
    @classmethod
    def set_debug(cls, enabled: bool):
        """Включает или отключает отладочные сообщения."""
        os.environ['ORRCLOCK_DEBUG'] = '1' if enabled else '0'
        _update_debug_state()
    
    @classmethod
    def debug(cls, message: str, *args, **kwargs):
        """Выводит отладочное сообщение, если отладка включена."""
        if cls.debug_enabled():
            # Удаляем [DEBUG] из сообщения, если оно уже есть
            if message.startswith('[DEBUG]'):
                message = message[7:].lstrip()
            print(f"[DEBUG] {message}", *args, **kwargs)
    
    @classmethod
    def info(cls, message: str, *args, **kwargs):
        """Выводит информационное сообщение."""
        print(f"[INFO] {message}", *args, **kwargs)
    
    @classmethod
    def warning(cls, message: str, *args, **kwargs):
        """Выводит предупреждающее сообщение."""
        print(f"[WARNING] {message}", *args, **kwargs)
    
    @classmethod
    def error(cls, message: str, *args, **kwargs):
        """Выводит сообщение об ошибке."""
        print(f"[ERROR] {message}", *args, **kwargs, file=sys.stderr)

# Создаем глобальный экземпляр логгера
logger = Logger()

# Настраиваем перехват стандартного вывода
sys.stdout = DebugFilterStream(sys.stdout)

# Переопределяем глобальный print, чтобы он использовал наш фильтр
def custom_print(*args, **kwargs):
    # Если это отладочное сообщение и отладка отключена, пропускаем его
    if args and isinstance(args[0], str) and args[0].startswith('[DEBUG]') and not logger.debug_enabled():
        return
    _original_print(*args, **kwargs)

builtins.print = custom_print
