from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

def create_prayer_times_layout(self, base_font_size):

    prayer_times_layout = GridLayout(
        cols=2,  # Два столбца: название и время
        size_hint_x=1,  # Занимает всю ширину
        size_hint_y=None,  # Фиксированная высота
        height=base_font_size * 4.0,  # Высота для 6 строк
        padding=(base_font_size * 0.15, 0)   # Отступы по краям layout
    )

    prayer_times = [
        ('Təhəccüd ---', '00:30'),   # Полуночная молитва
        ('İmsak ------', '05:30'),   # Утренняя молитва до восхода
        ('Günəş ------', '05:30'),   # Восход
        ('Günorta ----', '13:00'),   # Полуденная молитва
        ('İkindi -----', '15:00'),   # Послеполуденная молитва
        ('Axşam ------', '16:30'),   # Вечерняя молитва
        ('Gecə -------', '20:30')    # Ночная молитва
    ]

    for prayer_name, prayer_time in prayer_times:
        # Label для названия молитвы
        prayer_name_label = Label(
            text=prayer_name,
            font_name='FontSourceCodePro-Regular',
            font_size=base_font_size * 0.4,  # Маленький размер
            color=(1, 1, 1, 1),  # Белый цвет
            halign='left',
            text_size=(prayer_times_layout.width * 0.6, None),
            size_hint_x=0.75  # Занимает большую часть ширины
        )
        prayer_name_label.bind(size=prayer_name_label.setter('text_size'))

        # Label для времени молитвы
        prayer_time_label = Label(
            text=prayer_time,
            font_name='FontDSEG7-Bold',
            font_size=base_font_size * 0.45,  # Большой размер шрифта
            color=(1, 1, 1, 1),  # Белый цвет
            halign='right',
            text_size=(prayer_times_layout.width * 0.4, None),
            size_hint_x=0.4  # Занимает меньшую часть ширины
        )
        prayer_time_label.bind(size=prayer_time_label.setter('text_size'))

        # Добавляем Labels в layout
        prayer_times_layout.add_widget(prayer_name_label)
        prayer_times_layout.add_widget(prayer_time_label)

    return prayer_times_layout

def create_next_time_layout(self, base_font_size):
    """
    Создает layout для отображения следующего времени молитвы
    
    Args:
        base_font_size (float): Базовый размер шрифта
    
    Returns:
        GridLayout: Layout со следующим временем молитвы
    """
    # Создаем GridLayout для NextTimeName и NextTimeNumbers
    nex_time_layout = GridLayout(
        cols=3,  # Два столбца
        size_hint_x=1,  # Занимает всю ширину
        size_hint_y=None,  # Фиксированная высота
        height=base_font_size * 0.7,  # Высота пропорциональна базовому шрифту
    )

    # Создаем Label для NextTimeName
    next_time_name_1_label = Label(
        text='növbəti\nnamaza',
        font_name='FontSourceCodePro-Regular',
        font_size=base_font_size * 0.2,  # Маленький размер
        color=(1, 1, 1, 1),  # Белый цвет
        size_hint_x=1,  # Занимает всю ширину
        halign='right',  # Выравнивание вправо
    )

    # Создаем Label для NextTimeNumbers
    next_time_numbers_label = Label(
        text='00:00',
        font_name='FontDSEG7-Bold',  # Шрифт как у часиков
        font_size=base_font_size * 0.55,  # Большой размер шрифта
        color=(1, 1, 1, 1),  # Белый цвет
        size_hint_x=1,  # Занимает всю ширину
        halign='center',  # Выравнивание влево
    )

    next_time_name_2_label = Label(
        text='dəqiqə\nqalır',
        font_name='FontSourceCodePro-Regular',
        font_size=base_font_size * 0.2,  # Маленький размер
        color=(1, 1, 1, 1),  # Белый цвет
        size_hint_x=1,  # Занимает всю ширину
        halign='left',  # Выравнивание вправо
    )

    # Добавляем Label в GridLayout
    nex_time_layout.add_widget(next_time_name_1_label)
    nex_time_layout.add_widget(next_time_numbers_label)
    nex_time_layout.add_widget(next_time_name_2_label)
    
    return nex_time_layout
