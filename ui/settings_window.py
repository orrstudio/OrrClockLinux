import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
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
        
        # Создаем секцию выбора цвета
        color_section = create_color_section(self)
        
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
        
        # Секция админ-панели
        debug_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Такая же высота, как у других блоков
            padding=[dp(20), dp(15), dp(20), dp(20)],
            spacing=dp(10),
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока
        debug_title = Label(
            text='Панель администратора',
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
        
        def update_debug_title_size(*args):
            debug_title.text_size = (Window.width - dp(40), None)
            debug_title.texture_update()
        
        Window.bind(width=update_debug_title_size)
        Clock.schedule_once(update_debug_title_size)
        
        # Контейнер для элементов управления (3 колонки по 1/3 ширины)
        controls_layout = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Получаем текущее состояние отладочного режима из базы данных
        from utils.logger import _get_debug_state
        debug_enabled = _get_debug_state()
        
        # Метка (1/3 ширины) с переносом текста
        switch_label = ResponsiveLabel(
            text='Отладочный режим:',
            markup=True
        )
        
        # Переключатель (1/3 ширины)
        self.debug_switch = Switch(
            active=debug_enabled,
            size_hint_x=1/3
        )
        
        # Пустой виджет для выравнивания (1/3 ширины)
        empty_widget = Widget(size_hint_x=1/3)
        
        # Добавляем виджеты в контейнер
        controls_layout.add_widget(switch_label)
        controls_layout.add_widget(self.debug_switch)
        controls_layout.add_widget(empty_widget)
        
        # Добавляем виджеты в секцию
        debug_section.add_widget(debug_title)
        debug_section.add_widget(controls_layout)
        
        # Блок аудио уведомлений
        audio_section = GridLayout(
            cols=1,
            size_hint_y=None,
            height=dp(110),  # Такая же высота, как у других блоков
            padding=[dp(20), dp(15), dp(20), dp(20)],
            spacing=dp(10),
            size_hint=(1, None)
        )
        
        # Адаптивный заголовок блока
        audio_title = Label(
            text='Аудио уведомления',
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
        
        def update_audio_title_size(*args):
            audio_title.text_size = (Window.width - dp(40), None)
            audio_title.texture_update()
        
        Window.bind(width=update_audio_title_size)
        Clock.schedule_once(update_audio_title_size)
        
        # Контейнер для элементов управления (3 колонки по 1/3 ширины)
        controls_layout = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Метка (1/3 ширины) с переносом текста
        switch_label = ResponsiveLabel(
            text='Включить уведомления:',
            markup=True
        )
        
        # Переключатель (1/3 ширины)
        self.audio_switch = Switch(
            active=False,
            size_hint_x=1/3
        )
        
        # Кнопка (1/3 ширины)
        self.audio_button = Button(
            text='Настройки',
            size_hint_x=1/3,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        
        # Добавляем виджеты в контейнер
        controls_layout.add_widget(switch_label)
        controls_layout.add_widget(self.audio_switch)
        controls_layout.add_widget(self.audio_button)
        
        # Добавляем виджеты в секцию
        audio_section.add_widget(audio_title)
        audio_section.add_widget(controls_layout)
        
        # Добавляем блок аудио уведомлений перед админ-панелью
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(audio_section)
        
        # Добавляем секцию админ-панели
        content_container.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Разделитель
        content_container.add_widget(debug_section)
        
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
        
        # Раздел: Отладочный режим
        print("\n" + "-"*50)
        print("                ОТЛАДОЧНЫЙ РЕЖИМ")
        print("-"*50)
        if hasattr(self, 'debug_switch'):
            debug_state = "ВКЛЮЧЕН (Отладочные логи отображаются в консоли)" if self.debug_switch.active else "ВЫКЛЮЧЕН (Отладочные логи не отображаются в консоли)"
            print(f"{debug_state}")
        else:
            print("Отладочный режим: настройка недоступна")
        print("-"*50)
        
        # Раздел: Времена молитв из базы данных
        print("="*50)
        print("     ИМЕЮЩИЕСЯ ВРЕМЕНА МОЛИТВ В БАЗЕ ДАННЫХ")
        print("="*50 + "\n")
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
            
            # Выводим заголовок таблицы
            separator = "-" * 26
            print(separator)
            print(f"Date     | {today_display} | {tomorrow_display} |")
            print(separator)
            
            # Выводим времена молитв
            for prayer in prayer_columns:
                today_time = prayer_data[today_str].get(prayer, '00:00')
                tomorrow_time = prayer_data[tomorrow_str].get(prayer, '00:00')
                print(f"{prayer:<8} | {today_time} | {tomorrow_time} |")
            
            print(separator + "\n")
                
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
            
            # Сохраняем выбранные азаны для каждого блока
            if hasattr(self, 'selected_azan_spinner'):
                self.db.save_setting('azan_spinner', self.selected_azan_spinner)
                
            if hasattr(self, 'selected_azan_dropdown'):
                self.db.save_setting('azan_dropdown', self.selected_azan_dropdown)
                
            if hasattr(self, 'selected_azan_popup'):
                self.db.save_setting('azan_popup', self.selected_azan_popup)
                
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
                    print(f"[ИНФО] Отладочный режим {status}")
                    
                except Exception as e:
                    print(f"[ОШИБКА] Не удалось обновить отладочный режим: {e}")
                    # Пробуем сохранить состояние напрямую в БД на случай ошибки в логгере
                    try:
                        from data.database import SettingsDatabase
                        db = SettingsDatabase()
                        db.save_setting('debug_mode', '1' if debug_enabled else '0')
                        print("[ИНФО] Значение отладочного режима сохранено напрямую в БД")
                    except Exception as db_error:
                        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Не удалось сохранить состояние отладки: {db_error}")
                
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
