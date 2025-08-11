# data/database.py
from pathlib import Path
import sqlite3

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
        
        # Вставляем значения по умолчанию, если их нет
        default_settings = [
            ('color', 'lime'),
            ('debug_mode', '0')  # По умолчанию отладочный режим выключен
        ]
        
        for key, value in default_settings:
            self.cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES (?, ?)
            """, (key, value))
        
        # Создаем таблицу для хранения параметров главного окна, если она не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS window_settings (
                id INTEGER PRIMARY KEY,
                width INTEGER,
                height INTEGER,
                x INTEGER,
                y INTEGER
            )
        ''')
        
        # Создаем таблицу для хранения параметров окна настроек, если она не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings_window_settings (
                id INTEGER PRIMARY KEY,
                width INTEGER,
                height INTEGER,
                x INTEGER,
                y INTEGER
            )
        ''')
        
        self.connection.commit()

    def get_setting(self, key, default_value=None):
        """
        Получение значения настройки
        
        Args:
            key (str): Ключ настройки
            default_value: Значение по умолчанию, если настройка не найдена
            
        Returns:
            Значение настройки или default_value, если настройка не найдена
            
        Note:
            Для булевых значений возвращает строки '1' (True) или '0' (False)
        """
        # Значения по умолчанию для настроек
        default_settings = {
            'debug_mode': '0',  # По умолчанию отладочный режим выключен
            'color': 'lime',    # Цвет по умолчанию
            'azan_spinner': 'Azan 1',
            'azan_dropdown': 'Azan 1',
            'azan_popup': 'Azan 1'
        }
        
        # Если запрашиваемая настройка есть в значениях по умолчанию,
        # но не указано значение по умолчанию, используем наше
        if key in default_settings and default_value is None:
            default_value = default_settings[key]
        
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = self.cursor.fetchone()
            
            # Если настройка не найдена, сохраняем значение по умолчанию
            if result is None and key in default_settings:
                self.save_setting(key, default_settings[key])
                return default_settings[key]
                
            return result[0] if result is not None else default_value
            
        except Exception as e:
            print(f"Ошибка при получении настройки {key}: {e}")
            return default_value
    
    def save_setting(self, key, value):
        """Сохранение значения настройки"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) 
            VALUES (?, ?)
        """, (key, value))
        self.connection.commit()

    def save_window_settings(self, width, height, x, y):
        """
        Сохраняет настройки главного окна в БД
        """
        try:
            # Сохраняем абсолютные координаты
            self.cursor.execute('''
                INSERT OR REPLACE INTO window_settings 
                (id, width, height, x, y) 
                VALUES (1, ?, ?, ?, ?)
            ''', (width, height, x, y))
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при сохранении настроек главного окна: {e}")
            
    def save_settings_window_settings(self, width, height, x, y):
        """
        Сохраняет настройки окна настроек в БД
        """
        try:
            # Сохраняем абсолютные координаты
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings_window_settings 
                (id, width, height, x, y) 
                VALUES (1, ?, ?, ?, ?)
            ''', (width, height, x, y))
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при сохранении настроек окна настроек: {e}")

    def get_window_settings(self):
        """
        Загружает настройки главного окна из БД
        """
        try:
            self.cursor.execute('SELECT width, height, x, y FROM window_settings WHERE id = 1')
            settings = self.cursor.fetchone()
            if settings:
                return settings
        except Exception:
            pass
        return None
        
    def get_settings_window_settings(self):
        """
        Загружает настройки окна настроек из БД
        """
        try:
            self.cursor.execute('SELECT width, height, x, y FROM settings_window_settings WHERE id = 1')
            settings = self.cursor.fetchone()
            if settings:
                return settings
        except Exception as e:
            print(f"Ошибка при загрузке настроек окна настроек: {e}")
        return None

    def apply_window_settings(self, window):
        """
        Применяет настройки главного окна
        Если настройки не найдены в базе данных, устанавливает размеры по умолчанию 715x1000
        """
        settings = self.get_window_settings()
        if settings:
            width, height, x, y = settings
            window.size = (width, height)
            window.left = x
            window.top = y
            from kivy.logger import Logger
            Logger.info(f'Window: applying settings: size={width}x{height} position={x}x{y}')
        else:
            # Устанавливаем размеры по умолчанию, если настройки не найдены
            width, height = 715, 1000
            window.size = (width, height)
            # Центрируем окно на экране
            window.left = (window.system_size[0] - width) // 2
            window.top = (window.system_size[1] - height) // 2
            from kivy.logger import Logger
            Logger.info(f'Window: applying default settings: size={width}x{height} position={window.left}x{window.top}')
            
    def apply_settings_window_settings(self, window):
        """
        Применяет настройки окна настроек
        Если настройки не найдены в базе данных, оставляет текущие размеры и положение
        """
        settings = self.get_settings_window_settings()
        if settings:
            width, height, x, y = settings
            # Устанавливаем размеры окна
            if hasattr(window, 'size'):
                window.size = (width, height)
            
            # Устанавливаем позицию окна
            if hasattr(window, 'left') and hasattr(window, 'top'):
                window.left = x
                window.top = y
            elif hasattr(window, 'x') and hasattr(window, 'y'):
                window.x = x
                window.y = y
            
            # Принудительно обновляем размеры и позицию
            if hasattr(window, 'do_layout'):
                window.do_layout()
