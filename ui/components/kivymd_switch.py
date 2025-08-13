from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.properties import BooleanProperty

class CustomMDSwitch(MDAnchorLayout):
    """Кастомный переключатель на основе MDSwitch с настройками по умолчанию."""
    
    active = BooleanProperty(False)
    """Состояние переключателя (включен/выключен)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        
        # Создаем и настраиваем переключатель
        self.switch = MDSwitch(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            active=self.active,
            thumb_color_active=[0, 1, 0, 1],        # ярко-зелёный "светящийся"
            thumb_color_inactive=[1, 0, 0, 1],      # ярко-красный "светящийся"
            track_color_active=[0.15, 0.3, 0.15, 1], # тёмно-зелёный трек при включении
            track_color_inactive=[0.2, 0.1, 0.1, 1]  # тёмно-красный трек при выключении
        )
        
        # Привязываем изменение состояния
        self.switch.bind(active=self._on_switch_active)
        self.add_widget(self.switch)
    
    def _on_switch_active(self, instance, value):
        """Обработчик изменения состояния переключателя."""
        self.active = value
    
    def on_active(self, instance, value):
        """Обновление состояния при изменении свойства active."""
        if self.switch.active != value:
            self.switch.active = value
