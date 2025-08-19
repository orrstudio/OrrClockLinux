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

            # Вертикальные линии для трёх колонок
            # Первая линия на 40% (конец первой колонки)
            col1 = self.x + self.width * 0.4
            # Вторая линия на 60% (конец второй колонки, 40% + 20%)
            col2 = self.x + self.width * 0.6
            # Третья линия на 100% (конец третьей колонки, 60% + 40%)
            col3 = self.x + self.width
            
            Line(points=[col1, self.y, col1, self.top], width=1)
            Line(points=[col2, self.y, col2, self.top], width=1)
            Line(points=[col3, self.y, col3, self.top], width=1)

def create_notifications_section(settings_window):
    """Создаёт секцию уведомлений с таблицей 3x3."""

    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(210),
        padding=(dp(30), dp(5), dp(30), dp(5)),
        spacing=dp(5)
    )

    # Таблица
    table = BorderedGridLayout(
        cols=3,
        rows=3,
        size_hint_y=None,
        height=dp(150),
        spacing=0
    )

    # Адаптивные ширины — теперь от ширины таблицы
    def update_col_widths(*args):
        available_width = table.width  # ширина именно таблицы
        table.cols_minimum = {
            0: available_width * 0.4,  # 40% для первой колонки (текст)
            1: available_width * 0.2,  # 20% для второй колонки (переключатель)
            2: available_width * 0.4   # 40% для третьей колонки (кнопка)
        }

    # Привязываем к изменению размеров таблицы
    table.bind(size=lambda *_: update_col_widths())
    update_col_widths()

    # Данные для строк
    rows = [
        ("Voice", 'voice_switch', 'voice_button'),
        ("Visual", 'visual_switch', 'visual_button'),
        ("Adhan", 'azan_switch', 'azan_button')
    ]

    for text, switch_attr, button_attr in rows:
        # 1. Текст (слева по центру вертикально)
        label = Label(
            text=text,
            halign='left',
            valign='middle',
            font_size='22sp',
            bold=False,
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

        # 3. Кнопка с закругленными углами (по центру)
        button_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        button = RoundedButton(
            text="Settings",
            size_hint=(None, None),
            size=(dp(200), dp(35)),  # Увеличена ширина кнопки до 200dp
            border_radius=dp(10)  # Радиус скругления
        )
        button_layout.add_widget(button)
        setattr(settings_window, button_attr, button)
        table.add_widget(button_layout)

    container.add_widget(table)
    settings_window.notifications_section = container
    return container
