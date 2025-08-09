from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import locale
from ui.main_portrait_prayer_times import create_prayer_times_layout, PrayerTimesBox
from ui.next_prayer_time_box import NextPrayerTimeBox
from logic.date_formatted import create_gregorian_date_label, create_hijri_date_label, get_formatted_dates

def create_line_label(base_font_size):
    return Label(
        text='―' * 150,  # Много тире для линии
        font_name='FontSourceCodePro-Regular',
        color=(0.6, 0.5, 0.0, 1),  # Темно-желтый цвет для линий
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
    
    # Создаем виджет с временем до следующей молитвы (автообновляется каждую минуту)
    next_time_widget = NextPrayerTimeBox(base_font_size=base_font_size, app=self)

    # Добавляем виджеты в layout в нужном порядке
    portrait_layout.add_widget(create_space_label(base_font_size))  # Пустое пространство
    portrait_layout.add_widget(create_line_label(base_font_size))   # Линия-разделитель
    portrait_layout.add_widget(date_hijri_label)                    # Метка с датой Хиджры
    portrait_layout.add_widget(create_line_label(base_font_size))   # Линия-разделитель
    portrait_layout.add_widget(next_time_widget)                    # Виджет с временем до следующей молитвы
    portrait_layout.add_widget(create_line_label(base_font_size))   # Линия-разделитель
    
    # Добавляем реактивный layout с временами молитв
    self.prayer_times_box = PrayerTimesBox(base_font_size=base_font_size)
    print(f"[DEBUG] create_portrait_widgets: создан self.prayer_times_box = {self.prayer_times_box}, id = {id(self.prayer_times_box)}, type = {type(self.prayer_times_box)}")
    portrait_layout.add_widget(self.prayer_times_box)
    
    return portrait_layout
