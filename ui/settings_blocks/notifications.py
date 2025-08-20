from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty

from ui.components.custom_switch import CustomSwitch
from ui.components.custom_button import RoundedButton


# Список доступных муэдзинов (название, ключ)
MUEZZINS = [
    ('Default Adhan', 'switch_default_adhan'),
    ('Ahmed Al Nufais', 'switch_ahmed_al_nufais'),
    ('Mansour Al Zahrani', 'switch_mansour_al_zahrani'),
    ('Mehdi Yarrahi Fajr', 'switch_mehdi_yarrahi_fajr'),
    ('Mihr Com', 'switch_mihr_com'),
    ('Mishary Rashid Alafasy', 'switch_mishary_rashid_alafasy'),
    ('Old Adhan', 'switch_old_adhan')
]

# Получаем только имена муэдзинов для проверки
MUEZZIN_NAMES = [name for name, _ in MUEZZINS]

def is_valid_muezzin(name):
    """Проверяет, является ли имя муэдзина допустимым."""
    return name in MUEZZIN_NAMES


class MuezzinDialog(ModalView):
    """Диалоговое окно для выбора муэдзина."""
    
    selected_muezzin = StringProperty('')
    callback = ObjectProperty(None)
    
    def __init__(self, current_muezzin, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.5)  # Уменьшаем высоту окна
        self.auto_dismiss = False
        self.background = ''
        self.background_color = (0.1, 0.1, 0.1, 1)  #
        # Проверяем валидность текущего муэдзина
        self.selected_muezzin = current_muezzin if is_valid_muezzin(current_muezzin) else 'Default Adhan'
        
        # Основной контейнер с темным фоном
        self.layout = GridLayout(cols=1, spacing=10, padding=10)
        layout = self.layout  # Сохраняем ссылку для обратной совместимости
        
        # Создаем прямоугольник для фона
        with self.layout.canvas.before:
            self.bg_color = Color(0.1, 0.1, 0.1, 1)  # Темный цвет фона
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        
        def update_rect(instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
            
        self.layout.bind(pos=update_rect, size=update_rect)
        
        # Заголовок
        title = Label(
            text='Select Muezzin',
            size_hint_y=None,
            height=50,
            font_size='24sp',
            bold=True
        )
        layout.add_widget(title)
        
        # Контейнер для списка с прокруткой
        scroll = ScrollView(do_scroll_x=False)
        list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        # Добавляем переключатели для каждого муэдзина
        for name, _ in MUEZZINS:
            btn = ToggleButton(
                text=name,
                group='muezzins',
                size_hint_y=None,
                height=40,
                font_size='22sp',
                background_normal='',
                background_color=(0.2, 0.2, 0.2, 1) if name != self.selected_muezzin else (0.3, 0.5, 0.7, 1)
            )
            btn.state = 'down' if name == self.selected_muezzin else 'normal'
            btn.bind(on_press=lambda x, n=name: self.on_muezzin_selected(n))
            list_layout.add_widget(btn)
        
        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        
        # Кнопка отмены
        btn_cancel = Button(
            text='Cancel',
            size_hint_y=None,
            height=60,
            font_size='28sp',
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        btn_cancel.bind(on_press=self.dismiss)
        layout.add_widget(btn_cancel)
        
        self.add_widget(self.layout)
        
        # Принудительно обновляем размеры после отображения
        Clock.schedule_once(self._update_bg)
    
    def _update_bg(self, dt):
        # Обновляем размеры фона после отображения
        if hasattr(self, 'rect') and self.layout:
            self.rect.size = self.layout.size
            self.rect.pos = self.layout.pos
    
    def on_muezzin_selected(self, muezzin_name):
        """Обработчик выбора муэдзина"""
        self.selected_muezzin = muezzin_name
        if self.callback:
            self.callback(muezzin_name)
        self.dismiss()


class BorderedGridLayout(GridLayout):
    """Обычный GridLayout без границ."""
    pass

def create_notifications_section(settings_window):
    """Создаёт секцию уведомлений с таблицей 3x3."""

    container = GridLayout(
        cols=1,
        size_hint=(1, None),
        height=dp(100),  # Увеличиваем высоту контейнера для отображения всех элементов с отступами
        padding=(dp(10), dp(5), dp(10), dp(5)),
        spacing=dp(5)
    )

    # Таблица
    table = BorderedGridLayout(
        cols=2,  # Две колонки: текст и переключатель
        size_hint_y=None,
        spacing=0
    )
    
    # Вычисляем высоту таблицы на основе количества строк
    row_height = dp(70)  # Высота одной строки
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
        ("Visual Notification", 'visual_switch', '28sp', True, 0, dp(60)),
        ("           At Adhan", 'visual_switch_at_adhan', '22sp', False, 1, dp(30)),
        ("           15 min before", 'visual_switch_15_min', '22sp', False, 1, dp(30)),
        ("           30 min before", 'visual_switch_30_min', '22sp', False, 1, dp(30)),
        ("           45 min before", 'visual_switch_45_min', '22sp', False, 1, dp(30)),
        ("           60 min before", 'visual_switch_60_min', '22sp', False, 1, dp(30)),
        ("Voice Notification", 'voice_switch', '28sp', True, 0, dp(60)),
        ("           At Adhan", 'voice_switch_at_adhan', '22sp', False, 1, dp(30)),
        ("           15 min before", 'voice_switch_15_min', '22sp', False, 1, dp(30)),
        ("           30 min before", 'voice_switch_30_min', '22sp', False, 1, dp(30)),
        ("           45 min before", 'voice_switch_45_min', '22sp', False, 1, dp(30)),
        ("           60 min before", 'voice_switch_60_min', '22sp', False, 1, dp(30)),
        ("Play Adhan", 'switch_play_adhan', '28sp', True, 0, dp(60)),
        ("           Fajr", 'switch_fajr', '22sp', False, 1, dp(30)),
        ("           Dhuhr", 'switch_dhuhr', '22sp', False, 1, dp(30)),
        ("           Asr", 'switch_asr', '22sp', False, 1, dp(30)),
        ("           Maghrib", 'switch_maghrib', '22sp', False, 1, dp(30)),
        ("           Isha", 'switch_isha', '22sp', False, 1, dp(30)),
        ("Choose Muezzin", None, '28sp', True, 0, dp(60)),  # Без переключателя
        ("Muezzin", 'custom_button', '22sp', False, 1, dp(30)),
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
        
        # Если это строка с выбором муэдзина, добавляем отображение текущего выбора
        if text == "Muezzin":
            # Получаем текущий выбранный муэдзин из базы данных с проверкой валидности
            current_muezzin = settings_window.db.get_setting('selected_muezzin', 'Default Adhan')
            if not is_valid_muezzin(current_muezzin):
                current_muezzin = 'Default Adhan'
                settings_window.db.save_setting('selected_muezzin', current_muezzin)
            
            # Обновляем текст и настройки лейбла с выбранным муэдзином
            label.text = current_muezzin
            label.font_size = '22sp'
            label.halign = 'left'
            label.valign = 'middle'
            label.size_hint_x = 0.8
            label.text_size = (dp(300), None)  # Устанавливаем ширину для текста
            label.padding = (dp(55), 0, 0, 0)  # Добавляем отступ слева
            
            # Функция для обновления размера текста с сохранением выравнивания
            def update_muezzin_text_size(inst, val):
                padding = dp(10)
                inst.text_size = (val[0] - padding, None)
                inst.halign = 'left'
                inst.valign = 'middle'
                inst.canvas.ask_update()
            
            # Применяем нашу функцию обновления размера
            label.bind(size=update_muezzin_text_size)
            
            # Сохраняем ссылку на лейбл для обновления текста
            settings_window.muezzin_label = label
            
            # Создаем контейнер для кнопки выбора (аналогично контейнеру для переключателей)
            switch_layout = GridLayout(cols=1, size_hint=(0.2, None), height=dp(40))
            
            # Кнопка выбора
            button_layout = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
                size_hint_x=0.2,
                size_hint_y=1
            )
            button = RoundedButton(
                text='Choose',
                size_hint=(None, None),
                size=(dp(100), dp(40)),
                font_size='16sp'
            )
            
            # Обработчик нажатия на кнопку выбора
            def show_muezzin_dialog(instance):
                current = settings_window.db.get_setting('selected_muezzin', 'Default Adhan')
                dialog = MuezzinDialog(current_muezzin=current)
                
                def on_muezzin_selected(muezzin_name):
                    # Обновляем текст в лейбле
                    settings_window.muezzin_label.text = muezzin_name
                    settings_window.muezzin_label.font_size = '22sp'
                    settings_window.muezzin_label.halign = 'left'
                    settings_window.muezzin_label.valign = 'middle'
                    # Обновляем размер текста с учетом текущей ширины
                    settings_window.muezzin_label.text_size = (settings_window.muezzin_label.width - dp(10), None)
                    # Сохраняем выбор в базу данных
                    settings_window.db.save_setting('selected_muezzin', muezzin_name)
                
                dialog.callback = on_muezzin_selected
                dialog.open()
            
            button.bind(on_press=show_muezzin_dialog)
            switch_layout.add_widget(button)
            
            # Добавляем лейбл и контейнер с кнопкой в таблицу
            table.add_widget(label)
            table.add_widget(switch_layout)
            
            # Пропускаем стандартную обработку для этой строки
            continue

        def update_text_size(inst, val):
            padding = dp(10)  # ваш желаемый отступ слева
            inst.text_size = (val[0] - padding, None)  # уменьшаем ширину на padding
            inst.canvas.ask_update()

        label.bind(size=update_text_size)
        table.add_widget(label)

        # 2. Kivy переключатель (по центру)
        # Обработка кнопки Choose перенесена в начало функции
        if switch_attr is not None and switch_attr != 'custom_button':
            switch_layout = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
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
            table.add_widget(GridLayout(cols=1, size_hint=(0.2, None), height=switch_height))

        # Кнопка удалена

    container.add_widget(table)
    settings_window.notifications_section = container
    return container
