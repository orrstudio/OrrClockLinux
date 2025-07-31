import requests
import json
from datetime import datetime, timedelta
from data.database import SettingsDatabase
from kivy.clock import Clock

class PrayerTimesManager:
    def __init__(self):
        self.db = SettingsDatabase()
        self._setup_database()
        self.api_url = "http://api.aladhan.com/v1/timingsByCity"
        self.city = "baku"
        self.country = "AZ"
        self.method = 13  # Method 13 is for Azerbaijan
        self.prayer_times = [
            "Midnight",
            "Fajr",
            "Sunrise",
            "Dhuhr",
            "Asr",
            "Maghrib",
            "Isha"
        ]

    def _setup_database(self):
        """Создает таблицу для хранения времён молитв"""
        self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prayer_times (
                date TEXT PRIMARY KEY,
                Midnight TEXT,
                Fajr TEXT,
                Sunrise TEXT,
                Dhuhr TEXT,
                Asr TEXT,
                Maghrib TEXT,
                Isha TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db.connection.commit()

    def _get_prayer_times_for_two_days(self):
        """Получает времена молитв только на сегодня и завтра"""
        today = datetime.now()
        prayer_times_data = {}
        
        for offset in range(2):  # 0 = сегодня, 1 = завтра
            date = today + timedelta(days=offset)
            params = {
                'city': self.city,
                'country': self.country,
                'method': self.method,
                'date': date.strftime('%d-%m-%Y')
            }
            try:
                response = requests.get(self.api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data['code'] == 200:
                        times = data['data']['timings']
                        current_times = {prayer: times[prayer] for prayer in self.prayer_times}
                        prayer_times_data[date.strftime('%Y-%m-%d')] = current_times
            except Exception as e:
                print(f"Error fetching prayer times for {date}: {str(e)}")
                continue
        return prayer_times_data

    def update_prayer_times(self):
        """Обновляет времена молитв в базе данных только на сегодня и завтра"""
        prayer_times_data = self._get_prayer_times_for_two_days()
        
        for date_str, times in prayer_times_data.items():
            # Проверяем, есть ли запись в базе
            self.db.cursor.execute('SELECT * FROM prayer_times WHERE date = ?', (date_str,))
            result = self.db.cursor.fetchone()
            
            # Если нет или запись старая (более 30 дней), обновляем
            if not result or self._is_valid_cache(result):
                # Формируем SQL запрос для вставки/обновления
                columns = ['date'] + self.prayer_times
                placeholders = ['?'] * (len(columns))
                values = [date_str] + [times.get(prayer, '') for prayer in self.prayer_times]
                
                sql = f"INSERT OR REPLACE INTO prayer_times ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                self.db.cursor.execute(sql, values)
                
        self.db.connection.commit()

    def get_prayer_times(self, date=None):
        """
        Получает времена молитв для указанной даты или текущей.
        1. Сначала ищет в базе
        2. Если нет — пробует загрузить из API и сохранить
        3. Если и API не дал — возвращает нули
        Args:
            date: datetime object или None для текущей даты
        Returns:
            dict: времена молитв для указанной даты
        """
        if date is None:
            date = datetime.now()
        date_str = date.strftime('%Y-%m-%d')

        # 1. Проверяем, есть ли времена молитв в базе
        self.db.cursor.execute('SELECT * FROM prayer_times WHERE date = ?', (date_str,))
        result = self.db.cursor.fetchone()
        if result and self._is_valid_cache(result):
            prayer_times = {
                prayer: result[i+1]  # +1 потому что первый элемент - дата
                for i, prayer in enumerate(self.prayer_times)
            }
            # Если все значения prayer_times равны '00:00', пробуем обновить из API
            if all(v == '00:00' for v in prayer_times.values()):
                api_times = self._try_fetch_and_store_api_times(date, date_str)
                if api_times:
                    return api_times
            return prayer_times

        # 2. Если нет — пробуем получить из API
        api_times = self._try_fetch_and_store_api_times(date, date_str)
        if api_times:
            return api_times
        # 3. Если и API не дал — возвращаем нули
        return {prayer: '00:00' for prayer in self.prayer_times}

    def _try_fetch_and_store_api_times(self, date, date_str):
        """Пробует получить времена молитв из API, сохранить в базу и вернуть их. Если не получилось — вернуть None."""
        params = {
            'city': self.city,
            'country': self.country,
            'method': self.method,
            'date': date.strftime('%d-%m-%Y')
        }
        try:
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 200:
                    times = data['data']['timings']
                    prayer_times = {prayer: times[prayer] for prayer in self.prayer_times}
                    # Сохраняем в базу
                    columns = ['date'] + self.prayer_times
                    placeholders = ['?'] * (len(columns))
                    values = [date_str] + [prayer_times.get(prayer, '') for prayer in self.prayer_times]
                    sql = f"INSERT OR REPLACE INTO prayer_times ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                    self.db.cursor.execute(sql, values)
                    self.db.connection.commit()
                    return prayer_times
        except Exception as e:
            print(f"Error fetching prayer times from API for {date_str}: {str(e)}")
        return None

    def _get_days_with_data(self, days_ahead=7):
        """
        Возвращает количество дней с данными в базе вперед от текущей даты
        Args:
            days_ahead (int): количество дней вперед, которые нужно проверить
        Returns:
            int: количество дней с данными
        """
        today = datetime.now()
        self.db.cursor.execute('''
            SELECT COUNT(*) FROM prayer_times 
            WHERE date BETWEEN ? AND ?
        ''', (
            today.strftime('%Y-%m-%d'),
            (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        ))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0

    def _load_month_in_background(self):
        """Загружает данные на месяц в фоновом режиме"""
        def _load_month(dt):
            try:
                self.update_prayer_times()
            except Exception as e:
                print(f"Error loading month data: {str(e)}")

        # Вызываем обновление через Clock.schedule_once
        Clock.schedule_once(_load_month, 0)

    def _is_valid_cache(self, db_result):
        """Проверяет актуальность кэша в базе"""
        # Пока простая проверка - кэш валиден 30 дней
        created_at = datetime.strptime(db_result[-1], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - created_at).days < 30

# Создаем глобальный экземпляр для использования в других модулях
prayer_times_manager = PrayerTimesManager()
