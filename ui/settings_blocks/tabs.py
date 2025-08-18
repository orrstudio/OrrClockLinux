"""
Модуль для работы с вкладками в окне настроек.
"""

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.lang import Builder

# Загружаем стили для вкладок
Builder.load_string('''
<CustomTabbedPanel>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    tab_width: '200dp'
    tab_height: '50dp'
    background_color: 0.1, 0.1, 0.1, 1
    background_image: ''
    border: [0, 0, 0, 0]  # Убираем границы
    
<CustomTabbedPanelHeader>:
    background_color: 0.1, 0.1, 0.1, 1
    background_normal: ''
    background_down: ''
    # Меняем цвет текста в зависимости от состояния
    color: (1, 1, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
    font_size: '24sp'
    padding: ('15dp', '10dp')
    
    # Делаем текст жирным для активной вкладки
    bold: True if self.state == 'down' else False
    
    canvas.before:
        # Фон вкладки - более светлый для активной
        Color:
            rgba: (0.5, 0.5, 0.5, 1) if self.state == 'down' else (0.5, 0.5, 0.5, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        # Добавляем обводку для активной вкладки
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'down' else (0, 0, 0, 1)
        Line:
            rectangle: (self.x, self.y, self.width, 2)
''')

# Создаем кастомные классы для вкладок
class CustomTabbedPanel(TabbedPanel):
    pass

class CustomTabbedPanelHeader(TabbedPanelHeader):
    pass

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
    # Создаем кастомную панель вкладок
    tab_panel = CustomTabbedPanel(
        do_default_tab=False,
        tab_width=dp(200),  # Ширина вкладки
        tab_height=dp(50),  # Высота вкладки
        tab_pos='top_mid',
        padding=dp(5)  # Внутренний отступ панели
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
