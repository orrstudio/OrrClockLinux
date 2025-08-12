"""
Модуль для работы с всплывающим окном выбора азана (Popup).
Содержит классы и функции для управления всплывающим окном выбора азана в настройках.
"""

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp


def create_azan_popup_section(settings_window):
    """
    Создает секцию с кнопкой для вызова всплывающего окна выбора азана.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        
    Returns:
        GridLayout: Секция с настройкой выбора азана через Popup
    """
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.core.window import Window
    from kivy.clock import Clock
    
    # Секция выбора азана через Popup
    popup_section = GridLayout(
        cols=1,
        size_hint_y=None,
        height=dp(110),  # Такая же высота, как у остальных блоков
        padding=[dp(20), dp(15), dp(20), dp(20)],
        spacing=dp(10),
        size_hint=(1, None)
    )
    
    # Адаптивный заголовок блока с Popup
    popup_title = Label(
        text='Azan (Popup + ListView)',
        color=(1, 1, 1, 1),
        font_size=sp(22),
        size_hint=(1, None),
        height=dp(30),
        halign='left',
        valign='middle',
        text_size=(Window.width - dp(40), None),
        padding=(0, dp(5)),
        shorten=True,
        shorten_from='right'
    )
    
    def update_popup_title_size(*args):
        popup_title.text_size = (Window.width - dp(40), None)
        popup_title.texture_update()
    
    Window.bind(width=update_popup_title_size)
    Clock.schedule_once(update_popup_title_size)
    
    # Кнопка для вызова Popup
    popup_btn = Button(
        text=settings_window.selected_azan_popup if hasattr(settings_window, 'selected_azan_popup') else 'Azan 1',
        size_hint_y=None,
        height=dp(40),
        background_color=(0.3, 0.3, 0.3, 1),
        color=(1, 1, 1, 1),
        font_size=sp(18)
    )
    
    # Привязываем метод показа попапа к кнопке
    popup_btn.bind(on_release=settings_window.show_azan_popup)
    
    # Добавляем элементы в секцию
    popup_section.add_widget(popup_title)
    popup_section.add_widget(popup_btn)
    
    # Сохраняем ссылку на кнопку для последующего обновления
    settings_window.popup_btn = popup_btn
    
    return popup_section


class SelectableButton(RecycleDataViewBehavior, Button):
    """Кнопка для выбора азана в RecycleView"""
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    text = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        """Обновляет атрибуты кнопки при изменении данных"""
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Обработчик нажатия на кнопку"""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Применяет выделение к выбранному элементу"""
        self.selected = is_selected
        if is_selected:
            self.parent.parent.parent.selected_azan = self.text
            _on_azan_selected(self.parent.parent.parent.settings_window, self.text)


class SelectableRecycleBoxLayout(RecycleBoxLayout):
    """Макет с возможностью выбора для RecycleView"""


class AzanRecycleView(RecycleView):
    """RecycleView для отображения списка азанов"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [{'text': f'Azan {i+1}'} for i in range(3)]


def show_azan_popup(settings_window, instance):
    """
    Показывает всплывающее окно с выбором азана.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        instance: Экземпляр кнопки, вызвавшей попап
    """
    # Создаем контейнер для содержимого попапа
    content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
    
    # Создаем RecycleView
    rv = AzanRecycleView()
    rv.viewclass = 'SelectableButton'
    rv.layout_manager = SelectableRecycleBoxLayout(orientation='vertical')
    content.add_widget(rv)
    
    # Кнопка отмены
    btn_cancel = Button(
        text='Cancel',
        size_hint_y=None,
        height=dp(50),
        background_color=(0.7, 0, 0, 1)
    )
    
    # Создаем попап
    popup = Popup(
        title='Select Azan',
        content=content,
        size_hint=(0.8, 0.8),
        auto_dismiss=False
    )
    
    # Сохраняем ссылку на settings_window для доступа из SelectableButton
    content.settings_window = settings_window
    
    # Привязываем кнопку отмены к закрытию попапа
    btn_cancel.bind(on_release=popup.dismiss)
    
    # Добавляем виджеты в контейнер
    content.add_widget(btn_cancel)
    
    # Показываем попап
    popup.open()


def _on_azan_selected(settings_window, azan_text):
    """
    Обработчик выбора азана в попапе.
    
    Args:
        settings_window: Экземпляр SettingsWindow
        azan_text: Выбранный текст азана
    """
    settings_window.selected_azan_popup = azan_text
    if hasattr(settings_window, 'popup_btn'):
        settings_window.popup_btn.text = azan_text
