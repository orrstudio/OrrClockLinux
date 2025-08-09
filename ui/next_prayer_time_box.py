from kivy.clock import Clock
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.animation import Animation
from datetime import datetime, timedelta
from kivy.core.text import LabelBase
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
        # Используем SVG иконки
        super().__init__(**kwargs)
        self.base_font_size = base_font_size
        self.cols = 3
        self.size_hint_x = 1
        self.size_hint_y = None
        self.height = base_font_size * 0.7  # Увеличили высоту контейнера
        self.padding = [0, base_font_size * 0, 0, base_font_size * 0]  # Добавили отступы сверху и снизу
        
        # Цвета для анимации иконок
        self.normal_icon_color = (0.6, 0.5, 0.0, 1)  # Темно-желтый
        self.highlight_icon_color = (1.0, 0.84, 0.0, 1)  # Ярко-желтый
        self.black_color = (0, 0, 0, 1)  # Черный цвет
        self.is_animating = False
        self.animation_duration = 0.75  # Длительность анимации в секундах
        
        # Создаем иконки молитвенного времени (используем иконку prayer_times из Material Symbols)
        self.prayer_icon_left = Label(
            text='\ueab2',  # Код иконки prayer_times из Material Symbols
            font_name=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf'),
            font_size=base_font_size * 0.5,
            color=self.normal_icon_color  # Используем свойство для цвета
        )
        
        self.time_label = Label(
            text='00:00',
            font_name='FontDSEG7-Bold',
            font_size=base_font_size * 0.55,
            color=(1, 0, 0, 1),  # Красный для времени следующей молитвы
            halign='center',
            size_hint_x=1
        )
        
        self.prayer_icon_right = Label(
            text='\uf353',  # Код иконки prayer_times из Material Symbols
            font_name=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf'),
            font_size=base_font_size * 0.5,
            color=self.normal_icon_color  # Используем свойство для цвета
        )
        
        # Добавляем виджеты в layout
        self.add_widget(self.prayer_icon_left)
        self.add_widget(self.time_label)
        self.add_widget(self.prayer_icon_right)
        
        # Запускаем обновление каждую минуту
        self._update_event = None
        
        # Немедленное обновление времени при создании виджета
        self.update_time()
        
    def on_kv_post(self, *args):
        # Запускаем таймер после инициализации виджета в дереве
        self._update_event = Clock.schedule_interval(lambda dt: self.update_time(), 60)  # Обновляем каждую минуту
        
    def animate_icons(self, *args):
        """Анимация изменения цвета иконок"""
        if self.is_animating:
            return
            
        self.is_animating = True
        
        # Останавливаем предыдущие анимации, если они есть
        if hasattr(self, '_anim_left'):
            self._anim_left.cancel(self.prayer_icon_left)
        if hasattr(self, '_anim_right'):
            self._anim_right.cancel(self.prayer_icon_right)
        
        # Устанавливаем начальный темно-желтый цвет
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        
        # Создаем анимацию для левой иконки
        self._anim_left = (
            Animation(color=self.highlight_icon_color, duration=self.animation_duration) +  # Темно-желтый -> Ярко-желтый
            Animation(color=self.black_color, duration=self.animation_duration) +           # Ярко-желтый -> Черный
            Animation(color=self.highlight_icon_color, duration=self.animation_duration)    # Черный -> Ярко-желтый
        )
        self._anim_left.repeat = True
        
        # Создаем анимацию для правой иконки
        self._anim_right = (
            Animation(color=self.highlight_icon_color, duration=self.animation_duration) +  # Темно-желтый -> Ярко-желтый
            Animation(color=self.black_color, duration=self.animation_duration) +           # Ярко-желтый -> Черный
            Animation(color=self.highlight_icon_color, duration=self.animation_duration)    # Черный -> Ярко-желтый
        )
        self._anim_right.repeat = True
        
        # Применяем анимацию к иконкам
        self._anim_left.start(self.prayer_icon_left)
        self._anim_right.start(self.prayer_icon_right)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(self.stop_animation, 60)
    
    def stop_animation(self, *args):
        """Останавливаем анимацию и возвращаем исходный цвет"""
        if hasattr(self, '_anim_left'):
            self._anim_left.cancel(self.prayer_icon_left)
        if hasattr(self, '_anim_right'):
            self._anim_right.cancel(self.prayer_icon_right)
            
        self.is_animating = False
        # Возвращаем исходный темно-желтый цвет
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
    
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
            
            # Для отладки выводим в консоль информацию о смене времени
            debug_info = f"Текущее время: {current_time.strftime('%H:%M:%S')}, "
            debug_info += f"Следующий намаз: {next_prayer_time_str}, "
            debug_info += f"Осталось: {time_until_str}"
            print(debug_info)
            
            # Проверяем, изменилось ли время намаза (сравниваем с предыдущим значением)
            if hasattr(self, 'previous_time_str') and self.previous_time_str != time_until_str:
                print(f"Время изменилось с {self.previous_time_str} на {time_until_str}")
                # Если время изменилось, запускаем анимацию
                self.animate_icons()
            
            # Сохраняем текущее время для следующей проверки
            self.previous_time_str = time_until_str
            
            # Обновляем текст
            self.time_label.text = time_until_str
            
        except Exception as e:
            print(f"[ERROR] Error updating next prayer time: {e}")
    
    def on_parent(self, widget, parent):
        # Отписываемся от таймера при удалении виджета
        if parent is None and hasattr(self, '_update_event') and self._update_event:
            self._update_event.cancel()
