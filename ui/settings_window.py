"""
Settings Window Module.
Реализует минималистичный интерфейс настроек с выбором цвета.

Основные компоненты:
- Компактный заголовок
- Сетка из 9 цветов с выделением активного белой рамкой
- Кнопки Save/Cancel для применения/отмены изменений
"""

import logging

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
# Удаляем устаревший импорт ListView и ListItemButton
# и используем Spinner вместо ListView
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

# Импортируем компоненты интерфейса
from ui.settings_color import ColorButton

# Импортируем базу данных и утилиты
from data.database import SettingsDatabase
from logic.display_utils import is_mobile_device

logger = logging.getLogger(__name__)

class SettingsCard(GridLayout):
    """Карточка для группы настроек"""
    def __init__(self, title="", **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.row_default_height = dp(5)
        self.size_hint_y = None
        self.height = dp(200)  # Начальная высота
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        # Фон карточки
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Заголовок секции
        if title:
            title_label = Label(
                text=title.upper(),
                color=(1, 1, 1, 0.8),
                font_size=sp(16),
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            title_label.bind(size=title_label.setter('text_size'))
            self.add_widget(title_label)
            
    def _update_rect(self, instance, value):
        """Обновляет позицию и размер фонового прямоугольника"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SettingsSection(ScrollView):
    """Секция настроек"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(500)  # Будет обновляться динамически
        
        # Фон секции
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 0.95)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Основной layout с адаптивными отступами
        self.layout = GridLayout(
            cols=1,
            orientation='vertical', 
            spacing=0,
            padding=0,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.add_widget(self.layout)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class CustomButton(Button):
    def __init__(self, icon_path='', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.icon_path = icon_path
        self.icon_size = dp(30)
        
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
        with self.canvas.after:
            self.icon_color = Color(1, 1, 1, 1)
            self.icon = Rectangle(source=self.icon_path, size=(self.icon_size, self.icon_size))
        
        self.bind(pos=self._update_icon, size=self._update_icon)
        self.bind(size=self._update_background, pos=self._update_background)
    
    def _update_icon(self, *args):
        if hasattr(self, 'icon'):
            # Явно вычисляем центр
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            
            self.icon.pos = (
                center_x - self.icon_size/2,
                center_y - self.icon_size/2
            )
            self.icon.size = (self.icon_size, self.icon_size)
            
    def _update_background(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

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
    
    # Список доступных цветов
    colors = {
        'lime': (0, 1, 0, 1),
        'aqua': (0, 1, 1, 1),
        'blue': (0, 0, 1, 1),
        'red': (1, 0, 0, 1),
        'yellow': (1, 1, 0, 1),
        'white': (1, 1, 1, 1)
    }

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
        
        # Загружаем настройки для каждого блока азана отдельно
        self.selected_azan_spinner = self.db.get_setting('azan_spinner') or 'Azan 1'
        self.selected_azan_dropdown = self.db.get_setting('azan_dropdown') or 'Azan 1'
        self.selected_azan_popup = self.db.get_setting('azan_popup') or 'Azan 1'
        
        # Проверяем корректность значений
        valid_azans = ['Azan 1', 'Azan 2', 'Azan 3']
        if self.selected_azan_spinner not in valid_azans:
            self.selected_azan_spinner = 'Azan 1'
        if self.selected_azan_dropdown not in valid_azans:
            self.selected_azan_dropdown = 'Azan 1'
        if self.selected_azan_popup not in valid_azans:
            self.selected_azan_popup = 'Azan 1'
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
        
        # Заголовок
        title_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(30),
            padding=[dp(20), 0]
        )
        
        # Фон заголовка
        with title_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.title_rect = Rectangle(pos=title_layout.pos, size=title_layout.size)
        title_layout.bind(pos=self._update_title_rect, size=self._update_title_rect)
        
        # Текст заголовка
        title_label = Label(
            text='SETTINGS',
            color=(1, 1, 1, 1),
            font_size=sp(16),
            bold=True,
            halign='center',
            valign='center'
        )
        title_layout.add_widget(title_label)
        
        # Основной контейнер для всех секций
        content_container = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=0,
            padding=0
        )
        content_container.bind(minimum_height=content_container.setter('height'))
        
        # Контент (ScrollView)
        content_layout = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            size_hint=(1, 1)
        )
        
        # Основной вертикальный контейнер для блока выбора цвета
        color_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Увеличиваем высоту для учета отступов
            padding=[dp(20), dp(15), dp(20), dp(20)],  # Отступы: слева, сверху, справа, снизу
            spacing=dp(10),
            row_force_default=True,
            row_default_height=dp(30),  # Высота строки по умолчанию
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока выбора цвета
        color_title = Label(
            text='Saatın rəngi',
            color=(1, 1, 1, 1),
            font_size=sp(22),
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            valign='middle',
            text_size=(Window.width - dp(40), None),
            shorten=True,
            shorten_from='right',
            padding=(0, dp(5))
        )
        
        def update_color_title_size(*args):
            color_title.text_size = (Window.width - dp(40), None)
            color_title.texture_update()
        
        Window.bind(width=update_color_title_size)
        Clock.schedule_once(update_color_title_size)
        
        # Сетка цветов (в один ряд)
        colors_grid = GridLayout(
            cols=6,
            spacing=dp(5),
            size_hint_y=None,
            height=dp(25)  # Фиксированная высота для строки с цветами
        )
        
        # Создаем кнопки цветов
        for color_name, color_tuple in self.colors.items():
            color_button = ColorButton(
                color_name=color_name,
                color_tuple=color_tuple,
                text='',
                size_hint=(1, 1),
                background_normal=''
            )
            color_button.bind(on_release=self._on_color_button_press)
            
            # Сохраняем кнопку если это активный цвет
            if color_name == self.initial_color:
                self.active_button = color_button
            
            colors_grid.add_widget(color_button)
        
        # Собираем блок выбора цвета
        color_section.add_widget(color_title)  # Добавляем заголовок
        color_section.add_widget(colors_grid)  # Добавляем сетку цветов
        
        # Блок выбора азана
        azan_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Такая же высота, как у блока цветов
            padding=[dp(20), dp(15), dp(20), dp(20)],
            spacing=dp(10),
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока выбора азана
        azan_title = Label(
            text='Azan səsi',
            color=(1, 1, 1, 1),
            font_size=sp(22),
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            valign='middle',
            text_size=(Window.width - dp(40), None),
            padding=(0, dp(5)),
            shorten=True,
            shorten_from='right'
        )
        
        def update_azan_title_size(*args):
            azan_title.text_size = (Window.width - dp(40), None)
            azan_title.texture_update()
        
        Window.bind(width=update_azan_title_size)
        Clock.schedule_once(update_azan_title_size)
        
        # Выпадающий список для выбора азана
        self.azan_spinner = Spinner(
            text='Azan 1',
            values=('Azan 1', 'Azan 2', 'Azan 3'),
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        
        # Обработчик выбора значения
        self.azan_spinner.bind(text=self.on_azan_selected)
        
        # Добавляем виджеты в секцию
        azan_section.add_widget(azan_title)
        azan_section.add_widget(self.azan_spinner)
        
        # Блок с DropDown
        dropdown_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Такая же высота, как у остальных блоков
            padding=[dp(20), dp(15), dp(20), dp(20)],
            spacing=dp(10),
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока с DropDown
        dropdown_title = Label(
            text='Azan (DropDown)',
            color=(1, 1, 1, 1),
            font_size=sp(22),
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            valign='middle',
            text_size=(Window.width - dp(40), None),
            padding=(0, dp(5)),
            shorten=True,
            shorten_from='right'
        )
        
        def update_dropdown_title_size(*args):
            dropdown_title.text_size = (Window.width - dp(40), None)
            dropdown_title.texture_update()
        
        Window.bind(width=update_dropdown_title_size)
        Clock.schedule_once(update_dropdown_title_size)
        
        # Кнопка для вызова DropDown
        self.dropdown_btn = Button(
            text='Azan 1',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        
        # Создаем выпадающее меню
        self.dropdown = DropDown()
        for item in ['Azan 1', 'Azan 2', 'Azan 3']:
            btn = Button(
                text=item, 
                size_hint_y=None, 
                height=dp(40),
                background_color=(0.25, 0.25, 0.25, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=lambda btn: self.select_dropdown_item(btn.text))
            self.dropdown.add_widget(btn)
        
        # Привязываем кнопку к выпадающему меню
        self.dropdown_btn.bind(on_release=self.dropdown.open)
        
        # Добавляем элементы в секцию
        dropdown_section.add_widget(dropdown_title)
        dropdown_section.add_widget(self.dropdown_btn)
        
        # Блок с Popup и ListView
        popup_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Такая же высота, как у остальных блоков
            padding=[dp(20), dp(15), dp(20), dp(20)],
            spacing=dp(10),
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока с Popup
        popup_title = Label(
            text='Azan (Popup + ListView)',
            color=(1, 1, 1, 1),
            font_size=sp(22),
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            valign='middle',
            text_size=(Window.width - dp(40), None),
            padding=(0, dp(5)),
            shorten=True,
            shorten_from='right'
        )
        
        def update_popup_title_size(*args):
            popup_title.text_size = (Window.width - dp(40), None)
            popup_title.texture_update()
        
        Window.bind(width=update_popup_title_size)
        Clock.schedule_once(update_popup_title_size)
        
        # Кнопка для вызова Popup
        self.popup_btn = Button(
            text=self.selected_azan_popup if hasattr(self, 'selected_azan_popup') else 'Azan 1',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        self.popup_btn.bind(on_release=self.show_azan_popup)
        
        # Добавляем элементы в секцию
        popup_section.add_widget(popup_title)
        popup_section.add_widget(self.popup_btn)
        
        # Инициализируем ссылки на виджеты для доступа из других методов
        self.color_section = color_section
        self.azan_section = azan_section
        self.dropdown_section = dropdown_section
        self.popup_section = popup_section
        
        # Добавляем все виджеты в основной контейнер
        content_container.clear_widgets()  # Очищаем контейнер
        
        # Добавляем блоки с отступами
        content_container.add_widget(color_section)
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(azan_section)
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(dropdown_section)
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(popup_section)
        
        # Обновляем размеры после добавления всех виджетов
        Clock.schedule_once(self.print_sizes, 0.5)
        
        # Добавляем контейнер в ScrollView
        content_layout.add_widget(content_container)
        
        # Нижняя панель с кнопками
        bottom_panel = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10),
            padding=[dp(20), dp(5)]
        )
        
        # Фон нижней панели
        with bottom_panel.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bottom_rect = Rectangle(pos=bottom_panel.pos, size=bottom_panel.size)
        bottom_panel.bind(pos=self._update_bottom_rect, size=self._update_bottom_rect)
        
        # Стиль кнопок
        button_style = {
            'size_hint_x': 0.5,
            'size_hint_y': None,
            'height': dp(50),
            'font_size': sp(22)
        }
        
        # Кнопки управления
        cancel_button = CustomButton(
            icon_path='fonts/Awesome/use/x.png',
            text="",  # Убираем текст
            background_color=(3, 0, 0, 1),
            **button_style
        )
        
        accept_button = CustomButton(
            icon_path='fonts/Awesome/use/ok.png',
            text="",  # Убираем текст
            background_color=(0, 0.7, 0, 1),
            **button_style
        )

        cancel_button.bind(on_release=self.dismiss)
        accept_button.bind(on_release=self.on_accept)
        
        bottom_panel.add_widget(cancel_button)
        bottom_panel.add_widget(accept_button)
        
        # Собираем все вместе
        main_layout.add_widget(title_layout)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(bottom_panel)
        
        # Добавляем основной layout в окно
        self.add_widget(main_layout)
        
        # Добавляем рамку к активной кнопке после отрисовки
        Clock.schedule_once(self._add_initial_border, 0)

    def _add_initial_border(self, dt):
        """Добавляет рамку к изначально активной кнопке и инициализирует выбранные азаны."""
        if hasattr(self, 'active_button') and self.active_button is not None:
            self._add_border_to_button(self.active_button)
            
        # Устанавливаем выбранные азаны в соответствующих виджетах
        if hasattr(self, 'azan_spinner') and hasattr(self, 'selected_azan_spinner'):
            if self.selected_azan_spinner in self.azan_spinner.values:
                self.azan_spinner.text = self.selected_azan_spinner
                
        if hasattr(self, 'dropdown_btn') and hasattr(self, 'selected_azan_dropdown'):
            self.dropdown_btn.text = self.selected_azan_dropdown
            
        if hasattr(self, 'popup_btn') and hasattr(self, 'selected_azan_popup'):
            self.popup_btn.text = self.selected_azan_popup
    
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
            
            # Инициализируем выбранные азаны, если они еще не были инициализированы
            if not hasattr(self, 'selected_azan_spinner'):
                self.selected_azan_spinner = self.db.get_setting('azan_spinner') or 'Azan 1'
            if not hasattr(self, 'selected_azan_dropdown'):
                self.selected_azan_dropdown = self.db.get_setting('azan_dropdown') or 'Azan 1'
            if not hasattr(self, 'selected_azan_popup'):
                self.selected_azan_popup = self.db.get_setting('azan_popup') or 'Azan 1'
        except Exception as e:
            logger.error(f"Error in _on_color_button_press: {e}")

    def on_azan_selected(self, spinner, text):
        """Обработчик выбора азана в Spinner"""
        self.selected_azan_spinner = text
        
    def select_dropdown_item(self, text):
        """Обработчик выбора азана в DropDown"""
        self.dropdown_btn.text = text
        self.selected_azan_dropdown = text
        self.dropdown.dismiss()
        
    def show_azan_popup(self, instance):
        """Показывает всплывающее окно с выбором азана"""
        # Создаем Spinner с выбором азана
        spinner = Spinner(
            text=self.selected_azan_popup if hasattr(self, 'selected_azan_popup') else 'Azan 1',
            values=('Azan 1', 'Azan 2', 'Azan 3'),
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Создаем всплывающее окно
        popup = Popup(
            title='Выберите азан',
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        # Создаем контейнер для Spinner
        layout = GridLayout(cols=1, spacing=10, padding=10)
        layout.add_widget(Widget())  # Пустой виджет для центрирования
        layout.add_widget(spinner)
        layout.add_widget(Widget())  # Пустой виджет для центрирования
        
        # Добавляем Spinner во всплывающее окно
        popup.content = layout
        
        # Обработчик выбора элемента
        spinner.bind(text=lambda instance, value: self._on_azan_selected(value))
        
        # Открываем всплывающее окно
        popup.open()
            
    def _on_azan_selected(self, azan_text):
        """Обработчик выбора азана в Spinner"""
        if not azan_text or azan_text == 'Выберите азан':
            return
        
        try:
            # Обновляем текст кнопки
            self.popup_btn.text = azan_text
            
            # Сохраняем выбранное значение
            self.selected_azan_popup = azan_text
            
            # Закрываем всплывающее окно
            for child in Window.children:
                if isinstance(child, Popup):
                    child.dismiss()
                    break
        except Exception as e:
            logger.error(f"Ошибка в _on_azan_selected: {e}")

    def on_azan_selected(self, spinner, text):
        """Обработчик выбора азана в Spinner"""
        self.selected_azan_spinner = text
            
    def select_dropdown_item(self, text):
        """Обработчик выбора азана в DropDown"""
        self.dropdown_btn.text = text
        self.selected_azan_dropdown = text
        self.dropdown.dismiss()
        


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
            
            # Инициализируем выбранные азаны, если они еще не были инициализированы
            if not hasattr(self, 'selected_azan_spinner'):
                self.selected_azan_spinner = self.db.get_setting('azan_spinner') or 'Azan 1'
            if not hasattr(self, 'selected_azan_dropdown'):
                self.selected_azan_dropdown = self.db.get_setting('azan_dropdown') or 'Azan 1'
            if not hasattr(self, 'selected_azan_popup'):
                self.selected_azan_popup = self.db.get_setting('azan_popup') or 'Azan 1'
                
        except Exception as e:
            print(f"Ошибка при обработке нажатия на кнопку: {e}")
    
    def on_azan_selected(self, spinner, text):
        """Обработчик выбора азана в Spinner"""
        self.selected_azan_spinner = text
            
    def select_dropdown_item(self, text):
        """Обработчик выбора азана в DropDown"""
        self.dropdown_btn.text = text
        self.selected_azan_dropdown = text
        self.dropdown.dismiss()
        
    def show_azan_popup(self, instance):
        """Показывает всплывающее окно с выбором азана"""
        # Создаем Spinner с выбором азана
        spinner = Spinner(
            text=self.selected_azan_popup if hasattr(self, 'selected_azan_popup') else 'Azan 1',
            values=('Azan 1', 'Azan 2', 'Azan 3'),
            size_hint=(None, None),
            size=(200, 44),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Создаем всплывающее окно
        popup = Popup(
            title='Выберите азан',
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        # Создаем контейнер для Spinner
        layout = GridLayout(cols=1, spacing=10, padding=10)
        layout.add_widget(Widget())  # Пустой виджет для центрирования
        layout.add_widget(spinner)
        layout.add_widget(Widget())  # Пустой виджет для центрирования
        
        # Добавляем Spinner во всплывающее окно
        popup.content = layout
        
        # Обработчик выбора элемента
        spinner.bind(text=lambda instance, value: self._on_azan_selected(value))
        
        # Открываем всплывающее окно
        popup.open()
    
    def _on_azan_selected(self, azan_text):
        """Обработчик выбора азана в Spinner"""
        if not azan_text or azan_text == 'Выберите азан':
            return
        
        try:
            # Обновляем текст кнопки
            self.popup_btn.text = azan_text
            
            # Сохраняем выбранное значение
            self.selected_azan_popup = azan_text
            
            # Закрываем всплывающее окно
            for child in Window.children:
                if isinstance(child, Popup):
                    child.dismiss()
                    break
        except Exception as e:
            print(f"Ошибка в _on_azan_selected: {e}")
    
    def on_azan_selected(self, spinner, text):
        """Обработчик выбора азана в Spinner"""
        self.selected_azan_spinner = text
    
    def select_dropdown_item(self, text):
        """Обработчик выбора азана в DropDown"""
        self.dropdown_btn.text = text
        self.selected_azan_dropdown = text
        self.dropdown.dismiss()
    
    def print_sizes(self, *args, show_before_save=False):
        """
        Выводит информацию о текущих настройках.
        
        Args:
            show_before_save (bool): Если True, показывает настройки перед сохранением
        """
        # Заголовок раздела размеров и позиций окон
        print("\n" + "="*50)
        print("         РАЗМЕР И ПОЗИЦИЯ ОКОН ПРИЛОЖЕНИЯ")
        print("="*50 + "\n")
        
        # Раздел: Главное окно
        print("-"*50)
        print("                  ГЛАВНОЕ ОКНО")
        print("-"*50)
        try:
            # Получаем сохраненные настройки главного окна из базы данных
            main_settings = self.db.get_window_settings()
            if main_settings:
                width, height, x, y = main_settings
                print(f"Размер: {int(width)} x {int(height)}")
                print(f"Позиция: x={int(x)}, y={int(y)}")
            else:
                print("Данные главного окна не найдены в базе")
        except Exception as e:
            print(f"Ошибка при получении данных главного окна: {e}")
        print("-"*50)
        
        # Раздел: Окно настроек
        print("                 ОКНО НАСТРОЕК")
        print("-"*50)
        try:
            # Получаем сохраненные настройки окна настроек из базы данных
            settings = self.db.get_settings_window_settings()
            if settings:
                width, height, x, y = settings
                print(f"Размер: {int(width)} x {int(height)}")
                print(f"Позиция: x={int(x)}, y={int(y)}")
            else:
                print("Данные окна настроек не найдены в базе")
        except Exception as e:
            print(f"Ошибка при получении данных окна настроек: {e}")
        print("-"*50 + "\n")
        
        # Заголовок раздела настроек приложения
        print("="*50)
        print("               НАСТРОЙКИ ПРИЛОЖЕНИЯ")
        print("="*50 + "\n")
        
        # Раздел: Цвет часов
        print("                    ЦВЕТ ЧАСОВ")
        print("-"*50)
        if hasattr(self, 'selected_color'):
            color_name = self.selected_color.capitalize()
            print(f"{color_name}")
        print("-"*50)
        
        # Раздел: Настройка азанов
        print("                 НАСТРОЙКА АЗАНОВ")
        print("-"*50)
        if hasattr(self, 'selected_azan_spinner'):
            print(f"Spinner: {self.selected_azan_spinner}")
        if hasattr(self, 'selected_azan_dropdown'):
            print(f"DropDown: {self.selected_azan_dropdown}")
        if hasattr(self, 'selected_azan_popup'):
            print(f"Popup: {self.selected_azan_popup}")
        print("-"*50)
        
        # Раздел: Размеры блоков
        print("                  РАЗМЕРЫ БЛОКОВ")
        print("-"*50)
        if hasattr(self, 'azan_section'):
            print(f"Spinner: size={self.azan_section.size}, pos={self.azan_section.pos}")
        if hasattr(self, 'dropdown_section'):
            print(f"DropDown: size={self.dropdown_section.size}, pos={self.dropdown_section.pos}")
        if hasattr(self, 'popup_section'):
            print(f"Popup: size={self.popup_section.size}, pos={self.popup_section.pos}")
        print("-"*50 + "\n")
        
        # Раздел: Времена молитв из базы данных
        print("="*50)
        print("     ИМЕЮЩИЕСЯ ВРЕМЕНА МОЛИТВ В БАЗЕ ДАННЫХ")
        print("="*50 + "\n")
        try:
            # Импортируем менеджер молитв
            from logic.prayer_times import prayer_times_manager
            
            # Получаем данные из базы
            cursor = prayer_times_manager.db.connection.cursor()
            
            # Получаем текущую дату и дату завтра
            from datetime import datetime, timedelta
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            date_format = "%Y-%m-%d"
            
            cursor.execute('''
                SELECT * FROM prayer_times 
                WHERE date = ? OR date = ?
                ORDER BY date ASC
            ''', (today.strftime(date_format), tomorrow.strftime(date_format)))
            
            # Получаем строки с данными
            rows = cursor.fetchall()
            
            if rows:
                # Получаем заголовки колонок
                columns = [desc[0] for desc in cursor.description]
                
                # Пропускаем служебные поля
                skip_columns = {'date', 'created_at'}
                prayer_columns = [col for col in columns if col not in skip_columns]
                
                # Формируем данные для вывода
                dates = []
                prayer_data = {col: [] for col in prayer_columns}
                
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Форматируем дату из YYYY-MM-DD в DD/MM
                    date_parts = row_dict['date'].split('-')
                    if len(date_parts) == 3:
                        dates.append(f"{date_parts[2]}/{date_parts[1]}")
                    else:
                        dates.append(row_dict['date'])
                    
                    for col in prayer_columns:
                        time_value = row_dict.get(col, '--:--')
                        # Оставляем только часы и минуты (первые 5 символов)
                        prayer_data[col].append(time_value[:5] if time_value else '--:--')
                
                # Выводим заголовок с датами
                header = "Date     |"
                separator = "----------"
                
                for date in dates:
                    header += f" {date} |"
                    separator += "-------"
                
                print(separator)
                print(header)
                print(separator)
                
                # Выводим времена молитв
                for prayer in prayer_columns:
                    times = prayer_data[prayer]
                    line = f"{prayer:<9}|"
                    for time in times:
                        line += f" {time} |"
                    print(line)
                
                print(separator + "\n")
            else:
                print("В базе данных нет информации о временах молитв\n")
                
        except Exception as e:
            print(f"Ошибка при получении данных из базы: {e}\n")
        
        print("="*21 + " КОНЕЦ " + "="*22 + "\n")

    def on_accept(self, *args):
        """Сохраняет настройки при нажатии кнопки Save."""
        try:
            # Сохраняем цвет, если выбран
            if hasattr(self, 'selected_color') and self.selected_color:
                # Преобразуем название цвета в нижний регистр
                color_key = self.selected_color.lower()
                
                if color_key in self.colors:
                    # Сохраняем в базу данных
                    self.db.save_setting('color', color_key)
                    
                    # Применяем цвет через callback
                    if self.apply_callback:
                        self.apply_callback(self.colors[color_key])
                else:
                    print(f"Предупреждение: Неизвестный цвет: {self.selected_color}")
            
            # Сохраняем выбранные азаны для каждого блока
            if hasattr(self, 'selected_azan_spinner'):
                self.db.save_setting('azan_spinner', self.selected_azan_spinner)
                
            if hasattr(self, 'selected_azan_dropdown'):
                self.db.save_setting('azan_dropdown', self.selected_azan_dropdown)
                
            if hasattr(self, 'selected_azan_popup'):
                self.db.save_setting('azan_popup', self.selected_azan_popup)
            
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
    
    @staticmethod
    def get_color_tuple(color_name):
        """Преобразование названия цвета в RGB"""
        colors = {
            'lime': (0, 1, 0, 1),
            'aqua': (0, 1, 1, 1),
            'blue': (0, 0, 1, 1),
            'red': (1, 0, 0, 1),
            'yellow': (1, 1, 0, 1),
            'white': (1, 1, 1, 1)
        }
        return colors.get(color_name, (0, 1, 0, 1))  

    @staticmethod
    def get_color_name(color_tuple):
        """Преобразование RGB в название цвета"""
        colors = {
            (0, 1, 0, 1): 'lime',
            (0, 1, 1, 1): 'aqua',
            (0, 0, 1, 1): 'blue',
            (1, 0, 0, 1): 'red',
            (1, 1, 0, 1): 'yellow',
            (1, 1, 1, 1): 'white'
        }
        return colors.get(color_tuple, 'lime')
