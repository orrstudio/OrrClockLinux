from kivy.clock import Clock
import os
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
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
    
    # Ссылка на главное приложение для доступа к часам
    app = ObjectProperty(None)
    
    def __init__(self, base_font_size, app=None, **kwargs):
        # Используем SVG иконки
        super().__init__(**kwargs)
        self.app = app
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
        print("[DEBUG] Запуск анимации иконок")
        
        if self.is_animating:
            print("[DEBUG] Анимация уже запущена, пропускаем")
            return
            
        self.is_animating = True
        print("[DEBUG] Установлен флаг is_animating = True")
        
        # Останавливаем предыдущие анимации, если они есть
        if hasattr(self, '_anim_left'):
            print("[DEBUG] Отмена предыдущей анимации левой иконки")
            self._anim_left.cancel(self.prayer_icon_left)
        if hasattr(self, '_anim_right'):
            print("[DEBUG] Отмена предыдущей анимации правой иконки")
            self._anim_right.cancel(self.prayer_icon_right)
        
        # Устанавливаем начальный темно-желтый цвет
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        print("[DEBUG] Установлен начальный цвет иконок")
        
        # Устанавливаем ярко-желтый цвет для иконок
        self.prayer_icon_left.color = self.highlight_icon_color
        self.prayer_icon_right.color = self.highlight_icon_color
        
        # Создаем анимацию изменения прозрачности для левой иконки (мигание)
        self._anim_left = Animation(opacity=0.3, duration=0.75) + Animation(opacity=1, duration=0.75)
        self._anim_left.repeat = True
        
        # Создаем анимацию для правой иконки (с небольшой задержкой)
        self._anim_right = Animation(opacity=0.3, duration=0.75) + Animation(opacity=1, duration=0.75)
        self._anim_right.repeat = True
        
        # Запускаем анимации
        print("[DEBUG] Запуск анимаций иконок")
        self._anim_left.start(self.prayer_icon_left)
        Clock.schedule_once(lambda dt: self._anim_right.start(self.prayer_icon_right), 0.25)
        
        # Запускаем анимацию часов, если доступно приложение
        if self.app and hasattr(self.app, 'start_clock_animation'):
            print("[DEBUG] Запуск анимации часов")
            self.app.start_clock_animation()
        else:
            print("[DEBUG] У приложения нет метода start_clock_animation")
            print(f"[DEBUG] Доступные методы: {[m for m in dir(self.app) if not m.startswith('_')]}")
        
        # Если есть ссылка на PrayerTimesBox, запускаем его анимацию
        if hasattr(self, 'prayer_times_box') and self.prayer_times_box:
            print("[DEBUG] Запуск анимации списка молитв")
            self.prayer_times_box.start_animation()
        
        # Останавливаем анимацию через 1 минуту
        print("[DEBUG] Планируем остановку анимации через 60 секунд")
        Clock.schedule_once(self.stop_animation, 60)
    
    def stop_animation(self, *args):
        """Останавливаем анимацию иконок"""
        if not self.is_animating:
            return
            
        print("[DEBUG] Остановка анимации иконок")
        self.is_animating = False
        
        # Отменяем предыдущие анимации
        if hasattr(self, '_anim_left'):
            self._anim_left.cancel(self.prayer_icon_left)
            
        # Возвращаем иконки в исходное состояние (темно-желтый цвет, полная непрозрачность)
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        self.prayer_icon_left.opacity = 1.0
        self.prayer_icon_right.opacity = 1.0
        if hasattr(self, '_anim_right'):
            self._anim_right.cancel(self.prayer_icon_right)
        
        # Возвращаем исходный цвет
        self.prayer_icon_left.color = self.normal_icon_color
        self.prayer_icon_right.color = self.normal_icon_color
        
        # Останавливаем анимацию часов, если доступно приложение
        if self.app and hasattr(self.app, 'stop_clock_animation'):
            print("[DEBUG] Остановка анимации часов")
            self.app.stop_clock_animation()
            
        # Останавливаем анимацию списка молитв, если есть ссылка
        if hasattr(self, 'prayer_times_box') and self.prayer_times_box:
            print("[DEBUG] Остановка анимации списка молитв")
            self.prayer_times_box.stop_animation()
            
        # Отменяем запланированные события
        if hasattr(self, '_stop_event') and self._stop_event:
            self._stop_event.cancel()
            self._stop_event = None
    
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
            
            # Проверяем, изменилось ли время следующего намаза (а не оставшееся время)
            current_next_prayer = f"{next_prayer_time_str}"
            if hasattr(self, 'previous_next_prayer'):
                if self.previous_next_prayer != current_next_prayer:
                    print(f"Время намаза изменилось с {self.previous_next_prayer} на {current_next_prayer}")
                    # Если изменилось время намаза, запускаем анимацию
                    self.animate_icons()
            
            # Сохраняем текущее время следующего намаза для следующей проверки
            self.previous_next_prayer = current_next_prayer
            
            # Обновляем текст
            self.time_label.text = time_until_str
            
        except Exception as e:
            print(f"[ERROR] Error updating next prayer time: {e}")
    
    def on_parent(self, widget, parent):
        # Отписываемся от таймера при удалении виджета
        if parent is None and hasattr(self, '_update_event') and self._update_event:
            self._update_event.cancel()
