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

from ui.components.custom_switch import CustomSwitch
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
        settings_window: Экземпляр SettingsWindow с доступом к базе данных
        
    Returns:
        bool: Текущее состояние отладочного режима
    """
    try:
        if hasattr(settings_window, 'db'):
            # Пытаемся получить значение из базы данных
            debug_mode = settings_window.db.get_setting('debug_mode')
            # Преобразуем строковое значение в булево
            return debug_mode == '1' if debug_mode is not None else False
        return False
    except Exception as e:
        logger.error(f'Ошибка при загрузке состояния отладочного режима: {e}')
        return False

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
            
            # Создаем прокручиваемое содержимое
            scroll = ScrollView()
            content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
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
            
            popup = Popup(
                title='Log cleaning completed',
                title_size='24sp',
                title_align='center',
                content=scroll,
                size_hint=(None, None),
                size=(500, 400)
            )
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
        text='Действие 1',
        size_hint_y=None,
        height=dp(50),
        font_size='18sp',
        background_normal='',
        background_color=(0.2, 0.6, 0.8, 1)
    )
    
    # Вторая кнопка
    btn2 = Button(
        text='Действие 2',
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
        title='Дополнительные действия',
        title_size='24sp',
        title_align='center',
        content=content,
        size_hint=(None, None),
        size=(dp(400), dp(250))
    )
    
    # Привязываем действия к кнопкам
    btn1.bind(on_press=lambda x: logger.info("Выбрано действие 1") or popup.dismiss())
    btn2.bind(on_press=lambda x: logger.info("Выбрано действие 2") or popup.dismiss())
    
    # Показываем окно
    popup.open()

def on_debug_switch(switch_instance, value, settings_window):
    """
    Обработчик изменения состояния переключателя отладочного режима.
    
    Args:
        switch_instance: Экземпляр переключателя
        value: Новое значение переключателя (True/False)
        settings_window: Экземпляр окна настроек
    """
    # Только логируем изменение состояния, без сохранения в БД
    status = 'Enabled' if value else 'Disabled'
    logger.info(f'Debug Mode changed to: {status} (will be saved on accept)')

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
        height=dp(210),  # Такая же высота, как у уведомлений
        padding=(dp(30), dp(5), dp(30), dp(5)),
        spacing=dp(5)
    )
    
    # Функция для обновления размера текста с отступом
    def update_text_size(inst, val):
        padding = dp(15)  # Отступ слева 15dp
        inst.text_size = (val[0] - padding, None)
        inst.canvas.ask_update()

    # Таблица настроек
    table = BorderedGridLayout(
        cols=2,  # 2 колонки (текст и элемент управления)
        rows=8,  # 8 строк
        size_hint_y=None,
        height=dp(600),  # Высота для 8 строк
        spacing=0
    )
    
    # Настройка ширины столбцов
    def update_col_widths(*args):
        available_width = table.width  # ширина таблицы
        table.cols_minimum = {
            0: available_width * 0.7,  # 70% для текста
            1: available_width * 0.3   # 30% для элементов управления
        }
    
    table.bind(size=update_col_widths)
    update_col_widths()
    
    # Строка 1: Debug Mode + переключатель
    label1 = Label(
        text="Debug Mode",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label1.bind(size=update_text_size)
    table.add_widget(label1)
    
    # Контейнер с центрированием для переключателя Debug Mode
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    debug_switch = CustomSwitch(
        size_hint=(None, None),
        size=(dp(90), dp(40))
    )
    debug_switch.active = load_debug_state(settings_window)
    debug_switch.bind(active=lambda instance, value: on_debug_switch(instance, value, settings_window))
    settings_window.debug_switch = debug_switch
    anchor.add_widget(debug_switch)
    table.add_widget(anchor)
    
    # Строка 2: Logs in Terminal + кнопка Open
    label2 = Label(
        text="Logs in Terminal",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label2.bind(size=update_text_size)
    table.add_widget(label2)
    
    # Контейнер с центрированием для кнопки Open Terminal
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    btn_terminal = RoundedButton(
        text="Open",
        size_hint=(None, None),
        size=(dp(90), dp(35)),
        border_radius=dp(10)
    )
    btn_terminal.bind(on_press=open_logs_terminal)
    anchor.add_widget(btn_terminal)
    table.add_widget(anchor)
    
    # Строка 3: Logs in Editor + кнопка Open
    label3 = Label(
        text="Logs in Editor",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label3.bind(size=update_text_size)
    table.add_widget(label3)
    
    # Контейнер с центрированием для кнопки Open Editor
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    btn_editor = RoundedButton(
        text="Open",
        size_hint=(None, None),
        size=(dp(90), dp(35)),
        border_radius=dp(10)
    )
    btn_editor.bind(on_press=open_logs_in_editor)
    anchor.add_widget(btn_editor)
    table.add_widget(anchor)
    
    # Строка 4: Logging to File + переключатель
    label4 = Label(
        text="Logging to File",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label4.bind(size=update_text_size)
    table.add_widget(label4)
    
    # Контейнер с центрированием для переключателя Logging to File
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    logging_switch = CustomSwitch(
        size_hint=(None, None),
        size=(dp(90), dp(40))
    )
    logging_switch.active = False
    settings_window.logging_switch = logging_switch
    anchor.add_widget(logging_switch)
    table.add_widget(anchor)
    
    # Строка 5: Clear Old Log Files + кнопка Clear
    label5 = Label(
        text="Clear Old Log Files",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label5.bind(size=update_text_size)
    table.add_widget(label5)
    
    # Контейнер с центрированием для кнопки Clear
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    btn_clear = RoundedButton(
        text="Clear",
        size_hint=(None, None),
        size=(dp(90), dp(35)),
        border_radius=dp(10)
    )
    btn_clear.bind(on_press=clear_old_logs)
    anchor.add_widget(btn_clear)
    table.add_widget(anchor)
    
    # Строка 6: Additional Actions + переключатель
    label6 = Label(
        text="Additional Actions",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label6.bind(size=update_text_size)
    table.add_widget(label6)
    
    # Контейнер с центрированием для переключателя Additional Actions
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    actions_switch = CustomSwitch(
        size_hint=(None, None),
        size=(dp(90), dp(40))
    )
    actions_switch.active = False
    settings_window.actions_switch = actions_switch
    anchor.add_widget(actions_switch)
    table.add_widget(anchor)
    
    # Строка 7: Additional Actions + кнопка Show Actions
    label7 = Label(
        text="Additional Actions",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label7.bind(size=update_text_size)
    table.add_widget(label7)
    
    # Контейнер с центрированием для кнопки Show Actions
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    btn_show = RoundedButton(
        text="Show",
        size_hint=(None, None),
        size=(dp(90), dp(35)),
        border_radius=dp(10)
    )
    btn_show.bind(on_press=show_additional_actions)
    anchor.add_widget(btn_show)
    table.add_widget(anchor)
    
    # Строка 8: Additional Actions + переключатель
    label8 = Label(
        text="Additional Actions",
        halign='left',
        valign='middle',
        font_size='22sp',
        bold=False,
        size_hint_x=0.9
    )
    label8.bind(size=update_text_size)
    table.add_widget(label8)
    
    # Контейнер с центрированием для второго переключателя Additional Actions
    anchor = AnchorLayout(anchor_x='center', size_hint_x=1)
    actions_switch2 = CustomSwitch(
        size_hint=(None, None),
        size=(dp(90), dp(40))
    )
    actions_switch2.active = False
    settings_window.actions_switch2 = actions_switch2
    anchor.add_widget(actions_switch2)
    table.add_widget(anchor)
    
    container.add_widget(table)
    settings_window.admin_section = container
    return container
