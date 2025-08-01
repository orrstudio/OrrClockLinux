from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty
from datetime import datetime
from logic.prayer_times import prayer_times_manager
from logic.prayer_time_calculator import prayer_time_calculator

class NextPrayerTimeBox(GridLayout):
    """
    Виджет для отображения времени до следующей молитвы с автообновлением.
    Обновляется каждую минуту для отображения актуального времени до следующей молитвы.
    """
    
    next_prayer_time = StringProperty('00:00')
    time_until = StringProperty('00:00')
    base_font_size = NumericProperty(20)
    
    def __init__(self, base_font_size, **kwargs):
        super().__init__(**kwargs)
        self.base_font_size = base_font_size
        self.cols = 3
        self.size_hint_x = 1
        self.size_hint_y = None
        self.height = base_font_size * 0.7
        
        # Создаем виджеты
        self.next_time_name_1_label = Label(
            text='növbəti\nnamaza',
            font_name='FontSourceCodePro-Regular',
            font_size=base_font_size * 0.2,
            color=(1, 1, 1, 1),
            halign='right',
            size_hint_x=1
        )
        
        self.time_label = Label(
            text='00:00',
            font_name='FontDSEG7-Bold',
            font_size=base_font_size * 0.55,
            color=(1, 1, 1, 1),
            halign='center',
            size_hint_x=1
        )
        
        self.next_time_name_2_label = Label(
            text='dəqiqə\nqalır',
            font_name='FontSourceCodePro-Regular',
            font_size=base_font_size * 0.2,
            color=(1, 1, 1, 1),
            halign='left',
            size_hint_x=1
        )
        
        # Добавляем виджеты в layout
        self.add_widget(self.next_time_name_1_label)
        self.add_widget(self.time_label)
        self.add_widget(self.next_time_name_2_label)
        
        # Запускаем обновление каждую минуту
        self._update_event = None
        
        # Немедленное обновление времени при создании виджета
        self.update_time()
        
    def on_kv_post(self, *args):
        # Запускаем таймер после инициализации виджета в дереве
        self._update_event = Clock.schedule_interval(lambda dt: self.update_time(), 60)  # Обновляем каждую минуту
        
    def update_time(self):
        """Обновляет отображаемое время до следующей молитвы"""
        try:
            # Получаем текущее время
            current_time = datetime.now().time()
            
            # Получаем времена молитв
            prayer_times_data = prayer_times_manager.get_prayer_times()
            
            # Находим следующую молитву
            next_prayer_time_str = prayer_time_calculator.get_next_prayer_time(
                current_time, 
                prayer_times_data
            )
            
            # Вычисляем оставшееся время
            time_until_str = prayer_time_calculator.get_time_until_next_prayer(
                current_time,
                next_prayer_time_str
            )
            
            # Обновляем текст
            self.time_label.text = time_until_str
            
        except Exception as e:
            print(f"[ERROR] Error updating next prayer time: {e}")
    
    def on_parent(self, widget, parent):
        # Отписываемся от таймера при удалении виджета
        if parent is None and hasattr(self, '_update_event') and self._update_event:
            self._update_event.cancel()
