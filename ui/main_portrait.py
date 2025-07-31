from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import locale
from ui.main_portrait_prayer_times import create_prayer_times_layout, create_next_time_layout
from logic.date_formatted import create_gregorian_date_label, create_hijri_date_label, get_formatted_dates

def create_line_label(base_font_size):
    return Label(
        text='―' * 150,  # Много тире для линии
        font_name='FontSourceCodePro-Regular',
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
    
    # Создаем GridLayout для NextTimeName и NextTimeNumbers
    nex_time_layout = create_next_time_layout(self, base_font_size)

    # Добавляем виджеты в layout в нужном порядке
    portrait_layout.add_widget(create_space_label(base_font_size))
    portrait_layout.add_widget(date_hijri_label)
    portrait_layout.add_widget(create_line_label(base_font_size))  # line_label2
    portrait_layout.add_widget(nex_time_layout)
    portrait_layout.add_widget(create_line_label(base_font_size))  # line_label2
    
    # Добавляем layout с временами молитв
    prayer_times_layout = create_prayer_times_layout(self, base_font_size)
    portrait_layout.add_widget(prayer_times_layout)
    
    return portrait_layout
