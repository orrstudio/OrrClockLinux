import logging

from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch

# Импортируем базовые компоненты
from .settings_blocks.base import (
    ResponsiveLabel,
    SettingsCard,
    SettingsSection,
    CustomButton
)

# Импортируем компоненты настроек
from .settings_color import ColorButton
from .settings_blocks.colors import create_color_section, get_color_tuple, get_color_name
from .settings_blocks.header import create_header
from .settings_blocks.footer import create_footer

from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line


# Импортируем базу данных и утилиты
from data.database import SettingsDatabase
from logic.display_utils import is_mobile_device

logger = logging.getLogger(__name__)







class SettingsWindow(ModalView):
    """
    Окно настроек приложения.
    
    Attributes:
        db (SettingsDatabase): База данных настроек
        main_window: Ссылка на главное окно приложения
        apply_callback: Функция обратного вызова для применения настроек
        initial_color (str): Начальный цвет из настроек
        selected_color (str): Выбранный пользователем цвет
    """
    
    # Словарь цветов инициализируется в классе ColorSettings

    def __init__(self, db, main_window, apply_callback, **kwargs):
        """
        Инициализация окна настроек.
        
        Args:
            db (SettingsDatabase): База данных настроек
            main_window: Главное окно приложения
            apply_callback: Функция применения настроек
            **kwargs: Дополнительные аргументы
        """
        super().__init__(**kwargs)
        
        # Сохраняем начальные значения
        self.db = db
        self.main_window = main_window
        self.apply_callback = apply_callback
        
        # Сохраняем размеры главного окна
        self.main_window_size = (main_window.width, main_window.height) if hasattr(main_window, 'width') else (0, 0)
        self.main_window_pos = (main_window.x, main_window.y) if hasattr(main_window, 'x') else (0, 0)
        
        # Применяем сохраненные настройки окна после полной инициализации
        if not is_mobile_device():
            self.bind(on_open=self._apply_window_settings)
        
        # Получаем текущие настройки
        self.initial_color = self.db.get_setting('color')
        
        # Инициализируем переменные для хранения выбранных значений
        self.selected_color = self.initial_color
        
        # Настройки азана были удалены
        self.active_button = None  # Инициализируем как None
        
        # Настройка размеров окна
        self.size_hint = (1, 1)  # Полный размер экрана
        self.auto_dismiss = True
        self.padding = 0  # Убираем внутренний отступ ModalView
        self.background = ''  # Убираем стандартный фон
        self.background_color = (0, 0, 0, 1)  # Черный фон
        
        # Основной layout
        main_layout = GridLayout(
            cols=1,
            spacing=dp(0),
            size_hint=(1, 1)
        )
        
        # Создаем заголовок
        title_layout, self.title_rect = create_header()
        
        # Основной контейнер для всех секций
        content_container = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(15),  # Отступ между секциями
            padding=[dp(10), dp(10), dp(10), dp(10)]  # Отступы по краям
        )
        # Автоматическая подстройка высоты контейнера
        content_container.bind(minimum_height=content_container.setter('height'))
        
        # Контент (ScrollView)
        content_layout = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            size_hint=(1, 1),
            bar_width=dp(10),  # Ширина полосы прокрутки
            bar_color=(0.5, 0.5, 0.5, 0.5),  # Цвет полосы прокрутки
            bar_inactive_color=(0.5, 0.5, 0.5, 0.2)  # Цвет неактивной полосы прокрутки
        )
        
        # Создаем секцию выбора цвета
        color_section = create_color_section(self)
        
        # Импортируем и создаем секцию уведомлений
        from .settings_blocks.notifications import create_notifications_section
        notifications_section = create_notifications_section(self)
        
        # Импортируем и создаем секцию админ-панели
        from .settings_blocks.admin import create_admin_section
        admin_section = create_admin_section(self)
        
        # Инициализируем ссылки на виджеты для доступа из других методов
        self.color_section = color_section
        
        # Добавляем все виджеты в основной контейнер
        content_container.clear_widgets()  # Очищаем контейнер
        
        # Добавляем блоки с отступами
        content_container.add_widget(color_section)
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(notifications_section)
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(admin_section)
        
        # Обновляем размеры после добавления всех виджетов
        Clock.schedule_once(self.print_sizes, 0.5)
        
        # Добавляем контейнер в ScrollView
        content_layout.add_widget(content_container)
        
        # Создаем нижнюю панель с кнопками
        bottom_panel, self.bottom_rect = create_footer(
            dismiss_callback=self.dismiss,
            accept_callback=self.on_accept
        )
        
        # Собираем все вместе
        main_layout.add_widget(title_layout)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(bottom_panel)
        
        # Добавляем основной layout в окно
        self.add_widget(main_layout)
        
        # Добавляем рамку к активной кнопке после отрисовки
        Clock.schedule_once(self._add_initial_border, 0)

    def _add_initial_border(self, dt):
        """Добавляет рамку к изначально активной кнопке."""
        if hasattr(self, 'active_button') and self.active_button is not None:
            self._add_border_to_button(self.active_button)
    
    def _add_border_to_button(self, button):
        """
        Добавляет белую рамку к кнопке.
        
        Args:
            button: Кнопка, к которой добавляется рамка
        """
        if button is None:
            return
            
        button.canvas.after.clear()
        with button.canvas.after:
            Color(1, 1, 1, 1)
            self.border_line = Line(rectangle=(button.x, button.y, button.width, button.height), width=1.5)
        
        # Привязываем обновление рамки к изменению размера и позиции кнопки
        button.bind(pos=self._update_border, size=self._update_border)
    
    def _update_border(self, instance, value):
        """Обновляет размер и позицию рамки при изменении размера кнопки"""
        if hasattr(self, 'border_line'):
            self.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def _add_border_to_button(self, button):
        """
        Добавляет белую рамку к кнопке.
        
        Args:
            button: Кнопка, к которой добавляется рамка
        """
        if button is None:
            return
            
        button.canvas.after.clear()
        with button.canvas.after:
            Color(1, 1, 1, 1)
            self.border_line = Line(rectangle=(button.x, button.y, button.width, button.height), width=1.5)
        
        # Привязываем обновление рамки к изменению размера и позиции кнопки
        button.bind(pos=self._update_border, size=self._update_border)
    
    def _update_border(self, instance, value):
        """Обновляет размер и позицию рамки при изменении размера кнопки"""
        if hasattr(self, 'border_line'):
            self.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def _on_color_button_press(self, button):
        """
        Обработка нажатия на цветную кнопку.
        
        Args:
            button: Нажатая кнопка
        """
        try:
            # Убираем рамку со старой активной кнопки
            if hasattr(self, 'active_button') and self.active_button != button:
                self.active_button.canvas.after.clear()
            
            # Добавляем рамку на новую кнопку
            self._add_border_to_button(button)
            
            # Сохраняем ссылку на активную кнопку
            self.active_button = button
            
            # Устанавливаем выбранный цвет из нажатой кнопки
            self.selected_color = button.color_name.lower()
                
        except Exception as e:
            print(f"Ошибка при обработке нажатия на кнопку: {e}")
    
    def print_sizes(self, *args, show_before_save=False):
        """
        Выводит информацию о текущих настройках.
        
        Args:
            show_before_save (bool): Если True, показывает настройки перед сохранением
        """
        # Вспомогательная функция для вывода разделителя
        def print_separator():
            print("=" * 37)
            
        # Вспомогательная функция для вывода заголовка
        def print_header(title):
            print(f"| {title.center(34)}|")
            print("" + "-" * 37)
            
        # Вспомогательная функция для вывода строки с двумя значениями
        def print_row(label, value1, value2):
            print(f"| {label.ljust(16)}|{str(value1).center(8)}|{str(value2).center(8)}|")
            
        # Вспомогательная функция для вывода строки с одним значением
        def print_single_row(label, value):
            print(f"| {label.ljust(16)}| {str(value).center(16)}|")
            
        # Основной вывод
        print()  # Пустая строка перед началом вывода
        
        # Раздел: Главное окно
        print_separator()
        print_header("App Window")
        try:
            main_settings = self.db.get_window_settings()
            if main_settings:
                width, height, x, y = main_settings
                print_row("Size", int(width), int(height))
                print_row("Position", int(x), int(y))
            else:
                print("| No data found" + " " * 21 + "|")
        except Exception as e:
            print(f"| Error: {str(e)[:25]}" + " " * (36 - 9 - len(str(e)[:25])) + "|")
        
        # Раздел: Окно настроек
        print_separator()
        print_header("Settings Window")
        try:
            settings = self.db.get_settings_window_settings()
            if settings:
                width, height, x, y = settings
                print_row("Size", int(width), int(height))
                print_row("Position", int(x), int(y))
            else:
                print("| No data found" + " " * 21 + "|")
        except Exception as e:
            print(f"| Error: {str(e)[:25]}" + " " * (36 - 9 - len(str(e)[:25])) + "|")
        
        # Раздел: Тема
        print_separator()
        if hasattr(self, 'selected_color'):
            print_single_row("Theme", self.selected_color.capitalize())
        else:
            print_single_row("Theme", "Not set")
        
        # Раздел: Отладочный режим
        print_separator()
        if hasattr(self, 'debug_switch'):
            debug_state = "ENABLE" if self.debug_switch.active else "DISABLE"
            print_single_row("Debug Mode", debug_state)
        else:
            print_single_row("Debug Mode", "UNAVAILABLE")

        try:
            # Импортируем менеджер молитв
            from logic.prayer_times import prayer_times_manager
            from datetime import datetime, timedelta
            
            # Получаем текущую дату и дату завтра
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            date_format = "%Y-%m-%d"
            today_str = today.strftime(date_format)
            tomorrow_str = tomorrow.strftime(date_format)
            
            # Получаем данные из базы для сегодня и завтра
            cursor = prayer_times_manager.db.connection.cursor()
            cursor.execute('''
                SELECT * FROM prayer_times 
                WHERE date = ? OR date = ?
                ORDER BY date ASC
            ''', (today_str, tomorrow_str))
            
            # Получаем строки с данными
            rows = cursor.fetchall()
            
            # Получаем заголовки колонок
            columns = [desc[0] for desc in cursor.description]
            
            # Пропускаем служебные поля
            skip_columns = {'date', 'created_at'}
            prayer_columns = [col for col in columns if col not in skip_columns]
            
            # Создаем словарь для хранения данных по датам
            prayer_data = {
                today_str: {col: '00:00' for col in prayer_columns},  # По умолчанию нули
                tomorrow_str: {col: '00:00' for col in prayer_columns}  # По умолчанию нули
            }
            
            # Заполняем данные из базы
            for row in rows:
                row_dict = dict(zip(columns, row))
                date = row_dict['date']
                if date in prayer_data:
                    for col in prayer_columns:
                        if col in row_dict and row_dict[col]:
                            prayer_data[date][col] = row_dict[col][:5]  # Берем только часы и минуты
            
            # Формируем даты для заголовка
            today_display = f"{today.day:02d}/{today.month:02d}"
            tomorrow_display = f"{tomorrow.day:02d}/{tomorrow.month:02d}"
            
            # Разделитель перед таблицей молитв
            print_separator()
            print_header("Data from Base")
            
            # Заголовки дат
            print(f"| {'Date'.ljust(16)}|{today_display.center(8)}|{tomorrow_display.center(8)}|")
            print("|" + "-" * 17 + "|" + "-" * 8 + "|" + "-" * 8 + "|")
            
            # Выводим времена молитв с выравниванием
            prayer_map = {
                'Midnight': 'Midnight',
                'Fajr': 'Fajr',
                'Sunrise': 'Sunrise',
                'Dhuhr': 'Dhuhr',
                'Asr': 'Asr',
                'Maghrib': 'Maghrib',
                'Isha': 'Isha'
            }
            
            for eng_name, display_name in prayer_map.items():
                today_time = prayer_data[today_str].get(eng_name, '--:--')
                tomorrow_time = prayer_data[tomorrow_str].get(eng_name, '--:--')
                print(f"| {display_name.ljust(16)}|{str(today_time).center(8)}|{str(tomorrow_time).center(8)}|")
            
            # Закрывающий разделитель и пустая строка
            print_separator()
            print()  # Пустая строка после таблицы
                
        except Exception as e:
            print(f"Ошибка при получении данных из базы: {e}\n")

    def on_accept(self, *args):
        """Сохраняет настройки при нажатии кнопки Save."""
        try:
            # Сохраняем цвет, если выбран
            if hasattr(self, 'selected_color') and self.selected_color:
                # Преобразуем название цвета в нижний регистр
                color_key = self.selected_color.lower()
                
                # Сохраняем в базу данных
                self.db.save_setting('color', color_key)
                
                # Применяем цвет через callback
                if hasattr(self, 'apply_callback') and self.apply_callback:
                    # Получаем цвет из color_settings, если он доступен
                    if hasattr(self, 'color_settings') and hasattr(self.color_settings, 'colors'):
                        color_tuple = self.color_settings.colors.get(color_key, (0, 1, 0, 1))
                    else:
                        # Стандартный цвет, если color_settings не доступен
                        color_tuple = (0, 1, 0, 1)  # Зеленый по умолчанию
                    
                    self.apply_callback(color_tuple)
            
            # Сохраняем состояние отладочного режима
            if hasattr(self, 'debug_switch'):
                debug_enabled = self.debug_switch.active
                
                try:
                    from utils.logger import logger
                    
                    # Устанавливаем новое состояние отладки
                    # Метод set_debug сам сохранит состояние в БД и обновит логгер
                    logger.set_debug(debug_enabled)
                    
                    # Выводим сообщение о результате
                    status = 'включён' if debug_enabled else 'выключен'
                    logging.info(f'Отладочный режим {status}')
                    
                except Exception as e:
                    logging.error(f'Не удалось обновить отладочный режим: {e}')
                    # Пробуем сохранить состояние напрямую в БД на случай ошибки в логгере
                    try:
                        from data.database import SettingsDatabase
                        db = SettingsDatabase()
                        db.save_setting('debug_mode', '1' if debug_enabled else '0')
                        logging.info('Значение отладочного режима сохранено напрямую в БД')
                    except Exception as db_error:
                        logging.error(f'Критическая ошибка: не удалось сохранить состояние отладки: {db_error}')
                
            # Выводим обновленные настройки после сохранения
            self.print_sizes(show_before_save=False)
            
            self.dismiss()
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
            self.dismiss()
    
    def _update_title_rect(self, instance, value):
        """Обновляет фон заголовка."""
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size
    
    def _update_bottom_rect(self, instance, value):
        """Обновляет фон нижней панели."""
        self.bottom_rect.pos = instance.pos
        self.bottom_rect.size = instance.size

    def on_window_resize(self, instance, width, height):
        """
        Обновляет размеры окна при изменении размера экрана.
        
        Args:
            width: Новая ширина окна
            height: Новая высота окна
        """
        self.width = min(dp(400), width * 0.95)
        self.height = min(dp(500), height * 0.95)
    
    def _apply_window_settings(self, *args):
        """
        Применяет сохраненные настройки окна после его полной инициализации.
        """
        if hasattr(self, 'db'):
            from kivy.core.window import Window
            
            # Получаем текущие настройки окна из базы данных
            settings = self.db.get_settings_window_settings()
            if settings:
                width, height, x, y = settings
                
                # Устанавливаем размеры окна
                Window.size = (width, height)
                
                # Устанавливаем позицию окна
                Window.left = x
                Window.top = y
                
                # Принудительно обновляем окно
                Window.update_viewport()
            
    def dismiss(self, *args):
        """
        Закрывает окно настроек.
        
        Если настройки не были сохранены, возвращает исходный цвет.
        """
        # Если окно уже закрывается, выходим
        if hasattr(self, '_window') and self._window is None:
            return
        
        # Восстанавливаем исходный цвет, если настройки не были сохранены
        if not self.selected_color or args:  
            if hasattr(self.main_window, 'update_color') and self.initial_color:
                self.main_window.update_color(self.initial_color)
        
        # Сохраняем настройки окна при закрытии
        if not is_mobile_device() and hasattr(self, 'db'):
            from kivy.core.window import Window
            
            # Получаем текущую позицию окна
            x, y = Window.left, Window.top
            
            # Сохраняем настройки окна
            self.db.save_settings_window_settings(
                width=Window.width,
                height=Window.height,
                x=x,
                y=y
            )
            
        # Вызываем оригинальный метод закрытия
        super().dismiss(*args)
    
    # Методы get_color_tuple и get_color_name перенесены в модуль settings_blocks.colors
