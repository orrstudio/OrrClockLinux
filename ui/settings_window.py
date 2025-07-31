"""
Settings Window Module.
Реализует минималистичный интерфейс настроек с выбором цвета.

Основные компоненты:
- Компактный заголовок
- Сетка из 9 цветов с выделением активного белой рамкой
- Кнопки Save/Cancel для применения/отмены изменений

Текущая структура:

ModalView (SettingsWindow)
  └─ main_layout (GridLayout)
      ├─ title_layout (GridLayout)
      │    └─ title_label (Label)
      ├─ content_layout (ScrollView)
      │    └─ colors_grid (GridLayout)
      │         └─ color_buttons (ColorButton) x9
      └─ bottom_panel (GridLayout)
           ├─ cancel_button (Button)
           └─ accept_button (Button)

Все компоненты:

1. main_layout:    GridLayout с cols=1, 
                   spacing=dp(0), size_hint=(1, 1)
2. title_layout:   GridLayout с cols=1, 
                   size_hint_y=None, 
                   height=dp(30), 
                   padding=[dp(20), 0]
3. content_layout: ScrollView с do_scroll_x=False, 
                   do_scroll_y=True, 
                   size_hint=(1, 1)
4. colors_grid:    GridLayout с cols=3, 
                   spacing=dp(10), 
                   size_hint_y=None, 
                   padding=[dp(20), dp(10)]
5. bottom_panel:   GridLayout с cols=2, 
                   size_hint_y=None, 
                   height=dp(60), 
                   spacing=dp(10), 
                   padding=[dp(20), dp(5)]

"""

from kivy.uix.modalview import ModalView
from ui.settings_color import ColorButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from data.database import SettingsDatabase
import logging
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
        'magenta': (1, 0, 1, 1),
        'pink': (1, 0.75, 0.8, 1),
        'grey': (0.7, 0.7, 0.7, 1),
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
        self.initial_color = self.db.get_setting('color')
        self.selected_color = self.initial_color
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
        
        # Контент (ScrollView)
        content_layout = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            size_hint=(1, 1)
        )
        
        # Сетка цветов
        colors_grid = GridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            padding=[dp(20), dp(10)]
        )
        colors_grid.bind(minimum_height=colors_grid.setter('height'))
        
        # Создаем кнопки цветов
        for color_name, color_tuple in self.colors.items():
            color_button = ColorButton(
                color_name=color_name,
                color_tuple=color_tuple,
                text='',
                size_hint=(1, None),
                height=dp(50),
                background_normal=''
            )
            color_button.bind(on_release=self._on_color_button_press)
            
            # Сохраняем кнопку если это активный цвет
            if color_name == self.initial_color:
                self.active_button = color_button
            
            colors_grid.add_widget(color_button)
        
        # Добавляем сетку цветов в ScrollView
        content_layout.add_widget(colors_grid)
        
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
            self.border_line = Line(rectangle=(button.x, button.y, button.width, button.height), width=2)
        
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
            
            # Обновляем активную кнопку
            self.active_button = button
            
            # Сохраняем выбранный цвет
            self.selected_color = button.color_name.lower()
        except Exception as e:
            logger.error(f"Error in _on_color_button_press: {e}")

    def on_accept(self, *args):
        """Сохраняет настройки при нажатии кнопки Save."""
        try:
            if self.selected_color:
                # Преобразуем название цвета в нижний регистр
                color_key = self.selected_color.lower()
                
                if color_key in self.colors:
                    # Сохраняем в базу данных
                    self.db.save_setting('color', color_key)
                    
                    # Применяем цвет через callback
                    if self.apply_callback:
                        self.apply_callback(self.colors[color_key])
                else:
                    logger.warning(f"Unknown color: {self.selected_color}")
            self.dismiss()
        except Exception as e:
            logger.error(f"Error in on_accept: {e}")
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
    
    def dismiss(self, *args):
        """При отмене возвращаем исходный цвет"""
        if not self.selected_color or args:  
            if hasattr(self.main_window, 'update_color') and self.initial_color:
                self.main_window.update_color(self.initial_color)
        super().dismiss()
    
    @staticmethod
    def get_color_tuple(color_name):
        """Преобразование названия цвета в RGB"""
        colors = {
            'lime': (0, 1, 0, 1),
            'aqua': (0, 1, 1, 1),
            'blue': (0, 0, 1, 1),
            'red': (1, 0, 0, 1),
            'yellow': (1, 1, 0, 1),
            'magenta': (1, 0, 1, 1),
            'pink': (1, 0.75, 0.8, 1),
            'grey': (0.7, 0.7, 0.7, 1),
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
            (1, 0, 1, 1): 'magenta',
            (1, 0.75, 0.8, 1): 'pink',
            (0.7, 0.7, 0.7, 1): 'grey',
            (1, 1, 1, 1): 'white'
        }
        return colors.get(color_tuple, 'lime')  
