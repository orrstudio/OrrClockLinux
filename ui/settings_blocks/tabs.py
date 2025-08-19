"""
Модуль для работы с вкладками в окне настроек.
"""

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp, sp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import RoundedRectangle, Color
from kivy.properties import NumericProperty, ObjectProperty

# Инициализируем Window для использования в kv-разметке
Window = Window

# Добавляем Window в глобальный контекст для использования в KV
from kivy.core.window import Window

# Загружаем стили для вкладок
Builder.load_string('''
<CustomTabbedPanel>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    # Адаптивные размеры вкладок (инициализируем значениями по умолчанию)
    tab_width: dp(150)
    tab_height: dp(40)
    background_color: 0.1, 0.1, 0.1, 1
    background_image: ''
    border: [0, 0, 0, 0]  # Убираем границы
    do_default_tab: False
    tab_pos: 'top_mid'
    tab_width_min: dp(100)  # Минимальная ширина вкладки
    
<CustomTabbedPanelHeader>:
    background_color: 0.1, 0.1, 0.1, 1
    background_normal: ''
    background_down: ''
    # Адаптивные стили текста
    color: (1, 1, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
    font_size: sp(20)  # Фиксированный размер шрифта, будет обновляться в коде
    padding: (dp(10), dp(5))  # Уменьшенные отступы
    text_size: self.width - dp(20), None  # Автоматический перенос текста
    halign: 'center'
    valign: 'middle'
    canvas.before:
        Color:
            rgba: (0.2, 0.7, 0.2, 1) if self.state == 'down' else (0.15, 0.15, 0.15, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5, 5, 0, 0]  # Скругляем только верхние углы
    
    # Делаем текст жирным для активной вкладки
    bold: True if self.state == 'down' else False
    
    canvas.before:
        # Адаптивный фон вкладки
        Color:
            rgba: (0.5, 0.5, 0.5, 1) if self.state == 'down' else (0.3, 0.3, 0.3, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(5), dp(5), 0, 0]  # Закругленные углы сверху
''')

# Создаем кастомные классы для вкладок
class CustomTabbedPanel(TabbedPanel):
    """Кастомная панель вкладок с адаптивными размерами."""
    
    def __init__(self, **kwargs):
        # Устанавливаем начальные размеры
        self.tab_width = min(dp(Window.width * 0.3), dp(200))
        self.tab_height = max(dp(Window.height * 0.06), dp(40))
        
        super().__init__(**kwargs)
        
        # Привязываем обновление размеров при изменении окна
        Window.bind(width=self._update_tab_sizes)
        Window.bind(height=self._update_tab_sizes)
        
        # Инициализируем размеры
        self._update_tab_sizes()
    
    def _update_tab_sizes(self, *args):
        """Обновляет размеры вкладок при изменении размеров окна."""
        if not self.get_root_window():
            return
            
        try:
            # Обновляем ширину вкладок (не более 200dp и не менее 30% ширины окна)
            new_width = min(dp(Window.width * 0.3), dp(200))
            new_height = max(dp(Window.height * 0.06), dp(40))
            
            if self.tab_width != new_width or self.tab_height != new_height:
                self.tab_width = new_width
                self.tab_height = new_height
                
                # Обновляем размер шрифта для всех вкладок
                for tab in self.tab_list:
                    if hasattr(tab, 'update_font_size'):
                        tab.update_font_size()
        except Exception as e:
            import traceback
            print(f"Ошибка при обновлении размеров вкладок: {e}")
            print(traceback.format_exc())

class CustomTabbedPanelHeader(TabbedPanelHeader):
    """Кастомный заголовок вкладки с адаптивными размерами."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.1, 0.1, 0.1, 1)
        self.color = (0.8, 0.8, 0.8, 1)
        self.bold = False
        self.markup = True
        self.halign = 'center'
        self.valign = 'middle'
        self.padding = (dp(10), dp(5))
    
    def on_state(self, instance, value):
        if value == 'down':
            self.background_color = (0.2, 0.7, 0.2, 1)
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.background_color = (0.15, 0.15, 0.15, 1)
            self.color = (0.8, 0.8, 0.8, 1)
            self.bold = False
    
    def update_font_size(self):
        """Обновляет размер шрифта в зависимости от размера окна."""
        try:
            if hasattr(self, 'parent') and hasattr(self.parent, 'tab_width'):
                # Размер шрифта зависит от ширины вкладки
                base_size = max(sp(16), min(sp(24), sp(self.parent.tab_width * 0.15)))
                self.font_size = base_size
        except Exception as e:
            # В случае ошибки используем размер по умолчанию
            self.font_size = sp(18)

def create_tab(name):
    """
    Создает вкладку с указанным именем.
    
    Args:
        name (str): Название вкладки
        
    Returns:
        tuple: (CustomTabbedPanelHeader, GridLayout) - заголовок вкладки и её содержимое
    """
    # Создаем вкладку с использованием кастомного класса
    tab = CustomTabbedPanelHeader(text=name)
    
    # Создаем контейнер для содержимого вкладки
    content = GridLayout(
        cols=1,
        spacing=dp(10),
        padding=dp(10),
        size_hint_y=None
    )
    content.bind(minimum_height=content.setter('height'))
    
    # Добавляем контейнер во вкладку
    tab.content = content
    
    return tab, content

def create_tabbed_interface():
    """
    Создает панель с вкладками для настроек.
    
    Returns:
        tuple: (CustomTabbedPanel, dict) - панель с вкладками и словарь с контейнерами вкладок
    """
    # Создаем кастомную панель вкладок с адаптивными размерами
    tab_panel = CustomTabbedPanel(
        tab_pos='top_mid',
        padding=dp(5),  # Внутренний отступ панели
        background_color=(0.1, 0.1, 0.1, 1)
    )
    
    # Создаем вкладки
    theme_tab, theme_content = create_tab('Theme')
    notification_tab, notification_content = create_tab('Notification')
    admin_tab, admin_content = create_tab('Admin Panel')
    
    # Добавляем вкладки на панель
    tab_panel.add_widget(theme_tab)
    tab_panel.add_widget(notification_tab)
    tab_panel.add_widget(admin_tab)
    
    # Словарь для доступа к контейнерам вкладок
    tab_contents = {
        'theme': theme_content,
        'notification': notification_content,
        'admin': admin_content
    }
    
    return tab_panel, tab_contents
