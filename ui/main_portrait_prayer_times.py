from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.clock import Clock
from logic.prayer_times import prayer_times_manager
from datetime import datetime, time
from .theme_color_schemes import get_theme_scheme, COLORS as THEME_COLORS
from utils.logger import logger  # Импорт кастомного логгера

class PrayerTimesBox(GridLayout):
    """
    GridLayout для реактивного отображения времён молитв.
    Обновляет только текст Label-ов при изменении данных через callback.
    """
    def __init__(self, base_font_size, **kwargs):
        super().__init__(cols=2, size_hint_x=1, size_hint_y=None, height=base_font_size * 4.0, padding=(base_font_size * 0.15, 0), **kwargs)
        self.base_font_size = base_font_size
        self._update_event = None  # Для хранения ссылки на событие обновления
        
        # Инициализация цветовой схемы по умолчанию
        self.current_scheme = get_theme_scheme('lime')  # Текущая цветовая схема
        
        # Маппинг между азербайджанскими названиями и ключами API
        self.prayer_mapping = {
            'Təhəccüd ---': 'Midnight',
            'İmsak ------': 'Fajr',
            'Günəş ------': 'Sunrise',
            'Günorta ----': 'Dhuhr',
            'İkindi -----': 'Asr',
            'Axşam ------': 'Maghrib',
            'Gecə -------': 'Isha'
        }
        self.prayer_labels = {}  # {api_key: {'time_label': Label, 'name_label': Label}}
        self._original_colors = {}  # Для хранения исходных цветов
        self._animation_event = None
        self._is_animating = False
        
        self._build_layout()
        prayer_times_manager.add_update_listener(self.refresh_prayer_times)
        self.refresh_prayer_times()
        
        # Запускаем таймер для обновления активной молитвы каждую секунду для более точного отслеживания
        self._update_event = Clock.schedule_interval(lambda dt: self.refresh_prayer_times(), 1)

    def _build_layout(self):
        prayer_times_data = prayer_times_manager.get_prayer_times()
        for prayer_name, api_key in self.prayer_mapping.items():
            prayer_name_label = Label(
                text=prayer_name,
                font_name='FontSourceCodePro-Regular',
                font_size=self.base_font_size * 0.4,
                color=(0.6, 0.5, 0.0, 1),  # Темно-желтый для текста молитв
                halign='left',
                text_size=(self.width * 0.6, None),
                size_hint_x=0.75
            )
            prayer_name_label.bind(size=prayer_name_label.setter('text_size'))
            prayer_time = prayer_times_data.get(api_key, '00:00')
            prayer_time_label = Label(
                text=prayer_time,
                font_name='FontDSEG7-Bold',
                font_size=self.base_font_size * 0.45,
                color=(0.6, 0.5, 0.0, 1),  # Темно-желтый для текста молитв
                halign='right',
                text_size=(self.width * 0.4, None),
                size_hint_x=0.4
            )
            prayer_time_label.bind(size=prayer_time_label.setter('text_size'))
            self.add_widget(prayer_name_label)
            self.add_widget(prayer_time_label)
            self.prayer_labels[api_key] = {
                'time_label': prayer_time_label,
                'name_label': prayer_name_label
            }

    def _is_within_15_minutes_before_prayer(self, prayer_time, current_time):
        """Проверяет, осталось ли до времени намаза 15 минут или меньше"""
        if not prayer_time or not current_time:
            return False
            
        # Преобразуем время в datetime для удобства вычислений
        prayer_dt = datetime.combine(datetime.today(), prayer_time)
        current_dt = datetime.combine(datetime.today(), current_time)
        
        # Вычисляем разницу во времени
        time_diff = (prayer_dt - current_dt).total_seconds()
        
        # Возвращаем True, если до намаза осталось от 0 до 15 минут
        return 0 <= time_diff <= 900  # 900 секунд = 15 минут
    
    def update_colors(self, scheme_name='lime'):
        """
        Обновляет цвета элементов в соответствии с выбранной темой
        
        Args:
            scheme_name: Имя темы (по умолчанию 'lime')
        """
        try:
            from kivy.logger import Logger
            Logger.debug(f'[PrayerTimesBox] Начало обновления цветов на тему: {scheme_name}')
            
            # Получаем новую цветовую схему
            new_scheme = get_theme_scheme(scheme_name)
            if not new_scheme:
                Logger.error(f'[PrayerTimesBox] Ошибка: Неверное имя темы: {scheme_name}')
                Logger.error(f'[PrayerTimesBox] Доступные темы: {list(COLOR_SCHEMES.keys())}')
                return
                
            self.current_scheme = new_scheme
            Logger.debug(f'[PrayerTimesBox] Новая цветовая схема: {self.current_scheme}')
            
            # Проверяем наличие элементов перед обновлением
            if not hasattr(self, 'prayer_labels') or not self.prayer_labels:
                Logger.error('[PrayerTimesBox] Ошибка: prayer_labels не инициализирован')
                return
                
            # Принудительно обновляем цвета с помощью refresh_prayer_times
            Logger.debug('[PrayerTimesBox] Вызов refresh_prayer_times()')
            self.refresh_prayer_times()
            
            # Проверяем, применились ли цвета
            if hasattr(self, 'prayer_labels'):
                for api_key, labels in self.prayer_labels.items():
                    Logger.debug(f'[PrayerTimesBox] {api_key} - цвет времени: {labels["time_label"].color}')
                    Logger.debug(f'[PrayerTimesBox] {api_key} - цвет названия: {labels["name_label"].color}')
            
            Logger.info(f'[PrayerTimesBox] Цвета успешно обновлены на тему: {scheme_name}')
            
        except Exception as e:
            import traceback
            from kivy.logger import Logger
            Logger.error(f'[PrayerTimesBox] Ошибка при обновлении цветов: {str(e)}')
            Logger.error(f'[PrayerTimesBox] Трассировка: {traceback.format_exc()}')

    def refresh_prayer_times(self):
        from kivy.logger import Logger
        Logger.debug('[PrayerTimesBox.refresh_prayer_times] Начало обновления времен молитв')
        
        prayer_times_data = prayer_times_manager.get_prayer_times()
        current_time = datetime.now().time()
        
        # Логируем полученные данные
        Logger.debug(f'[PrayerTimesBox.refresh_prayer_times] Текущее время: {current_time}')
        Logger.debug(f'[PrayerTimesBox.refresh_prayer_times] Данные молитв: {prayer_times_data}')
        Logger.debug(f'[PrayerTimesBox.refresh_prayer_times] Текущая цветовая схема: {self.current_scheme if hasattr(self, "current_scheme") else "Не определена"}')
        
        # Получаем текущую активную молитву
        current_prayer = None
        prayer_times_list = []
        
        # Собираем все времена молитв и сортируем их
        for api_key, time_str in prayer_times_data.items():
            if api_key in self.prayer_mapping.values():
                try:
                    prayer_time = datetime.strptime(time_str, '%H:%M').time()
                    prayer_times_list.append((api_key, prayer_time))
                except (ValueError, TypeError):
                    continue
        
        # Сортируем времена молитв
        prayer_times_list.sort(key=lambda x: x[1])
        
        # Находим текущую активную молитву (последняя молитва, время которой прошло)
        # и следующую молитву
        current_prayer = None
        next_prayer = None
        next_prayer_time = None
        
        for i, (api_key, prayer_time) in enumerate(prayer_times_list):
            if prayer_time > current_time:
                next_prayer = api_key
                next_prayer_time = prayer_time
                break
            current_prayer = api_key
        
        # Если текущее время позже последней молитвы, то активной считается последняя молитва дня,
        # а следующей - первая молитва следующего дня
        if current_prayer is None and prayer_times_list:
            current_prayer = prayer_times_list[-1][0]
        if next_prayer is None and prayer_times_list:
            next_prayer = prayer_times_list[0][0]
            next_prayer_time = prayer_times_list[0][1]
        
        # Обновляем текст и цвет для всех меток
        for api_key, labels in self.prayer_labels.items():
            # Обновляем текст времени молитвы
            time_text = prayer_times_data.get(api_key, '00:00')
            labels['time_label'].text = time_text
            
            # Проверяем, что current_prayer и next_prayer определены
            current_prayer_defined = current_prayer is not None
            next_prayer_defined = next_prayer is not None
            
            # Устанавливаем цвета из текущей схемы
            if current_prayer_defined and api_key == current_prayer:
                # Активное время
                color = self.current_scheme['active_time']
                color_type = 'active_time'
            elif next_prayer_defined and api_key == next_prayer:
                # Следующая молитва
                color = self.current_scheme['next_time']
                color_type = 'next_time'
            else:
                # Обычное время молитвы
                color = self.current_scheme['prayer_times']
                color_type = 'prayer_times'
            
            # Применяем цвет к времени и названию молитвы
            labels['time_label'].color = color
            labels['name_label'].color = color
            
            # Логируем установленные цвета
            from kivy.logger import Logger
            Logger.debug(f'[PrayerTimesBox.refresh_prayer_times] Установлен цвет для {api_key} ({time_text}): {color} (тип: {color_type})')

    def on_parent(self, widget, parent):
        # Автоматическая отписка при удалении с экрана
        if parent is None:
            prayer_times_manager.remove_update_listener(self.refresh_prayer_times)
            if hasattr(self, '_update_event') and self._update_event:
                self._update_event.cancel()
            self.stop_animation()
            
    def start_animation(self):
        """Запускаем анимацию: делаем все молитвы прозрачными, кроме текущей"""
        import logging
        
        if self._is_animating:
            return
            
        self._is_animating = True
        logging.info('[Notification] Starting active prayer blink animation')
        
        # Получаем текущую активную молитву
        current_prayer = self._get_current_prayer()
        
        # Сохраняем текущие цвета и прозрачность
        self._original_colors = {}
        for api_key, labels in self.prayer_labels.items():
            self._original_colors[api_key] = {
                'time_color': labels['time_label'].color,
                'name_color': labels['name_label'].color,
                'time_opacity': labels['time_label'].opacity,
                'name_opacity': labels['name_label'].opacity
            }
            
            # Делаем все молитвы прозрачными, кроме активной
            if api_key != current_prayer:
                labels['time_label'].opacity = 0.0
                labels['name_label'].opacity = 0.0
            else:
                labels['time_label'].opacity = 1.0
                labels['name_label'].opacity = 1.0
        
        # Запускаем мигание для активной молитвы
        self._update_animation()
        
        # Останавливаем анимацию через 60 секунд
        if hasattr(self, '_stop_timer'):
            self._stop_timer.cancel()
        self._stop_timer = Clock.schedule_once(self.stop_animation, 60)
    
    def stop_animation(self, *args):
        """Останавливаем анимацию и обновляем цвета в соответствии с текущим временем"""
        import logging
        
        if not self._is_animating:
            return
            
        logging.info('Notification: Stopping prayer list animation')
        self._is_animating = False
        
        # Отменяем запланированные события
        if hasattr(self, '_blink_event'):
            self._blink_event.cancel()
        if hasattr(self, '_stop_timer'):
            self._stop_timer.cancel()
        
        # Восстанавливаем видимость всех молитв
        for api_key, labels in self.prayer_labels.items():
            # Восстанавливаем видимость
            labels['time_label'].opacity = 1.0
            labels['name_label'].opacity = 1.0
        
        # Обновляем все цвета в соответствии с текущим временем
        self.refresh_prayer_times()
        
        # Очищаем сохраненные цвета, так как они больше не нужны
        self._original_colors = {}
    
    def _get_current_prayer(self):
        """Возвращает ключ текущей активной молитвы"""
        prayer_times_data = prayer_times_manager.get_prayer_times()
        current_time = datetime.now().time()
        
        # Собираем все времена молитв и сортируем их
        prayer_times_list = []
        for api_key, time_str in prayer_times_data.items():
            if api_key in self.prayer_mapping.values():
                try:
                    prayer_time = datetime.strptime(time_str, '%H:%M').time()
                    prayer_times_list.append((api_key, prayer_time))
                except (ValueError, TypeError):
                    continue
        
        # Сортируем времена молитв
        prayer_times_list.sort(key=lambda x: x[1])
        
        # Находим текущую активную молитву (последняя молитва, время которой прошло)
        current_prayer = None
        for api_key, prayer_time in prayer_times_list:
            if prayer_time > current_time:
                break
            current_prayer = api_key
        
        # Если текущее время позже последней молитвы, то активной считается последняя молитва дня
        if current_prayer is None and prayer_times_list:
            current_prayer = prayer_times_list[-1][0]
            
        return current_prayer
    
    def _update_animation(self, *args):
        """Обновляет анимацию мигания активной молитвы с мгновенным переключением"""
        if not self._is_animating:
            return
            
        # Получаем текущую активную молитву
        current_prayer = self._get_current_prayer()
        if not current_prayer:
            return
            
        # Получаем метки активной молитвы
        labels = self.prayer_labels.get(current_prayer)
        if not labels:
            return
        
        # Меняем прозрачность на противоположную
        new_opacity = 0.0 if labels['time_label'].opacity == 1.0 else 1.0
        
        # Применяем новую прозрачность
        labels['time_label'].opacity = new_opacity
        labels['name_label'].opacity = new_opacity
        
        # Запускаем следующее переключение через 0.5 секунды
        if hasattr(self, '_blink_event'):
            self._blink_event.cancel()
        self._blink_event = Clock.schedule_once(self._update_animation, 0.5)

def create_prayer_times_layout(self, base_font_size):
    """Создает layout для отображения времён молитв"""
    
    # Получаем актуальные времена молитв
    prayer_times_data = prayer_times_manager.get_prayer_times()
    
    # Маппинг между азербайджанскими названиями и временами из API
    prayer_mapping = {
        'Təhəccüd ---': 'Midnight',
        'İmsak ------': 'Fajr',
        'Günəş ------': 'Sunrise',
        'Günorta ----': 'Dhuhr',
        'İkindi -----': 'Asr',
        'Axşam ------': 'Maghrib',
        'Gecə -------': 'Isha'
    }

    prayer_times_layout = GridLayout(
        cols=2,  # Два столбца: название и время
        size_hint_x=1,  # Занимает всю ширину
        size_hint_y=None,  # Фиксированная высота
        height=base_font_size * 4.0,  # Высота для 6 строк
        padding=(base_font_size * 0.15, 0)   # Отступы по краям layout
    )

    # Получаем текущее время
    current_time = datetime.now().time()
    
    # Создаем Labels для каждого времени молитвы
    for prayer_name, api_key in prayer_mapping.items():
        # Label для названия молитвы
        prayer_name_label = Label(
            text=prayer_name,
            font_name='FontSourceCodePro-Regular',
            font_size=base_font_size * 0.4,  # Маленький размер
            color=(0.6, 0.5, 0.0, 1),  # Темно-желтый для текста молитв
            halign='left',
            text_size=(prayer_times_layout.width * 0.6, None),
            size_hint_x=0.75  # Занимает большую часть ширины
        )
        prayer_name_label.bind(size=prayer_name_label.setter('text_size'))

        # Получаем время молитвы
        prayer_time = prayer_times_data.get(api_key, '00:00')
        
        prayer_time_label = Label(
            text=prayer_time,
            font_name='FontDSEG7-Bold',
            font_size=base_font_size * 0.45,  # Большой размер шрифта
            color=(0.6, 0.5, 0.0, 1),  # Темно-желтый для текста молитв
            halign='right',
            text_size=(prayer_times_layout.width * 0.4, None),
            size_hint_x=0.4  # Занимает меньшую часть ширины
        )
        prayer_time_label.bind(size=prayer_time_label.setter('text_size'))

        # Добавляем Labels в layout
        prayer_times_layout.add_widget(prayer_name_label)
        prayer_times_layout.add_widget(prayer_time_label)

    return prayer_times_layout

# Функция create_next_time_layout заменена на класс NextPrayerTimeBox в отдельном файле
