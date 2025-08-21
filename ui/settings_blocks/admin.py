"""
Модуль для работы с админ-панелью.
Содержит классы и функции для управления отладочным режимом и другими настройками администратора.
"""

import logging
import os
import subprocess
import threading
import shutil
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, BooleanProperty, StringProperty

from ui.components.custom_switch_checkbox import CustomCheckBox
from ui.components.custom_button import RoundedButton

# Настройка логирования
logger = logging.getLogger(__name__)

class BorderedGridLayout(GridLayout):
    """GridLayout с границами и адаптивными линиями."""
    border_color = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*self.border_color)
            # Внешняя рамка
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

            # Вертикальная линия между колонками (70% ширины)
            col1 = self.x + self.width * 0.7  # Конец первой колонки (70%)
            Line(points=[col1, self.y, col1, self.top], width=1)

def load_debug_state(settings_window):
    """
    Загружает состояние отладочного режима из базы данных.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        bool: True если отладочный режим включен, иначе False
    """
    try:
        db = settings_window.db
        debug_mode = db.get_setting('debug_mode', '0')
        return debug_mode == '1'
    except Exception as e:
        logger.error(f'Error loading debug state: {e}')
        return False

def load_logging_state(settings_window):
    """
    Загружает состояние логирования в файл из базы данных.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        bool: True если логирование в файл включено, иначе False
    """
    try:
        db = settings_window.db
        logging_enabled = db.get_setting('logging_to_file', '0')
        return logging_enabled == '1'
    except Exception as e:
        logger.error(f'Error loading logging state: {e}')
        return False

def save_logging_state(settings_window, enabled):
    """
    Сохраняет состояние логирования в файл в базу данных.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        enabled (bool): Включено ли логирование в файл
    """
    try:
        db = settings_window.db
        db.save_setting('logging_to_file', '1' if enabled else '0')
        logger.info(f'Logging to file set to: {enabled}')
    except Exception as e:
        logger.error(f'Error saving logging state: {e}')

def save_debug_state(settings_window, enabled):
    """Сохраняет состояние отладочного режима в базу данных."""
    try:
        from utils.logger import logger as app_logger
        from kivy.logger import Logger
        
        # Устанавливаем новое состояние отладки
        # Метод set_debug сам сохранит состояние в БД и обновит логгер
        app_logger.set_debug(enabled)
        
        # Выводим сообщение о результате
        status = 'Enabled' if enabled else 'Disabled'
        logger.info(f'Debug Mode: {status}')
        
    except Exception as e:
        Logger.error(f'Logger: Failed to update debug mode: {e}')
        # Пробуем сохранить состояние напрямую в БД на случай ошибки в логгере
        try:
            from data.database import SettingsDatabase
            db = SettingsDatabase()
            db.save_setting('debug_mode', '1' if enabled else '0')
            Logger.info('Logger: Debug mode value saved directly to the database')
        except Exception as db_error:
            logger.error(f'Критическая ошибка: не удалось сохранить состояние отладки: {db_error}')

def clear_old_logs(button_instance):
    """Удаляет все логи, кроме активного, включая логи Kivy."""
    try:
        # Получаем путь к директории приложения
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = os.path.join(app_dir, 'logs')
        
        deleted_files = []
        
        # Удаляем старые логи приложения (начинающиеся с 'logs_')
        app_logs = sorted(
            [f for f in os.listdir(logs_dir) if f.startswith('logs_') and f.endswith('.txt')],
            key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)),
            reverse=True
        )
        
        # Удаляем все логи приложения, кроме самого нового
        for log_file in app_logs[1:]:
            file_path = os.path.join(logs_dir, log_file)
            os.remove(file_path)
            deleted_files.append(f"logs: {log_file}")
        
        # Удаляем все логи Kivy (начинающиеся с 'kivy_')
        kivy_logs = [f for f in os.listdir(logs_dir) if f.startswith('kivy_')]
        for kivy_log in kivy_logs:
            file_path = os.path.join(logs_dir, kivy_log)
            os.remove(file_path)
            deleted_files.append(f"kivy: {kivy_log}")
        
        # Показываем уведомление об успешном удалении
        if deleted_files:
            message = "Deleted files:\n" + "\n".join(deleted_files)
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.scrollview import ScrollView
            from kivy.uix.boxlayout import BoxLayout
            
            # Создаем прокручиваемое содержимое с фиксированной высотой
            scroll = ScrollView(size_hint_y=None, height=350)  # Уменьшаем высоту ScrollView
            content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=[10, 5, 10, 10])
            content.bind(minimum_height=content.setter('height'))
            
            # Добавляем заголовок и список файлов
            content.add_widget(Label(
                text='Deleted files:',
                size_hint_y=None,
                height=50,
                font_size='22sp',
                bold=True,
                halign='left',
                text_size=(400, None)
            ))
            
            for file in deleted_files:
                content.add_widget(Label(
                    text=file,
                    size_hint_y=None,
                    height=15,  # Уменьшена высота с 50 до 15 пикселей
                    font_size='18sp',
                    halign='left',
                    text_size=(400, None),
                    shorten=True,
                    shorten_from='right',
                    ellipsis_options={'ellipsis': '...'},
                    padding=(0, 2, 0, 2)  # Добавлены отступы сверху и снизу
                ))
            
            scroll.add_widget(content)
            
            # Создаем контейнер для основного содержимого и кнопки закрытия
            main_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[0, 0, 0, 10])
            main_layout.add_widget(scroll)
            
            # Создаем кнопку закрытия с иконкой, как у кнопки сохранения
            from ui.components.custom_button import CustomButton
            close_button = CustomButton(
                icon_path='fonts/Awesome/use/ok.png',
                text='',  # Без текста, только иконка
                size_hint_y=None,
                height=dp(50),
                background_color=(0.1, 0.5, 0.8, 1),  # Синий цвет, как у кнопки сохранения
                font_size='20sp'
            )
            
            # Добавляем кнопку в контейнер
            main_layout.add_widget(close_button)
            
            # Создаем попап с новым макетом
            popup = Popup(
                title='Log cleaning completed',
                title_size='24sp',
                title_align='center',
                content=main_layout,
                size_hint=(None, None),
                size=(500, 500)  # Общая высота окна с учетом отступов
            )
            
            # Привязываем действие закрытия к кнопке
            close_button.bind(on_release=popup.dismiss)
            
            # Открываем попап
            popup.open()
        else:
            logger.info("No old logs to delete")
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            
            content = Label(
                text='No old logs to delete',
                font_size='20sp',
                size_hint_y=None,
                height=50,
                halign='center',
                valign='middle'
            )
            
            popup = Popup(
                title='Log cleaning',
                title_size='24sp',
                title_align='center',
                content=content,
                size_hint=(None, None),
                size=(400, 150)
            )
            popup.open()
            
    except Exception as e:
        logger.error(f"Error deleting old logs: {e}")


def open_logs_in_editor(button_instance):
    """Открывает лог-файл в текстовом редакторе по умолчанию."""
    try:
        # Получаем путь к директории приложения
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logs_dir = os.path.join(app_dir, 'logs')
        
        # Получаем последний созданный файл лога
        log_files = sorted(
            [f for f in os.listdir(logs_dir) if f.startswith('logs_') and f.endswith('.txt')],
            key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)),
            reverse=True
        )
        
        if log_files:
            log_file = os.path.join(logs_dir, log_files[0])
            # Используем xdg-open для открытия в редакторе по умолчанию
            subprocess.Popen(['xdg-open', log_file])
        else:
            logger.warning("Не найден файл лога для открытия")
    except Exception as e:
        logger.error(f"Ошибка при открытии лога в редакторе: {e}")

def open_logs_terminal(button_instance):
    """Открывает терминал с отображением логов приложения."""
    def open_terminal():
        try:
            # Получаем путь к директории приложения
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            logs_dir = os.path.join(app_dir, 'logs')
            
            # Получаем последний созданный файл лога
            log_files = sorted(
                [f for f in os.listdir(logs_dir) if f.startswith('logs_') and f.endswith('.txt')],
                key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)),
                reverse=True
            )
            
            if log_files:
                log_file = os.path.join(logs_dir, log_files[0])
                script_content = f'''#!/bin/bash
                echo "Отслеживание логов (для выхода нажмите Ctrl+C):"
                if [ -f "{log_file}" ]; then
                    tail -f "{log_file}"
                else
                    echo "Файл логов не найден: {log_file}"
                fi
                read -p "Нажмите Enter для выхода..."
                '''
            else:
                script_content = '''#!/bin/bash
                echo "Файлы логов не найдены в директории logs."
                echo "Проверьте настройки логирования в приложении."
                read -p "Нажмите Enter для выхода..."
                '''
            
            # Создаем временный скрипт для отображения логов
            import tempfile
            import stat
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as f:
                script_path = f.name
                f.write(script_content)
            
            # Устанавливаем права на выполнение
            os.chmod(script_path, os.stat(script_path).st_mode | stat.S_IEXEC)
            
            # Список возможных команд для открытия терминала
            terminal_commands = [
                # Стандартные команды для разных окружений рабочего стола
                ['xdg-terminal', '--', script_path],
                ['x-terminal-emulator', '-e', script_path],
                ['terminator', '-x', 'bash', script_path],  # Терминатор
                ['gnome-terminal', '--', script_path],
                ['konsole', '-e', script_path],
                ['xfce4-terminal', '-x', script_path],
                ['lxterminal', '-e', script_path],
                ['mate-terminal', '--command', script_path],
                ['alacritty', '-e', 'bash', script_path],
                ['urxvt', '-e', 'bash', script_path],
                ['xterm', '-e', 'bash', script_path],
                # Если ничего не помогло, пробуем просто bash в текущей консоли
                ['bash', script_path]
            ]
            
            # Пробуем выполнить команды по очереди, пока не сработает
            for cmd in terminal_commands:
                try:
                    # Проверяем, существует ли исполняемый файл
                    if cmd[0] != 'bash' and not shutil.which(cmd[0]):
                        continue
                    
                    # Пробуем выполнить команду
                    subprocess.Popen(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
                    return  # Успешно открыли терминал, выходим из функции
                    
                except (FileNotFoundError, OSError) as e:
                    continue  # Пробуем следующую команду
            
            # Если ни одна команда не сработала
            print("Не удалось открыть терминал. Установите терминал, например: sudo pacman -S xterm или terminator")
            # Удаляем временный файл, если не удалось открыть терминал
            os.unlink(script_path)
        except Exception as e:
            print(f"Ошибка при открытии терминала с логами: {e}")
    
    # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
    threading.Thread(target=open_terminal, daemon=True).start()

def show_additional_actions(instance):
    """
    Показывает всплывающее окно с дополнительными действиями.
    
    Args:
        instance: Экземпляр кнопки, вызвавшей это окно
    """
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.metrics import dp
    from kivy.uix.button import Button
    
    # Создаем контейнер для кнопок
    content = BoxLayout(
        orientation='vertical',
        spacing=dp(10),
        padding=dp(20),
        size_hint=(1, None),
        height=dp(150)
    )
    
    # Первая кнопка
    btn1 = Button(
        text='Action for test 1',
        size_hint_y=None,
        height=dp(50),
        font_size='18sp',
        background_normal='',
        background_color=(0.2, 0.6, 0.8, 1)
    )
    
    # Вторая кнопка
    btn2 = Button(
        text='Action for test 2',
        size_hint_y=None,
        height=dp(50),
        font_size='18sp',
        background_normal='',
        background_color=(0.8, 0.3, 0.3, 1)
    )
    
    # Добавляем кнопки в контейнер
    content.add_widget(btn1)
    content.add_widget(btn2)
    
    # Создаем всплывающее окно
    popup = Popup(
        title='Additional actions',
        title_size='24sp',
        title_align='center',
        content=content,
        size_hint=(None, None),
        size=(dp(400), dp(250))
    )
    
    # Привязываем действия к кнопкам
    btn1.bind(on_press=lambda x: logger.info("Action 1 selected") or popup.dismiss())
    btn2.bind(on_press=lambda x: logger.info("Action 2 selected") or popup.dismiss())
    
    # Показываем окно
    popup.open()

def on_debug_switch(switch_instance, value, settings_window):
    """
    Обработчик изменения состояния переключателя отладочного режима.
    
    Args:
        switch_instance: Экземпляр переключателя
        value: Новое значение переключателя (True/False)
        settings_window: Экземпляр SettingsWindow
    """
    # Сохраняем состояние в атрибут, чтобы применить его при нажатии "Сохранить"
    settings_window.debug_mode_pending = value
    logger.info(f'Debug Mode changed to: {value} (will be saved on accept)')

def on_logging_switch(switch_instance, value, settings_window):
    """
    Обработчик изменения состояния переключателя логирования в файл.
    
    Args:
        switch_instance: Экземпляр переключателя
        value: Новое значение переключателя (True/False)
        settings_window: Экземпляр SettingsWindow
    """
    # Сохраняем состояние в атрибут, чтобы применить его при нажатии "Сохранить"
    settings_window.logging_to_file_pending = value
    logger.info(f'Logging to file changed to: {value} (will be saved on accept)')

def create_admin_section(settings_window):
    """
    Создает секцию с настройками админ-панели в виде таблицы.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройками админ-панели
    """
    # Основной контейнер секции
    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(180),  # Уменьшенная высота контейнера
        padding=(dp(20), dp(5), dp(20), dp(5)),  # Уменьшенные отступы по бокам
        spacing=dp(3)  # Уменьшенное расстояние между элементами
    )
    
    # Функция для обновления размера текста с отступом
    def update_text_size(inst, val):
        padding = dp(15)  # Отступ слева 15dp
        inst.text_size = (val[0] - padding, None)
        inst.halign = 'left'
        inst.valign = 'middle'
        inst.canvas.ask_update()

    # Таблица настроек
    table = GridLayout(
        cols=2,  # 2 колонки (текст и элемент управления)
        size_hint_y=None,
        spacing=0  # Убираем отступы между строками
    )
    
    # Вычисляем высоту таблицы на основе количества строк
    row_height = dp(50)  # Высота одной строки
    num_rows = 8  # Количество строк в таблице
    table.height = row_height * num_rows
    
    # Настройка ширины колонок
    def update_col_widths(*args):
        available_width = table.width  # ширина таблицы
        table.cols_minimum = {
            0: available_width * 0.8,  # 80% для текста
            1: available_width * 0.2   # 20% для элементов управления
        }
    
    table.bind(size=update_col_widths)
    update_col_widths()
    
    # Данные для строк таблицы
    rows = [
        ("Debug Mode", 'debug_switch', '28sp', True, 0, dp(50)),
        ("Logs in Terminal", 'terminal_button', '28sp', True, 0, dp(50)),
        ("Logs in Editor", 'editor_button', '28sp', True, 0, dp(50)),
        ("Clear Old Log Files", 'clear_button', '28sp', True, 0, dp(50)),
        ("Logging to File (Not work)", 'logging_switch', '28sp', True, 0, dp(50)),
        ("Any New Action 1", 'new_action_1_button', '22sp', False, 1, dp(30)),
        ("Any New Action 2", 'new_action_2_switch', '22sp', False, 1, dp(30)),
        ("Any New Action 3", 'new_action_3_switch', '22sp', False, 1, dp(30))
    ]
    
    # Создаем строки таблицы
    for text, switch_attr, font_size, is_bold, _, switch_height in rows:
        # Создаем лейбл
        label = Label(
            text=text,
            font_size=font_size,
            bold=is_bold,
            halign='left',
            valign='middle',
            size_hint_x=0.8,
            text_size=(None, None),
            padding=(dp(15), 0, 0, 0)  # Отступ слева
        )
        
        # Функция для обновления размера текста
        def update_text_size(inst, val):
            padding = dp(15)  # Отступ слева
            inst.text_size = (val[0] - padding, None)
            inst.halign = 'left'
            inst.valign = 'middle'
            inst.canvas.ask_update()
        
        label.bind(size=update_text_size)
        table.add_widget(label)
        
        # Создаем контейнер для переключателя/кнопки
        if 'switch' in switch_attr:
            switch_layout = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
                size_hint=(0.2, None),
                height=switch_height
            )
            
            # Создаем переключатель
            switch = CustomCheckBox(
                size_hint=(None, None),
                height=dp(30)  # Высота переключателя
            )
            
            # Настраиваем переключатель в зависимости от типа
            if switch_attr == 'debug_switch':
                switch.active = load_debug_state(settings_window)
                switch.bind(active=lambda i, v, sw=settings_window: on_debug_switch(i, v, sw))
                settings_window.debug_switch = switch
            elif switch_attr == 'logging_switch':
                switch.active = load_logging_state(settings_window)
                switch.bind(active=lambda i, v, sw=settings_window: on_logging_switch(i, v, sw))
                settings_window.logging_to_file_pending = switch.active
                settings_window.logging_switch = switch
            elif switch_attr in ['new_action_switch', 'another_action_switch']:
                switch.active = False
                setattr(settings_window, switch_attr, switch)
            
            switch_layout.add_widget(switch)
            table.add_widget(switch_layout)
            
        # Создаем кнопки
        elif 'button' in switch_attr:
            button_layout = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
                size_hint=(0.2, None),
                height=switch_height
            )
            
            # Создаем кнопку с адаптивным размером под текст
            button = None
            if switch_attr == 'terminal_button':
                button = RoundedButton(
                    text="Open",
                    size_hint=(None, None),
                    size=(dp(100), dp(40)),
                    font_size='16sp',
                    bg_color=(0.1, 0.5, 0.8, 1),
                    bg_color_press=(0.2, 0.6, 0.9, 1),
                    border_radius=dp(10)
                )
                button.bind(on_press=open_logs_terminal)
            elif switch_attr == 'editor_button':
                button = RoundedButton(
                    text="Open",
                    size_hint=(None, None),
                    size=(dp(100), dp(40)),
                    font_size='16sp',
                    bg_color=(0.1, 0.5, 0.8, 1),
                    bg_color_press=(0.2, 0.6, 0.9, 1),
                    border_radius=dp(10)
                )
                button.bind(on_press=open_logs_in_editor)
            elif switch_attr == 'clear_button':
                button = RoundedButton(
                    text="Clear",
                    size_hint=(None, None),
                    size=(dp(100), dp(40)),
                    font_size='16sp',
                    bg_color=(0.1, 0.5, 0.8, 1),
                    bg_color_press=(0.2, 0.6, 0.9, 1),
                    border_radius=dp(10)
                )
                button.bind(on_press=clear_old_logs)
            elif switch_attr == 'new_action_1_button':
                button = RoundedButton(
                    text="Show",
                    size_hint=(None, None),
                    size=(dp(100), dp(40)),
                    font_size='16sp',
                    bg_color=(0.1, 0.5, 0.8, 1),
                    bg_color_press=(0.2, 0.6, 0.9, 1),
                    border_radius=dp(10)
                )
                button.bind(on_press=show_additional_actions)
            
            # Если кнопка была создана, добавляем её в макет
            if button is not None:
                # Создаем контейнер для кнопки с фиксированным размером
                button_container = GridLayout(
                    cols=1,
                    size_hint=(None, None),
                    width=dp(120),
                    height=dp(50),
                    padding=(dp(10), dp(5), dp(10), dp(5))
                )
                button_container.add_widget(button)
                button_layout.add_widget(button_container)
            
            # Добавляем строку с кнопкой в таблицу
            table.add_widget(button_layout)
    
    # Добавляем таблицу в контейнер
    container.add_widget(table)
    
    # Сохраняем ссылку на секцию настроек
    settings_window.admin_section = container
    
    return container
