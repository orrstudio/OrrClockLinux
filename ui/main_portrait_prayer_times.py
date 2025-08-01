from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from logic.prayer_times import prayer_times_manager
from logic.prayer_time_calculator import prayer_time_calculator
from datetime import datetime, time

class PrayerTimesBox(GridLayout):
    """
    GridLayout для реактивного отображения времён молитв.
    Обновляет только текст Label-ов при изменении данных через callback.
    """
    def __init__(self, base_font_size, **kwargs):
        super().__init__(cols=2, size_hint_x=1, size_hint_y=None, height=base_font_size * 4.0, padding=(base_font_size * 0.15, 0), **kwargs)
        self.base_font_size = base_font_size
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
        # Словари для хранения виджетов меток
        self.prayer_name_labels = {}  # {api_key: Label}
        self.prayer_time_labels = {}  # {api_key: Label}
        self.current_prayer = None  # Текущая активная молитва
        
        self._build_layout()
        prayer_times_manager.add_update_listener(self.refresh_prayer_times)
        self.refresh_prayer_times()
        # Schedule current prayer update every minute
        self._clock_event = Clock.schedule_interval(self.update_current_prayer, 60)

    def _build_layout(self):
        prayer_times_data = prayer_times_manager.get_prayer_times()
        for prayer_name, api_key in self.prayer_mapping.items():
            # Create prayer name label
            prayer_name_label = Label(
                text=prayer_name,
                font_name='FontSourceCodePro-Regular',
                font_size=self.base_font_size * 0.4,
                color=(0.6, 0.5, 0.0, 1),  # Dark yellow for inactive prayer names
                halign='left',
                text_size=(self.width * 0.6, None),
                size_hint_x=0.75
            )
            prayer_name_label.bind(size=prayer_name_label.setter('text_size'))
            
            # Create prayer time label
            prayer_time = prayer_times_data.get(api_key, '00:00')
            prayer_time_label = Label(
                text=prayer_time,
                font_name='FontDSEG7-Bold',
                font_size=self.base_font_size * 0.45,
                color=(0.6, 0.5, 0.0, 1),  # Dark yellow for inactive prayer times
                halign='right',
                text_size=(self.width * 0.4, None),
                size_hint_x=0.4
            )
            prayer_time_label.bind(size=prayer_time_label.setter('text_size'))
            
            # Add widgets to layout
            self.add_widget(prayer_name_label)
            self.add_widget(prayer_time_label)
            
            # Store references to the labels
            self.prayer_name_labels[api_key] = prayer_name_label
            self.prayer_time_labels[api_key] = prayer_time_label
            
        # Schedule the first update of current prayer highlighting
        Clock.schedule_once(self.update_current_prayer, 0.1)

    def refresh_prayer_times(self):
        prayer_times_data = prayer_times_manager.get_prayer_times()
        for api_key, label in self.prayer_time_labels.items():
            label.text = prayer_times_data.get(api_key, '00:00')
        # Update current prayer highlighting
        self.update_current_prayer()

    def get_prayer_info(self, current_time):
        """
        Возвращает кортеж (current_prayer, next_prayer) на основе текущего времени.
        current_prayer - текущая активная молитва
        next_prayer - следующая молитва после текущей
        """
        prayer_times = prayer_times_manager.get_prayer_times()
        current_prayer = None
        next_prayer = None
        found_current = False
        
        # Конвертируем времена молитв в объекты времени
        prayer_times_list = []
        for prayer_name, time_str in prayer_times.items():
            try:
                t = datetime.strptime(time_str, '%H:%M').time()
                prayer_times_list.append((prayer_name, t))
            except (ValueError, AttributeError):
                continue
        
        # Сортируем по времени
        prayer_times_list.sort(key=lambda x: x[1])
        
        # Находим текущую молитву и следующую за ней
        for i, (prayer_name, prayer_time) in enumerate(prayer_times_list):
            if prayer_time > current_time:
                if not found_current:
                    # Если это первое время больше текущего, то предыдущая молитва - текущая
                    current_prayer = prayer_times_list[i-1][0] if i > 0 else prayer_times_list[-1][0]
                    next_prayer = prayer_name
                break
            current_prayer = prayer_name
            next_prayer = prayer_times_list[0][0] if i == len(prayer_times_list) - 1 else None
        
        # Если текущее время после последней молитвы, то текущая - последняя, следующая - первая
        if current_prayer is None and prayer_times_list:
            current_prayer = prayer_times_list[-1][0]
            next_prayer = prayer_times_list[0][0]
        
        return current_prayer, next_prayer
    
    def update_current_prayer(self, *args):
        current_time = datetime.now().time()
        current_prayer, next_prayer = self.get_prayer_info(current_time)
        
        # Цвета из настроек часов
        COLOR_BRIGHT_AQUA = (0.0, 1.0, 1.0, 1.0)    # Аквамарин (aqua)
        COLOR_YELLOW = (1.0, 1.0, 0.0, 1.0)         # Жёлтый (yellow) - используется для следующей молитвы
        COLOR_DARK_YELLOW = (0.6, 0.5, 0.0, 1)      # Тёмно-жёлтый (неактивные элементы)
        
        # Обновляем цвета для всех молитв
        for api_key in self.prayer_name_labels:
            if api_key == current_prayer:
                # Текущая молитва - яркий аквамарин
                self.prayer_name_labels[api_key].color = COLOR_BRIGHT_AQUA
                self.prayer_time_labels[api_key].color = COLOR_BRIGHT_AQUA
            elif api_key == next_prayer:
                # Следующая молитва - жёлтый (как в настройках часов)
                self.prayer_name_labels[api_key].color = COLOR_YELLOW
                self.prayer_time_labels[api_key].color = COLOR_YELLOW
            else:
                # Остальные молитвы - тёмно-жёлтый
                self.prayer_name_labels[api_key].color = COLOR_DARK_YELLOW
                self.prayer_time_labels[api_key].color = COLOR_DARK_YELLOW
        
        # Обновляем ссылку на текущую молитву
        self.current_prayer = current_prayer
    
    def on_parent(self, widget, parent):
        # Automatically unsubscribe when removed from screen
        if parent is None:
            prayer_times_manager.remove_update_listener(self.refresh_prayer_times)
            # Also cancel the clock event
            if hasattr(self, '_clock_event'):
                self._clock_event.cancel()

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
            color=(0.8, 0.7, 0.1, 1),  # Тускло-желтый цвет
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
            color=(0.0, 0.75, 0.75, 1.0),  # Аквамариновый цвет
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
