from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import ListProperty

from ui.components.custom_switch import CustomSwitch
from ui.components.custom_button import RoundedButton

class BorderedGridLayout(GridLayout):
    """GridLayout с границами и адаптивными линиями."""
    border_color = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*self.border_color)
            # Внешняя рамка
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

            # Вертикальные линии для двух колонок
            # Линия на 80% (конец первой колонки)
            col1 = self.x + self.width * 0.8
            # Линия на 100% (конец второй колонки)
            col2 = self.x + self.width
            
            Line(points=[col1, self.y, col1, self.top], width=1)
            Line(points=[col2, self.y, col2, self.top], width=1)

def create_notifications_section(settings_window):
    """Создаёт секцию уведомлений с таблицей 3x3."""

    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(750),  # Увеличиваем высоту контейнера для отображения всех элементов
        padding=(dp(30), dp(5), dp(30), dp(5)),
        spacing=dp(5)
    )

    # Таблица
    table = BorderedGridLayout(
        cols=2,  # Две колонки: текст и переключатель
        rows=14,  # 14 строк: заголовок + 5 настроек уведомлений + Play Adhan + 7 намазов
        size_hint_y=None,
        height=dp(700),  # Увеличиваем высоту для отображения всех строк
        spacing=0
    )

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
        ("Voice Notification", 'voice_switch', '24sp', True, 0),
        ("           At Adhan", 'switch_at_adhan', '20sp', False, 1),
        ("           15 min before", 'switch_15_min', '20sp', False, 1),
        ("           30 min before", 'switch_30_min', '20sp', False, 1),
        ("           45 min before", 'switch_45_min', '20sp', False, 1),
        ("           60 min before", 'switch_60_min', '20sp', False, 1),
        ("Play Adhan", 'switch_play_adhan', '24sp', True, 0),
        ("           Fajr", 'switch_fajr', '20sp', False, 1),
        ("           Dhuhr", 'switch_dhuhr', '20sp', False, 1),
        ("           Asr", 'switch_asr', '20sp', False, 1),
        ("           Maghrib", 'switch_maghrib', '20sp', False, 1),
        ("           Isha", 'switch_isha', '20sp', False, 1),
    ]

    for text, switch_attr, font_size, is_bold, _ in rows:
        # 1. Текст (слева по центру вертикально)
        label = Label(
            text=text,
            font_size=font_size,
            bold=is_bold,
            halign='left',
            valign='middle',
            size_hint_x=0.8
        )

        def update_text_size(inst, val):
            padding = dp(30)  # ваш желаемый отступ слева
            inst.text_size = (val[0] - padding, None)  # уменьшаем ширину на padding
            inst.canvas.ask_update()

        label.bind(size=update_text_size)
        table.add_widget(label)

        # 2. Kivy переключатель (по центру)
        switch_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        switch = CustomSwitch(
            size_hint=(None, None),
            size=(dp(100), dp(40))  # Увеличена ширина переключателя до 100dp
        )
        switch_layout.add_widget(switch)
        setattr(settings_window, switch_attr, switch)  # Сохраняем ссылку на сам переключатель
        table.add_widget(switch_layout)

        # Кнопка удалена

    container.add_widget(table)
    settings_window.notifications_section = container
    return container
