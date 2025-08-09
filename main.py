import kivy
from datetime import datetime
import math
from kivy.animation import Animation
kivy.require('2.2.1')

# Импорты базовых классов Kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.input.motionevent import MotionEvent
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.metrics import sp, dp
from kivy.uix.anchorlayout import AnchorLayout

# Импорты локальных модулей приложения
from ui.settings_window import SettingsWindow
from ui.settings_manager import SettingsManager
from ui.clock_widget import ClockWidget
from data.database import SettingsDatabase
from logic.clock_functions import get_formatted_time
from ui.main_portrait import create_portrait_widgets
from ui.main_landscape import create_landscape_prayer_times_table
from ui.main_square import create_square_prayer_times_table
from logic.display_utils import is_mobile_device
from logic.fonts_registration import register_fonts
from logic.prayer_time_calculator import prayer_time_calculator
from logic.hijri_date import hijri_date_manager
from logic.midnight_update_manager import MidnightUpdateManager
from logic.prayer_times import prayer_times_manager

class MainWindowApp(App):
    def on_new_day(self):
        """
        Метод вызывается в полночь для пересчёта и обновления всех данных, зависящих от даты.
        - Проверяет и обновляет данные в базе (молитвы, хиджра и т.д.)
        - Обновляет все связанные с датой элементы UI
        - Запускает все необходимые проверки для нового дня
        """
        # Принудительно обновляем дату хиджры (пересчёт и кэширование)
        hijri_date_manager.get_hijri_date()

        # Принудительно обновляем времена молитв (запрос к API и обновление базы)
        print("[DEBUG] on_new_day: вызываю update_prayer_times() ДО пересоздания layout")
        prayer_times_manager.update_prayer_times()

        # Пересоздаём/обновляем UI для нового дня
        if hasattr(self, 'layout'):
            self.on_window_resize(Window, Window.width, Window.height)
            print(f"[DEBUG] on_new_day: self.prayer_times_box = {getattr(self, 'prayer_times_box', None)}, type = {type(getattr(self, 'prayer_times_box', None))}")
            if hasattr(self, 'prayer_times_box') and self.prayer_times_box:
                print("[DEBUG] on_new_day: вызываю refresh_prayer_times() у self.prayer_times_box (после update_prayer_times и пересоздания layout)")
                self.prayer_times_box.refresh_prayer_times()
        
        # Обновляем заголовок (время)
        if hasattr(self, 'title_label'):
            self.title_label.text = self.get_current_time(self.is_colon_visible)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_window = 'main'
        # Инициализируем базу данных настроек
        self.settings_db = SettingsDatabase()
        
    def get_time_until_next_prayer(self, prayer_times_data):
        """
        Вычисляет и возвращает время до следующей молитвы
        Args:
            prayer_times_data: словарь с временами молитв
        Returns:
            str: время до следующей молитвы в формате HH:MM
        """
        current_time = datetime.now().time()
        next_prayer_time = self.prayer_time_calculator.get_next_prayer_time(current_time, prayer_times_data)
        return self.prayer_time_calculator.get_time_until_next_prayer(current_time, next_prayer_time)
        
    def build(self):
        # --- MidnightUpdateManager ---
        self.midnight_update_manager = MidnightUpdateManager()
        self.midnight_update_manager.register_callback(self.on_new_day)
        # --- END MidnightUpdateManager ---
        # Пытаемся применить сохраненные настройки окна
        if not is_mobile_device():
            self.settings_db.apply_window_settings(Window)

        # Создаем менеджер настроек перед применением цвета
        self.settings_manager = SettingsManager(None, self)
        
        # Регистрация шрифтов
        register_fonts()
        
        # Создаем глобальный экземпляр для вычисления времени молитв
        self.prayer_time_calculator = prayer_time_calculator
        
        # Черный фон
        Window.clearcolor = (0, 0, 0, 1)
        
        # Привязываем обработчик двойного касания
        Window.bind(on_touch_down=self.on_window_touch_down_double_tap)
        
        # Основной layout - GridLayout
        self.layout = GridLayout(
            cols=1,  # Один столбец
            spacing=Window.height * 0.01,  # Увеличить отступ между виджетами
            padding=0
        )
        
        # Создаем заголовок
        self.title_label = Label(
            text=self.get_current_time(), 
            font_name="fonts/DSEG-Classic/DSEG7Classic-Bold.ttf",
            color=(0, 1, 0, 1),  # Зеленый цвет для часов
            size_hint_x=1,  # занимает всю ширину
            size_hint_y=None,  # отключаем автоматическую высоту
            height=str(Window.width * 0.3) + 'dp',  # высота зависит от ширины
            pos_hint={'top': 1},  # прижат к верху
            font_size=str(Window.width // 3.5) + 'sp',  # начальный размер шрифта
            halign='center',  # центрирование текста
            opacity=1,  # Начальная прозрачность (1 - полностью непрозрачный)
        )
        
        # Привязываем обновление размера шрифта и высоты к изменению размера окна
        Window.bind(width=self.update_title_font_size)
        Window.bind(height=self.update_title_height)
        Window.bind(on_resize=self.on_window_resize)
        
        # Добавляем заголовок в начало макета
        self.layout.add_widget(self.title_label)

        # Определение ориентации и создание соответствующей таблицы молитв
        current_orientation = self.get_current_orientation()
        
        if current_orientation == 'portrait':
            portrait_layout = GridLayout(
                cols=1,
                spacing=dp(0),
                size_hint=(1, 1)
            )
            
            # Создаем и заполняем портретный layout
            portrait_layout = self.create_portrait_widgets(portrait_layout)
            main_window_body = portrait_layout
        elif current_orientation == 'landscape':
            main_window_body = create_landscape_prayer_times_table(self)
        else:  # square
            main_window_body = create_square_prayer_times_table(self)
        
        # Добавление таблицы молитв, если она не None
        if main_window_body:
            self.layout.add_widget(main_window_body)

        # Запускаем таймер обновления времени и мигания точек каждые 0.5 секунды
        self.is_colon_visible = True
        Clock.schedule_interval(self.update_time_with_colon, 0.5)

        # Устанавливаем текущее окно
        self.current_window = 'main'
        
        # Применяем сохраненный цвет
        Clock.schedule_once(self.apply_initial_color, 0.1)
        
        return self.layout

    def get_current_orientation(self):
        """
        Точное определение ориентации экрана
        """
        width, height = Window.size
        
        if width > height * 1.2:
            return 'landscape'
        elif height > width * 1.2:
            return 'portrait'
        else:
            return 'square'

    def save_main_window_state(self):
        """
        Сохраняет текущие параметры главного окна
        """
        if not is_mobile_device() and hasattr(self, 'settings_db'):
            # Сохраняем текущие параметры окна
            self.settings_db.save_window_settings(
                width=Window.width,
                height=Window.height,
                x=Window.left,
                y=Window.top
            )
    
    def restore_main_window_state(self):
        """
        Восстанавливает сохраненные параметры главного окна
        """
        if not is_mobile_device() and hasattr(self, 'settings_db'):
            self.settings_db.apply_window_settings(Window)
    
    def on_window_touch_down_double_tap(self, window, touch):
        """
        Обработчик двойного касания
        """
        if touch.is_double_tap:
            # Открываем окно настроек
            self.settings_manager = SettingsManager(None, self)
            self.settings_manager.open_settings_window()
        return False

    def update_title_font_size(self, instance, width):
        """
        Обновляем размер шрифта в зависимости от ширины окна
        """
        self.title_label.font_size = str(width // 3.5) + 'sp'

    def update_title_height(self, instance, height):
        """
        Обновляем высоту заголовка в зависимости от ширины окна
        """
        self.title_label.height = str(Window.width * 0.3) + 'dp'

    def get_current_time(self, show_colon=True):
        """
        Получаем текущее время с возможностью скрыть двоеточие
        """
        return get_formatted_time(show_colon)
    
    def update_time_with_colon(self, dt):
        """
        Обновляем время с мигающим двоеточием
        """
        self.is_colon_visible = not self.is_colon_visible
        self.title_label.text = self.get_current_time(self.is_colon_visible)

    def _on_clock_widget_created(self, clock_widget=None):
        """
        Обновляем ссылку на виджет часов в менеджере настроек
        """
        # Если clock_widget не передан, используем текущий виджет часов
        if clock_widget is None and hasattr(self.clock_widget, 'clock_widget'):
            clock_widget = self.clock_widget.clock_widget
        
        self.settings_manager.clock_label = clock_widget
        self.settings_manager.apply_saved_color()

    def apply_initial_color(self, dt):
        """
        Применение начального цвета после инициализации
        """
        initial_color = self.settings_manager.db.get_setting('color')
        if initial_color:
            color_tuple = SettingsWindow.get_color_tuple(initial_color)
            self.update_title_color(color_tuple)
        
    def update_title_color(self, color):
        """Обновляем цвет заголовка"""
        self.title_label.color = color
        
    def start_clock_animation(self, *args):
        """Запускаем анимацию мигания часов"""
        print("[DEBUG] Запуск анимации часов")
        
        # Останавливаем предыдущую анимацию, если она есть
        self.stop_clock_animation()
            
        # Сохраняем исходный цвет и прозрачность
        if not hasattr(self, '_original_clock_color'):
            self._original_clock_color = self.title_label.color.copy()
            print("[DEBUG] Сохранен исходный цвет часов:", self._original_clock_color)
            
        # Устанавливаем начальную прозрачность
        self.title_label.opacity = 1
        print(f"[DEBUG] Начальная прозрачность: {self.title_label.opacity}")
        
        # Создаем функцию для мигания, которая будет вызываться периодически
        def blink_clock(dt):
            if not hasattr(self, '_blinking') or not self._blinking:
                return
                
            # Инвертируем прозрачность
            new_opacity = 0 if self.title_label.opacity > 0.5 else 1
            Animation.cancel_all(self.title_label, 'opacity')
            anim = Animation(opacity=new_opacity, duration=0.5)
            anim.start(self.title_label)
            
            # Запускаем следующий кадр анимации
            if hasattr(self, '_blink_event'):
                self._blink_event.cancel()
            self._blink_event = Clock.schedule_once(blink_clock, 0.5)
        
        # Запускаем анимацию мигания
        self._blinking = True
        blink_clock(0)
        print("[DEBUG] Анимация мигания запущена")
        
        # Останавливаем анимацию через 1 минуту
        def stop_blinking(dt):
            if hasattr(self, '_blinking') and self._blinking:
                print("[DEBUG] Остановка мигания по таймеру")
                self._blinking = False
                if hasattr(self, '_blink_event'):
                    self._blink_event.cancel()
                self.stop_clock_animation()
        
        if hasattr(self, '_stop_clock_event'):
            self._stop_clock_event.cancel()
        self._stop_clock_event = Clock.schedule_once(stop_blinking, 60)
        print("[DEBUG] Запланирована остановка анимации через 60 секунд")
        print("[DEBUG] Запланирована остановка анимации через 60 секунд")
        
    def stop_clock_animation(self, *args):
        """Останавливаем анимацию и восстанавливаем исходное состояние"""
        print("[DEBUG] Остановка анимации часов")
        
        # Отменяем все анимации прозрачности
        Animation.cancel_all(self.title_label, 'opacity')
        
        # Останавливаем мигание, если оно активно
        if hasattr(self, '_blinking'):
            self._blinking = False
            print("[DEBUG] Флаг _blinking установлен в False")
            
        # Отменяем запланированные события
        if hasattr(self, '_blink_event'):
            self._blink_event.cancel()
            print("[DEBUG] Отменено событие _blink_event")
            
        if hasattr(self, '_stop_clock_event'):
            self._stop_clock_event.cancel()
            print("[DEBUG] Отменено событие _stop_clock_event")
        
        # Восстанавливаем исходную прозрачность и цвет
        if hasattr(self, '_original_clock_color'):
            self.title_label.color = self._original_clock_color
            print("[DEBUG] Восстановлен исходный цвет часов")
            
        self.title_label.opacity = 1
        print(f"[DEBUG] Восстановлена прозрачность: {self.title_label.opacity}")
        
        # Принудительно обновляем отображение
        self.title_label.canvas.ask_update()
        
    def update_color(self, color_name):
        """
        Обновляем цвет по имени
        """
        color_tuple = SettingsWindow.get_color_tuple(color_name)
        self.update_title_color(color_tuple)

    def calculate_font_size(self, scale_factor=5):
        """
        Простой процент от высоты (Window.height * scale_factor) 
        дает слишком резкие изменения размера шрифта 
        а логарифмическая формула делает изменения более плавными.
        """
        # Логарифмическая шкала берет меньшую сторону 
        # экрана для более плавного масштабирования
        base_size = min(Window.width, Window.height)
        
        # Логарифмическая функция для более 
        # естественного масштабирования. 
        # Делаем масштабирование нелинейным 
        # (медленнее растет при больших размерах)
        logarithmic_scale = math.log(base_size + 1, 10)  # +1 чтобы избежать деления на ноль
        
        # Применяем нелинейное масштабирование 
        # умножая на размер и коэффициент
        font_size = logarithmic_scale * base_size * scale_factor
        
        # Устанавливаем жесткие границы. 
        # Ограничивая размер (не меньше 10 
        # и не больше 20% от размера экрана)
        return max(min(font_size, base_size * 0.2), 10)

    def on_window_resize(self, instance, width, height):
        """
        Обработчик изменения размера окна
        """
        # Удаляем старую таблицу
        for child in self.layout.children[:]:
            if isinstance(child, GridLayout) and child != self.title_label:
                self.layout.remove_widget(child)
        
        # Определяем новую ориентацию
        current_orientation = self.get_current_orientation()
        
        # Создаем новую таблицу
        if current_orientation == 'portrait':
            portrait_layout = GridLayout(
                cols=1,
                spacing=dp(0),
                size_hint=(1, 1)
            )
            
            # Создаем и заполняем портретный layout
            portrait_layout = self.create_portrait_widgets(portrait_layout)
            main_window_body = portrait_layout
        elif current_orientation == 'landscape':
            main_window_body = create_landscape_prayer_times_table(self)
        else:  # square
            main_window_body = create_square_prayer_times_table(self)
        
        # Добавляем таблицу, если она не None
        if main_window_body:
            self.layout.add_widget(main_window_body)

    def classify_block_orientation(self, block):
        """
        Классифицирует блок по его ориентации
        
        :param block: Kivy виджет
        :return: 'portrait', 'landscape', или 'square'
        """
        # Получаем размеры блока
        width = block.width
        height = block.height
        
        # Определяем ориентацию с некоторым допуском
        tolerance = 0.1  # 10% погрешности
        
        if abs(width - height) / max(width, height) <= tolerance:
            return 'square'
        elif width > height * (1 + tolerance):
            return 'landscape'
        elif height > width * (1 + tolerance):
            return 'portrait'
        else:
            return 'square'

    def separate_blocks_by_orientation(self, layout):
        """
        Разделяет блоки layout по ориентации
        
        :param layout: Kivy layout
        :return: Словарь с разделенными блоками
        """
        orientations = {
            'portrait': [],
            'landscape': [],
            'square': []
        }
        
        for child in layout.children:
            orientation = self.classify_block_orientation(child)
            orientations[orientation].append(child)
        
        return orientations

    def create_portrait_widgets(self, layout):
        """
        Создает виджеты для портретной ориентации
        """
        from ui.main_portrait import create_portrait_widgets as create_portrait_widgets_func
        
        # Используем функцию из main_portrait с новой сигнатурой
        return create_portrait_widgets_func(self, layout)

    def on_stop(self):
        """
        Вызывается при закрытии приложения
        """
        self.settings_db.save_window_settings(
            width=Window.width,
            height=Window.height,
            x=Window.left,
            y=Window.top
        )

if __name__ == "__main__":
    MainWindowApp().run()
