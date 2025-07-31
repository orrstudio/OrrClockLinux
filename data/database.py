# data/database.py
from pathlib import Path
import sqlite3
from logic.display_utils import is_mobile_device, find_current_monitor, get_monitor_info
from kivy.core.window import Window

class SettingsDatabase:
    def __init__(self, db_path='data/settings.db'):
        # Создаем директорию data если её нет
        Path("data").mkdir(exist_ok=True)
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Вставляем значение по умолчанию для цвета, если его нет
        self.cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('color', 'lime')
        """)
        
        # Создаем таблицу для хранения параметров окна, если она не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS window_settings (
                id INTEGER PRIMARY KEY,
                width INTEGER,
                height INTEGER,
                x INTEGER,
                y INTEGER
            )
        ''')
        
        self.connection.commit()

    def get_setting(self, key):
        """Получение значения настройки"""
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def save_setting(self, key, value):
        """Сохранение значения настройки"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) 
            VALUES (?, ?)
        """, (key, value))
        self.connection.commit()

    def save_window_settings(self, width, height, x, y):
        """
        Сохраняет настройки окна в БД
        """
        try:
            # Сохраняем абсолютные координаты
            self.cursor.execute('''
                INSERT OR REPLACE INTO window_settings 
                (id, width, height, x, y) 
                VALUES (1, ?, ?, ?, ?)
            ''', (width, height, x, y))
            self.connection.commit()
        except Exception:
            pass

    def get_window_settings(self):
        """
        Загружает настройки окна из БД
        """
        try:
            self.cursor.execute('SELECT width, height, x, y FROM window_settings WHERE id = 1')
            settings = self.cursor.fetchone()
            if settings:
                return settings
        except Exception:
            pass
        return None

    def apply_window_settings(self, window):
        """
        Применяет настройки окна
        """
        settings = self.get_window_settings()
        if settings:
            width, height, x, y = settings
            window.size = (width, height)
            window.left = x
            window.top = y
