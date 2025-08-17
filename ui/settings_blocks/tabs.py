"""
Модуль для работы с вкладками в окне настроек.
"""

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp

def create_tab(name):
    """
    Создает вкладку с указанным именем.
    
    Args:
        name (str): Название вкладки
        
    Returns:
        tuple: (TabbedPanelHeader, GridLayout) - заголовок вкладки и её содержимое
    """
    # Создаем вкладку
    tab = TabbedPanelHeader(
        text=name,
        font_size=dp(14),
        background_color=(0.2, 0.2, 0.2, 1),
        background_normal='',
        background_down='',
        color=(1, 1, 1, 1)
    )
    
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
        tuple: (TabbedPanel, dict) - панель с вкладками и словарь с контейнерами вкладок
    """
    # Создаем панель вкладок
    tab_panel = TabbedPanel(
        do_default_tab=False,
        tab_width=dp(120),
        tab_height=dp(40),
        background_color=(0.1, 0.1, 0.1, 1),
        border=[0, 0, 0, 0],
        background_image='',
        tab_pos='top_mid'
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
