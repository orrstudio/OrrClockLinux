import requests
import json
from datetime import datetime, timedelta
from data.database import SettingsDatabase
from kivy.clock import Clock

from kivy.clock import Clock

class PrayerTimesManager:
    def __init__(self):
        self._listeners = []
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
        self.db = SettingsDatabase()
        self._auto_update_event = None
        self._setup_database()

    def add_update_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_update_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_update(self):
        print("[DEBUG] prayer_times: вызван _notify_update (кол-во callback: {}):".format(len(self._listeners)))
        for callback in self._listeners:
            try:
                callback()
            except Exception as e:
                print(f"PrayerTimesManager: ошибка в callback: {e}")


    def _setup_database(self):
        """Инициализирует базу данных и запускает фоновое обновление"""
        try:
            # Создаем таблицу, если её нет
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
            print("[DEBUG] prayer_times: таблица создана или уже существует")
            
            # Пробуем загрузить данные из кэша
            today_times = self.get_prayer_times()
            has_valid_data = any(v != '00:00' for v in today_times.values())
            
            if has_valid_data:
                print("[DEBUG] prayer_times: используем кэшированные данные")
                # Уведомляем подписчиков о загрузке кэшированных данных
                Clock.schedule_once(lambda dt: self._notify_update(), 0.1)
            else:
                print("[DEBUG] prayer_times: кэш пуст, будут использованы значения по умолчанию")
                # Все равно уведомляем подписчиков, чтобы UI загрузился с дефолтными значениями
                Clock.schedule_once(lambda dt: self._notify_update(), 0.1)
            
            # Запускаем фоновое обновление с небольшой задержкой
            Clock.schedule_once(lambda dt: self._background_update_check(), 0.5)
            
        except Exception as e:
            print(f"[ERROR] Ошибка при инициализации базы данных: {e}")
            # В любом случае уведомляем подписчиков, чтобы UI загрузился
            Clock.schedule_once(lambda dt: self._notify_update(), 0.1)
    
    def _background_update_check(self):
        """Проверяет и обновляет данные в фоновом режиме"""
        try:
            today_times = self.get_prayer_times()
            has_valid_data = any(v != '00:00' for v in today_times.values())
            
            if not has_valid_data:
                print("[DEBUG] prayer_times: кэш пуст, запускаем обновление")
                self.start_auto_update()
            else:
                # Проверяем актуальность данных
                self.db.cursor.execute('''
                    SELECT date FROM prayer_times 
                    WHERE date = ? AND created_at >= datetime('now', '-24 hours')
                ''', (datetime.now().strftime('%Y-%m-%d'),))
                
                if not self.db.cursor.fetchone():
                    print("[DEBUG] prayer_times: данные устарели, обновляем")
                    self.update_prayer_times()
                else:
                    print("[DEBUG] prayer_times: данные актуальны, обновление не требуется")
                    
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке обновлений: {e}")

    def _get_prayer_times_for_two_days(self):
        """Получает времена молитв только на сегодня и завтра с таймаутом"""
        import requests
        from requests.exceptions import RequestException, Timeout, ConnectionError
        
        today = datetime.now()
        prayer_times_data = {}
        
        for offset in range(2):  # 0 = сегодня, 1 = завтра
            date = today + timedelta(days=offset)
            date_str = date.strftime('%Y-%m-%d')
            params = {
                'city': self.city,
                'country': self.country,
                'method': self.method,
            }
            
            try:
                # Устанавливаем таймаут в 5 секунд на запрос
                response = requests.get(
                    f"{self.api_url}/{date.strftime('%d-%m-%Y')}",
                    params=params,
                    timeout=5  # 5 секунд на соединение + ответ
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200:
                        times = data.get('data', {}).get('timings', {})
                        current_times = {prayer: times.get(prayer, '00:00') for prayer in self.prayer_times}
                        prayer_times_data[date_str] = current_times
                        print(f"[DEBUG] prayer_times: Успешно получены данные для {date_str}")
                        continue  # Переходим к следующей дате
                
                print(f"[WARNING] Не удалось получить данные для {date_str}: {response.status_code}")
                
            except Timeout:
                print(f"[WARNING] Таймаут при запросе данных для {date_str}")
            except ConnectionError:
                print(f"[WARNING] Ошибка соединения при запросе данных для {date_str}")
            except RequestException as e:
                print(f"[WARNING] Ошибка при запросе данных для {date_str}: {str(e)}")
            except Exception as e:
                print(f"[ERROR] Непредвиденная ошибка при запросе данных для {date_str}: {str(e)}")
        
        return prayer_times_data

    def update_prayer_times(self):
        """Асинхронно обновляет времена молитв в базе данных"""
        print("[DEBUG] prayer_times: запуск асинхронного обновления времён молитв")
        
        def _update_in_thread():
            try:
                # Получаем данные с таймаутом
                prayer_times_data = self._get_prayer_times_for_two_days()
                if not prayer_times_data:
                    print("[DEBUG] Нет данных для обновления")
                    return
                
                updated = False
                for date_str, times in prayer_times_data.items():
                    try:
                        self.db.cursor.execute('SELECT * FROM prayer_times WHERE date = ?', (date_str,))
                        result = self.db.cursor.fetchone()
                        
                        if result:
                            # Обновляем только если что-то изменилось
                            need_update = any(result[i+1] != times.get(prayer, '00:00') 
                                          for i, prayer in enumerate(self.prayer_times))
                            if need_update:
                                self.db.cursor.execute(
                                    'UPDATE prayer_times SET ' + 
                                    ', '.join([f'{k} = ?' for k in self.prayer_times]) + 
                                    ' WHERE date = ?',
                                    [times.get(k, '00:00') for k in self.prayer_times] + [date_str]
                                )
                                updated = True
                        else:
                            # Нет записи — вставляем
                            self.db.cursor.execute(
                                'INSERT INTO prayer_times (date, ' + 
                                ', '.join(self.prayer_times) + 
                                ') VALUES (?, ' + ', '.join(['?']*len(self.prayer_times)) + ')',
                                [date_str] + [times.get(k, '00:00') for k in self.prayer_times]
                            )
                            updated = True
                            
                    except Exception as e:
                        print(f"[ERROR] Ошибка при обновлении данных для {date_str}: {e}")
                        continue
                
                if updated:
                    try:
                        self.db.connection.commit()
                        print("[DEBUG] prayer_times: данные успешно обновлены")
                        # Уведомляем в основном потоке
                        Clock.schedule_once(lambda dt: self._notify_update(), 0)
                    except Exception as e:
                        print(f"[ERROR] Ошибка при сохранении в базу: {e}")
                
                # Проверяем, появились ли валидные данные
                today_times = self.get_prayer_times()
                if any(v != '00:00' for v in today_times.values()):
                    self.stop_auto_update()
                    
            except Exception as e:
                print(f"[ERROR] Критическая ошибка при обновлении времён молитв: {e}")
                # В случае ошибки останавливаем автообновление, чтобы не нагружать систему
                self.stop_auto_update()
        
        # Запускаем обновление в отдельном потоке
        import threading
        thread = threading.Thread(target=_update_in_thread, daemon=True)
        thread.start()

    def get_prayer_times(self, date=None):
        print("[DEBUG] prayer_times: вызван get_prayer_times")
        """
        Получает времена молитв для указанной даты или текущей.
        1. Сначала ищет в базе
        2. Если нет — возвращает нули (обновление только через автообновление!)
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
            return {k: result[i+1] for i, k in enumerate(self.prayer_times)}
        else:
            # Не делаем никаких сетевых операций здесь!
            return {k: '00:00' for k in self.prayer_times}

    def start_auto_update(self):
        if not hasattr(self, '_auto_update_event') or self._auto_update_event is None:
            print('[DEBUG] prayer_times: старт автообновления')
            from kivy.clock import Clock
            self._auto_update_event = Clock.schedule_interval(self._auto_update_callback, 15)

    def stop_auto_update(self):
        if hasattr(self, '_auto_update_event') and self._auto_update_event:
            print('[DEBUG] prayer_times: стоп автообновления')
            self._auto_update_event.cancel()
            self._auto_update_event = None

    def _auto_update_callback(self, dt):
        print('[DEBUG] prayer_times: автообновление из API...')
        self.update_prayer_times()
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
                    self._notify_update()
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
