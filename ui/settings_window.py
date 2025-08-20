import logging
from kivy.logger import Logger

from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

# Импортируем базовые компоненты
from ui.components.custom_button import CustomButton

# Импортируем компоненты настроек
from .settings_blocks.colors import create_color_section, get_color_tuple, ColorSettings
from .settings_blocks.header import create_header
from .settings_blocks.footer import create_footer
from .settings_blocks.utils import add_border, print_sizes
from .settings_blocks.window_settings import apply_window_settings, on_window_resize, save_window_settings
from .settings_blocks.tabs import create_tabbed_interface

from kivy.clock import Clock
from kivy.metrics import dp

# Импортируем утилиты
from logic.display_utils import is_mobile_device

logger = logging.getLogger(__name__)

# Константы для работы с вкладками
TAB_INDEXES = {
    'theme': 0,
    'notification': 1,
    'admin': 2
}

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
        logger.info(f'Получен цвет из базы данных: {self.initial_color}')
        
        # Инициализируем переменные для хранения выбранных значений
        self.selected_color = self.initial_color
        logger.info(f'Установлен selected_color: {self.selected_color}')
        
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
        
        # Создаем панель с вкладками
        tab_panel, tab_contents = create_tabbed_interface()
        
        # Сохраняем ссылку на панель вкладок
        self.tab_panel = tab_panel
        
        # Получаем контейнеры вкладок
        theme_content = tab_contents['theme']
        notification_content = tab_contents['notification']
        admin_content = tab_contents['admin']
        
        # Получаем ссылки на вкладки
        notification_tab = next((tab for tab in tab_panel.tab_list 
                               if getattr(tab, 'text', '').lower() == 'notification'), 
                              None)
        
        # Создаем контейнер для содержимого вкладок
        content_container = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(15),  # Отступ между секциями
            padding=[dp(10), dp(10), dp(10), dp(10)]  # Отступы по краям
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
        
        # Добавляем виджеты во вкладку "Theme"
        theme_content.add_widget(color_section)
        
        # Добавляем виджеты во вкладку "Notification"
        notification_content.add_widget(notifications_section)
        
        # Добавляем виджеты во вкладку "Admin Panel"
        admin_content.add_widget(admin_section)
        
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
        
        # Добавляем панель вкладок в основной контейнер
        content_container.add_widget(tab_panel)
        
        # Ссылка на панель вкладок уже сохранена ранее
        
        # Привязываемся к событию открытия окна для переключения вкладки
        self.bind(on_open=self._on_settings_window_open)
        
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

    def _on_settings_window_open(self, *args):
        """Вызывается при открытии окна настроек."""
        Logger.debug('Метод _on_settings_window_open вызван')
        
        # Выводим информацию о вкладках до привязки обработчика
        if hasattr(self, 'tab_panel') and hasattr(self.tab_panel, 'tab_list'):
            Logger.debug('Текущие вкладки:')
            for i, tab in enumerate(self.tab_panel.tab_list):
                tab_text = getattr(tab, 'text', 'без названия').lower()
                tab_id = TAB_INDEXES.get(tab_text, i)
                logger.debug(f'  Вкладка {i}: "{tab_text}" (ID: {tab_id})')
        
        # Привязываем обработчик изменения вкладки
        self.tab_panel.bind(current_tab=self._on_tab_changed)
        
        def switch_to_saved_tab(dt):
            """Переключается на сохраненную вкладку."""
            logger.debug('switch_to_saved_tab: начало выполнения')
            try:
                if not hasattr(self.tab_panel, 'tab_list') or not self.tab_panel.tab_list:
                    logger.warning('switch_to_saved_tab: список вкладок пуст')
                    return
                
                # Получаем сохраненный ID вкладки из базы данных
                saved_tab_id = int(self.db.get_setting('active_settings_tab', '1'))
                logger.debug(f'switch_to_saved_tab: сохраненный ID вкладки: {saved_tab_id}')
                
                # Находим вкладку с соответствующим ID
                target_tab = None
                for tab in self.tab_panel.tab_list:
                    tab_name = getattr(tab, 'text', '').lower()
                    tab_id = TAB_INDEXES.get(tab_name, -1)
                    if tab_id == saved_tab_id:
                        target_tab = tab
                        break
                
                if target_tab:
                    logger.debug(f'switch_to_saved_tab: переключение на вкладку "{getattr(target_tab, "text", "")}"')
                    self.tab_panel.switch_to(target_tab)
                    
                    # Обновляем визуальное состояние вкладок
                    for tab in self.tab_panel.tab_list:
                        tab.state = 'down' if tab == target_tab else 'normal'
                        tab.canvas.ask_update()
                    
                    logger.debug('switch_to_saved_tab: переключение выполнено успешно')
                else:
                    logger.warning(f'switch_to_saved_tab: не найдена вкладка с ID {saved_tab_id}')
                    
            except Exception as e:
                logger.error(f'switch_to_saved_tab: ошибка при переключении вкладки: {e}')
        
        # Запускаем без задержки
        Clock.schedule_once(switch_to_saved_tab, 0)
        
    def _on_tab_changed(self, instance, value):
        """Обработчик изменения активной вкладки."""
        try:
            if not hasattr(self, 'tab_panel') or not hasattr(self.tab_panel, 'tab_list'):
                return
                
            # Получаем индекс активной вкладки
            tab_index = self.tab_panel.tab_list.index(value) if value in self.tab_panel.tab_list else -1
            if tab_index >= 0:
                self._save_active_tab(tab_index)
        except Exception as e:
            Logger.error(f'Error in _on_tab_changed: {e}')
    
    def _save_active_tab(self, tab_index):
        """
        Сохраняет индекс активной вкладки в базу данных и логирует событие.
        
        Args:
            tab_index: Индекс вкладки в tab_list
        """
        try:
            if not hasattr(self, 'db') or not hasattr(self.tab_panel, 'tab_list'):
                Logger.debug('_save_active_tab: Нет доступа к db или tab_list')
                return
            
            # Получаем текущую активную вкладку
            current_tab = self.tab_panel.current_tab
            if not current_tab:
                Logger.debug('_save_active_tab: Не удалось определить текущую вкладку')
                return
                
            # Получаем имя вкладки
            tab_name = getattr(current_tab, 'text', f'Вкладка {tab_index}').lower()
            Logger.debug(f'_save_active_tab: Текущая вкладка: {tab_name} (индекс: {tab_index})')
            
            # Получаем жестко заданный индекс вкладки
            tab_id = TAB_INDEXES.get(tab_name, tab_index)
            
            # Сохраняем в базу данных ID вкладки
            self.db.save_setting('active_settings_tab', str(tab_id))
            
            # Логируем событие
            Logger.info(f'[Переключение вкладки] {tab_name} (ID: {tab_id})')
            
        except Exception as e:
            Logger.error(f'Ошибка при сохранении активной вкладки: {e}')

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
                
            # Сохраняем настройку логирования в файл
            if hasattr(self, 'logging_to_file_pending'):
                try:
                    from data.database import SettingsDatabase
                    db = SettingsDatabase()
                    db.save_setting('logging_to_file', '1' if self.logging_to_file_pending else '0')
                    Logger.info(f'Logger: Logging to file set to {self.logging_to_file_pending}')
                except Exception as e:
                    Logger.error(f'Logger: Failed to save logging to file setting: {e}')
            
            # Сохраняем настройки уведомлений
            try:
                # Основные переключатели
                if hasattr(self, 'visual_notifications_pending'):
                    self.db.save_setting('visual_notifications', '1' if self.visual_notifications_pending else '0')
                    Logger.info(f'Notifications: Visual notifications set to {self.visual_notifications_pending}')
                
                if hasattr(self, 'voice_notifications_pending'):
                    self.db.save_setting('voice_notifications', '1' if self.voice_notifications_pending else '0')
                    Logger.info(f'Notifications: Voice notifications set to {self.voice_notifications_pending}')
                
                if hasattr(self, 'play_adhan_pending'):
                    self.db.save_setting('play_adhan', '1' if self.play_adhan_pending else '0')
                    Logger.info(f'Notifications: Play adhan set to {self.play_adhan_pending}')
                
                # Визуальные уведомления
                if hasattr(self, 'visual_at_adhan_pending'):
                    self.db.save_setting('visual_at_adhan', '1' if self.visual_at_adhan_pending else '0')
                    Logger.info(f'Notifications: Visual at adhan set to {self.visual_at_adhan_pending}')
                
                if hasattr(self, 'visual_15_min_pending'):
                    self.db.save_setting('visual_15_min', '1' if self.visual_15_min_pending else '0')
                    Logger.info(f'Notifications: Visual 15 min before set to {self.visual_15_min_pending}')
                
                if hasattr(self, 'visual_30_min_pending'):
                    self.db.save_setting('visual_30_min', '1' if self.visual_30_min_pending else '0')
                    Logger.info(f'Notifications: Visual 30 min before set to {self.visual_30_min_pending}')
                
                if hasattr(self, 'visual_45_min_pending'):
                    self.db.save_setting('visual_45_min', '1' if self.visual_45_min_pending else '0')
                    Logger.info(f'Notifications: Visual 45 min before set to {self.visual_45_min_pending}')
                
                if hasattr(self, 'visual_60_min_pending'):
                    self.db.save_setting('visual_60_min', '1' if self.visual_60_min_pending else '0')
                    Logger.info(f'Notifications: Visual 60 min before set to {self.visual_60_min_pending}')
                
                # Голосовые уведомления
                if hasattr(self, 'voice_at_adhan_pending'):
                    self.db.save_setting('voice_at_adhan', '1' if self.voice_at_adhan_pending else '0')
                    Logger.info(f'Notifications: Voice at adhan set to {self.voice_at_adhan_pending}')
                
                if hasattr(self, 'voice_15_min_pending'):
                    self.db.save_setting('voice_15_min', '1' if self.voice_15_min_pending else '0')
                    Logger.info(f'Notifications: Voice 15 min before set to {self.voice_15_min_pending}')
                
                if hasattr(self, 'voice_30_min_pending'):
                    self.db.save_setting('voice_30_min', '1' if self.voice_30_min_pending else '0')
                    Logger.info(f'Notifications: Voice 30 min before set to {self.voice_30_min_pending}')
                
                if hasattr(self, 'voice_45_min_pending'):
                    self.db.save_setting('voice_45_min', '1' if self.voice_45_min_pending else '0')
                    Logger.info(f'Notifications: Voice 45 min before set to {self.voice_45_min_pending}')
                
                if hasattr(self, 'voice_60_min_pending'):
                    self.db.save_setting('voice_60_min', '1' if self.voice_60_min_pending else '0')
                    Logger.info(f'Notifications: Voice 60 min before set to {self.voice_60_min_pending}')
                
                # Настройки азана
                if hasattr(self, 'fajr_adhan_pending'):
                    self.db.save_setting('fajr_adhan', '1' if self.fajr_adhan_pending else '0')
                    Logger.info(f'Notifications: Fajr adhan set to {self.fajr_adhan_pending}')
                
                if hasattr(self, 'dhuhr_adhan_pending'):
                    self.db.save_setting('dhuhr_adhan', '1' if self.dhuhr_adhan_pending else '0')
                    Logger.info(f'Notifications: Dhuhr adhan set to {self.dhuhr_adhan_pending}')
                
                if hasattr(self, 'asr_adhan_pending'):
                    self.db.save_setting('asr_adhan', '1' if self.asr_adhan_pending else '0')
                    Logger.info(f'Notifications: Asr adhan set to {self.asr_adhan_pending}')
                
                if hasattr(self, 'maghrib_adhan_pending'):
                    self.db.save_setting('maghrib_adhan', '1' if self.maghrib_adhan_pending else '0')
                    Logger.info(f'Notifications: Maghrib adhan set to {self.maghrib_adhan_pending}')
                
                if hasattr(self, 'isha_adhan_pending'):
                    self.db.save_setting('isha_adhan', '1' if self.isha_adhan_pending else '0')
                    Logger.info(f'Notifications: Isha adhan set to {self.isha_adhan_pending}')
                    
            except Exception as e:
                Logger.error(f'Notifications: Failed to save notification settings: {e}')
            
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
