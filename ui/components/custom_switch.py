from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.properties import BooleanProperty, ColorProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.clock import Clock

class CustomSwitch(Widget):
    """Кастомный переключатель с анимацией."""
    
    active = BooleanProperty(False)
    """Состояние переключателя (включен/выключен)."""
    
    thumb_color = ColorProperty([1, 1, 1, 1])
    """Цвет ползунка переключателя."""    
    track_color_active = ColorProperty([0.15, 0.3, 0.15, 1])
    """Цвет фона во включенном состоянии."""
    
    track_color_inactive = ColorProperty([0.2, 0.1, 0.1, 1])
    """Цвет фона в выключенном состоянии."""
    
    thumb_padding = NumericProperty(4)
    """Отступ ползунка от краев."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (60, 30)
        
        # Инициализация графики
        self._track = None
        self._thumb = None
        self._track_color = None
        self._thumb_color = None
        
        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics,
            active=self._update_state
        )
        
        # Инициализация графики
        self._init_graphics()
    
    def _init_graphics(self):
        """Инициализация графических элементов."""
        with self.canvas:
            # Фон (трек)
            self._track_color = Color(*self.track_color_inactive)
            self._track = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.height/2,]
            )
            
            # Ползунок (thumb)
            self._thumb_color = Color(*self.thumb_color)
            self._thumb = RoundedRectangle(
                pos=self._get_thumb_pos(),
                size=(self.height - 2*self.thumb_padding, self.height - 2*self.thumb_padding),
                radius=[(self.height - 2*self.thumb_padding)/2,]
            )
    
    def _get_thumb_pos(self):
        """Возвращает позицию ползунка в зависимости от состояния."""
        if self.active:
            return (self.right - self.height + self.thumb_padding, self.y + self.thumb_padding)
        return (self.x + self.thumb_padding, self.y + self.thumb_padding)
    
    def _update_graphics(self, *args):
        """Обновляет графические элементы при изменении размера/позиции."""
        if None in (self._track, self._thumb):
            return
            
        self._track.pos = self.pos
        self._track.size = self.size
        self._thumb.pos = self._get_thumb_pos()
        self._track.radius = [self.height/2,]
        self._thumb.radius = [(self.height - 2*self.thumb_padding)/2,]
    
    def _update_state(self, *args):
        """Обновляет состояние переключателя с анимацией."""
        if not hasattr(self, '_thumb'):
            return
            
        # Анимация движения ползунка
        anim = Animation(
            pos=self._get_thumb_pos(),
            d=0.2,
            t='out_quad'
        )
        
        # Обновление цвета фона
        if self.active:
            self._track_color.rgba = self.track_color_active
        else:
            self._track_color.rgba = self.track_color_inactive
        
        anim.start(self._thumb)
    
    def on_touch_down(self, touch):
        """Обработчик нажатия на переключатель."""
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return super().on_touch_down(touch)


class CustomMDSwitch(MDAnchorLayout):
    """Адаптер для CustomSwitch с настройками по умолчанию."""
    
    active = BooleanProperty(False)
    """Состояние переключателя (включен/выключен)."""
    
    def __init__(self, width=64, height=36, thumb_padding=4, 
                 thumb_color_active=None, thumb_color_inactive=None, **kwargs):
        """
        Инициализация кастомного переключателя.
        
        Аргументы:
            width: Ширина переключателя в пикселях
            height: Высота переключателя в пикселях
            thumb_padding: Отступ ползунка от краев
            thumb_color_active: Цвет ползунка во включенном состоянии [R,G,B,A]
            thumb_color_inactive: Цвет ползунка в выключенном состоянии [R,G,B,A]
            **kwargs: Дополнительные аргументы для родительского класса
        """
        super().__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        
        # Устанавливаем размеры
        self.size_hint = (None, None)
        self.size = (width, height)
        
        # Цвета ползунка в разных состояниях
        self.thumb_color_active = thumb_color_active or [0, 1, 0, 1]      # ярко-зеленый при включении
        self.thumb_color_inactive = thumb_color_inactive or [1, 0, 0, 1]  # ярко-красный при выключении
        
        # Создаем и настраиваем переключатель
        self.switch = CustomSwitch(
            active=self.active,
            thumb_color=self.thumb_color_inactive,  # Начальный цвет ползунка
            track_color_active=[0.15, 0.3, 0.15, 1],  # тёмно-зелёный трек при включении
            track_color_inactive=[0.2, 0.1, 0.1, 1],  # тёмно-красный трек при выключении
            size=(width, height),
            thumb_padding=thumb_padding
        )
        
        # Привязываем изменение состояния
        self.switch.bind(active=self._on_switch_active)
        self.add_widget(self.switch)
    
    def _on_switch_active(self, instance, value):
        """Обработчик изменения состояния переключателя."""
        self.active = value
        # Меняем цвет ползунка в зависимости от состояния
        if hasattr(self, 'switch') and hasattr(self.switch, '_thumb_color'):
            self.switch._thumb_color.rgba = (
                self.thumb_color_active if value 
                else self.thumb_color_inactive
            )
    
    def on_active(self, instance, value):
        """Обновление состояния при изменении свойства active."""
        if self.switch.active != value:
            self.switch.active = value
