import logging
from kivy.logger import Logger

from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

# Импортируем базовые компоненты
from .settings_blocks.base import CustomButton

# Импортируем компоненты настроек
from .settings_blocks.colors import create_color_section, get_color_tuple, ColorSettings
from .settings_blocks.header import create_header
from .settings_blocks.footer import create_footer
from .settings_blocks.utils import add_border, print_sizes
from .settings_blocks.window_settings import apply_window_settings, on_window_resize, save_window_settings

from kivy.clock import Clock
from kivy.metrics import dp

# Импортируем утилиты
from logic.display_utils import is_mobile_device

logger = logging.getLogger(__name__)

class SettingsWindow(ModalView):
    """
    Окно настроек приложения.
    
    Основной класс, отвечающий за отображение и управление настройками приложения.
    Использует модульную структуру для организации кода.
    
    Attributes:
        db: База данных настроек
        main_window: Ссылка на главное окно приложения
        apply_callback: Функция обратного вызова для применения настроек
        initial_color (str): Начальный цвет из настроек
        selected_color (str): Выбранный пользователем цвет
        color_section: Ссылка на секцию выбора цвета
        title_rect: Прямоугольник фона заголовка
        bottom_rect: Прямоугольник фона нижней панели
        active_button: Текущая активная кнопка
    """

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
        
        # Инициализируем настройки цветов
        self.color_settings = ColorSettings(self)
        
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
            add_border(self.active_button)

    def print_sizes(self, *args, show_before_save=False):
        """
        Выводит отладочную информацию о настройках приложения.
        
        Args:
            show_before_save (bool): Если True, показывает настройки перед сохранением
            
        Returns:
            Результат выполнения функции print_sizes из модуля utils
        """
        return print_sizes(self.db, show_before_save)

    def on_accept(self, *args):
        """Сохраняет настройки при нажатии кнопки Save."""
        try:
            # Сохраняем настройки цвета через экземпляр ColorSettings, если он доступен
            if hasattr(self, 'color_settings') and hasattr(self.color_settings, 'save_color_settings'):
                self.color_settings.save_color_settings()
            else:
                # Резервный вариант, если color_settings не доступен
                if hasattr(self, 'selected_color') and self.selected_color:
                    color_key = self.selected_color.lower()
                    self.db.save_setting('color', color_key)
                    if hasattr(self, 'apply_callback') and self.apply_callback:
                        color_tuple = get_color_tuple(color_key)
                        self.apply_callback(color_tuple)
            
            # Сохраняем состояние отладочного режима
            if hasattr(self, 'debug_switch'):
                debug_enabled = self.debug_switch.active
                
                try:
                    from utils.logger import logger
                    
                    # Устанавливаем новое состояние отладки
                    # Метод set_debug сам сохранит состояние в БД и обновит логгер
                    logger.set_debug(debug_enabled)
                    
                    # Выводим сообщение о результате через Kivy Logger
                    from kivy.logger import Logger
                    status = 'ENABLED' if debug_enabled else 'DISABLED'
                    Logger.info(f'Logger: Debug Mode {status}')
                    
                except Exception as e:
                    from kivy.logger import Logger
                    Logger.error(f'Logger: Failed to update debug mode: {e}')
                    # Пробуем сохранить состояние напрямую в БД на случай ошибки в логгере
                    try:
                        from data.database import SettingsDatabase
                        db = SettingsDatabase()
                        db.save_setting('debug_mode', '1' if debug_enabled else '0')
                        Logger.info('Logger: Debug mode value saved directly to database')
                    except Exception as db_error:
                        logging.error(f'Critical error: failed to save debug state: {db_error}')
                
            # Выводим обновленные настройки после сохранения
            self.print_sizes(show_before_save=False)
            
            self.dismiss()
        except Exception as e:
            Logger.error(f'Error saving settings: {e}')
            self.dismiss()
    
    # Метод _update_title_rect перенесен в модуль header.py
    # Метод _update_bottom_rect перенесен в модуль footer.py

    def on_window_resize(self, instance, width, height):
        """
        Обновляет размеры окна при изменении размера экрана.
        
        Args:
            instance: Экземпляр виджета, вызвавшего событие
            width: Новая ширина окна
            height: Новая высота окна
        """
        on_window_resize(self, instance, width, height)
    
    def _apply_window_settings(self, *args):
        """
        Применяет сохраненные настройки окна после его полной инициализации.
        """
        apply_window_settings(self)
            
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
            save_window_settings(self)
            
        # Вызываем оригинальный метод закрытия
        super().dismiss(*args)
    
    # Методы get_color_tuple и get_color_name перенесены в модуль settings_blocks.colors
