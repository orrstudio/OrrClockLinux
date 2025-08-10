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
        
        # Для анимации мигания времени следующего намаза
        self._is_time_blinking = False
        self._blink_event = None
        self._blink_opacity = 1.0
        self._blink_direction = -1  # Направление изменения прозрачности
        
        # Для анимации предупреждения за 30 минут
        self._is_30min_warning = False
        self._30min_blink_event = None
        self._30min_blink_opacity = 1.0
        self._30min_blink_direction = -1
        
        # Для анимации предупреждения за 45 минут
        self._is_45min_warning = False
        self._45min_blink_event = None
        self._45min_blink_opacity = 1.0
        self._45min_blink_direction = -1
        
        # Для анимации предупреждения за 60 минут
        self._is_60min_warning = False
        self._60min_blink_event = None
        self._60min_blink_opacity = 1.0
        self._60min_blink_direction = -1
        
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
        self._update_event = Clock.schedule_interval(lambda dt: self.update_time(), 5)  # Обновляем каждую секунду
        
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
            
        # Останавливаем мигание времени, если оно активно
        self._stop_time_blink()
    
    def _update_time_blink(self, dt):
        """Обновление анимации мигания времени следующего намаза"""
        if not self._is_time_blinking:
            return
            
        # Изменяем прозрачность
        self._blink_opacity += self._blink_direction * 0.1
        
        # Меняем направление, если достигли границ
        if self._blink_opacity <= 0.3:
            self._blink_opacity = 0.3
            self._blink_direction = 1
        elif self._blink_opacity >= 1.0:
            self._blink_opacity = 1.0
            self._blink_direction = -1
            
        # Применяем прозрачность к метке времени
        if hasattr(self, 'time_label'):
            self.time_label.opacity = self._blink_opacity
    
    def _start_time_blink(self):
        """Запуск анимации мигания времени следующего намаза"""
        if self._is_time_blinking:
            return
            
        print("[DEBUG] Запуск мигания времени следующего намаза")
        self._is_time_blinking = True
        self._blink_opacity = 1.0
        self._blink_direction = -1
        
        # Запускаем обновление анимации каждые 100 мс
        self._blink_event = Clock.schedule_interval(self._update_time_blink, 0.1)
    
    def _stop_time_blink(self):
        """Остановка анимации мигания времени следующего намаза"""
        if not self._is_time_blinking:
            return
            
        print("[DEBUG] Остановка мигания времени следующего намаза")
        self._is_time_blinking = False
        
        # Отменяем запланированное обновление
        if self._blink_event:
            self._blink_event.cancel()
            self._blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _update_30min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 30 минут"""
        if not self._is_30min_warning or not hasattr(self, 'time_label'):
            return
            
        # Изменяем прозрачность
        self._30min_blink_opacity += self._30min_blink_direction * 0.1
        
        # Меняем направление, если достигли границ
        if self._30min_blink_opacity <= 0.3:
            self._30min_blink_opacity = 0.3
            self._30min_blink_direction = 1
        elif self._30min_blink_opacity >= 1.0:
            self._30min_blink_opacity = 1.0
            self._30min_blink_direction = -1
            
        # Применяем прозрачность к метке времени
        self.time_label.opacity = self._30min_blink_opacity
    
    def _start_60min_warning(self):
        """Запуск анимации предупреждения за 60 минут"""
        if self._is_60min_warning:
            return
            
        print("[DEBUG] Запуск анимации предупреждения за 60 минут")
        self._is_60min_warning = True
        self._60min_blink_opacity = 1.0
        self._60min_blink_direction = -1
        
        # Запускаем обновление анимации каждые 100 мс
        self._60min_blink_event = Clock.schedule_interval(self._update_60min_blink, 0.1)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_60min_warning(), 60)
        
    def _update_60min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 60 минут"""
        if not self._is_60min_warning or not hasattr(self, 'time_label'):
            return
            
        # Изменяем прозрачность
        self._60min_blink_opacity += self._60min_blink_direction * 0.1
        
        # Меняем направление, если достигли границ
        if self._60min_blink_opacity <= 0.3:
            self._60min_blink_opacity = 0.3
            self._60min_blink_direction = 1
        elif self._60min_blink_opacity >= 1.0:
            self._60min_blink_opacity = 1.0
            self._60min_blink_direction = -1
            
        # Применяем прозрачность к метке времени
        self.time_label.opacity = self._60min_blink_opacity
        
    def _stop_60min_warning(self):
        """Остановка анимации предупреждения за 60 минут"""
        if not self._is_60min_warning:
            return
            
        print("[DEBUG] Остановка анимации предупреждения за 60 минут")
        self._is_60min_warning = False
        
        # Отменяем запланированное обновление
        if self._60min_blink_event:
            self._60min_blink_event.cancel()
            self._60min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _start_45min_warning(self):
        """Запуск анимации предупреждения за 45 минут"""
        if self._is_45min_warning:
            return
            
        print("[DEBUG] Запуск анимации предупреждения за 45 минут")
        self._is_45min_warning = True
        self._45min_blink_opacity = 1.0
        self._45min_blink_direction = -1
        
        # Запускаем обновление анимации каждые 100 мс
        self._45min_blink_event = Clock.schedule_interval(self._update_45min_blink, 0.1)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_45min_warning(), 60)
        
    def _update_45min_blink(self, dt):
        """Обновление анимации мигания предупреждения за 45 минут"""
        if not self._is_45min_warning or not hasattr(self, 'time_label'):
            return
            
        # Изменяем прозрачность
        self._45min_blink_opacity += self._45min_blink_direction * 0.1
        
        # Меняем направление, если достигли границ
        if self._45min_blink_opacity <= 0.3:
            self._45min_blink_opacity = 0.3
            self._45min_blink_direction = 1
        elif self._45min_blink_opacity >= 1.0:
            self._45min_blink_opacity = 1.0
            self._45min_blink_direction = -1
            
        # Применяем прозрачность к метке времени
        self.time_label.opacity = self._45min_blink_opacity
        
    def _stop_45min_warning(self):
        """Остановка анимации предупреждения за 45 минут"""
        if not self._is_45min_warning:
            return
            
        print("[DEBUG] Остановка анимации предупреждения за 45 минут")
        self._is_45min_warning = False
        
        # Отменяем запланированное обновление
        if self._45min_blink_event:
            self._45min_blink_event.cancel()
            self._45min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
            
    def _start_30min_warning(self):
        """Запуск анимации предупреждения за 30 минут"""
        if self._is_30min_warning:
            return
            
        print("[DEBUG] Запуск анимации предупреждения за 30 минут")
        self._is_30min_warning = True
        self._30min_blink_opacity = 1.0
        self._30min_blink_direction = -1
        
        # Запускаем обновление анимации каждые 100 мс
        self._30min_blink_event = Clock.schedule_interval(self._update_30min_blink, 0.1)
        
        # Останавливаем анимацию через 1 минуту
        Clock.schedule_once(lambda dt: self._stop_30min_warning(), 60)
    
    def _stop_30min_warning(self):
        """Остановка анимации предупреждения за 30 минут"""
        if not self._is_30min_warning:
            return
            
        print("[DEBUG] Остановка анимации предупреждения за 30 минут")
        self._is_30min_warning = False
        
        # Отменяем запланированное обновление
        if self._30min_blink_event:
            self._30min_blink_event.cancel()
            self._30min_blink_event = None
            
        # Восстанавливаем полную видимость
        if hasattr(self, 'time_label'):
            self.time_label.opacity = 1.0
    
    def _is_within_15_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза 15 минут или меньше"""
        return self._get_minutes_until_prayer(current_time, next_prayer_time_str) <= 15
    
    def _is_exactly_30_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 30 минут"""
        minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
        return minutes == 30
        
    def _is_exactly_45_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 45 минут"""
        minutes = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
        return minutes == 45
        
    def _is_exactly_60_minutes_before_prayer(self, current_time, next_prayer_time_str):
        """Проверяет, осталось ли до намаза ровно 60 минут, включая случай с переходом на следующий день"""
        try:
            # Преобразуем время намаза в объект datetime
            prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            
            # Получаем текущую дату
            current_date = datetime.now().date()
            
            # Создаем объекты datetime для текущего времени и времени намаза
            current_dt = datetime.combine(current_date, current_time)
            prayer_dt = datetime.combine(current_date, prayer_time)
            
            # Если время намаза уже прошло сегодня, берем намаз на следующий день
            if prayer_dt <= current_dt:
                prayer_dt += timedelta(days=1)
                print(f"[DEBUG] Время намаза {next_prayer_time_str} перенесено на следующий день")
            
            # Вычисляем разницу во времени
            time_diff = prayer_dt - current_dt
            
            # Преобразуем разницу в минуты
            minutes = int(time_diff.total_seconds() / 60)
            
            print(f"[DEBUG] Проверка 60 минут: текущее время={current_time}, намаз={prayer_dt.time()}, осталось минут={minutes}")
            
            if minutes == 60:
                print(f"[DEBUG] Найдено 60 минут до намаза {prayer_dt.time()}")
                return True
            else:
                print(f"[DEBUG] До намаза {prayer_dt.time()} осталось {minutes} минут (не 60)")
                return False
                
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке 60 минут до намаза: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_minutes_until_prayer(self, current_time, next_prayer_time_str):
        """Возвращает количество минут до намаза"""
        try:
            # Преобразуем время намаза в объект datetime
            prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            
            # Получаем текущую дату
            current_date = datetime.now().date()
            
            # Создаем объекты datetime для текущего времени и времени намаза
            current_dt = datetime.combine(current_date, current_time)
            prayer_dt = datetime.combine(current_date, prayer_time)
            
            # Если время намаза уже прошло сегодня, берем намаз на следующий день
            if prayer_dt < current_dt:
                prayer_dt += timedelta(days=1)
                print(f"[DEBUG] Время намаза {next_prayer_time_str} перенесено на следующий день")
            
            # Вычисляем разницу во времени
            time_diff = prayer_dt - current_dt
            
            # Преобразуем разницу в минуты
            minutes = int(time_diff.total_seconds() / 60)
            
            print(f"[DEBUG] Расчет времени до намаза: текущее={current_time}, намаз={next_prayer_time_str}, минут до намаза={minutes}")
            
            return minutes
                
        except Exception as e:
            print(f"[ERROR] Ошибка при вычислении времени до намаза: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def update_time(self):
        """Обновляет отображаемое время до следующей молитвы"""
        try:
            # Получаем текущее время
            now = datetime.now()
            current_time = now.time()
            
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
            
            # Проверяем, наступило ли уже время следующего намаза
            next_prayer_time = datetime.strptime(next_prayer_time_str, '%H:%M').time()
            current_date = now.date()
            prayer_dt = datetime.combine(current_date, next_prayer_time)
            current_dt = datetime.combine(current_date, current_time)
            
            # Получаем оставшееся время в минутах
            minutes_until = self._get_minutes_until_prayer(current_time, next_prayer_time_str)
            
            # Управление анимациями в зависимости от оставшегося времени
            print(f"[DEBUG] Управление анимациями: текущее время={current_time}, намаз={next_prayer_time_str}, минут до намаза={minutes_until}")
            
            # Проверяем, наступило ли время намаза
            if current_dt >= prayer_dt:
                # Время намаза наступило, останавливаем все анимации
                print("[DEBUG] Время намаза наступило или прошло, останавливаем все анимации")
                if self._is_time_blinking:
                    print(f"[DEBUG] Останавливаем быстрое мигание (время намаза наступило)")
                    self._stop_time_blink()
                if self._is_30min_warning:
                    print("[DEBUG] Останавливаем 30-минутное предупреждение (время намаза наступило)")
                    self._stop_30min_warning()
                if self._is_45min_warning:
                    print("[DEBUG] Останавливаем 45-минутное предупреждение (время намаза наступило)")
                    self._stop_45min_warning()
                if self._is_60min_warning:
                    print("[DEBUG] Останавливаем 60-минутное предупреждение (время намаза наступило)")
                    self._stop_60min_warning()
            elif minutes_until <= 15:
                # Менее 15 минут до намаза - запускаем быстрое мигание
                if not self._is_time_blinking:
                    print(f"[DEBUG] До намаза {next_prayer_time_str} осталось {minutes_until} минут, запускаем быстрое мигание")
                    self._start_time_blink()
                # Останавливаем другие предупреждения, если они активны
                if self._is_30min_warning:
                    self._stop_30min_warning()
                if self._is_45min_warning:
                    self._stop_45min_warning()
                if self._is_60min_warning:
                    self._stop_60min_warning()
            elif self._is_exactly_30_minutes_before_prayer(current_time, next_prayer_time_str):
                # Ровно 30 минут до намаза - запускаем 30-минутное предупреждение
                if not self._is_30min_warning and not self._is_time_blinking:
                    print(f"[DEBUG] До намаза {next_prayer_time_str} осталось 30 минут, запускаем 30-минутное предупреждение")
                    self._start_30min_warning()
                # Останавливаем другие предупреждения, если они активны
                if self._is_45min_warning:
                    self._stop_45min_warning()
                if self._is_60min_warning:
                    self._stop_60min_warning()
            elif self._is_exactly_45_minutes_before_prayer(current_time, next_prayer_time_str):
                # Ровно 45 минут до намаза - запускаем 45-минутное предупреждение
                if not self._is_45min_warning and not self._is_time_blinking and not self._is_30min_warning:
                    print(f"[DEBUG] До намаза {next_prayer_time_str} осталось 45 минут, запускаем 45-минутное предупреждение")
                    self._start_45min_warning()
                # Останавливаем 60-минутное предупреждение, если оно активно
                if self._is_60min_warning:
                    self._stop_60min_warning()
            elif self._is_exactly_60_minutes_before_prayer(current_time, next_prayer_time_str):
                # Ровно 60 минут до намаза - запускаем 60-минутное предупреждение
                print(f"[DEBUG] Проверка условий для 60-минутного предупреждения:")
                print(f"[DEBUG] _is_60min_warning: {self._is_60min_warning}")
                print(f"[DEBUG] _is_time_blinking: {self._is_time_blinking}")
                print(f"[DEBUG] _is_30min_warning: {self._is_30min_warning}")
                print(f"[DEBUG] _is_45min_warning: {self._is_45min_warning}")
                
                if not self._is_60min_warning and not self._is_time_blinking and not self._is_30min_warning and not self._is_45min_warning:
                    print(f"[DEBUG] До намаза {next_prayer_time_str} остался 1 час, запускаем 60-минутное предупреждение")
                    self._start_60min_warning()
                else:
                    print("[DEBUG] 60-минутное предупреждение не запущено из-за активных анимаций")
            else:
                # В остальных случаях останавливаем все анимации, если их условия не выполняются
                if self._is_time_blinking and minutes_until > 15:
                    print(f"[DEBUG] Останавливаем быстрое мигание, так как условия не выполняются")
                    self._stop_time_blink()
                if self._is_30min_warning and not self._is_exactly_30_minutes_before_prayer(current_time, next_prayer_time_str):
                    print(f"[DEBUG] Останавливаем 30-минутное предупреждение, так как условия не выполняются")
                    self._stop_30min_warning()
                if self._is_45min_warning and not self._is_exactly_45_minutes_before_prayer(current_time, next_prayer_time_str):
                    print(f"[DEBUG] Останавливаем 45-минутное предупреждение, так как условия не выполняются")
                    self._stop_45min_warning()
                if self._is_60min_warning and not self._is_exactly_60_minutes_before_prayer(current_time, next_prayer_time_str):
                    print(f"[DEBUG] Останавливаем 60-минутное предупреждение, так как условия не выполняются")
                    self._stop_60min_warning()
            
            # Для отладки выводим в консоль информацию о смене времени
            debug_info = f"Текущее время: {current_time.strftime('%H:%M:%S')}, "
            debug_info += f"Следующий намаз: {next_prayer_time_str}, "
            debug_info += f"Осталось: {time_until_str}"
            if self._is_time_blinking:
                debug_info += " [МИГАНИЕ АКТИВНО]"
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
