from ui.settings_window import SettingsWindow
from ui.settings_blocks.colors import get_color_tuple, get_color_name
from data.database import SettingsDatabase
from kivy.core.window import Window  # Локальный импорт для избежания циклических зависимостей

class SettingsManager:
    def __init__(self, clock_label, main_window):
        """
        Инициализация менеджера настроек
        
        Args:
            clock_label: Виджет часов для применения настроек
            main_window: Главное окно для обновления цвета заголовка
        """
        self.db = SettingsDatabase()
        self.clock_label = clock_label
        self.main_window = main_window
        self.initial_color = self.db.get_setting('color')

    def apply_saved_color(self):
        """Применение сохраненного цвета при инициализации"""
        saved_color = self.db.get_setting('color')
        if saved_color and hasattr(self.clock_label, 'color'):
            self.clock_label.color = get_color_tuple(saved_color)

    def open_settings_window(self):
        """
        Открытие окна настроек с сохранением параметров главного окна
        """
        # Сохраняем текущие параметры главного окна
        if hasattr(self.main_window, 'save_main_window_state'):
            self.main_window.save_main_window_state()
            
        # Создаем и открываем окно настроек
        settings_window = SettingsWindow(
            self.db, 
            main_window=self.main_window,  
            apply_callback=self.apply_settings
        )
        
        # Сохраняем ссылку на окно настроек в главном окне
        self.main_window.settings_window = settings_window
        
        # Привязываем обработчик закрытия окна настроек
        settings_window.bind(on_dismiss=self.on_settings_dismiss)
        settings_window.open()
        
        # Настройки окна применяются автоматически при создании SettingsWindow
        # в его методе __init__ через db.apply_settings_window_settings(self)
    
    def on_settings_dismiss(self, instance):
        """
        Обработчик закрытия окна настроек
        Восстанавливаем параметры главного окна и очищаем ссылку на окно настроек
        """
        if hasattr(self.main_window, 'restore_main_window_state'):
            self.main_window.restore_main_window_state()
        
        # Очищаем ссылку на окно настроек
        if hasattr(self.main_window, 'settings_window'):
            self.main_window.settings_window = None

    def apply_settings(self, color_tuple):
        """
        Применение новых настроек цвета
        
        Args:
            color_tuple: Кортеж цвета (r, g, b, a)
        """
        from kivy.logger import Logger
        
        try:
            # Обновляем цвет часов
            if hasattr(self.clock_label, 'apply_settings'):
                # Вызываем apply_settings у часов
                self.clock_label.apply_settings(color_tuple)
            elif hasattr(self.clock_label, 'color'):
                # Резервный вариант - напрямую устанавливаем цвет
                self.clock_label.color = color_tuple
            
            # Получаем имя темы по цвету
            color_name = get_color_name(color_tuple)
            Logger.debug(f'Applying theme: {color_name}')
            
            # Сохраняем выбранный цвет в базу
            self.db.save_setting('color', color_name)
            self.initial_color = color_name
            
            # Обновляем цвет заголовка и тему приложения
            if hasattr(self, 'main_window'):
                if hasattr(self.main_window, 'update_color'):
                    self.main_window.update_color(color_name)
                
                # Обновляем тему в PrayerTimesBox, если он существует
                if hasattr(self.main_window, 'prayer_times_box') and self.main_window.prayer_times_box is not None:
                    Logger.debug(f'Updating theme in PrayerTimesBox to: {color_name}')
                    self.main_window.prayer_times_box.update_colors(color_name)
                    
                # Обновляем тему в NextPrayerTimeBox, если он существует
                if hasattr(self.main_window, 'next_prayer_time_box') and self.main_window.next_prayer_time_box is not None:
                    Logger.debug(f'Updating theme in NextPrayerTimeBox to: {color_name}')
                    self.main_window.next_prayer_time_box.update_colors(color_name)
                    
        except Exception as e:
            Logger.error(f'Error applying theme: {str(e)}')

    def cancel_settings(self):
        """
        Отмена изменений настроек, возврат к первоначальному цвету
        """
        if self.initial_color and hasattr(self.clock_label, 'color'):
            initial_color_tuple = get_color_tuple(self.initial_color)
            self.clock_label.color = initial_color_tuple
