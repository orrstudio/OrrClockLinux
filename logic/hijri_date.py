from datetime import datetime
from datetime import datetime
from hijri_converter import Gregorian
from data.database import SettingsDatabase
import locale

class HijriDateManager:
    def __init__(self):
        self.db = SettingsDatabase()
        self._setup_database()

    def _setup_database(self):
        """Создает таблицу для хранения дат хиджры"""
        self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hijri_dates (
                date TEXT PRIMARY KEY,
                hijri_date TEXT NOT NULL,
                hijri_month TEXT NOT NULL,
                hijri_year TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db.connection.commit()

    def _get_current_hijri_date(self):
        """Получает текущую дату хиджры"""
        hijri = Gregorian.today().to_hijri()
        return hijri

    def _format_hijri_date(self, hijri_date):
        """Форматирует дату хиджры в нужном формате"""
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        return {
            'day': str(hijri_date.day),  # День
            'month': str(hijri_date.month),  # Месяц
            'year': str(hijri_date.year),  # Год
            'full_date': f"{hijri_date.day}/{hijri_date.month}/{hijri_date.year}"
        }

    def get_hijri_date(self, date=None):
        """
        Получает дату хиджры для указанной даты или текущей
        Args:
            date: datetime object или None для текущей даты
        Returns:
            dict: отформатированная дата хиджры
        """
        if date is None:
            date = datetime.now()
            
        date_str = date.strftime('%Y-%m-%d')
        
        # Проверяем, есть ли дата в базе
        self.db.cursor.execute('SELECT * FROM hijri_dates WHERE date = ?', (date_str,))
        result = self.db.cursor.fetchone()
        
        if result and self._is_valid_cache(result):
            return {
                'day': result[1],
                'month': result[2],
                'year': result[3],
                'full_date': f"{result[1]}{result[2]}{result[3]}"
            }
        
        # Если нет в базе или кэш устарел, вычисляем заново
        hijri = self._get_current_hijri_date()
        formatted = self._format_hijri_date(hijri)
        
        # Сохраняем в базу
        self.db.cursor.execute('''
            INSERT OR REPLACE INTO hijri_dates 
            (date, hijri_date, hijri_month, hijri_year)
            VALUES (?, ?, ?, ?)
        ''', (date_str, formatted['day'], formatted['month'], formatted['year']))
        self.db.connection.commit()
        
        return formatted

    def _is_valid_cache(self, db_result):
        """Проверяет актуальность кэша в базе"""
        # Пока простая проверка - кэш валиден 30 дней
        created_at = datetime.strptime(db_result[4], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - created_at).days < 30

# Создаем глобальный экземпляр для использования в других модулях
hijri_date_manager = HijriDateManager()
