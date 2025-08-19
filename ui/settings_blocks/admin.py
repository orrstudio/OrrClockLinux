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
from kivy.properties import ListProperty

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

            # Вертикальные линии
            col1 = self.x + self.width * 0.4
            col2 = self.x + self.width * 0.7
            Line(points=[col1, self.y, col1, self.top], width=1)
            Line(points=[col2, self.y, col2, self.top], width=1)

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
    
    # Таблица настроек
    table = BorderedGridLayout(
        cols=3,
        rows=3,
        size_hint_y=None,
        height=dp(150),  # Такая же высота, как у уведомлений
        spacing=0
    )
    
    # Настройка ширины столбцов
    def update_col_widths(*args):
        available_width = table.width  # ширина именно таблицы
        table.cols_minimum = {
            0: available_width * 0.4,
            1: available_width * 0.3,
            2: available_width * 0.3
        }
    
    table.bind(size=update_col_widths)
    update_col_widths()
    
    # Данные для строк
    rows = [
        ("Debug Mode", 'debug_switch', 'debug_button'),
        ("Feature 2", 'feature2_switch', 'feature2_button'),
        ("Feature 3", 'feature3_switch', 'feature3_button')
    ]

    for text, switch_attr, button_attr in rows:
        # 1. Текст (слева по центру вертикально)
        label = Label(
            text=text,
            halign='left',
            valign='middle',
            font_size='22sp',
            bold=False,
            size_hint_x=0.8
        )

        def update_text_size(inst, val):
            padding = dp(30)  # отступ слева
            inst.text_size = (val[0] - padding, None)
            inst.canvas.ask_update()

        label.bind(size=update_text_size)
        table.add_widget(label)

        # 2. Переключатель (по центру)
        switch_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        if switch_attr == 'debug_switch':
            # Используем существующий переключатель для debug
            debug_enabled = load_debug_state(settings_window)
            switch = CustomSwitch(
                size_hint=(None, None),
                size=(dp(64), dp(40))  # Размер как в уведомлениях
            )
            switch.active = debug_enabled
            switch.bind(active=lambda instance, value: on_debug_switch(instance, value, settings_window))
            settings_window.debug_switch = switch
        else:
            switch = CustomSwitch(
                size_hint=(None, None),
                size=(dp(64), dp(40))
            )
            switch.active = False
        
        switch_layout.add_widget(switch)
        setattr(settings_window, switch_attr, switch)
        table.add_widget(switch_layout)

        # 3. Кнопка с закругленными углами (по центру)
        button_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        button = RoundedButton(
            text="Логи" if switch_attr == 'debug_switch' else "Button",
            size_hint=(None, None),
            size=(dp(100), dp(35)),
            border_radius=dp(10)  # Радиус скругления
        )
        if switch_attr == 'debug_switch':
            button.bind(on_press=open_logs_terminal)
        button_layout.add_widget(button)
        setattr(settings_window, button_attr, button)
        table.add_widget(button_layout)
    
    container.add_widget(table)
    settings_window.admin_section = container
    return container
