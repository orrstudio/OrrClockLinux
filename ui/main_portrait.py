from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import locale
from ui.main_portrait_prayer_times import create_prayer_times_layout, PrayerTimesBox
from ui.next_prayer_time_box import NextPrayerTimeBox
from logic.date_formatted import create_gregorian_date_label, create_hijri_date_label, get_formatted_dates
from utils.logger import logger

def create_line_label(base_font_size, color=None):
    """
    Создает Label с разделительной линией
    
    Args:
        base_font_size (float): Базовый размер шрифта
        color (tuple, optional): Цвет линии в формате (R, G, B, A). 
                              Если не указан, используется цвет по умолчанию.
    """
    # Если цвет не передан, используем темно-желтый по умолчанию
    line_color = color if color is not None else (0.6, 0.5, 0.0, 1)
    
    return Label(
        text='―' * 150,  # Много тире для линии
        font_name='FontSourceCodePro-Regular',
        color=line_color,
        height=base_font_size * 0.1, # Фиксированная высота
        size_hint_y=None,  # Нужно для фиксированной высоты
    )

def create_space_label(base_font_size):
    return Label(
        text=' ', 
        height=base_font_size * 0.02,  # Фиксированная высота
        size_hint_y=None  # Нужно для фиксированной высоты
    )

def create_portrait_widgets(self, portrait_layout):
    """
    Создает и добавляет виджеты в портретный layout
    
    Args:
        portrait_layout (GridLayout): Layout для добавления виджетов
    
    Returns:
        GridLayout: Layout с добавленными виджетами
    """
    # Устанавливаем локаль для корректного отображения даты
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    
    # Расчет базового размера шрифта
    base_font_size = self.calculate_font_size(scale_factor=0.15)

    # Создаем Label для даты Хиджры (включает обе даты)
    date_hijri_label = create_hijri_date_label(base_font_size)
    
    # Получаем текущую тему из настроек
    from data.database import SettingsDatabase
    from ui.theme_color_schemes import get_theme_scheme
    
    settings_db = SettingsDatabase()
    current_theme = settings_db.get_setting('color', 'lime')  # По умолчанию 'lime'
    theme_colors = get_theme_scheme(current_theme)

    # Создаем Label для даты Хиджры (включает обе даты) с цветом из темы
    date_hijri_label = create_hijri_date_label(base_font_size, color=theme_colors['date_text'])
    
    # Сохраняем ссылку на метку даты в основном классе приложения
    self.date_hijri_label = date_hijri_label
    
    # Создаем виджет с временем до следующей молитвы (автообновляется каждую минуту)
    next_time_widget = NextPrayerTimeBox(base_font_size=base_font_size, app=self)
    self.next_prayer_time_box = next_time_widget  # Сохраняем ссылку на виджет в MainWindowApp
    
    # Устанавливаем текущую цветовую схему для next_prayer_time_box
    next_time_widget.update_colors(current_theme)

    # Создаем разделительные линии и сохраняем ссылки на них
    separator1 = create_line_label(base_font_size, color=theme_colors['separator'])
    separator2 = create_line_label(base_font_size, color=theme_colors['separator'])
    separator3 = create_line_label(base_font_size, color=theme_colors['separator'])
    
    # Сохраняем ссылки на разделители в основном классе приложения
    if not hasattr(self, 'separator_lines'):
        self.separator_lines = []
    self.separator_lines.extend([separator1, separator2, separator3])

    # Добавляем виджеты в layout в нужном порядке
    portrait_layout.add_widget(create_space_label(base_font_size))  # Пустое пространство
    portrait_layout.add_widget(separator1)                          # Первая линия-разделитель
    portrait_layout.add_widget(date_hijri_label)                    # Метка с датой Хиджры
    portrait_layout.add_widget(separator2)                          # Вторая линия-разделитель
    portrait_layout.add_widget(next_time_widget)                    # Виджет с временем до следующей молитвы
    portrait_layout.add_widget(separator3)                          # Третья линия-разделитель
    
    # Создаем реактивный layout с временами молитв
    self.prayer_times_box = PrayerTimesBox(base_font_size=base_font_size)
    
    # Устанавливаем текущую цветовую схему
    self.prayer_times_box.update_colors(current_theme)
    
    from kivy.logger import Logger
    Logger.debug(f'Created prayer_times_box: {type(self.prayer_times_box).__name__} (id: {id(self.prayer_times_box)}) with theme: {current_theme}')
    
    # Связываем NextPrayerTimeBox с PrayerTimesBox для синхронизации анимаций
    next_time_widget.prayer_times_box = self.prayer_times_box
    Logger.debug('Linked NextPrayerTimeBox with PrayerTimesBox for animation synchronization')
    
    # Добавляем виджет в layout
    portrait_layout.add_widget(self.prayer_times_box)
    
    return portrait_layout
