from ui.settings_window import SettingsWindow
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
            self.clock_label.color = SettingsWindow.get_color_tuple(saved_color)

    def open_settings_window(self):
        """Открытие окна настроек"""
        settings_window = SettingsWindow(
            self.db, 
            main_window=self.main_window,  
            apply_callback=self.apply_settings
        )
        settings_window.open()

    def apply_settings(self, color_tuple):
        """
        Применение новых настроек цвета
        
        Args:
            color_tuple: Кортеж цвета (r, g, b, a)
        """
        if hasattr(self.clock_label, 'apply_settings'):
            # Вызываем apply_settings у часов
            self.clock_label.apply_settings(color_tuple)
        elif hasattr(self.clock_label, 'color'):
            # Резервный вариант - напрямую устанавливаем цвет
            self.clock_label.color = color_tuple
        
        # Сохраняем выбранный цвет в базу
        color_name = SettingsWindow.get_color_name(color_tuple)
        self.db.save_setting('color', color_name)
        self.initial_color = color_name
        
        # Обновляем цвет заголовка, если есть ссылка на главное окно
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'update_color'):
            self.main_window.update_color(color_name)
        else:
            pass

    def cancel_settings(self):
        """
        Отмена изменений настроек, возврат к первоначальному цвету
        """
        if self.initial_color and hasattr(self.clock_label, 'color'):
            initial_color_tuple = SettingsWindow.get_color_tuple(self.initial_color)
            self.clock_label.color = initial_color_tuple
