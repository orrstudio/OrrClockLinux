from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
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
        self._build_layout()
        prayer_times_manager.add_update_listener(self.refresh_prayer_times)
        self.refresh_prayer_times()
        
        # Запускаем таймер для обновления активной молитвы каждую минуту
        from kivy.clock import Clock
        self._update_event = Clock.schedule_interval(lambda dt: self.refresh_prayer_times(), 60)

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
        
        for i, (api_key, prayer_time) in enumerate(prayer_times_list):
            if prayer_time > current_time:
                next_prayer = api_key
                break
            current_prayer = api_key
        
        # Если текущее время позже последней молитвы, то активной считается последняя молитва дня,
        # а следующей - первая молитва следующего дня
        if current_prayer is None and prayer_times_list:
            current_prayer = prayer_times_list[-1][0]
        if next_prayer is None and prayer_times_list:
            next_prayer = prayer_times_list[0][0]
        
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
