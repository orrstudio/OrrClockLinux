from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import ListProperty

from ui.components.custom_switch import CustomSwitch
from ui.components.custom_button import RoundedButton

class BorderedGridLayout(GridLayout):
    """Обычный GridLayout без границ."""
    pass

def create_notifications_section(settings_window):
    """Создаёт секцию уведомлений с таблицей 3x3."""

    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(1500),  # Увеличиваем высоту контейнера для отображения всех элементов с отступами
        padding=(dp(30), dp(5), dp(30), dp(5)),
        spacing=dp(5)
    )

    # Таблица
    table = BorderedGridLayout(
        cols=2,  # Две колонки: текст и переключатель
        size_hint_y=None,
        spacing=0
    )
    
    # Вычисляем высоту таблицы на основе количества строк
    row_height = dp(50)  # Высота одной строки
    num_rows = 10  # Общее количество строк
    table.height = row_height * num_rows

    # Адаптивные ширины — теперь от ширины таблицы
    def update_col_widths(*args):
        available_width = table.width  # ширина именно таблицы
        table.cols_minimum = {
            0: available_width * 0.8,  # 80% для первой колонки (текст)
            1: available_width * 0.2   # 20% для второй колонки (переключатель)
        }

    # Привязываем к изменению размеров таблицы
    table.bind(size=lambda *_: update_col_widths())
    update_col_widths()
    
    # Данные для строк
    rows = [
        ("Visual Notification", 'visual_switch', '28sp', True, 0, dp(35)),
        ("           At Adhan", 'visual_switch_at_adhan', '22sp', False, 1, dp(30)),
        ("           15 min before", 'visual_switch_15_min', '22sp', False, 1, dp(30)),
        ("           30 min before", 'visual_switch_30_min', '22sp', False, 1, dp(30)),
        ("           45 min before", 'visual_switch_45_min', '22sp', False, 1, dp(30)),
        ("           60 min before", 'visual_switch_60_min', '22sp', False, 1, dp(30)),
        ("           ", None, '12sp', False, 1, dp(10)),
        ("Voice Notification", 'voice_switch', '28sp', True, 0, dp(35)),
        ("           At Adhan", 'voice_switch_at_adhan', '22sp', False, 1, dp(30)),
        ("           15 min before", 'voice_switch_15_min', '22sp', False, 1, dp(30)),
        ("           30 min before", 'voice_switch_30_min', '22sp', False, 1, dp(30)),
        ("           45 min before", 'voice_switch_45_min', '22sp', False, 1, dp(30)),
        ("           60 min before", 'voice_switch_60_min', '22sp', False, 1, dp(30)),
        ("           ", None, '12sp', False, 1, dp(10)),
        ("Play Adhan", 'switch_play_adhan', '28sp', True, 0, dp(35)),
        ("           Fajr", 'switch_fajr', '22sp', False, 1, dp(30)),
        ("           Dhuhr", 'switch_dhuhr', '22sp', False, 1, dp(30)),
        ("           Asr", 'switch_asr', '22sp', False, 1, dp(30)),
        ("           Maghrib", 'switch_maghrib', '22sp', False, 1, dp(30)),
        ("           Isha", 'switch_isha', '22sp', False, 1, dp(30)),
        ("           ", None, '12sp', False, 1, dp(10)),
        ("Choose Muezzin", None, '28sp', True, 0, dp(35)),  # Без переключателя
        ("           Default Adhan", 'switch_default_adhan', '22sp', False, 1, dp(30)),
        ("           Ahmed Al Nufais", 'switch_ahmed_al_nufais', '22sp', False, 1, dp(30)),
        ("           Mansour Al Zahrani", 'switch_mansour_al_zahrani', '22sp', False, 1, dp(30)),
        ("           Mehdi Yarrahi Fajr", 'switch_mehdi_yarrahi_fajr', '22sp', False, 1, dp(30)),
        ("           Mihr Com", 'switch_mihr_com', '22sp', False, 1, dp(30)),
        ("           Mishary Rashid Alafasy", 'switch_mishary_rashid_alafasy', '22sp', False, 1, dp(30)),
        ("           Mishary Rashid Alafasy Fajr", 'switch_mishary_rashid_alafasy_fajr', '22sp', False, 1, dp(30)),
        ("           Old Adhan", 'switch_old_adhan', '22sp', False, 1, dp(30)),
    ]

    for text, switch_attr, font_size, is_bold, _, switch_height in rows:
        # 1. Текст (слева, прижат к низу)
        label = Label(
            text=text,
            font_size=font_size,
            bold=is_bold,
            halign='left',
            valign='bottom',  # Прижимаем текст к низу
            size_hint_x=0.8,
            text_size=(None, None),
            padding=(0, 0, 0, 0)  # Небольшой отступ снизу
        )

        def update_text_size(inst, val):
            padding = dp(30)  # ваш желаемый отступ слева
            inst.text_size = (val[0] - padding, None)  # уменьшаем ширину на padding
            inst.canvas.ask_update()

        label.bind(size=update_text_size)
        table.add_widget(label)

        # 2. Kivy переключатель (по центру)
        # Для строк без переключателя (где switch_attr = None) создаем пустой контейнер
        if switch_attr is not None:
            switch_layout = AnchorLayout(
                anchor_x='center',
                anchor_y='top',
                size_hint=(0.2, None),
                height=switch_height
            )
            # Увеличиваем размер переключателя для заголовков (с font_size='28sp')
            switch_size = (dp(90), dp(30)) if font_size == '28sp' else (dp(60), dp(20))
            switch = CustomSwitch(
                size_hint=(None, None),
                size=switch_size
            )
            switch_layout.add_widget(switch)
            setattr(settings_window, switch_attr, switch)  # Сохраняем ссылку на сам переключатель
            table.add_widget(switch_layout)
        else:
            # Для строк без переключателя добавляем пустой виджет, чтобы сохранить выравнивание
            table.add_widget(BoxLayout(size_hint=(0.2, None), height=switch_height))

        # Кнопка удалена

    container.add_widget(table)
    settings_window.notifications_section = container
    return container
