from datetime import datetime
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

# Словари для конвертации в римские цифры
WEEKDAY_TO_ROMAN = {
    0: 'I',     # Понедельник
    1: 'II',    # Вторник
    2: 'III',   # Среда
    3: 'IV',    # Четверг
    4: 'V',     # Пятница
    5: 'VI',    # Суббота
    6: 'VII'    # Воскресенье
}

MONTH_TO_ROMAN = {
    1: 'I',
    2: 'II',
    3: 'III',
    4: 'IV',
    5: 'V',
    6: 'VI',
    7: 'VII',
    8: 'VIII',
    9: 'IX',
    10: 'X',
    11: 'XI',
    12: 'XII'
}

HIJRI_MONTH_TO_ROMAN = {
    1: 'I',     # Мухаррам
    2: 'II',    # Сафар
    3: 'III',   # Раби аль-авваль
    4: 'IV',    # Раби ас-сани
    5: 'V',     # Джумада аль-уля
    6: 'VI',    # Джумада ас-сани
    7: 'VII',   # Раджаб
    8: 'VIII',  # Шаабан
    9: 'IX',    # Рамадан
    10: 'X',    # Шавваль
    11: 'XI',   # Зу-ль-када
    12: 'XII'   # Зу-ль-хиджа
}

def get_formatted_dates():
    """
    Возвращает отформатированные даты
    Returns:
        dict: Словарь с частями даты и их шрифтами
    """
    current_date = datetime.now()
    
    # Григорианская дата в формате IV - 05.XII.2024
    weekday = current_date.weekday()
    month = current_date.month
    
    # Части даты с указанием шрифтов и размеров
    date_parts = {
        'weekday': {
            'text': f"  -  {WEEKDAY_TO_ROMAN[weekday]}  - ",  # Добавляем разделитель здесь
            'font': 'DalekBold', 
            'font_size': 40
        },
        'day': {
            'text': current_date.strftime('%d'),
            'font': 'FontDSEG7-Light',
            'font_size': 40
        },
        'month': {
            'text': f"/{MONTH_TO_ROMAN[month]}/",
            'font': 'GothicRegular',
            'font_size': 40
        },
        'year': {
            'text': current_date.strftime('%Y'),
            'font': 'FontDSEG7-Light',
            'font_size': 40
        },
        'full_gregorian': f" - {WEEKDAY_TO_ROMAN[weekday]} - {current_date.strftime('%d')}.{MONTH_TO_ROMAN[month]}.{current_date.strftime('%Y')}",
        
        # Части для даты хиджры с размерами
        'hijri_day': {
            'text': '15',
            'font': 'FontDSEG7-Light',
            'font_size': 40
        },
        'hijri_month': {
            'text': f"/{HIJRI_MONTH_TO_ROMAN[12]}/",
            'font': 'GothicRegular',
            'font_size': 40
        },
        'hijri_year': {
            'text': '1445',
            'font': 'FontDSEG7-Light',
            'font_size': 40
        }
    }
    
    return date_parts

def create_gregorian_date_label(base_font_size):
    """
    Создает Label для григорианской даты с разными шрифтами и размерами в одной строке
    
    Args:
        base_font_size (float): Базовый размер шрифта
    
    Returns:
        Label: Label с датой в одной строке
    """
    formatted_dates = get_formatted_dates()
    
    # Получаем размеры для каждой части из словаря или используем значения по умолчанию
    weekday_size = formatted_dates["weekday"].get('font_size', base_font_size * 0.24)
    day_size = formatted_dates["day"].get('font_size', base_font_size * 0.19)
    month_size = formatted_dates["month"].get('font_size', base_font_size * 0.24)
    year_size = formatted_dates["year"].get('font_size', base_font_size * 0.19)
    
    # Формируем текст с разметкой для разных шрифтов и размеров
    marked_text = (
        f'[size={int(weekday_size)}][font=DalekBold]{formatted_dates["weekday"]["text"]}[/font][/size]'
        f'[size={int(day_size)}][font=FontDSEG7-Light]{formatted_dates["day"]["text"]}[/font][/size]'
        f'[size={int(month_size)}][font=GothicRegular]{formatted_dates["month"]["text"]}[/font][/size]'
        f'[size={int(year_size)}][font=FontDSEG7-Light]{formatted_dates["year"]["text"]}[/font][/size]'
    )
    
    # Создаем Label с поддержкой разметки
    date_label = Label(
        text=marked_text,
        markup=True,  # Включаем поддержку разметки
        color=(1, 1, 1, 1),
        size_hint_x=1,
        size_hint_y=None,
        height=base_font_size * 0.3,  # Увеличиваем высоту для разных размеров
        halign='center',
        valign='middle'
    )
    
    return date_label

def create_hijri_date_label(base_font_size):
    """
    Создает Label с датами хиджры и григорианской в одной строке
    
    Args:
        base_font_size (float): Базовый размер шрифта
    
    Returns:
        Label: Label с обеими датами в одной строке
    """
    formatted_dates = get_formatted_dates()
    
    # Рассчитываем базовый размер на основе ширины окна
    window_width = Window.width
    adaptive_base_size = window_width * 0.04  # 4% от ширины окна
    
    # Получаем размеры для каждой части из словаря или используем адаптивные значения
    hijri_day_size = int(adaptive_base_size * 1)    # чуть меньше базового
    hijri_month_size = int(adaptive_base_size * 1.0)
    hijri_year_size = int(adaptive_base_size * 1)   # чуть меньше базового
    greg_weekday_size = int(adaptive_base_size * 1.0)
    greg_day_size = int(adaptive_base_size * 1)      # для дня
    greg_month_size = int(adaptive_base_size * 1.0)
    greg_year_size = int(adaptive_base_size * 1)     # для года
    
    # Формируем текст с разметкой для обеих дат
    marked_text = (
        # Дата хиджры
        f'[size={hijri_year_size}][font=FontDSEG7-Light]{formatted_dates["hijri_year"]["text"]}[/font][/size]'
        f'[size={hijri_month_size}][font=GothicRegular]{formatted_dates["hijri_month"]["text"]}[/font][/size]'
        f'[size={hijri_day_size}][font=FontDSEG7-Light]{formatted_dates["hijri_day"]["text"]}[/font][/size]'
        # Григорианская дата
        f'[size={greg_weekday_size}][font=DalekBold]{formatted_dates["weekday"]["text"]}[/font][/size]'
        f'[size={greg_day_size}][font=FontDSEG7-Light]{formatted_dates["day"]["text"]}[/font][/size]'
        f'[size={greg_month_size}][font=GothicRegular]{formatted_dates["month"]["text"]}[/font][/size]'
        f'[size={greg_year_size}][font=FontDSEG7-Light]{formatted_dates["year"]["text"]}[/font][/size]'
    )
    
    # Создаем Label с поддержкой разметки
    date_label = Label(
        text=marked_text,
        markup=True,
        color=(1, 1, 1, 1),
        size_hint_x=1,
        size_hint_y=None,
        height=window_width * 0.06,  # Высота тоже адаптивная
        halign='center',
        valign='middle',
        text_size=(Window.width, window_width * 0.06)  # Задаем полный размер текста
    )
    
    # Привязываем обновление размеров к изменению размера окна
    Window.bind(width=lambda *args: update_label_size(date_label))
    
    return date_label

def update_label_size(label, *args):
    """
    Обновляет размеры метки при изменении размера окна
    """
    window_width = Window.width
    adaptive_base_size = window_width * 0.04
    
    # Обновляем высоту метки
    label.height = window_width * 0.06
    label.text_size = (window_width, window_width * 0.06)
    
    # Рассчитываем новые размеры
    hijri_day_size = int(adaptive_base_size * 1)
    hijri_month_size = int(adaptive_base_size * 1)
    hijri_year_size = int(adaptive_base_size * 1)
    greg_weekday_size = int(adaptive_base_size * 1)
    greg_day_size = int(adaptive_base_size * 1)
    greg_month_size = int(adaptive_base_size * 1)
    greg_year_size = int(adaptive_base_size * 1)
    
    # Получаем форматированные даты заново
    formatted_dates = get_formatted_dates()
    
    # Обновляем текст с новыми размерами
    marked_text = (
        f'[size={hijri_year_size}][font=FontDSEG7-Light]{formatted_dates["hijri_year"]["text"]}[/font][/size]'
        f'[size={hijri_month_size}][font=GothicRegular]{formatted_dates["hijri_month"]["text"]}[/font][/size]'
        f'[size={hijri_day_size}][font=FontDSEG7-Light]{formatted_dates["hijri_day"]["text"]}[/font][/size]'
        f'[size={greg_weekday_size}][font=DalekBold]{formatted_dates["weekday"]["text"]}[/font][/size]'
        f'[size={greg_day_size}][font=FontDSEG7-Light]{formatted_dates["day"]["text"]}[/font][/size]'
        f'[size={greg_month_size}][font=GothicRegular]{formatted_dates["month"]["text"]}[/font][/size]'
        f'[size={greg_year_size}][font=FontDSEG7-Light]{formatted_dates["year"]["text"]}[/font][/size]'
    )
    
    # Обновляем текст метки
    label.text = marked_text
    label.texture_update()