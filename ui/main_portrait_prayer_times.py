from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.animation import Animation
from kivy.clock import Clock
from logic.prayer_times import prayer_times_manager
from logic.prayer_time_calculator import prayer_time_calculator
from datetime import datetime

class PrayerTimesBox(GridLayout):
    """
    GridLayout для реактивного отображения времён молитв.
    Обновляет только текст Label-ов при изменении данных через callback.
    """
    def __init__(self, base_font_size, **kwargs):
        super().__init__(cols=2, size_hint_x=1, size_hint_y=None, height=base_font_size * 4.0, padding=(base_font_size * 0.15, 0), **kwargs)
        self.base_font_size = base_font_size
        self._update_event = None  # Для хранения ссылки на событие обновления
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
        self._next_prayer_blink_event = None
        self._is_next_prayer_blinking = False
        
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
    
    def _start_next_prayer_blink(self, next_prayer_key):
        """Запускает анимацию мигания для следующего намаза"""
        if self._is_next_prayer_blinking:
            return
            
        print("[DEBUG] Запуск мигания следующего намаза:", next_prayer_key)
        self._is_next_prayer_blinking = True
        self._next_prayer_key = next_prayer_key
        self._update_next_prayer_blink()
    
    def _stop_next_prayer_blink(self):
        """Останавливает анимацию мигания для следующего намаза"""
        if not self._is_next_prayer_blinking:
            return
            
        print("[DEBUG] Остановка мигания следующего намаза")
        self._is_next_prayer_blinking = False
        
        # Отменяем запланированное событие мигания
        if self._next_prayer_blink_event:
            self._next_prayer_blink_event.cancel()
            self._next_prayer_blink_event = None
        
        # Восстанавливаем полную непрозрачность для следующего намаза
        if hasattr(self, '_next_prayer_key') and self._next_prayer_key in self.prayer_labels:
            labels = self.prayer_labels[self._next_prayer_key]
            labels['time_label'].opacity = 1.0
            labels['name_label'].opacity = 1.0
    
    def _update_next_prayer_blink(self, *args):
        """Обновляет анимацию мигания для следующего намаза"""
        if not self._is_next_prayer_blinking or not hasattr(self, '_next_prayer_key'):
            return
            
        # Получаем метки следующего намаза
        labels = self.prayer_labels.get(self._next_prayer_key)
        if not labels:
            return
        
        # Инвертируем прозрачность (мигание)
        current_opacity = labels['time_label'].opacity
        new_opacity = 0.3 if current_opacity > 0.7 else 1.0
        
        # Применяем новую прозрачность
        labels['time_label'].opacity = new_opacity
        labels['name_label'].opacity = new_opacity
        
        # Запускаем следующее обновление через 0.5 секунды
        self._next_prayer_blink_event = Clock.schedule_once(
            self._update_next_prayer_blink, 0.5
        )
    
    def refresh_prayer_times(self):
        prayer_times_data = prayer_times_manager.get_prayer_times()
        current_time = datetime.now().time()
        
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
        
        # Проверяем, нужно ли запускать мигание для следующей молитвы
        if next_prayer_time and next_prayer:
            if self._is_within_15_minutes_before_prayer(next_prayer_time, current_time):
                if not self._is_next_prayer_blinking or getattr(self, '_next_prayer_key', None) != next_prayer:
                    self._start_next_prayer_blink(next_prayer)
            else:
                self._stop_next_prayer_blink()
        else:
            self._stop_next_prayer_blink()
        
        # Обновляем текст и цвет для всех меток
        for api_key, labels in self.prayer_labels.items():
            # Обновляем текст времени молитвы
            labels['time_label'].text = prayer_times_data.get(api_key, '00:00')
            
            # Устанавливаем цвета
            is_active = api_key == current_prayer
            is_next = api_key == next_prayer
            
            if is_active:
                # Аквамариновый для активной молитвы
                color = (0, 1, 1, 1)
            elif is_next:
                # Жёлтый для следующей молитвы
                color = (1, 1, 0, 1)
            else:
                # Темно-желтый для неактивных молитв
                color = (0.6, 0.5, 0.0, 1)
            
            # Применяем цвет к времени и названию молитвы
            labels['time_label'].color = color
            labels['name_label'].color = color

    def on_parent(self, widget, parent):
        # Автоматическая отписка при удалении с экрана
        if parent is None:
            prayer_times_manager.remove_update_listener(self.refresh_prayer_times)
            if hasattr(self, '_update_event') and self._update_event:
                self._update_event.cancel()
            self.stop_animation()
            
    def start_animation(self):
        """Запускаем анимацию: делаем все молитвы прозрачными, кроме текущей"""
        if self._is_animating:
            return
            
        self._is_animating = True
        print("[DEBUG] Запуск анимации списка молитв")
        
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
                labels['time_label'].opacity = 0
                labels['name_label'].opacity = 0
        
        # Запускаем анимацию мигания для активной молитвы
        self._update_animation()
        
        # Останавливаем анимацию через 60 секунд
        self._animation_event = Clock.schedule_once(self.stop_animation, 60)
    
    def stop_animation(self, *args):
        """Останавливаем анимацию и обновляем цвета в соответствии с текущим временем"""
        if not self._is_animating:
            return
            
        print("[DEBUG] Остановка анимации списка молитв")
        self._is_animating = False
        
        # Отменяем запланированные события
        if self._animation_event:
            self._animation_event.cancel()
            self._animation_event = None
        
        # Отменяем все анимации и восстанавливаем видимость всех молитв
        for api_key, labels in self.prayer_labels.items():
            # Отменяем анимации
            Animation.cancel_all(labels['time_label'])
            Animation.cancel_all(labels['name_label'])
            
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
    
    def _update_animation(self):
        """Обновляет анимацию мигания активной молитвы"""
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
            
        # Создаем анимацию мигания для активной молитвы
        anim = Animation(opacity=0.3, duration=0.75) + Animation(opacity=1.0, duration=0.75)
        anim.repeat = True
        
        # Применяем анимацию к меткам времени и названия молитвы
        anim.start(labels['time_label'])
        anim.start(labels['name_label'])
        
        # Запускаем следующее обновление через 1.5 секунды (длительность полного цикла)
        Clock.schedule_once(lambda dt: self._update_animation(), 1.5)

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
